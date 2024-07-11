try:
    import time
    import streamlit as st
    from app.utils.trading_period import is_market_open, display_market_status
    from app.db.common import DB, Stocks
    import pandas as pd
    from loguru import logger
except:
    import streamlit as st
    st.switch_page('landing.py')

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
            indices = st.button("Indices", use_container_width=True, type="primary")
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

    with st.container():
        all_indices, constituents = st.columns([3.4, 5])

        with all_indices:
            with st.container():
                title, dropdown = st.columns(2)

                with title:
                    st.header("Indices")

                with dropdown:
                    indices_df = pd.DataFrame(supabase.fetch_records('index_price_view'))
                    indices_df.set_index('Index', inplace=True)
                    st.session_state.index_selected = st.selectbox("Select index to see constituents:", ['All'] + indices_df.index.tolist(),
                                         index=0,
                                         label_visibility="collapsed")

                indices_container_placeholder = st.empty()


        with constituents:
            with st.container(border=True, height=600):
                name, search_bar = st.columns(2)

                with name:
                    name_container = st.empty()

                with search_bar:
                    stock_query = st.text_input("Find out what's happening...",
                                                placeholder="Enter stock name...",
                                                label_visibility="collapsed")
                    search_button = st.button("Check what's happening", use_container_width=True, type="primary")

                    if stock_query or search_button:
                        if stock_query:
                            with st.spinner('Loading...'):
                                st.session_state.stock_info_code = stock_query
                                st.session_state.referrer = "indices"
                                logger.info(f"Stock info search: {st.session_state.stock_info_code}")
                                st.switch_page("pages/search.py")
                        else:
                            st.error("Please enter a search query")
                stocks_container_placeholder = st.empty()

    while True:
        with indices_container_placeholder.container():
            indices_df = pd.DataFrame(supabase.fetch_records('index_price_view'))

            indices_view_df = st.dataframe(
                indices_df,
                on_select='rerun',
                selection_mode="single-row",
                height=525,
                hide_index=True,
            )

            index_selected_rows = indices_view_df.selection.rows

            if index_selected_rows:
                st.session_state.index_selected = indices_df.iloc[index_selected_rows]['Index'].tolist()[0]

        if st.session_state.index_selected != "All":
            with name_container:
                st.header(f"{st.session_state.index_selected} Contributors")
        else:
            with name_container:
                st.header(f"All Stocks")

        with stocks_container_placeholder.container():
            if st.session_state.index_selected == "All":

                latest_cash_df = pd.DataFrame(supabase.fetch_records('stock_prices_equity_indices_view'))
                latest_cash_df = latest_cash_df.sort_values(by="Day Change (%)", ascending=False)

                constituents_view_df = st.dataframe(
                    latest_cash_df, 
                    use_container_width=True, 
                    height=450,
                    hide_index=True,
                    on_select='rerun',
                    selection_mode='single-row',
                    )
                
                constituents_selected_rows = constituents_view_df.selection.rows

                if constituents_selected_rows:
                    selection = latest_cash_df.iloc[constituents_selected_rows]['Stock'].tolist()[0]
                    st.session_state.stock_info_co_name = stock.get_exact_name_from_stock_symbol(selection)
                    st.switch_page('pages/stock_info.py')
                    break

            else:                    
                latest_cash_df = pd.DataFrame(
                    supabase.fetch_records('index_constituents_equity_indices_view', ('Index', 'ilike', f"*{st.session_state.index_selected}*")))
                latest_cash_df = latest_cash_df.sort_values(by="Day Change (%)", ascending=False)

                constituents_view_df = st.dataframe(
                    latest_cash_df, 
                    use_container_width=True, 
                    height=450,
                    hide_index=True,
                    on_select='rerun',
                    selection_mode='single-row',
                    )
                
                constituents_selected_rows = constituents_view_df.selection.rows

                if constituents_selected_rows:
                    selection = latest_cash_df.iloc[constituents_selected_rows]['Stock'].tolist()[0]
                    st.session_state.stock_info_co_name = stock.get_exact_name_from_stock_symbol(selection)
                    st.session_state.user_selection = True
                    break

        if not is_market_open():
            break

        time.sleep(5)
    
    if st.session_state.user_selection:
        st.switch_page('pages/stock_info.py')
