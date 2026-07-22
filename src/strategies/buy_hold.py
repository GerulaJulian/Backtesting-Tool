"""
Beschreibung: Einmaliger Kauf am Anfang, Halten bis zum Ende.
"""

import pandas as pd

testPrices = pd.DataFrame({"Close": [100, 110, 90, 120]})

def sim_buy_hold(testPrices: pd.DataFrame, investAmount: float) -> pd.Series:
    startPrice = testPrices["Close"].iloc[0]
    shares = investAmount / startPrice
    portfolioValue = testPrices["Close"] * shares
    return portfolioValue

if __name__ == "__main__":
    simRes = sim_buy_hold(testPrices, 1000)
    print(simRes)

