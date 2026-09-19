"""
Code-Tester
"""
from data_loader import load_price_data
from strategies.buy_hold import sim_buy_hold
from strategies.dca import sim_dca
from strategies.high_low import sim_high_low
from strategies.rsi import sim_rsi
import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import date

def calculated_return(portfolioValue: pd.Series, investedAmount: float) -> float:
    CalcReturn = (portfolioValue.iloc[-1] - investedAmount) / investedAmount * 100
    return CalcReturn

tickerdata = yf.Ticker("AAPL").get_history_metadata()
print(tickerdata["firstTradeDate"])
launchdate = date.fromtimestamp(tickerdata["firstTradeDate"])
print(launchdate)
