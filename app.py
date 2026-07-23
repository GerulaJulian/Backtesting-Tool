"""
Actual doc
"""

from src.data_loader import load_price_data
from src.strategies.buy_hold import sim_buy_hold
from src.strategies.dca import sim_dca
from src.strategies.high_low import sim_high_low
from src.strategies.rsi import sim_rsi
import streamlit as st
from streamlit_searchbox import st_searchbox
import yfinance as yf

st.title("Backtesting-Tool")

def search(searchTerm):
    if not searchTerm:
        return []
    searchResults = yf.Search(searchTerm).quotes
    dispResults = []
    for entry in searchResults:
        dispResults.append((f"{entry['shortname']} - {entry['symbol']}", entry['symbol']))
    return dispResults

ticker = st_searchbox(search, placeholder="Unternehmen suchen", key="tickerSearch")
startDate = st.date_input("Startdatum")
endDate = st.date_input("Enddatum")
strategy = st.selectbox("Strategie", ["Buy and Hold", "DCA", "High and Low", "RSI"])
investAmount = st.number_input("Investitionsbetrag(€)", min_value=0.0, value=100.0)

if strategy == "High and Low":
    lookBackTime = st.number_input("In welchem Zeitraum sollen höchst und tief pujnkte ermittelt", min_value=0, value=30)
    userPercent = st.number_input("Anteil der bei Hochpunkt verkauft wird(%)", min_value=0, max_value=100, value=50)
    userPercent = userPercent / 100
elif strategy == "RSI":
    lookBackTime = st.number_input("In welchem Zeitraum sollen höchst und tief pujnkte ermittelt", min_value=0, value=14)
    userPercent = st.number_input("Anteil der bei Hochpunkt verkauft wird(%)", min_value=0, max_value=100, value=50)
    userPercent = userPercent / 100


if st.button("Test starten"):
    prices = load_price_data(ticker, str(startDate), str(endDate))
    if strategy == "Buy and Hold":
        result = sim_buy_hold(prices, investAmount)
        invested = investAmount
    elif strategy == "DCA":
        result = sim_dca(prices, investAmount)
        invested = investAmount * len(result)
    elif strategy == "High and Low":
        result, buyAmount = sim_high_low(prices, investAmount, lookBackTime, userPercent)
        invested = investAmount * buyAmount
    elif strategy == "RSI":
        result, buyAmount = sim_rsi(prices, investAmount, lookBackTime, userPercent)
        invested = investAmount * buyAmount

    calcReturn = (result.iloc[-1] - invested) / invested * 100

    st.write("Price data for", ticker)
    st.write(f"Rendite: {calcReturn:.2f}%")