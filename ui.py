import streamlit as st
import pandas as pd
import plotly.express as px
from analysis import TECH_STOCKS, get_stock_data, get_price_history, get_sentiment_analysis

def display_ui():
    """
    The main function to display the Streamlit UI.
    """
    st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")

    st.title("Tech Stock Analysis Dashboard")

    # --- Sidebar for stock selection ---
    st.sidebar.header("Stock Selection")

    # Allow user to select from the default list or add their own
    all_stocks = sorted(list(set(TECH_STOCKS)))
    selected_tickers = st.sidebar.multiselect(
        "Select stocks from the list:",
        options=all_stocks,
        default=['AAPL', 'MSFT', 'GOOG']
    )

    custom_ticker = st.sidebar.text_input("Or add a stock ticker (e.g., AMZN):")
    if st.sidebar.button("Add Ticker") and custom_ticker:
        if custom_ticker.upper() not in selected_tickers:
            selected_tickers.append(custom_ticker.upper())

    if not selected_tickers:
        st.warning("Please select at least one stock ticker.")
        return

    # --- Main content with tabs ---
    tab1, tab2 = st.tabs(["Fundamental Analysis", "Sentiment Analysis"])

    with tab1:
        st.header("Fundamental Analysis")

        # Fetch and display fundamental data
        with st.spinner("Fetching fundamental data..."):
            fundamental_data = get_stock_data(selected_tickers)

        st.subheader("Key Metrics")
        st.dataframe(fundamental_data)

        # --- Charts for Visualization ---
        st.subheader("Visualizations")

        # Price History Line Chart
        st.write("#### Stock Price History (Last Year)")
        history_ticker = st.selectbox("Select stock for price history:", selected_tickers)
        if history_ticker:
            with st.spinner(f"Fetching price history for {history_ticker}..."):
                price_history = get_price_history(history_ticker)
            fig_price = px.line(price_history, x=price_history.index, y='Close', title=f"{history_ticker} Price History")
            st.plotly_chart(fig_price, use_container_width=True)

        # Market Cap Comparison Bar Chart
        st.write("#### Market Cap Comparison")
        if not fundamental_data.empty:
            fig_market_cap = px.bar(fundamental_data, x='Ticker', y='Market Cap', title="Market Capitalization of Selected Stocks")
            st.plotly_chart(fig_market_cap, use_container_width=True)

    with tab2:
        st.header("Sentiment Analysis")
        st.info("This feature uses the Gemini API for deep research. Please be patient as it may take a moment.")

        sentiment_ticker = st.selectbox("Select a stock for sentiment analysis:", selected_tickers)

        if st.button(f"Analyze Sentiment for {sentiment_ticker}"):
            with st.spinner(f"Performing sentiment analysis for {sentiment_ticker}..."):
                sentiment_result = get_sentiment_analysis(sentiment_ticker)

            st.subheader(f"Sentiment for {sentiment_ticker}")
            st.write(sentiment_result)

if __name__ == '__main__':
    # This file is intended to be run via the main.py script
    # but you can run it directly for testing if you have Streamlit installed.
    # To run: streamlit run ui.py
    display_ui()
