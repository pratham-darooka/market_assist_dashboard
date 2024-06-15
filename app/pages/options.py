import streamlit as st
from streamlit_lottie import st_lottie
from utils.trading_period import display_market_status
from app.db.supabase_engine import SupabaseSingleton

st.set_page_config(layout="wide", page_title="Market Assist", page_icon="\U0001F4C8", initial_sidebar_state="collapsed")

if __name__ == "__main__":
    supabase = SupabaseSingleton()

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
            trading_screen = st.button("Options", use_container_width=True, type="primary")
            if trading_screen:
                st.switch_page("pages/options.py")

        with nav_bar_item5:
            news = st.button("Today's Headlines", use_container_width=True)
            if news:
                st.switch_page("pages/news.py")
    
    st.title("Page under maintainance...!!!")

    import pandas as pd
    import streamlit as st
    from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

    df = pd.DataFrame(supabase.table('stock_prices_equity_cash_view').select("*").execute().data)

    # select the columns you want the users to see
    gb = GridOptionsBuilder.from_dataframe(df)
    # configure selection
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_side_bar()
    gridOptions = gb.build()

    data = AgGrid(df,
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                # update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                key="options"
                )

    selected_rows = data["selected_rows"]

    if selected_rows is not None:
        if len(selected_rows) != 0:
            with st.container():
                st.markdown("##### Name")
                st.markdown(f":orange[{selected_rows}]")