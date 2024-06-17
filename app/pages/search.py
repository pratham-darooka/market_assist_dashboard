from app.utils.trading_period import display_market_status
from app.utils.whats_happening import fetch_and_parse_perplexity_output
from app.db.common import DB
import streamlit as st

st.set_page_config(layout="wide", page_title="Market Assist", page_icon="\U0001F4C8", initial_sidebar_state="collapsed")

if __name__ == "__main__":
    supabase = DB()

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

    search_results = supabase.search_stocks(st.session_state.stock_info_code)

    if len(search_results) > 1:
        with stock_info.container():
            st.title(f"_Top search results for..._ **{st.session_state.stock_info_code.upper()}**")
            stock_selection = st.radio(
                "Select the most relevant search result",
                [f"{result['company_name']}" for result in search_results[:15]],
                captions=[f"NSE Symbol: {result['stock_symbol']}" for result in search_results[:10]],
                index=None)
            if stock_selection:
                st.session_state.stock_info_co_name = stock_selection
                st.switch_page('pages/stock_info.py')
    elif len(search_results) == 1:
        st.session_state.stock_info_co_name = search_results[0]['company_name']
        st.switch_page('pages/stock_info.py')
    else:
        with stock_info.container():
            # st.title(f"_Nothing found for..._ **{st.session_state.stock_info_code.upper()}**")
            # back = st.button("Go Back!", type="primary", use_container_width=True)
            # if back:
            #     st.switch_page(f'pages/{st.session_state.referrer}.py')
            title = st.empty()
            
            with title:
                st.title(f"_Asking AI for..._ **{st.session_state.stock_info_code.title()}**")
            st.markdown(fetch_and_parse_perplexity_output(st.session_state.stock_info_code)['llm'])
            with title:
                st.title(f"_AI Response for..._ **{st.session_state.stock_info_code.title()}**")
            
            back = st.button("Go Back!", type="primary", use_container_width=True)
            if back:
                st.switch_page(f'pages/{st.session_state.referrer}.py')