try:
    import time
    from app.utils.trading_period import display_market_status, is_market_open
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    from app.db.common import DB, Stocks
    from loguru import logger
    from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
except:
    import streamlit as st
    st.switch_page('landing.py')
    

st.set_page_config(layout="wide", page_title="Market Assist", page_icon="\U0001F4C8", initial_sidebar_state="collapsed")

if __name__ == "__main__":
    supabase = DB()
    stock = Stocks()
    st.session_state.stock_info_co_name = None

    display_market_status()

    with st.container():
        nav_bar_item1, nav_bar_item2, nav_bar_item3, nav_bar_item4, nav_bar_item5 = st.columns(5)

        with nav_bar_item1:
            cash = st.button("Equity", use_container_width=True, type="primary")
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

    with st.container(border=True, height=650):
        title, stock_selection = st.columns(2)

        cash_df_container = st.empty()

        with title:
            st.header("All Stocks - Equity")

        with stock_selection:
            input_, button_ = st.columns([3, 1.5])

            with input_:
                stock_query = st.text_input("Find out what's happening...", placeholder="Enter stock name...",
                                            label_visibility="collapsed")
            with button_:
                search_button = st.button("Check what's happening", type="primary")

            if stock_query or search_button:
                if stock_query:
                    with st.spinner('Loading...'):
                        st.session_state.stock_info_code = stock_query
                        st.session_state.referrer = "equity"
                        logger.info(f"Stock info search: {st.session_state.stock_info_code}")
                        st.switch_page("pages/search.py")
                else:
                    st.error("Please enter a search query")

    while True:
        with cash_df_container:
            cash_df = pd.DataFrame(supabase.fetch_records('stock_prices_equity_cash_view'))
            cash_df.sort_values(by="Day Change (%)", ascending=False, inplace=True)

            equity_view_df = st.dataframe(
                cash_df,
                on_select='rerun',
                selection_mode="single-row",
                height=550,
                hide_index=True,
            )
            selected_rows = equity_view_df.selection.rows

            if selected_rows:
                selection = cash_df.iloc[selected_rows]['Stock'].tolist()[0]
                st.session_state.stock_info_co_name = stock.get_exact_name_from_stock_symbol(selection)
                st.session_state.user_selection = True
                break

        if not is_market_open():
            logger.info("Market not open, breaking flow")
            break

        time.sleep(5)
    
    if st.session_state.user_selection:
        st.switch_page('pages/stock_info.py')
