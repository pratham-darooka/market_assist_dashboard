from app.utils.trading_period import display_market_status
from app.db.common import DB, Stocks
import streamlit as st
from app.utils.headlines import fetch_recent_stock_news, format_ddg_news_as_markdown
from app.utils.helpers import display_data
from icecream import ic

st.set_page_config(layout="wide", page_title="Market Assist", page_icon="\U0001F4C8", initial_sidebar_state="collapsed")

if __name__ == "__main__":
    supabase = DB()
    stock = Stocks()

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

    stock_info = st.empty()

    with stock_info.container():
        stock_selected = supabase.fetch_records('stocks', ('company_name', 'eq', st.session_state.stock_info_co_name))[0]
        symbol = stock_selected['stock_symbol']
        name = stock_selected['company_name']

        st.title(f"{name} ({symbol})")
        
        stock_metrics = st.empty()
        stock_analysis = st.empty()

        col1, col2 = st.columns(2)

        with stock_metrics:
            with st.container(border=True):
                st.write("#### Stock Metrics")
                metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

                with metric_col1:
                    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
                
                with metric_col2:
                    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
                
                with metric_col3:
                    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
                
                with metric_col4:
                    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
                
                with metric_col5:
                    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")


        with stock_analysis:
            with st.container(border=True):
                st.write("#### Stock Insights")
                st.write("DEVELOPMENT IN PROGRESS")

        with col1:
            stock_events = st.empty()
        with col2:
            stock_news = st.empty()

        with stock_events:
            with st.container(border=True):
                st.write("#### Recent Corporate Events")
                display_data(stock.get_events(symbol))
        
        with stock_news:
            with st.container(border=True):
                st.markdown(format_ddg_news_as_markdown(fetch_recent_stock_news(name, symbol)))
