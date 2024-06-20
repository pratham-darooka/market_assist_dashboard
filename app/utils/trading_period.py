from datetime import datetime, time, timedelta
import pytz
import streamlit as st
from dateutil.parser import parse
from app.db.common import DB
from nsepythonserver import nse_holidays
from loguru import logger

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

@logger.catch
def need_run_update_script(table_name='stock_prices_equity', ttl=1):
    ist = pytz.timezone('Asia/Kolkata')
    market_end_time = time(15, 30)

    supabase = DB()
    response = supabase.fetch_records(table_name, sort_by_updated=True, limit=50)

    updated_at_times = [parse(item['updated_at']).astimezone(ist) for item in response]

    if not updated_at_times:
        logger.info("No data found in 'updated_at' column.")
        return True

    total_timestamp = sum(dt.timestamp() for dt in updated_at_times)
    average_timestamp = total_timestamp / len(updated_at_times)
    average_updated_at = datetime.fromtimestamp(average_timestamp, ist)
    average_time = average_updated_at.time()
    average_day = average_updated_at.weekday()

    now = datetime.now(ist)

    # Check if the average update time is after market end time
    if average_time >= market_end_time:
        logger.info("Average update time is after market end time.")
        return False

    # Check if today is Saturday (5) or Sunday (6) and average update day is Friday (4)
    if now.weekday() >= 5 and average_day == 4:
        logger.info("Today is weekend and average update day is Friday.")
        return False

    # Check if the average update time plus TTL is still valid
    if ttl:
        ttl_duration = timedelta(seconds=ttl)
        average_updated_with_ttl = average_updated_at + ttl_duration
        if average_updated_with_ttl >= now:
            logger.info("TTL condition met, no need to update.")
            return False

    # All conditions passed, we need to run the update
    logger.success("All conditions passed, need to update.")
    return True


if __name__ == "__main__":
    ic(need_run_update_script('stock_prices_equity'))
    ic(need_run_update_script('index_prices'))
    ic(need_run_update_script('moneycontrol_data'))
    
