"""
Beschreibung: DCA strategie
"""

import pandas as pd

def sim_dca(prices: pd.DataFrame, invest_amount: float) -> pd.Series:
    filtered = prices["Close"][prices.index.day >= 15]
    buyDate = filtered.groupby(filtered.index.to_period("M")).head(1)
    sharesPerMonth = invest_amount / buyDate
    cumSumShares = sharesPerMonth.cumsum()
    portfolioValue = cumSumShares * buyDate
    return portfolioValue