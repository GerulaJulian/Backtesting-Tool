"""

"""
from strategies.buy_hold import sim_buy_and_hold
import pandas as pd

testPrices = pd.DataFrame({"Close": [100, 110, 90, 120]})

def calculated_return(portfolioValue: pd.Series) -> float:
    CalcReturn = (portfolioValue.iloc[-1] - portfolioValue[0]) / portfolioValue[0] * 100
    return CalcReturn

if __name__ == "__main__":
    simRes = sim_buy_and_hold(testPrices, 1000)
    returnPercent = int(calculated_return(simRes))
    print(f"{returnPercent}%")