"""
Beschreibung: Kauf bei tiefpunkt(von letzten "userinput" tagen) verkauf(von %)bei hochpunkt(von letzten "userinput" tagen)
"""

import pandas as pd

def sim_high_low(prices: pd.DataFrame, investAmount: float, lookBackWindow: int, userPercent: float) -> pd.Series:
    ## get lowest price for timeframe, and turn into true or false if it is the same as date Price
    rollingMin = prices["Close"].rolling(lookBackWindow).min()
    rollingMax = prices["Close"].rolling(lookBackWindow).max()
    isLowest = prices["Close"] == rollingMin
    isHighest = prices["Close"] == rollingMax

    ## base list
    sharesAmount = 0
    cashAmount = 0
    buyAmount = 0
    invested = 0
    investedOverTime = []
    portfolioValue = []

    # checks every day if price = low or high and calculates base list
    for date in prices.index:
        price = prices["Close"][date]
        low = isLowest[date]
        high = isHighest[date]
        
        if low:
            newShares = investAmount / price
            sharesAmount += newShares
            invested += investAmount
            buyAmount += 1
        elif high:
            newShares = sharesAmount * userPercent
            cashAmount += newShares * price
            sharesAmount = sharesAmount - newShares
        else:
            pass

        currentWorth = sharesAmount * price + cashAmount
        portfolioValue.append(currentWorth)
        investedOverTime.append(invested)
    return pd.Series(portfolioValue, index=prices.index), buyAmount, pd.Series(investedOverTime, index=prices.index)
        


