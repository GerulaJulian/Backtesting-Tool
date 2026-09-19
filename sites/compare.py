"""
multiple compareasion
"""

from src.data_loader import load_price_data
from src.strategies.buy_hold import sim_buy_hold
from src.strategies.dca import sim_dca
from src.strategies.high_low import sim_high_low
from src.strategies.rsi import sim_rsi
from src.utilities.currencies import CURRENCIES
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
    launchDate = date.today() - timedelta(hours=8760)
    if ticker != None:
        unixLaunchDate = yf.Ticker(ticker).get_history_metadata()
        launchDate = date.fromtimestamp(unixLaunchDate["firstTradeDate"])
    else:
        pass
    startDate = st.date_input("Startdatum", value=date.today() - timedelta(days=182), min_value=launchDate ,max_value=date.today() - timedelta(days=1))
with inputColEndDate:
    endDate = st.date_input("Enddatum", value=date.today(), min_value= launchDate, max_value=date.today())

# Column for Num input
inputColInvestAmount, _ = st.columns([0.5, 0.5], gap=None)
with inputColInvestAmount:
    inputFieldInvestAmount, inputFieldselCur = st.columns([0.35, 0.65], gap=None)
    with inputFieldInvestAmount:
        investAmount = st.number_input("Investitionsbetrag", min_value=0.0, value=100.0)
    with inputFieldselCur:
        selCur = st.selectbox("", options=list(CURRENCIES.keys()), format_func=lambda curCode: f"{curCode} - {CURRENCIES[curCode]}", index=0, key="singleCurrency", help="Betrag, der bei jedem Kaufsignal investiert wird (bzw. einmalig bei Buy and Hold).")

inputColLookBackTime, inputColUserPercent, _ = st.columns(3)
with inputColLookBackTime:
    lookBackTime = st.number_input("Zeitraum(Tage)", min_value=0, value=30, help="Anzahl Tage, über die der höchste/niedrigste Kurs zur Signal-Erkennung betrachtet wird.")
with inputColUserPercent:
    userPercent = st.number_input("Verkaufsanteil(%)", min_value=0, max_value=100, value=50, help="Anteil des aktuellen Bestands, der bei einem Verkaufssignal verkauft wird.")
    userPercent = userPercent / 100

if st.button("Strategien vergleichen"):
    if not ticker:
        st.warning("Es wurde keine Aktie ausgewählt...")
        st.stop()

    comparePrices = load_price_data(ticker, str(startDate), str(endDate), currency=selCur)

    resultBuyHold = sim_buy_hold(comparePrices, investAmount)
    investedBuyHold = pd.Series(investAmount, index=resultBuyHold.index)
    returnBuyHold = (resultBuyHold - investedBuyHold) / investedBuyHold * 100

    resultDCA = sim_dca(comparePrices, investAmount)
    investedDCA = pd.Series(range(1, len(resultDCA) + 1), index=resultDCA.index) * investAmount
    returnDCA = (resultDCA - investedDCA) / investedDCA * 100


    resultHighLow, buyAmountHighLow, investedHighLow = sim_high_low(comparePrices, investAmount, lookBackTime, userPercent)
    returnHighLow = (resultHighLow - investedHighLow) / investedHighLow * 100


    resultRSI, buyAmountRSI, investedRSI = sim_rsi(comparePrices, investAmount, lookBackTime, userPercent)
    returnRSI = (resultRSI - investedRSI) / investedRSI * 100

    compareData = pd.DataFrame({
        "Buy and Hold": returnBuyHold,
        "DCA": returnDCA,
        "High and Low": returnHighLow,
        "RSI": returnRSI,
    })
    compareData = compareData.ffill()

    figCompare = px.line(compareData, title="Strategien vergleichen | Rendite(%)", color_discrete_sequence=["#5E3122", "#2E6F73", "#B23A48", "#6B5895"])
    figCompare.update_layout(
                        plot_bgcolor="#F9D2BA", 
                        template="plotly_dark", 
                        title_font={"color": "#5E3122"},
                        legend_title_text="Strategie",
                        xaxis_title= "Datum",
                        xaxis={
                                "title": {"font": {"color": "#5E3122"}},
                                "gridcolor" : "#5E3122", 
                                "tickfont" : {"color": "#5E3122"},
                            },
                        yaxis_title="Rendite(%)",
                        yaxis={
                                "title": {"font": {"color": "#5E3122"}},
                                "gridcolor": "#5E3122", 
                                "tickfont" : {"color": "#5E3122"},
                            })
    st.plotly_chart(figCompare, config={"displayModeBar": False})


    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buy and Hold", f"{resultBuyHold.iloc[-1]:.2f} {selCur}", delta=f"{returnBuyHold.iloc[-1]:.2f}%")
    col2.metric("DCA", f"{resultDCA.iloc[-1]:.2f} {selCur}", delta=f"{returnDCA.iloc[-1]:.2f}%")
    with col3:
        if buyAmountHighLow == 0:
            st.metric("High/Low", "Kein Kauf")
            st.caption("Kein Kauf in dem gewählten Zeitraum.")
        else:            
            st.metric("High/Low", f"{resultHighLow.iloc[-1]:.2f} {selCur}", delta=f"{returnHighLow.iloc[-1]:.2f}%")
    with col4:
        if buyAmountRSI == 0:
            st.metric("RSI", "Kein Kauf")
            st.caption("Kein Kauf in dem gewählten Zeitraum.")
        else:            
            st.metric("RSI", f"{resultRSI.iloc[-1]:.2f} {selCur}", delta=f"{returnRSI.iloc[-1]:.2f}%")


    st.subheader("Investiert")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buy and Hold", f"{investedBuyHold.iloc[-1]:.2f} {selCur}")
    col2.metric("DCA", f"{investedDCA.iloc[-1]:.2f} {selCur}")
    with col3:
            if buyAmountHighLow == 0:
                st.metric("High/Low", "Kein Kauf")
                st.caption("Kein Kauf in dem gewählten Zeitraum.")
            else:       
                col3.metric("High/Low", f"{investedHighLow.iloc[-1]:.2f} {selCur}")
    with col4:
            if investedRSI.iloc[-1] == 0:
                st.metric("RSI", "Kein Kauf")
                st.caption("Kein Kauf in dem gewählten Zeitraum.")
            else:       
                col4.metric("RSI", f"{investedRSI.iloc[-1]:.2f} {selCur}")