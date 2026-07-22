"""

"""
from data_loader import load_price_data
from strategies.buy_hold import sim_buy_hold
from strategies.dca import sim_dca
import pandas as pd

def calculated_return(portfolioValue: pd.Series, investedAmount: float) -> float:
    CalcReturn = (portfolioValue.iloc[-1] - investedAmount) / investedAmount * 100
    return CalcReturn

if __name__ == "__main__":
    investedAmount = 1000
    importedPrices = load_price_data("AAPL", "2024-01-01", "2025-01-01")
    resultDCA = sim_dca(importedPrices, investedAmount)
    resultBuyHold = sim_buy_hold(importedPrices, investedAmount)
    amountBuyDay = len(resultDCA)
    sumInvestedAmount = investedAmount * amountBuyDay
    returnDCA = calculated_return(resultDCA, sumInvestedAmount)
    returnBuyHold = calculated_return(resultBuyHold, investedAmount)
    print(f"Portfolio Value: {resultDCA}€\nReturn: {returnDCA:.4f}%")
    print(40 * "-")
    print(f"Buy and Hold Return Percentage: {returnBuyHold:.4f}")
    