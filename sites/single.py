"""
EinzelAktien simulator
"""

from src.data_loader import load_price_data
from src.strategies.buy_hold import sim_buy_hold
from src.strategies.dca import sim_dca
from src.strategies.high_low import sim_high_low
from src.strategies.rsi import sim_rsi
from src.utilities.currencies import CURRENCIES
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
    launchDate = date.today() - timedelta(hours=8760)
    if ticker != None:
        unixLaunchDate = yf.Ticker(ticker).get_history_metadata()
        launchDate = date.fromtimestamp(unixLaunchDate["firstTradeDate"])
    else:
        pass
    startDate = st.date_input("Startdatum", value=date.today() - timedelta(days=182), min_value=launchDate ,max_value=date.today() - timedelta(days=1))
with inputColEndDate:
    endDate = st.date_input("Enddatum", value=date.today(), min_value=launchDate, max_value=date.today())

# Column for Strategy selection
inputColStrategy, _, _ = st.columns(3)
with inputColStrategy:  
    strategy = st.selectbox("Strategie", ["Buy and Hold", "DCA", "High and Low", "RSI"],help="Buy and Hold: einmaliger Kauf zu Beginn, kein Verkauf. DCA: fester Betrag wird monatlich investiert. High and Low: Kauf bei Tiefpunkten, Verkauf bei Hochpunkten im gewählten Zeitraum. RSI: Kauf bei überverkauftem Markt (RSI < 30), Verkauf bei überkauftem Markt (RSI > 70).")

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
    if strategy == "High and Low" or strategy == "RSI":
        lookBackTime = st.number_input("Zeitraum(Tage)", min_value=0, value=30, help="Anzahl Tage, über die der höchste/niedrigste Kurs zur Signal-Erkennung betrachtet wird.")
with inputColUserPercent:
    if strategy == "High and Low" or strategy == "RSI":
        userPercent = st.number_input("Verkaufsanteil(%)", min_value=0, max_value=100, value=50, help="Anteil des aktuellen Bestands, der bei einem Verkaufssignal verkauft wird.")
        userPercent = userPercent / 100


if st.button("Test starten"):
    if not ticker:
        st.warning("Es wurde keine Aktie ausgewählt...")
        st.stop()

    prices = load_price_data(ticker, str(startDate), str(endDate), currency=selCur)
    chartSingle = px.line(prices, x=prices.index, y="Close", title="Kursverlauf")
    chartSingle.update_layout(
                        plot_bgcolor="#F9D2BA", 
                        template="plotly_dark", 
                        title_font={"color": "#5E3122"},
                        xaxis_title= "Datum", 
                        xaxis={
                                "title": {"font": {"color": "#5E3122"}},
                                "gridcolor" : "#5E3122", 
                                "tickfont" : {"color": "#5E3122"},
                            },
                        yaxis_title= f"Wert({selCur})",
                        yaxis={
                                "title": {"font": {"color": "#5E3122"}},
                                "gridcolor": "#5E3122", 
                                "tickfont" : {"color": "#5E3122"},
                            })
    chartSingle.update_traces(line=dict(color= "#000000"))
    st.plotly_chart(chartSingle, config={"displayModeBar": False})
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
    winOrLoss = result.iloc[-1] - invested
    st.write("Daten für ", ticker)
    invCol, worCol, wLRCol = st.columns(3)
    invCol.metric("Investiert", f"{invested:.2f} {selCur}")
    worCol.metric("Portfolio Wert", f"{result.iloc[-1]:.2f} {selCur}")
    if winOrLoss >= 1:
        wLRCol.metric("Gewinn", f"{winOrLoss:.2f} {selCur}", delta=f"{calcReturn:.2f}%")
    elif winOrLoss <= 1:
        wLRCol.metric("Verlust", f"{winOrLoss:.2f} {selCur}", delta=f"{calcReturn:.2f}%")
    else:
        wLRCol.metric("Kein Gewinn oder Verlust", f"{winOrLoss:.2f} {selCur}", delta=f"{calcReturn:.2f}%")
    
    portfolioData = pd.DataFrame({
        "invested": investedSeries,
        "portfolioValue": result
    })
    fig2 = px.line(portfolioData, title=f"Investiert und Portfolio Wert({selCur})", color_discrete_sequence=["#000000", "#C97B3D"])
    fig2.update_layout(
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
                        yaxis_title= f"Wert({selCur})",
                        yaxis={
                                "title": {"font": {"color": "#5E3122"}},
                                "gridcolor": "#5E3122", 
                                "tickfont" : {"color": "#5E3122"},
                            })
    st.plotly_chart(fig3, config={"displayModeBar": False})