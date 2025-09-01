import pandas as pd
import yfinance as yf
import google.generativeai as genai
import os

# A list of top 30 tech stocks (US-based)
TECH_STOCKS = [
    'NVDA', 'MSFT', 'AAPL', 'GOOG', 'AMZN', 'META', 'AVGO', 'TSLA', 'ORCL',
    'NFLX', 'PLTR', 'CSCO', 'AMD', 'CRM', 'IBM', 'UBER', 'NOW', 'INTU',
    'TXN', 'QCOM', 'ANET', 'ADBE', 'MU', 'AMAT', 'PANW', 'LRCX', 'ADI',
    'ADP', 'KLAC', 'SNPS'
]

def get_stock_data(tickers):
    """
    Fetches fundamental data for a list of stock tickers.
    """
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        data.append({
            'Ticker': ticker,
            'Company Name': info.get('longName'),
            'Market Cap': info.get('marketCap'),
            'P/E Ratio': info.get('trailingPE'),
            'Dividend Yield': info.get('dividendYield')
        })
    return pd.DataFrame(data)

def get_price_history(ticker):
    """
    Fetches historical price data for a given stock ticker.
    """
    stock = yf.Ticker(ticker)
    # Get historical market data, e.g., for the last 1 year
    hist = stock.history(period="1y")
    return hist

def get_sentiment_analysis(ticker):
    """
    Performs sentiment analysis on a stock using the Gemini API.
    Note: This requires a configured Gemini API key.
    """
    try:
        # Ensure the API key is set as an environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable not set."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Perform a detailed sentiment analysis for the stock with ticker {ticker}.
        Your analysis should be based on recent news, social media trends, and financial reports.
        Please provide a sentiment score from -1 (very negative) to 1 (very positive)
        and a summary of your findings. The summary should be concise and highlight the
        key factors influencing the sentiment.

        Format your response as follows:
        Sentiment Score: [score]
        Summary: [Your summary here]
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during sentiment analysis: {e}"

if __name__ == '__main__':
    # Example usage:
    # To test this file directly, you can uncomment the following lines.
    # Make sure to set your GEMINI_API_KEY environment variable first.

    # print("Fetching fundamental data for tech stocks...")
    # fundamental_data = get_stock_data(TECH_STOCKS)
    # print(fundamental_data)

    # print("\nFetching price history for AAPL...")
    # price_history = get_price_history('AAPL')
    # print(price_history.head())

    # print("\nPerforming sentiment analysis for AAPL...")
    # sentiment = get_sentiment_analysis('AAPL')
    # print(sentiment)
    pass
