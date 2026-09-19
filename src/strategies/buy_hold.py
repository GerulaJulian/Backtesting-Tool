"""
Beschreibung: Einmaliger Kauf am Anfang, Halten bis zum Ende.
"""

import pandas as pd

def sim_buy_hold(prices: pd.DataFrame, investAmount: float) -> pd.Series:
    startPrice = prices["Close"].iloc[0]
    shares = investAmount / startPrice
    portfolioValue = prices["Close"] * shares
    return portfolioValue