import streamlit as st
import pandas as pd
import plotly.express as px
from analysis import (
    TECH_STOCKS,
    get_fundamental_data,
    get_sentiment_analysis,
    get_final_recommendation,
    get_price_history
)

def display_ui():
    """
    The main function to display the Streamlit UI for the stock analysis tool.
    """
    st.set_page_config(page_title="Advanced Stock Analyzer", layout="wide")

    # --- Sidebar for stock selection ---
    st.sidebar.title("Stock Selection")
    ticker = st.sidebar.selectbox(
        "Select a stock to analyze:",
        options=sorted(TECH_STOCKS)
    )

    if ticker:
        # --- Main Analysis Section ---
        st.title(f"Analysis for {ticker}")

        # Perform all analysis
        with st.spinner(f"Running full analysis for {ticker}..."):
            fundamental_data = get_fundamental_data(ticker)
            sentiment_status = get_sentiment_analysis(ticker)
            final_recommendation = get_final_recommendation(
                fundamental_data['Fundamental Status'],
                sentiment_status
            )

        st.header(f"{fundamental_data['Company Name']}")

        # --- Display the Final Recommendation ---
        st.subheader("Final Recommendation")

        # Color code the recommendation
        if "BUY" in final_recommendation:
            st.success(f"## {final_recommendation}")
        elif "SELL" in final_recommendation:
            st.error(f"## {final_recommendation}")
        else:
            st.warning(f"## {final_recommendation}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Fundamental Status", value=fundamental_data['Fundamental Status'])
        with col2:
            st.metric(label="Sentiment Status", value=sentiment_status)

        st.markdown("---")

        # --- Detailed Analysis Columns ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Fundamental Analysis")
            st.metric("Current Price", f"${fundamental_data['Current Price']:.2f}")
            st.metric("Intrinsic Value (DCF)", f"${fundamental_data['Intrinsic Value (DCF)']:.2f}" if isinstance(fundamental_data['Intrinsic Value (DCF)'], float) else fundamental_data['Intrinsic Value (DCF)'])

            with st.expander("DCF Model Assumptions"):
                st.text(fundamental_data['DCF Details'])

            st.subheader("Key Metrics")
            st.text(f"Market Cap: {fundamental_data['Market Cap'] / 1e9:.2f}B")
            st.text(f"P/E Ratio: {fundamental_data['P/E Ratio']:.2f}" if fundamental_data['P/E Ratio'] else "N/A")
            st.text(f"P/B Ratio: {fundamental_data['P/B Ratio']:.2f}" if fundamental_data['P/B Ratio'] else "N/A")
            st.text(f"Debt-to-Equity: {fundamental_data['Debt-to-Equity']:.2f}")
            st.text(f"Current Ratio: {fundamental_data['Current Ratio']:.2f}")
            st.text(f"Return on Equity (ROE): {fundamental_data['Return on Equity']:.2%}")
            st.text(f"Free Cash Flow (TTM): {fundamental_data['Free Cash Flow'] / 1e9:.2f}B")

        with col2:
            st.subheader("Price History (Last 1 Year)")
            price_history = get_price_history(ticker)
            fig_price = px.line(price_history, x=price_history.index, y='Close')
            fig_price.update_layout(title=f"{ticker} Daily Close Price", yaxis_title="Price (USD)")
            st.plotly_chart(fig_price, use_container_width=True)

        # --- Disclaimer ---
        st.markdown("---")
        st.error(
            "**DISCLAIMER:** This is an automated analysis for educational purposes only and NOT financial advice. "
            "The recommendation is based on a simplified model and does not account for all market risks. "
            "Consult a qualified financial advisor before making any investment decisions."
        )

if __name__ == '__main__':
    display_ui()
