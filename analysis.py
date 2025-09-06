import pandas as pd
import yfinance as yf
import google.generativeai as genai
import os
import numpy as np

# A list of top 30 tech stocks (US-based)
TECH_STOCKS = [
    'NVDA', 'MSFT', 'AAPL', 'GOOG', 'AMZN', 'META', 'AVGO', 'TSLA', 'ORCL',
    'NFLX', 'PLTR', 'CSCO', 'AMD', 'CRM', 'IBM', 'UBER', 'NOW', 'INTU',
    'TXN', 'QCOM', 'ANET', 'ADBE', 'MU', 'AMAT', 'PANW', 'LRCX', 'ADI',
    'ADP', 'KLAC', 'SNPS'
]

# --- Fundamental Analysis ---

def get_fundamental_data(ticker):
    """
    Fetches and calculates all required fundamental data for a single stock ticker.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    balance_sheet = stock.balance_sheet
    financials = stock.financials
    cashflow = stock.cashflow

    # Basic info
    market_cap = info.get('marketCap', 0)
    current_price = info.get('currentPrice', info.get('previousClose', 0))

    # Metrics from info
    pe_ratio = info.get('trailingPE')
    pb_ratio = info.get('priceToBook')

    # Metrics from balance sheet
    total_debt = balance_sheet.loc['Total Liab'].iloc[0] if 'Total Liab' in balance_sheet.index else 0
    total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0] if 'Total Stockholder Equity' in balance_sheet.index else 1
    debt_to_equity = total_debt / total_equity if total_equity else 0

    current_assets = balance_sheet.loc['Total Current Assets'].iloc[0] if 'Total Current Assets' in balance_sheet.index else 0
    current_liabilities = balance_sheet.loc['Total Current Liabilities'].iloc[0] if 'Total Current Liabilities' in balance_sheet.index else 1
    current_ratio = current_assets / current_liabilities if current_liabilities else 0

    # Metrics from financials
    net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else 0
    roe = net_income / total_equity if total_equity else 0

    # Free Cash Flow
    free_cash_flow = cashflow.loc['Total Cash From Operating Activities'].iloc[0] - cashflow.loc['Capital Expenditures'].iloc[0] if 'Total Cash From Operating Activities' in cashflow.index and 'Capital Expenditures' in cashflow.index else 0

    # DCF Calculation
    intrinsic_value, dcf_details = calculate_dcf(stock)

    # Fundamental Status
    fundamental_status = get_fundamental_status(intrinsic_value, current_price)

    return {
        'Ticker': ticker,
        'Company Name': info.get('longName', 'N/A'),
        'Current Price': current_price,
        'Market Cap': market_cap,
        'P/E Ratio': pe_ratio,
        'P/B Ratio': pb_ratio,
        'Debt-to-Equity': debt_to_equity,
        'Current Ratio': current_ratio,
        'Return on Equity': roe,
        'Free Cash Flow': free_cash_flow,
        'Intrinsic Value (DCF)': intrinsic_value,
        'Fundamental Status': fundamental_status,
        'DCF Details': dcf_details
    }

def calculate_dcf(stock, discount_rate=0.085, perpetual_growth_rate=0.025, projection_years=5):
    """
    Performs a simplified 2-stage Discounted Cash Flow (DCF) analysis.
    """
    cashflow_statement = stock.cashflow
    if 'Free Cash Flow' in cashflow_statement.index:
        # Use Yahoo Finance's FCF if available
        fcf_history = cashflow_statement.loc['Free Cash Flow'].dropna()
    elif 'Total Cash From Operating Activities' in cashflow_statement.index and 'Capital Expenditures' in cashflow_statement.index:
        fcf_history = (cashflow_statement.loc['Total Cash From Operating Activities'] - cashflow_statement.loc['Capital Expenditures']).dropna()
    else:
        return 0, "FCF data not available"

    if fcf_history.empty or fcf_history.iloc[0] <= 0:
        return 0, "Not applicable (Negative or no FCF)"

    # Simple growth rate: average of historical growth rates
    fcf_growth_rates = fcf_history.pct_change().dropna()
    if not fcf_growth_rates.empty:
        # Cap growth rate at a reasonable level (e.g., 15%) to avoid extreme projections
        growth_rate = min(fcf_growth_rates.mean(), 0.15)
    else:
        growth_rate = 0.05 # Default growth rate if no history

    if growth_rate <= 0:
        growth_rate = 0.05 # Ensure growth rate is positive

    # Project future FCF
    last_fcf = fcf_history.iloc[0]
    future_fcf = []
    for i in range(1, projection_years + 1):
        future_fcf.append(last_fcf * (1 + growth_rate)**i)

    # Discount future FCF to present value
    discounted_fcf = []
    for i, fcf in enumerate(future_fcf):
        discounted_fcf.append(fcf / (1 + discount_rate)**(i + 1))

    # Calculate terminal value
    terminal_value = (future_fcf[-1] * (1 + perpetual_growth_rate)) / (discount_rate - perpetual_growth_rate)

    # Discount terminal value to present value
    discounted_terminal_value = terminal_value / (1 + discount_rate)**projection_years

    # Calculate total intrinsic value
    total_intrinsic_value = sum(discounted_fcf) + discounted_terminal_value

    # Get shares outstanding
    shares_outstanding = stock.info.get('sharesOutstanding', 0)
    if shares_outstanding == 0:
        return 0, "Shares outstanding not available"

    intrinsic_value_per_share = total_intrinsic_value / shares_outstanding

    details = (f"FCF Growth (Stage 1): {growth_rate:.2%}\n"
               f"Discount Rate: {discount_rate:.2%}\n"
               f"Perpetual Growth (Stage 2): {perpetual_growth_rate:.2%}")

    return intrinsic_value_per_share, details


def get_fundamental_status(intrinsic_value, current_price):
    """
    Determines if a stock is Undervalued, Overvalued, or Fairly Valued.
    """
    if intrinsic_value == 0 or current_price == 0:
        return "N/A"

    diff = (intrinsic_value - current_price) / current_price
    if diff > 0.20:
        return "Undervalued"
    elif diff < -0.20:
        return "Overvalued"
    else:
        return "Fairly Valued"

def get_price_history(ticker):
    """
    Fetches historical price data for a given stock ticker.
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return hist

# --- Sentiment Analysis ---

def get_sentiment_analysis(ticker):
    """
    Performs sentiment analysis and returns 'Positive', 'Neutral', or 'Negative'.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "API Key Missing"

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Analyze the current sentiment for the stock with ticker {ticker} based on recent news and market chatter.
        Classify the sentiment as one of the following three options:
        - Positive
        - Neutral
        - Negative

        Return only the single word classification.
        """
        response = model.generate_content(prompt)
        # Clean up the response to get one of the three expected words
        sentiment = response.text.strip().capitalize()
        if sentiment in ["Positive", "Neutral", "Negative"]:
            return sentiment
        else:
            return "Neutral" # Default if the response is not as expected
    except Exception as e:
        return "API Error"

# --- Final Recommendation Logic ---

def get_final_recommendation(fundamental_status, sentiment_status):
    """
    Generates a final recommendation based on fundamental and sentiment analysis.
    """
    if fundamental_status == "Undervalued":
        if sentiment_status == "Positive":
            return "STRONG BUY"
        elif sentiment_status == "Neutral":
            return "BUY"
        else: # Negative
            return "HOLD"
    elif fundamental_status == "Fairly Valued":
        return "HOLD"
    elif fundamental_status == "Overvalued":
        if sentiment_status == "Positive":
            return "HOLD"
        elif sentiment_status == "Neutral":
            return "SELL"
        else: # Negative
            return "STRONG SELL"
    else:
        return "N/A"

if __name__ == '__main__':
    # Example usage:
    # To test this file directly, you can uncomment the following lines.
    # Make sure to set your GEMINI_API_KEY environment variable first.

    # test_ticker = 'AAPL'
    # print(f"--- Analysis for {test_ticker} ---")

    # fundamentals = get_fundamental_data(test_ticker)
    # for key, value in fundamentals.items():
    #     print(f"{key}: {value}")

    # print("\n--- Sentiment Analysis ---")
    # sentiment = get_sentiment_analysis(test_ticker)
    # print(f"Sentiment: {sentiment}")

    # print("\n--- Final Recommendation ---")
    # recommendation = get_final_recommendation(fundamentals['Fundamental Status'], sentiment)
    # print(f"Recommendation: {recommendation}")
    pass
