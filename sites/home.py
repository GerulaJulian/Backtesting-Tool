"""
Main Homepage
"""

from src.data_loader import load_price_data, load_price_data_multi
from src.utilities.currencies import CURRENCIES
from datetime import date, timedelta
import streamlit as st
import plotly.express as px

# Introduction text
st.title("Backtesting-tool")
st.write("Überblick über den S&P500 sowie Aktien welche in den letzten 30 Tagen besonders Stark gestiegen oder gefallen sind")
selCur = st.selectbox("Währung", options=list(CURRENCIES.keys()), format_func=lambda curCode: f"{curCode} - {CURRENCIES[curCode]}", index=0)

# Date check
enddate = date.today()
startdate = enddate - timedelta(days=30)

# S&P500
st.subheader("S&P500")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        prices = load_price_data("^GSPC", startdate, enddate, currency=selCur)
        closePrices = prices["Close"]
        percent = (closePrices.iloc[-1] - closePrices.iloc[0]) / closePrices.iloc[0] * 100
        st.metric("^GSPC", f"{closePrices.iloc[-1]:.2f} {selCur}", delta=f"{percent:.2f}%")
        sp500chart = px.line(prices, x=prices.index, y="Close", width=300, height=300)
        sp500chart.update_layout(
                                title="",
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
        sp500chart.update_traces(line=dict(color= "#000000"))
        st.plotly_chart(sp500chart, config={"displayModeBar": False})

# top gain, top losstheme.chartCategoricalColors
tickerList = (
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "TSLA", "META", "NFLX", "AMD", "INTC",
    "JPM", "V", "DIS", "KO", "PFE",
    "XOM", "BA", "WMT", "NKE", "ADBE"
)
priceList = load_price_data_multi(tickerList, startdate, enddate, currency=selCur)

change = []
for ticker in tickerList:
    priceMulti = priceList[ticker]
    percent = (priceMulti.iloc[-1] - priceMulti.iloc[0]) / priceMulti.iloc[0] * 100
    change.append((ticker, percent, priceMulti))

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
            st.metric(ticker, f"{prices.iloc[-1]:.2f} {selCur}", delta=f"{percent:.2f} %")
            topGainChart = px.line(prices, x=prices.index, y=prices, width=300, height=300, )
            topGainChart.update_layout(
                                title="",
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
            topGainChart.update_traces(line=dict(color= "#000000"))
            st.plotly_chart(topGainChart,  config={"displayModeBar": False}, key=f"topGain_{ticker}")
# Top gainers row 2
colGain = st.columns(3)
for col, (ticker, percent, prices) in zip(colGain, topGain2):
    with col:
        with st.container(border=True):
            st.metric(ticker, f"{prices.iloc[-1]:.2f} {selCur}", delta=f"{percent:.2f} %")
            topGainChart = px.line(prices, x=prices.index, y=prices, width=300, height=300)
            topGainChart.update_layout(
                                title="",
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
            topGainChart.update_traces(line=dict(color= "#000000"))
            st.plotly_chart(topGainChart, config={"displayModeBar": False}, key=f"topGain_{ticker}")

# Top losers
st.subheader("Top gefallen")
st.write("Aktien welche in den letzten 30 Tagen besonders gefallen sind")
# Top losers row 1 
colLoss = st.columns(3)
for col, (ticker, percent, prices) in zip(colLoss, topLoss1):
    with col:
        with st.container(border=True):
            st.metric(ticker, f"{prices.iloc[-1]:.2f} {selCur}", delta=f"{percent:.2f} %")
            topLossChart = px.line(prices, x=prices.index, y=prices, width=300, height=300)
            topLossChart.update_layout(
                                title="",
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
            topLossChart.update_traces(line=dict(color= "#000000"))
            st.plotly_chart(topLossChart, config={"displayModeBar": False}, key=f"topLoss_{ticker}")
# Top losers row 2
colLoss = st.columns(3)
for col, (ticker, percent, prices) in zip(colLoss, topLoss2):
    with col:
        with st.container(border=True):
            st.metric(ticker, f"{prices.iloc[-1]:.2f} {selCur}", delta=f"{percent:.2f}%")
            topLossChart = px.line(prices, x=prices.index, y=prices, width=300, height=300)
            topLossChart.update_layout(
                                title="",
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
            topLossChart.update_traces(line=dict(color= "#000000"))
            st.plotly_chart(topLossChart, config={"displayModeBar": False}, key=f"topLoss_{ticker}")

