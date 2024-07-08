import os
import time

import requests
from concurrent.futures import ThreadPoolExecutor
from app.db.supabase_engine import SupabaseSingleton
from app.db.common import DB
from app.utils.trading_period import is_market_open, need_run_update_script
from loguru import logger
from tenacity import retry, wait_fixed, stop_after_attempt


def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure we catch HTTP errors
    return response.json()


@retry(stop=stop_after_attempt(4), wait=wait_fixed(15))
def gather_data(mc_code, headers, price_headers):
    data = {"code": mc_code}

    urls = {
        "insights": f"https://api.moneycontrol.com/mcapi/extdata/v2/mc-insights?scId={mc_code}&type=c&deviceType=W",
        "daily_technicals": f"https://api.moneycontrol.com/mcapi/technicals/v2/details?scId={mc_code}&dur=D&deviceType=W",
        "weekly_technicals": f"https://api.moneycontrol.com/mcapi/technicals/v2/details?scId={mc_code}&dur=W&deviceType=W",
        "monthly_technicals": f"https://api.moneycontrol.com/mcapi/technicals/v2/details?scId={mc_code}&dur=M&deviceType=W",
        "analyst_ratings": f"https://api.moneycontrol.com/mcapi/v1/stock/estimates/analyst-rating?deviceType=W&scId={mc_code}&ex=N",
        "annual_earnings_forecast": f"https://api.moneycontrol.com/mcapi/v1/stock/estimates/earning-forecast?scId={mc_code}&ex=N&deviceType=W&frequency=12&financialType=C",
        "quarterly_earnings_forecast": f"https://api.moneycontrol.com/mcapi/v1/stock/estimates/earning-forecast?scId={mc_code}&ex=N&deviceType=W&frequency=3&financialType=C",
        "valuations": f"https://api.moneycontrol.com/mcapi/v1/stock/estimates/valuation?deviceType=W&scId={mc_code}&ex=N&financialType=C",
        "historical_earnings": f"https://api.moneycontrol.com/mcapi/v1/stock/estimates/hits-misses?deviceType=W&scId={mc_code}&ex=N&type=eps&financialType=C",
        "essential_questions": f"https://api.moneycontrol.com/mcapi/extdata/v2/mc-essentials?scId={mc_code}&type=ed&deviceType=W",
        "metadata": f"https://priceapi.moneycontrol.com/pricefeed/nse/equitycash/{mc_code}"
    }

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_data, url, headers if 'priceapi' not in url else price_headers): key for
                   key, url in urls.items()}
        for future in futures:
            key = futures[future]
            try:
                data[key] = future.result()['data']
            except Exception as e:
                logger.error(f"Error fetching {key} for {mc_code}: {e}")
                data[key] = None

    logger.info(f"Updated MC data for {mc_code}: {data}")

    return data


def main():
    supabase_engine = SupabaseSingleton()
    supabase = DB()
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Site': 'same-site',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Host': 'api.moneycontrol.com',
        'Origin': 'https://www.moneycontrol.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15 Ddg/16.6',
        'Connection': 'keep-alive',
        'Referer': 'https://www.moneycontrol.com/',
        'Sec-Fetch-Dest': 'empty',
        'auth-token': os.environ['MC_AUTH_TOKEN']
    }

    price_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Fetch-Site': 'same-site',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Mode': 'cors',
        'Host': 'priceapi.moneycontrol.com',
        'Origin': 'https://www.moneycontrol.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15 Ddg/16.6',
        'Connection': 'keep-alive',
        'Referer': 'https://www.moneycontrol.com/',
        'Sec-Fetch-Dest': 'empty',
        'auth-token': os.environ['MC_AUTH_TOKEN']
    }

    if is_market_open():
        mc_stocks = supabase_engine.table("moneycontrol_data").select("*, stocks(lot_size)").filter("stocks.lot_size", "gt", 0).execute().data
    else:
        mc_stocks = supabase.fetch_records('moneycontrol_data', )

    for item in mc_stocks:
        mc_code = item['code']
        upsert_dict = {"code": mc_code, 'name': item['name'], 'id': item['id']}
        upsert_dict.update(gather_data(mc_code, headers, price_headers))

        supabase.update_records('moneycontrol_data', upsert_dict)


if __name__ == "__main__":
    while True:
        # if not need_run_update_script('moneycontrol_data'):
        #     logger.info("No need to run updates, already updated!")
        #     break

        main()

        if not is_market_open():
            logger.info("No need to run further updates, market closed!")
            break

        time.sleep(60 * 60)
