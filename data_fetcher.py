import yfinance as yf
import pandas as pd

def fetch_data(symbol, interval="1d", period="3mo"):
    """
    Fetches recent OHLCV data using yfinance.
    Interval can be '1m', '5m', '15m', '30m', '1h', '1d', etc.
    """
    # Fetch data from yfinance API
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return None
        return df
    except Exception as e:
        raise Exception(f"Error fetching data for {symbol}: {e}")
