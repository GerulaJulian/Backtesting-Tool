"""
doc zum laden von daten
"""

import pandas as pd
import streamlit as st
import yfinance as yf

#Data loader für einzelne Strategeien(single.py)
@st.cache_data(ttl=3600, show_spinner="Kursdaten werden geladen...")
def load_price_data(ticker: str, start: str, end: str, currency: str = "EUR"):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True)
    df.columns = df.columns.get_level_values(0)

    if currency != "USD":
        forex = load_forex_data(currency, start, end)
        forex = forex.reindex(df.index)
        missingDays = forex.isna().sum()
        if missingDays > 5:
            st.warning(f"{missingDays} Tage ohne Kursdaten wurden aufgefüllt.")
        forex = forex.reindex(df.index).ffill().bfill()
        df["Close"] = df["Close"] * forex

        #Timezone mismatch fix
        if pd.isna(df["Close"].iloc[-1]):
            df = df.iloc[:-1]

    return df

#Data loader für meherere Strategien(home.py)
@st.cache_data(ttl=3600, show_spinner="Kursdaten werden geladen...")
def load_price_data_multi(tickers:tuple, start:str, end:str, currency: str = "EUR") -> pd.DataFrame:
    mdf = yf.download(list(tickers), start=start, end=end, auto_adjust=True, progress=False)
    mdf = mdf["Close"]

    if currency != "USD":
        forex = load_forex_data(currency, start, end)
        forex = forex.reindex(mdf.index)
        missingDays = forex.isna().sum()
        if missingDays > 5:
            st.warning(f"{missingDays} Tage ohne Kursdaten wurden aufgefüllt.")
        forex = forex.reindex(mdf.index).ffill().bfill()
        mdf = mdf.multiply(forex, axis=0)

        #Timezone mismatch fix
        if mdf.iloc[-1].isna().any():
            mdf = mdf.iloc[:-1]

    return mdf

#currency converter
@st.cache_data(ttl=3600)
def load_forex_data(curCode: str, start: str, end: str):
    if curCode == "USD":
        return None
    forex = yf.download(f"USD{curCode}=X", start=start, end=end, auto_adjust=True, progress=False)["Close"]

    if isinstance(forex, pd.DataFrame):
        forex = forex.squeeze("columns")

    return forex

if __name__ == "__main__":
    stockData = load_price_data("AAPL", "2024-01-01", "2025-01-01")