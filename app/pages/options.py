try:
    import streamlit as st
    from app.db.common import write_aggrid_df
    from streamlit_lottie import st_lottie
    from utils.trading_period import display_market_status
except:
    import streamlit as st
    st.switch_page('landing.py')

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
            trading_screen = st.button("Options", use_container_width=True, type="primary")
            if trading_screen:
                st.switch_page("pages/options.py")

        with nav_bar_item5:
            news = st.button("Today's Headlines", use_container_width=True)
            if news:
                st.switch_page("pages/news.py")
    
    st.title("Page under maintainance...!!!")
    
    import time
    from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

    a = st.empty()

    @st.cache_data()
    def load_data():
        import pandas as pd
        import numpy as np

        data = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [0, 0, 0]]), columns=['a', 'b', 'c'])
        return data
    
    @st.cache_data()
    def result(a, b):
        return a + b
    
    df = load_data()

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gridOptions = gb.build()

    data = AgGrid(
        df,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        gridOptions=gridOptions,
        # update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        autoSizeAllColumns=True,
        # key=f'equity_{datetime.now()}',
        key=f'equity',
        width="100%",
        reload_data=True,
        theme='alpine',
        height=550,
    )

    selection = data["selected_rows"]

    # Función para actualizar la columna 'c' en el Dataframe.
    def update_c_column(df):
        df['c'] = df.apply(lambda x: result(x['a'], x['b']), axis=1)


    # Activar la actualización
    if st.button("Update 'c' column"):
        update_c_column(df)
        st.write(df)
        # Crea un nuevo AgGrid!!!

    st.write(selection)

    while True:
        data.data = df
        # selected_rows = write_aggrid_df('stock_prices_equity', 'options')

        # if selected_rows is not None:
        #         with st.container():
        #             st.markdown("Stock")
        #             st.markdown(f"{list(selected_rows['stock_id'])[0]}")
        time.sleep(1)