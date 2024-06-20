try:
    import streamlit as st
    from app.utils.trading_period import display_market_status
    from app.utils.headlines import get_mc_news, get_et_news, get_finshots_news, format_news_as_markdown
    from nsepythonserver import nse_events
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
            trading_screen = st.button("Options", use_container_width=True)
            if trading_screen:
                st.switch_page("pages/options.py")

        with nav_bar_item5:
            news = st.button("Today's Headlines", use_container_width=True, type="primary")
            if news:
                st.switch_page("pages/news.py")

    st.title("Today's Headlines 🗞️")
    mc_news = get_mc_news()
    et_news = get_et_news()
    finshots = get_finshots_news()
    
    with st.container(border=True):
        with st.container():
            st.write("## Daily Finshots")
            with st.container(border=True):
                st.markdown(format_news_as_markdown(finshots, include_excerpt=True))

        col1, col2 = st.columns(2)

        with col1:
            st.write("## Moneycontrol")
            with st.container(border=True, height=450):
                st.markdown(format_news_as_markdown(mc_news))
        
        with col2:
            st.write("## Economic Times")
            with st.container(border=True, height=450):
                st.markdown(format_news_as_markdown(et_news))
        
        st.write("## Corporate Events")
        events = nse_events()
        events = events.rename(columns={'symbol': 'Stock Symbol', 'company': 'Company Name', 'purpose': 'Purpose Description', 'bm_desc': 'Board Meeting Description', 'date': 'Event Date'})
        events.set_index('Stock Symbol', inplace=True)
        st.dataframe(events, use_container_width=True)
                