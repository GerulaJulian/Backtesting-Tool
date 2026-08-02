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
from datetime import date, timedelta

st.title("Einzelaktien rechner")
st.write("Teste eine einzelne Anlagestrategie für eine gewählte Aktie.")

def search(searchTerm):
    if not searchTerm:
        return []
    searchResults = yf.Search(searchTerm).quotes
    dispResults = []
    for entry in searchResults:
        dispResults.append((f"{entry.get('shortname', entry.get('longname', 'Die eingabe ist fehlerhaft'))} - {entry['symbol']}", entry['symbol']))
    return dispResults

# Input fields
ticker = st_searchbox(search, placeholder="Unternehmen suchen", key="tickerSearch")
# column for Date selecion
inputColStartDate, _, inputColEndDate = st.columns(3)
with inputColStartDate:
    startDate = st.date_input("Startdatum", value=date.today() - timedelta(days=182))
with inputColEndDate:
    endDate = st.date_input("Enddatum", value=date.today())

# Column for Strategy selection
inputColStrategy, _, _, _, _ = st.columns(5)
with inputColStrategy:  
    strategy = st.selectbox("Strategie", ["Buy and Hold", "DCA", "High and Low", "RSI"], help="Buy and Hold: einmaliger Kauf zu Beginn, kein Verkauf. DCA: fester Betrag wird monatlich investiert. High and Low: Kauf bei Tiefpunkten, Verkauf bei Hochpunkten im gewählten Zeitraum. RSI: Kauf bei überverkauftem Markt (RSI < 30), Verkauf bei überkauftem Markt (RSI > 70).")

# Column for Num input
inputColInvestAmount, inputColLookBackTime, inputColUserPercent = st.columns(3)
with inputColInvestAmount:
    investAmount = st.number_input("Investitionsbetrag(€)", min_value=0.0, value=100.0, help="Betrag, der bei jedem Kaufsignal investiert wird (bzw. einmalig bei Buy and Hold).")
with inputColLookBackTime:
    if strategy == "High and Low" or strategy == "RSI":
        lookBackTime = st.number_input("Zeitraum(Tage)", min_value=0, value=30, help="Anzahl Tage, über die der höchste/niedrigste Kurs zur Signal-Erkennung betrachtet wird.")
with inputColUserPercent:
    if strategy == "High and Low" or strategy == "RSI":
        userPercent = st.number_input("Verkaufsanteil(%)", min_value=0, max_value=100, value=50, help="Anteil des aktuellen Bestands, der bei einem Verkaufssignal verkauft wird.")
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

    st.write("Daten für ", ticker)
    st.write(f"Rendite: {calcReturn:.2f}%")
