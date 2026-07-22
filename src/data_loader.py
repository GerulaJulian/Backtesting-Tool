"""
doc zum laden von daten
"""

import pandas as pd
import yfinance as yf


def load_price_data(ticker: str, start: str, end: str):
    df = yf.download(ticker, start=start, end=end)
    df.columns = df.columns.get_level_values(0)
    return df

if __name__ == "__main__":
    stockData = load_price_data("AAPL", "2024-01-01", "2025-01-01")