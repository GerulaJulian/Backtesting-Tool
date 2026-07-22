"""

"""
from data_loader import load_price_data
from strategies.buy_hold import sim_buy_and_hold
from strategies.dca import sim_dca
import pandas as pd

def calculated_return(portfolioValue: pd.Series, investedAmount: float) -> float:
    CalcReturn = (portfolioValue.iloc[-1] - investedAmount) / investedAmount * 100
    return CalcReturn

if __name__ == "__main__":
    investedAmount = 1000
    importedPrices = load_price_data("AAPL", "2024-01-01", "2025-01-01")
    result = sim_dca(importedPrices, investedAmount)
    amountBuyDay = len(result)
    sumInvestedAmount = investedAmount * amountBuyDay
    percentReturn = calculated_return(result, sumInvestedAmount)
    print(f"Portfolio Value: {result}€\nReturn: {percentReturn:.4f}%")
    