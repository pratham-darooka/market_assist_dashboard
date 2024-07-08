import asyncio

from app.utils.trading_period import is_market_open, need_run_update_script
import time
from loguru import logger
from app.db.common import DB, Stocks
from app.utils.helpers import purify_symbol


async def fetch_and_update_price_bulk(stock_ids: list[int]):
    supabase_ = DB()
    stocks = Stocks()
    stock_data = supabase_.fetch_records("stocks", ('id', 'in', tuple(stock_ids)))

    latest_futures_price_data_bulk = []
    next_futures_price_data_bulk = []
    last_futures_price_data_bulk = []

    for stock in stock_data:
        try:
            symbol = purify_symbol(stock['stock_symbol'])
            equity_price_data = await stocks.get_equity_quote(stock['id'], symbol)
            supabase_.update_records('stock_prices_equity', equity_price_data)
        except Exception as e:
            logger.error(f"Error updating stock: {stock['stock_symbol']}: {e}")
            raise Exception

        try:
            if stock['lot_size'] > 0:
                futures_quote = await stocks.get_futures_quote(stock['id'], symbol)

                if futures_quote[0] != {}:
                    latest_futures_price_data_bulk.extend([futures_quote[0]])
                if futures_quote[1] != {}:
                    next_futures_price_data_bulk.extend([futures_quote[1]])
                if futures_quote[2] != {}:
                    last_futures_price_data_bulk.extend([futures_quote[2]])

                if latest_futures_price_data_bulk:
                    supabase_.update_records('stock_prices_futures_latest_expiry', latest_futures_price_data_bulk)
                if next_futures_price_data_bulk:
                    supabase_.update_records('stock_prices_futures_next_expiry', next_futures_price_data_bulk)
                if last_futures_price_data_bulk:
                    supabase_.update_records('stock_prices_futures_last_expiry', last_futures_price_data_bulk)
        except Exception as e:
            logger.error(f"Error updating futures: {stock['stock_symbol']}: {e}")
            raise Exception


async def update_all_stocks_concurrently(stock_ids: list[int]):
    logger.info("Updating stocks")
    batch_size = 20  # Number of stocks to process in a single batch
    tasks = []
    for i in range(0, len(stock_ids), batch_size):
        batch = stock_ids[i:i + batch_size]
        tasks.append(fetch_and_update_price_bulk(batch))
    await asyncio.gather(*tasks)


async def main(all_stocks_list=None, fno_stocks_list=None):
    if fno_stocks_list is None:
        await update_all_stocks_concurrently([stock['id'] for stock in all_stocks_list])
    elif all_stocks_list is None:
        await update_all_stocks_concurrently([stock['id'] for stock in fno_stocks_list])
    else:
        logger.error("No stocks input")


if __name__ == "__main__":
    supabase = DB()

    all_stocks = supabase.fetch_records('stocks')
    fno_stocks = supabase.fetch_records('fno_stocks')

    while True:
        # if not need_run_update_script():
        #     logger.info("No need to run updates, already updated!")
        #     break

        if not is_market_open():
            asyncio.run(main(fno_stocks_list=fno_stocks))
            logger.info("No need to run further updates, market closed!")
            break
        else:
            asyncio.run(main(fno_stocks_list=all_stocks))

        time.sleep(1)
