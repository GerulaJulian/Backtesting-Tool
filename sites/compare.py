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
from datetime import date, timedelta

st.title("Compare")
st.write("Vergleiche alle Anlagestrategien und finde heraus welche bei dieser Aktie am sinnvollsten wäre.")

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

# Column for Num input
inputColInvestAmount, inputColLookBackTime, inputColUserPercent = st.columns(3)
with inputColInvestAmount:
    investAmount = st.number_input("Investitionsbetrag(€)", min_value=0.0, value=100.0, help="Betrag, der bei jedem Kaufsignal investiert wird (bzw. einmalig bei Buy and Hold).")
with inputColLookBackTime:
    lookBackTime = st.number_input("Zeitraum(Tage)", min_value=0, value=30, help="Anzahl Tage, über die der höchste/niedrigste Kurs zur Signal-Erkennung betrachtet wird.")
with inputColUserPercent:
    userPercent = st.number_input("Verkaufsanteil(%)", min_value=0, max_value=100, value=50, help="Anteil des aktuellen Bestands, der bei einem Verkaufssignal verkauft wird.")
    userPercent = userPercent / 100

if st.button("Strategien vergleichen"):
    comparePrices = load_price_data(ticker, str(startDate), str(endDate))

    resultBuyHold = sim_buy_hold(comparePrices, investAmount)
    investedBuyHold = pd.Series(investAmount, index=resultBuyHold.index)
    returnBuyHold = (resultBuyHold - investedBuyHold) / investedBuyHold * 100

    resultDCA = sim_dca(comparePrices, investAmount)
    investedDCA = pd.Series(range(1, len(resultDCA) + 1), index=resultDCA.index) * investAmount
    returnDCA = (resultDCA - investedDCA) / investedDCA * 100

    resultHighLow, _, investedHighLow = sim_high_low(comparePrices, investAmount, lookBackTime, userPercent)
    returnHighLow = (resultHighLow - investedHighLow) / investedHighLow * 100

    resultRSI, _, investedRSI = sim_rsi(comparePrices, investAmount, lookBackTime, userPercent)
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
