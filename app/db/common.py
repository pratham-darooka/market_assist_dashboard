from tenacity import retry, stop_after_attempt, wait_fixed
from nsepythonserver import expiry_list, nsefetch
from icecream import ic

import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
from app.db.supabase_engine import SupabaseSingleton
from loguru import logger
from app.utils.helpers import get_unique_dicts
from datetime import datetime, timedelta
from dateutil.parser import parse


class DB:
    def __init__(self):
        self.supabase = SupabaseSingleton()
        self._all_stocks = None
        self._fno_stocks = None

    @logger.catch
    def _fetch_records(self, table_name, condition=None, sort_by_updated=False):
        records = []
        try:
            if sort_by_updated:
                query = self.supabase.table(table_name).select('*').order('updated_at')
            else:
                query = self.supabase.table(table_name).select('*')

            if condition:
                query = query.filter(*condition)

            records = query.execute().data
            logger.info(f"Fetched {len(records)} records from {table_name}")
        except Exception as e:
            logger.error(f"Error fetching records from {table_name}: {e}")
        return records

    @logger.catch
    def _upsert_records(self, table_name, data):
        try:
            self.supabase.table(table_name).upsert(data).execute()
            logger.info(f"Updated {data} in {table_name}")
        except Exception as e:
            logger.error(f"Error updating {data} in {table_name}: {e}")

    def _fetch_all_stocks(self):
        return self._fetch_records('stocks')

    def _fetch_fno_stocks(self):
        return self._fetch_records('stocks', ('lot_size', 'gt', 0))

    def all_stocks(self):
        if self._all_stocks is None:
            self._all_stocks = self._fetch_all_stocks()
        return self._all_stocks

    def fno_stocks(self):
        if self._fno_stocks is None:
            self._fno_stocks = self._fetch_fno_stocks()
        return self._fno_stocks

    def search_stocks(self, query):
        filter_ = []
        filter_.extend(self._fetch_records('stocks', ('stock_symbol', 'ilike', f"*{query}*")))
        filter_.extend(self._fetch_records('stocks', ('company_name', 'ilike', f"*{query}*")))
        return get_unique_dicts(filter_)

    def fetch_records(self, table_name="stocks", condition=None, sort_by_updated=False):
        return self._fetch_records(table_name, condition, sort_by_updated)

    def update_records(self, table_name, data):
        return self._upsert_records(table_name, data)


class Dates:
    def __init__(self):
        self._latest = None
        self._next = None
        self._last = None
        self.supabase = DB()

    def _convert_date(self, date_str, reverse=False):
        if not reverse:
            # Parse the input date string
            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
            # Convert to the desired format
            formatted_date = date_obj.strftime('%Y-%m-%d')
            return formatted_date
        else:
            # Parse the input date string
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Convert to the desired format
            formatted_date = date_obj.strftime('%d-%b-%Y')
            return formatted_date

    def is_timestamp_old(self, timestamp):
        # Parse the timestamp
        dt = parse(timestamp)

        # Set the timezone to Indian Standard Time (IST)
        dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)

        # Calculate the difference between the timestamp and now
        now = datetime.now(tz=dt.tzinfo)
        diff = now - dt

        # Check if the timestamp is more than 12 hours old
        return diff > timedelta(hours=12)

    @logger.catch
    def dates(self):
        expiry_dates = self.supabase.fetch_records("expiry_dates")

        for dates in expiry_dates:
            if dates['timeline'] == "latest":
                self._latest = self._convert_date(dates["date"], reverse=True)
            elif dates['timeline'] == "next":
                self._next = self._convert_date(dates["date"], reverse=True)
            else:
                self._last = self._convert_date(dates["date"], reverse=True)

        if self.is_timestamp_old(expiry_dates[0]['updated_at']):
            new_dates = expiry_list('RELIANCE')
            date_dict = [
                {"timeline": "last", "date": self._convert_date(new_dates[2])},
                {"timeline": "next", "date": self._convert_date(new_dates[1])},
                {"timeline": "latest", "date": self._convert_date(new_dates[0])},
            ]
            self.supabase.update_records("expiry_dates", date_dict)

        return [self._latest, self._next, self._last]


class Stocks:
    supabase = DB()
    dates = Dates()

    def get_stock_symbol_from_name(self, name):
        return self.supabase.fetch_records('stocks', ('company_name', 'ilike', f'*{name}*'))[0]['stock_symbol']
    
    def get_name_from_stock_symbol(self, symbol):
        return self.supabase.fetch_records('stocks', ('stock_symbol', 'ilike', f'*{symbol}*'))[0]['company_name']

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(5))
    async def get_equity_quote(self, stk_id, symbol):
        equity_quote = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={symbol}")
        trade_info = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=trade_info")
        try:
            last_price = equity_quote['priceInfo']['lastPrice']
            previous_close = equity_quote['priceInfo']['previousClose']
            open_ = equity_quote['priceInfo']['open']
            change = equity_quote['priceInfo']['change']
            percent_change = equity_quote['priceInfo']['pChange']
        except:
            logger.error(f"{symbol} resource error: {equity_quote}")
            return {
                'stock_id': stk_id,
                'change': 0,
                'percent_change': 0,
                'traded_volume': 0,
                'buyers': 0,
                'sellers': 0,
            }

        try:
            traded_volume = trade_info['marketDeptOrderBook']['tradeInfo']['totalTradedVolume']
            buyers = trade_info['marketDeptOrderBook']['totalBuyQuantity']
            sellers = trade_info['marketDeptOrderBook']['totalSellQuantity']
        except:
            logger.error(f"{symbol} resource error: {trade_info}")
            return {
                'stock_id': stk_id,
                'change': 0,
                'percent_change': 0,
                'traded_volume': 0,
                'buyers': 0,
                'sellers': 0,
            }

        return {
            'stock_id': stk_id,
            'last_price': last_price,
            'previous_close': previous_close,
            'open': open_,
            'change': change,
            'percent_change': percent_change,
            'traded_volume': traded_volume,
            'buyers': buyers,
            'sellers': sellers,
        }

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(5))
    async def get_futures_quote(self, stk_id, symbol):
        expiry_dates = self.dates.dates()
        all_derivatives = nsefetch(f"https://www.nseindia.com/api/quote-derivative?symbol={symbol}")['stocks']

        upsert_dicts = [{} for _ in range(3)]
        expiry_idx_map = {expiry: idx for idx, expiry in enumerate(expiry_dates)}

        for derivative in all_derivatives:
            data = derivative['metadata']
            market_book = derivative['marketDeptOrderBook']
            expiry_date = data['expiryDate']

            if data['instrumentType'] == "Stock Futures" and expiry_date in expiry_dates:
                idx = expiry_idx_map[expiry_date]
                upsert_dicts[idx] = {
                    'fno_stock_id': stk_id,
                    'last_price': data['lastPrice'],
                    'previous_close': data['prevClose'],
                    'open': data['openPrice'],
                    'change': data['change'],
                    'percent_change': data['pChange'],
                    'traded_volume': data['numberOfContractsTraded'],
                    'buyers': market_book['totalBuyQuantity'],
                    'sellers': market_book['totalSellQuantity'],
                }
        return tuple(upsert_dicts)


def write_aggrid_df(table, key, height=550, condition=None, selection=True):
    supabase = DB()
    df = pd.DataFrame(supabase.fetch_records(table, condition=condition))

    if selection:
        # select the columns you want the users to see
        gb = GridOptionsBuilder.from_dataframe(df)
        # configure selection
        gb.configure_selection(selection_mode="single", use_checkbox=False)
        gb.configure_side_bar()
        gridOptions = gb.build()

        data = AgGrid(df,
                    gridOptions=gridOptions,
                    enable_enterprise_modules=True,
                    allow_unsafe_jscode=True,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                    autoSizeAllColumns=True,
                    key=key,
                    reload_data=True,
                    theme='material',
                    height=height
                    )

        selected_rows = data["selected_rows"]
        
        return selected_rows
    else:
        # select the columns you want the users to see
        gb = GridOptionsBuilder.from_dataframe(df)
        # configure selection
        gb.configure_side_bar()
        gridOptions = gb.build()

        data = AgGrid(df,
                    gridOptions=gridOptions,
                    enable_enterprise_modules=True,
                    allow_unsafe_jscode=True,
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                    autoSizeAllColumns=True,
                    key=key,
                    reload_data=True,
                    theme='material',
                    height=height
                    )


if __name__ == "__main__":
    # db = DB()
    # ic(db.fetch_records("stock_prices_equity", ('stock_id', 'in', (16, 17, 18)), sort_by_updated=True))
    # ic(db.fetch_records("stocks", ('id', 'in', (16, 17, 18))))

    # dates = Dates()
    # ic(dates.dates())
    #
    stx = Stocks()
    ic(stx.get_stock_symbol_from_name('Reliance Industries Limited'))
    # print(asyncio.run(stx.get_futures_quote(16, 'INFY')))
