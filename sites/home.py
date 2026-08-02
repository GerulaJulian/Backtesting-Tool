"""
Main Homepage
"""

from src.data_loader import load_price_data
from datetime import date, timedelta
import streamlit as st
import plotly.express as px

# Introduction text
st.title("Backtesting-tool")
st.write("Überblick über den S&P500 sowie Aktien welche in den letzten 30 Tagen besonders Stark gestiegen oder gefallen sind")

# Date check
enddate = date.today()
startdate = enddate - timedelta(days=30)

# S&P500
st.subheader("S&P500")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        prices = load_price_data("^GSPC", startdate, enddate)
        sp500chart = px.line(prices, x=prices.index, y="Close", labels={"x": "Datum", "y": "Aktien Wert(€)"}, width=300, height=300)
        st.plotly_chart(sp500chart, config={"displayModeBar": False})

# top gain, top loss
tickerList = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "TSLA", "META", "NFLX", "AMD", "INTC",
    "JPM", "V", "DIS", "KO", "PFE",
    "XOM", "BA", "WMT", "NKE", "ADBE"
]

change = []
for ticker in tickerList:
    prices = load_price_data(ticker, startdate, enddate)
    percent = (prices["Close"].iloc[-1] - prices["Close"].iloc[0]) / prices["Close"].iloc[0] * 100
    change.append((ticker, percent, prices["Close"]))

# Increased the most
topGain = sorted(change, key=lambda x: x[1], reverse=True)
topGain = topGain[:6]
topGain1 = topGain[:3]
topGain2 = topGain[3:6]
# Lost the most
topLoss = sorted(change, key=lambda x: x[1])
topLoss = topLoss[:6]
topLoss1 = topLoss[:3]
topLoss2 = topLoss[3:6]

# Top gainers
st.subheader("Top gestiegen")
st.write("Aktien welche in den letzten 30 Tagen besonders gestigen sind")
# Top gainers row 1 
colGain = st.columns(3)
for col, (ticker, percent, prices) in zip(colGain, topGain1):
    with col:
        with st.container(border=True):
            st.markdown(f"#### {ticker} | {percent:.2f}%")
            topGainChart = px.line(prices, x=prices.index, y=prices, labels={"x": "Datum", "y": "Aktien Wert(€)"}, height=200)
            st.plotly_chart(topGainChart, config={"displayModeBar": False})
# Top gainers row 2
colGain = st.columns(3)
for col, (ticker, percent, prices) in zip(colGain, topGain2):
    with col:
        with st.container(border=True):
            st.markdown(f"#### {ticker} | {percent:.2f}%")
            topGainChart = px.line(prices, x=prices.index, y=prices, labels={"x": "Datum", "y": "Aktien Wert(€)"}, height=200)
            st.plotly_chart(topGainChart, config={"displayModeBar": False})

# Top losers
st.subheader("Top gefallen")
st.write("Aktien welche in den letzten 30 Tagen besonders gefallen sind")
# Top losers row 1 
colLoss = st.columns(3)
for col, (ticker, percent, prices) in zip(colLoss, topLoss1):
    with col:
        with st.container(border=True):
            st.markdown(f"#### {ticker} | {percent:.2f}%")
            topLossChart = px.line(prices, x=prices.index, y=prices, labels={"x": "Datum", "y": "Aktien Wert(€)"}, height=200)
            st.plotly_chart(topLossChart, config={"displayModeBar": False})
# Top losers row 2
colLoss = st.columns(3)
for col, (ticker, percent, prices) in zip(colLoss, topLoss2):
    with col:
        with st.container(border=True):
            st.markdown(f"#### {ticker} | {percent:.2f}%")
            topLossChart = px.line(prices, x=prices.index, y=prices, labels={"x": "Datum", "y": "Aktien Wert(€)"}, height=200)
            st.plotly_chart(topLossChart, config={"displayModeBar": False})

