try:
    from app.utils.trading_period import display_market_status
    from app.db.common import DB, Stocks
    import streamlit as st
    from app.utils.headlines import fetch_recent_stock_news, format_ddg_news_as_markdown
    from app.utils.helpers import display_data
    from icecream import ic
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
        stock_selected_price_info = supabase.fetch_records('stock_prices_equity', ('stock_id', 'eq', stock_selected['id']))[0]
        stock_mc_data = supabase.fetch_records('moneycontrol_data', ('id', 'eq', stock_selected['moneycontrol_id']))[0]
        next_expiry_dates = supabase.fetch_records('expiry_dates', ('timeline', 'eq', 'next'))[0]
        latest_expiry_dates = supabase.fetch_records('expiry_dates', ('timeline', 'eq', 'latest'))[0]

        fno_stock = False
        
        if stock_selected['lot_size'] > 0:
            fno_stock = True
            stock_selected_latest_futures_price_info = supabase.fetch_records('stock_prices_futures_latest_expiry', ('fno_stock_id', 'eq', stock_selected['id']))[0]
            stock_selected_next_futures_price_info = supabase.fetch_records('stock_prices_futures_next_expiry', ('fno_stock_id', 'eq', stock_selected['id']))[0]
            stock_selected_last_futures_price_info = supabase.fetch_records('stock_prices_futures_last_expiry', ('fno_stock_id', 'eq', stock_selected['id']))[0]

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
                    st.metric(
                        label="Latest Price", 
                        value=f"₹{stock_selected_price_info['last_price']}", 
                        delta=f"{round(stock_selected_price_info['percent_change'], 2)}%"
                        )

                    st.metric(
                        label="P/E Ratio", 
                        value=f"₹{stock_selected_price_info['last_price']}", 
                        )      

                    st.metric(
                        label="Dividend Yield", 
                        value=f"{stock_mc_data['metadata']['DYCONS']}%", 
                        )              
                
                with metric_col2:
                    st.metric(
                        label="Day Change", 
                        value=f"₹{round(stock_selected_price_info['change'], 2)}",
                        delta=f"{'+ 🟢' if round(stock_selected_price_info['change'], 2) > 0 else '- 🔴'}",
                        )
                    
                    st.metric(
                        label="Industry P/E", 
                        value=f"{stock_mc_data['metadata']['IND_PE']}"
                        )
                    
                    st.metric(
                        label="Total Market Cap", 
                        value=f"₹{stock_mc_data['metadata']['MKTCAP']} cr.", 
                        )                    
                
                with metric_col3:
                    st.metric(
                        label="Traded Volume", 
                        value=f"{stock_selected_price_info['traded_volume']} lakhs",
                        )
                    
                    st.metric(
                        label="P/B Ratio", 
                        value=f"{stock_mc_data['metadata']['PE']}"
                        )

                    if fno_stock:
                        st.metric(
                            label="Lot Size", 
                            value=f"{stock_selected['lot_size']}", 
                            )
                
                with metric_col4:
                    st.metric(
                        label="Buyers", 
                        value=f"{stock_selected_price_info['buyers']}"
                        )

                    st.metric(
                        label="Book Value", 
                        value=f"₹{stock_mc_data['metadata']['BV']}"
                        )

                    if fno_stock:
                        st.metric(
                            label=f"Futures Price for {latest_expiry_dates['date']}", 
                            value=f"₹{stock_selected_latest_futures_price_info['last_price']}", 
                            delta=f"{round(stock_selected_latest_futures_price_info['percent_change'], 2)}%"
                            )
                
                with metric_col5:
                    st.metric(
                        label="Sellers", 
                        value=f"{stock_selected_price_info['sellers']}"
                        )
            
                    st.metric(
                        label="Face Value", 
                        value=f"₹{stock_mc_data['metadata']['FV']}"
                        )

                    if fno_stock:
                        st.metric(
                            label=f"Futures Price for {next_expiry_dates['date']}", 
                            value=f"₹{stock_selected_next_futures_price_info['last_price']}",
                            delta=f"{round(stock_selected_next_futures_price_info['percent_change'], 2)}%"
                            )

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