"""
multiple compareasion
"""

from src.data_loader import load_price_data
from src.strategies.buy_hold import sim_buy_hold
from src.strategies.dca import sim_dca
from src.strategies.high_low import sim_high_low
from src.strategies.rsi import sim_rsi
import streamlit as st
from streamlit_searchbox import st_searchbox
import yfinance as yf
import plotly.express as px
import pandas as pd

st.title("Compare")

def search(searchTerm):
    if not searchTerm:
        return []
    searchResults = yf.Search(searchTerm).quotes
    dispResults = []
    for entry in searchResults:
        dispResults.append((f"{entry.get('shortname', entry.get('longname', 'Die eingabe ist fehlerhaft'))} - {entry['symbol']}", entry['symbol']))
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

if st.button("Strategien vergleichen"):
    comparePrices = load_price_data(ticker, str(startDate), str(endDate))

    resultBuyHold = sim_buy_hold(comparePrices, investAmount)
    investedBuyHold = pd.Series(investAmount, index=resultBuyHold.index)
    returnBuyHold = (resultBuyHold - investedBuyHold) / investedBuyHold * 100

    resultDCA = sim_dca(comparePrices, investAmount)
    investedDCA = pd.Series(range(1, len(resultDCA) + 1), index=resultDCA.index) * investAmount
    returnDCA = (resultDCA - investedDCA) / investedDCA * 100

    resultHighLow, _, investedHighLow = sim_high_low(comparePrices, investAmount, 30, 1.0)
    returnHighLow = (resultHighLow - investedHighLow) / investedHighLow * 100

    resultRSI, _, investedRSI = sim_rsi(comparePrices, investAmount, 14, 1.0)
    returnRSI = (resultRSI - investedRSI) / investedRSI * 100


    compareData = pd.DataFrame({
        "Buy and Hold": returnBuyHold,
        "DCA": returnDCA,
        "High and Low": returnHighLow,
        "RSI": returnRSI,
    })
    compareData = compareData.ffill()

    figCompare = px.line(compareData, title="Strategien vergleichen | Rendite(%)", labels={"x": "Datum", "y": "%"})
    st.plotly_chart(figCompare)
