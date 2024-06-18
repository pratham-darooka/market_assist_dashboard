import asyncio

from app.utils.trading_period import is_market_open, need_run_update_script
import time
from loguru import logger
from app.db.common import DB
from app.utils.helpers import purify_symbol, purify_prices
from tenacity import retry, stop_after_attempt, wait_fixed
from nsepythonserver import nsefetch
import requests


@retry(stop=stop_after_attempt(2), wait=wait_fixed(5))
async def get_nse_quote(idx_id, symbol):
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={symbol}"
    try:
        quote = nsefetch(url)['data'][0]
        quote_dict = {
            'index_id': idx_id,
            'last_price': quote['lastPrice'],
            'open': quote['open'],
            'previous_close': quote['previousClose'],
            'percent_change': quote['pChange'],
            'change': quote['change'],
            'day_low': quote['dayLow'],
            'day_high': quote['dayHigh'],
        }
        return quote_dict
    except Exception as e:
        logger.error(f"Error fetching NSE data: {e}")


@retry(stop=stop_after_attempt(2), wait=wait_fixed(5))
async def get_bse_quote(idx_id, symbol):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Site": "same-site",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "api.bseindia.com",
        "Sec-Fetch-Mode": "cors",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.bseindia.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15 Ddg/16.6",
        "Connection": "keep-alive",
        "Referer": "https://www.bseindia.com/",
        "Sec-Fetch-Dest": "empty",
        "Priority": "u=0, i"
    }
    url = "https://api.bseindia.com/BseIndiaAPI/api/GetLinknew/w?code=96"
    try:
        session = requests.Session()
        session.trust_env = False

        response = session.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error fetching BSE data: {response.status_code}")

        quote = response.json()
        quote_dict = {
            'index_id': idx_id,
            'last_price': purify_prices(quote['CurrValue']),
            'open': purify_prices(quote['I_open']),
            'previous_close': purify_prices(quote['Prev_Close']),
            'percent_change': purify_prices(quote['ChgPer']),
            'change': purify_prices(quote['Chg']),
            'day_low': purify_prices(quote['Low']),
            'day_high': purify_prices(quote['High']),
        }
        return quote_dict
    except Exception as e:
        logger.error(f"Error fetching BSE data: {e}")


async def fetch_and_update_price(idx_id: int):
    supabase_ = DB()

    try:
        indices = supabase_.fetch_records('indices', ('id', 'eq', idx_id))[0]

        symbol = purify_symbol(indices['index_symbol'])

        if indices['exchange_listed'] == "NSE":
            price_data = await get_nse_quote(idx_id, symbol)
        elif indices['exchange_listed'] == "BSE":
            price_data = await get_bse_quote(idx_id, symbol)
        else:
            price_data = {}
            logger.error("Invalid index exchange!")

        supabase_.update_records('index_prices', price_data)
    except Exception as e:
        logger.error(f"Error updating index {idx_id}: {str(e)}")


async def main(index_list=None):
    if index_list is None:
        index_list = []
    for item in index_list:
        await fetch_and_update_price(item['id'])


if __name__ == "__main__":
    supabase = DB()
    index_list = supabase.fetch_records("indices")
    while True:
        if not need_run_update_script("index_prices"):
            break
        
        asyncio.run(main(index_list))

        if not is_market_open():
            logger.info("No need to run updates, market closed!")
            break

        time.sleep(5)
