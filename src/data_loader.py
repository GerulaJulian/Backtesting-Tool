"""
Lädt historische Kursdaten für ein gegebenes Ticker-Symbol.
Monat 1: erstmal nur mit yfinance testen.
"""

import pandas as pd
import yfinance as yf


def load_price_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Lädt Tagesschlusskurse für ein Ticker-Symbol im gewünschten Zeitraum.

    Args:
        ticker: z.B. "^GSPC" für S&P500, "AAPL" für Apple
        start: Startdatum im Format "YYYY-MM-DD"
        end: Enddatum im Format "YYYY-MM-DD"

    Returns:
        DataFrame mit Datum als Index und mind. der Spalte "Close"
    """
    df = yf.download(ticker, start=start, end=end)
    return df


if __name__ == "__main__":
    # Kleiner Testlauf: S&P500 der letzten Jahre laden und anzeigen
    data = load_price_data("^GSPC", "2023-01-01", "2024-01-01")
    print(data.head())
    print(f"\n{len(data)} Handelstage geladen.")
