from datetime import datetime, time, timedelta
import pytz


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
    import streamlit as st

    if is_market_open():
        html = f"""
        <h1 style="font-size: 40px; font-weight: bold; color: green; text-align: center;">Market Status: Open 🏢</h1>
        """
        st.markdown(html, unsafe_allow_html=True)
    else:
        html = f"""
        <h1 style="font-size: 40px; font-weight: bold; color: red; text-align: center;">Market Status: Closed 🚫</h1>
        """
        st.markdown(html, unsafe_allow_html=True)


if __name__ == "__main__":
    print(is_market_open())
