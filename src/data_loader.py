"""
Laedt historische Kursdaten fuer ein gegebenes Ticker-Symbol.
Monat 1: erstmal nur mit yfinance testen.

TODO: von Julian selbst geschrieben (siehe Anleitung im Chat)
"""

import pandas as pd
import yfinance as yf


def load_price_data(ticker: str, start: str, end: str):
    df = yf.download(ticker, start=start, end=end)
    return df

if __name__ == "__main__":
    result = load_price_data("AAPL", "2024-01-01", "2025-01-01")
    print(result)