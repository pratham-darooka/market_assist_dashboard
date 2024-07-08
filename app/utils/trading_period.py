from datetime import datetime, time, timedelta
import pytz
import streamlit as st
from dateutil.parser import parse
from app.db.common import DB
from nsepythonserver import nse_holidays
from loguru import logger
from icecream import ic

def is_market_open():
    # Define IST timezone
    ist = pytz.timezone('Asia/Kolkata')

    # Get current time in IST
    now = datetime.now(ist)

    # Define market open and close times
    market_open = time(9, 15)
    market_close = time(15, 30)

    # Check if today is a weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # Saturday or Sunday
        logger.info("Market closed today!")
        return False

    # Check if current time is within trading hours
    if market_open <= now.time() <= market_close and not is_holiday_today():
        return True

    logger.info("Market closed today!")
    return False


def is_holiday_today():
    try:
        # Get the list of holidays for the current market
        holidays = nse_holidays()['FO']

        # Get today's date
        today = datetime.now().strftime('%d-%b-%Y')

        # Check if today is a holiday
        is_holiday = any(holiday['tradingDate'] == today for holiday in holidays)

        if is_holiday:
            return True
        else:
            return False
    except:
        return True


def display_market_status():
    if is_market_open():
        html = f"""
        <h1 style="font-size: 40px; font-weight: bold; color: green; text-align: center;">Market Status: Open 🏢</h1>
        """
        st.markdown(html, unsafe_allow_html=True)

        with st.sidebar:
            reset = st.button("Reset Dashboard", type="primary")
            if reset:
                st.switch_page('landing.py')
    else:
        html = f"""
        <h1 style="font-size: 40px; font-weight: bold; color: red; text-align: center;">Market Status: Closed 🚫</h1>
        """
        st.markdown(html, unsafe_allow_html=True)

        with st.sidebar:
            reset = st.button("Reset Dashboard", type="primary")
            if reset:
                st.switch_page('landing.py')

def get_last_trading_day(now):
    ist = pytz.timezone('Asia/Kolkata')
    market_close_time = time(15, 30)
    
    if now.weekday() == 5:  # Saturday
        last_trading_day = now - timedelta(days=1)
    elif now.weekday() == 6:  # Sunday
        last_trading_day = now - timedelta(days=2)
    elif now.time() <= market_close_time:  # If current time is before or equal to market close time today
        last_trading_day = now
    else:
        last_trading_day = now - timedelta(days=1)
    
    # Adjust last_trading_day to the latest weekday before today, if today is a weekend day
    while last_trading_day.weekday() >= 5:  # Skip weekend days
        last_trading_day -= timedelta(days=1)
    
    last_trading_day = last_trading_day.replace(hour=15, minute=30, second=0, microsecond=0)
    return last_trading_day

@logger.catch
def need_run_update_script(table_name='stock_prices_equity'):
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    supabase = DB()
    response = supabase.fetch_records(table_name, sort_by_updated=True, limit=50)
    
    if not response:
        logger.info(f"No data found in '{table_name}'.")
        return True
    
    # Get the most recent update time
    update_times = [parse(record['updated_at']).astimezone(ist) for record in response]
    average_update_time = sum((ut - datetime(1970, 1, 1, tzinfo=ist)).total_seconds() for ut in update_times) / len(update_times)
    average_update_time = datetime.fromtimestamp(average_update_time, tz=ist)
    logger.info(f"Average update time: {average_update_time}")

    # Determine the last trading day
    last_trading_day = get_last_trading_day(now)
    logger.info(f"Last trading day: {last_trading_day}")

    # Check if the latest update time is before the last trading day
    if average_update_time < last_trading_day:
        logger.info(f"Latest update is before the last trading day. Need to update {table_name}.")
        return True

    logger.info(f"No update needed for {table_name}.")
    return False


if __name__ == "__main__":
    ic(is_market_open())
    ic(need_run_update_script('stock_prices_equity'))
    ic(need_run_update_script('stock_prices_futures_latest_expiry'))
    ic(need_run_update_script('index_prices'))
    ic(need_run_update_script('moneycontrol_data'))
    
