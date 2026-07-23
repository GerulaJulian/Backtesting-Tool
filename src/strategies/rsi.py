"""
Beschreibung: Rsi...
"""

import pandas as pd

def sim_rsi(prices: pd.DataFrame, investAmount: float, period: int, userPercent: float) -> pd.Series:
    ## calculations
    diff = prices["Close"].diff()
    gain = diff.clip(lower=0)
    avgGain = gain.rolling(period).mean()
    loss = -diff.clip(upper=0)
    avgLoss = loss.rolling(period).mean()
    rs = avgGain / avgLoss
    rsi = 100 - (100 / (1 + rs))

    ## Base list
    sharesAmount = 0
    cashAmount = 0
    buyAmount = 0
    portfolioValue = []

    for date in prices.index:
        price = prices["Close"][date]
        low = rsi[date] < 30
        high = rsi[date] > 70
        
        if low:
            newShares = investAmount / price
            sharesAmount += newShares
            buyAmount += 1
        elif high:
            newShares = sharesAmount * userPercent
            cashAmount += newShares * price
            sharesAmount = sharesAmount - newShares
        else:
            pass

        currentWorth = sharesAmount * price + cashAmount
        portfolioValue.append(currentWorth)
    return pd.Series(portfolioValue, index=prices.index), buyAmount
