"""
EinzelAktien simulator
"""

from src.data_loader import load_price_data
from src.strategies.buy_hold import sim_buy_hold
from src.strategies.dca import sim_dca
from src.strategies.high_low import sim_high_low
from src.strategies.rsi import sim_rsi
import streamlit as st
from streamlit_searchbox import st_searchbox
import plotly.express as px
import pandas as pd
import yfinance as yf

st.title("single")

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

if st.button("Test starten"):
    prices = load_price_data(ticker, str(startDate), str(endDate))
    chartSingle = px.line(prices, x=prices.index, y="Close", title="Kursverlauf", labels={"x": "Datum", "y": "Aktien Wert(€)"})
    st.plotly_chart(chartSingle)
    if strategy == "Buy and Hold":
        result = sim_buy_hold(prices, investAmount)
        invested = investAmount
        investedSeries = pd.Series(investAmount, index=result.index)
    elif strategy == "DCA":
        result = sim_dca(prices, investAmount)
        invested = investAmount * len(result)
        investedSeries = pd.Series(range(1, len(result) + 1), index=result.index) * investAmount
    elif strategy == "High and Low":
        result, buyAmount, investedSeries = sim_high_low(prices, investAmount, lookBackTime, userPercent)
        invested = investAmount * buyAmount
    elif strategy == "RSI":
        result, buyAmount, investedSeries = sim_rsi(prices, investAmount, lookBackTime, userPercent)
        invested = investAmount * buyAmount

    calcReturn = (result.iloc[-1] - invested) / invested * 100
    fig2 = px.line(x=result.index, y=result, title="Portfloio Wert(€)", labels={"x": "Datum", "y": "Portfolio Wert(€)"})
    st.plotly_chart(fig2)

    portfolioData = pd.DataFrame({
        "invested": investedSeries,
        "portfolioValue": result
    })
    fig3 = px.line(portfolioData, title="Investiert und Portfolio Wert(€)", labels={"x": "Datum", "y": "€"})
    st.plotly_chart(fig3)

    st.write("Price data for", ticker)
    st.write(f"Rendite: {calcReturn:.2f}%")
