from datetime import datetime, time, timedelta
import pytz
import streamlit as st
from dateutil.parser import parse
from app.db.common import DB

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
        return False

    # Check if current time is within trading hours
    if market_open <= now.time() <= market_close:
        return True
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

# Function to determine if the update script needs to be run
def need_run_update_script(table_name='stock_prices_equity'):
    # Define IST timezone
    ist = pytz.timezone('Asia/Kolkata')
    market_end_time = time(15, 30)

    supabase = DB()

    # Query the database to get the `updated_at` column
    response = supabase.fetch_records('stock_prices_equity')

    updated_at_times = [parse(item['updated_at']).astimezone(ist) for item in response]

    if not updated_at_times:
        print("No data found in 'updated_at' column.")
        return False

    # Calculate the average of the `updated_at` times
    total_timestamp = sum(dt.timestamp() for dt in updated_at_times)
    average_timestamp = total_timestamp / len(updated_at_times)
    average_updated_at = datetime.fromtimestamp(average_timestamp, ist)
    average_time = average_updated_at.time()
    average_day = average_updated_at.weekday()

    # Check if the average time is at the end of the trading day
    if average_time == market_end_time:
        return False

    # Check if today is Saturday or Sunday and if the average updated_at is on Friday
    now = datetime.now(ist)
    if now.weekday() >= 5 and average_day == 4:
        return False

    # Check if the market is currently open
    return is_market_open()


if __name__ == "__main__":
    need_run_update_script()
    
