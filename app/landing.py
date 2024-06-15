import streamlit as st
from streamlit_lottie import st_lottie
from utils.trading_period import display_market_status
from utils.services import trigger_update_jobs

st.set_page_config(layout="wide", page_title="Market Assist", page_icon="\U0001F4C8", initial_sidebar_state="collapsed")

if __name__ == "__main__":    
    display_market_status()

    with st.container():
        nav_bar_item1, nav_bar_item2, nav_bar_item3, nav_bar_item4, nav_bar_item5 = st.columns(5)

        with nav_bar_item1:
            cash = st.button("Equity", use_container_width=True)
            if cash:
                st.switch_page("pages/equity.py")

        with nav_bar_item2:
            futures = st.button("Futures", use_container_width=True)
            if futures:
                st.switch_page("pages/futures.py")

        with nav_bar_item3:
            indices = st.button("Indices", use_container_width=True)
            if indices:
                st.switch_page("pages/indices.py")

        with nav_bar_item4:
            trading_screen = st.button("Options", use_container_width=True)
            if trading_screen:
                st.switch_page("pages/options.py")

        with nav_bar_item5:
            news = st.button("Today's Headlines", use_container_width=True)
            if news:
                st.switch_page("pages/news.py")

    _, lottie, _ = st.columns(3)
    with lottie:
        st.markdown("<h1 style='text-align: center;'>Welcome to Market Assist!</h1>", unsafe_allow_html=True)
        st_lottie("https://lottie.host/836ee98f-16f5-4a44-a95a-3e72c45a9e35/SEABuyXqck.json", quality="low", height=500,
                  width=500)

    trigger_update_jobs()

    st.toast("Setting up screen", icon='👀')