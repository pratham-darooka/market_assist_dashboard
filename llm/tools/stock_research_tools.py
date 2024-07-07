from crewai_tools import BaseTool
from app.db.common import DB

class SearchSymbolTool(BaseTool):
    name : str = 'Get NSE symbol for stock'
    description : str = 'Retrieve a dict with search results for the required stock. Search the stock in the db to fetch possible stock_symbol.'

    def _run(self, stock: str) -> dict:
        supabase = DB()
        return supabase.search_stocks(query=stock)

class PriceDataTool(BaseTool):
    name : str = 'Get stock price data'
    description : str = 'Get current stock price data JSON. Includes equity and futures (all expiry dates, latest being the most recent and last being the most far out).'

    def _run(self, stock_nse_symbol: str) -> dict:
        supabase = DB()

        id = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]['id']

        equity_price_data = supabase.fetch_records('stock_prices_equity', condition=('stock_id', 'eq', id))[0]
        latest_futures_price_data = supabase.fetch_records('stock_prices_futures_latest_expiry', condition=('fno_stock_id', 'eq', id))[0]
        next_futures_price_data = supabase.fetch_records('stock_prices_futures_next_expiry', condition=('fno_stock_id', 'eq', id))[0]
        last_futures_price_data = supabase.fetch_records('stock_prices_futures_last_expiry', condition=('fno_stock_id', 'eq', id))[0]

        return {
            'equity_price_data': equity_price_data,
            'latest_futures_price_data': latest_futures_price_data,
            'next_futures_price_data': next_futures_price_data,
            'last_futures_price_data': last_futures_price_data,
        }

class DailyTechnicalTool(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> dict:
        """Useful to get EMA, SMA, Pivot Levels (in INR) daily technical metrics of a company"""
        supabase = DB()

        id = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]['moneycontrol_id']
        moneycontrol_data = supabase.fetch_records('moneycontrol_data', condition=('id', 'eq', id))[0]['daily_technicals']
        
        return {
            'ema': moneycontrol_data['ema'],
            'sma': moneycontrol_data['sma'],
            'pivotLevels': moneycontrol_data['pivotLevels']
            }

class WeeklyTechnicalTool(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> str:
        """Useful to get EMA, SMA, Pivot Levels (in INR) weekly technical metrics of a company"""
        supabase = DB()

        id = supabase.fetch_records('stocks', condition=('stock_symbol', 'eq', stock_nse_symbol))[0]['moneycontrol_id']
        moneycontrol_data = supabase.fetch_records('moneycontrol_data', condition=('id', 'eq', id))[0]['weekly_technicals']
        
        return {
            'ema': moneycontrol_data['ema'],
            'sma': moneycontrol_data['sma'],
            'pivotLevels': moneycontrol_data['pivotLevels']
            }

class MonthlyTechnicalTool(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> str:
        """Useful to get EMA, SMA, Pivot Levels (in INR) monthly technical metrics of a company"""
        supabase = DB()
        
        id = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]['moneycontrol_id']
        moneycontrol_data = supabase.fetch_records('moneycontrol_data', condition=('id', 'eq', id))[0]['monthly_technicals']
        
        return {
            'ema': moneycontrol_data['ema'],
            'sma': moneycontrol_data['sma'],
            'pivotLevels': moneycontrol_data['pivotLevels']
            }

class AnnualEarningsForecast(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> str:
        """Useful to get annual forward EPS (in INR), revenue (in INR Crores.), net profit (in INR Crores.) projections of a company"""
        supabase = DB()
        
        id = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]['moneycontrol_id']
        moneycontrol_data = supabase.fetch_records('moneycontrol_data', condition=('id', 'eq', id))[0]['annual_earnings_forecast']
        
        return {
            'eps': moneycontrol_data['eps'],
            'revenue': moneycontrol_data['revenue'],
            'netProfit': moneycontrol_data['netProfit']
            }

class QuarterlyEarningsForecast(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> str:
        """Useful to get quarterly forward EPS (in INR), revenue (in INR Crores.), net profit (in INR Crores.) projections of a company"""
        supabase = DB()
        
        id = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]['moneycontrol_id']
        moneycontrol_data = supabase.fetch_records('moneycontrol_data', condition=('id', 'eq', id))[0]['quarterly_earnings_forecast']
        
        return {
            'eps': moneycontrol_data['eps'],
            'revenue': moneycontrol_data['revenue'],
            'netProfit': moneycontrol_data['netProfit']
            }

class HistoricalEarningsHitsOrMiss(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> str:
        """Useful to get quarterly hits/miss for historical EPS (in INR), revenue (in INR Crores.), net profit (in INR Crores.) of a company"""
        supabase = DB()
        
        id = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]['moneycontrol_id']
        moneycontrol_data = supabase.fetch_records('moneycontrol_data', condition=('id', 'eq', id))[0]['historical_earnings']
        
        return {
            'eps': moneycontrol_data['list'],
            }

class FinancialInfo(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> str:
        """Useful to get current financial memtrics of a company like P/B ratio, Book Value, Face Value, P/E ratio, market cap, lot size, dividend yield, etc."""
        supabase = DB()
                
        stock = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]
        id = stock['moneycontrol_id']
        moneycontrol_data = supabase.fetch_records('moneycontrol_data', condition=('id', 'eq', id))[0]['metadata']
        
        return {
            'book-value': moneycontrol_data['BV'],
            'face-value': moneycontrol_data['FV'],
            'price-to-book': moneycontrol_data['PB'],
            'price-to-earnings': moneycontrol_data['PE'],
            'industry-price-to-earnings': moneycontrol_data['IND_PE'],
            'dividend-yield': moneycontrol_data['DYCONS'],
            'market-cap-in-crores': moneycontrol_data['MKTCAP'],
            'lot-size': moneycontrol_data['MKT_LOT'],
            'industry': stock['basic_industry'],
            'sector': stock['sector'],
            }

class IndexConstituent(BaseTool):
    name : str = ''
    description : str = ''

    def _run(self, stock_nse_symbol: str) -> str:
        """Useful to find indices which have the stock as a constituent."""
        supabase = DB()

        stock = supabase.fetch_records(condition=('stock_symbol', 'eq', stock_nse_symbol))[0]
        index_ids = supabase.fetch_records('index_constituents', condition=('stock_id', 'eq', stock['id']))
        index_price_data = []
        for item in index_ids:
            name = supabase.fetch_records('indices', condition=('id', 'eq', item['index_id']))[0]['index_symbol']
            index_price_data.append(
                    {
                        name: supabase.fetch_records('index_prices', condition=('index_id', 'eq', item['index_id']))[0]
                    }
                )

        return index_price_data

if __name__ == "__main__":
    from icecream import ic

    i = IndexConstituent()
    ic(i._run('RELIANCE'))

    a = AnnualEarningsForecast()
    ic(a._run('IDEA'))
    
    q = QuarterlyEarningsForecast()
    ic(q._run('IDEA'))

    f = FinancialInfo()
    ic(f._run('IDEA'))

    sym = SearchSymbolTool()
    ic(sym._run('Reliance'))

    pd = PriceDataTool()
    ic(pd._run('IDEA'))
    
    d = DailyTechnicalTool()
    ic(d._run('IDEA'))
    
    w = WeeklyTechnicalTool()
    ic(w._run('IDEA'))
    
    m = MonthlyTechnicalTool()
    ic(m._run('IDEA'))