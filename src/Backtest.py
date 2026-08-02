"""

"""
from data_loader import load_price_data
from strategies.buy_hold import sim_buy_hold
from strategies.dca import sim_dca
from strategies.high_low import sim_high_low
from strategies.rsi import sim_rsi
import pandas as pd

def calculated_return(portfolioValue: pd.Series, investedAmount: float) -> float:
    CalcReturn = (portfolioValue.iloc[-1] - investedAmount) / investedAmount * 100
    return CalcReturn

if __name__ == "__main__":
    ## Get data
    investedAmount = 1000
    importedPrices = load_price_data("AAPL", "2024-01-01", "2025-01-01")

    ## Get simulated result
    resultDCA = sim_dca(importedPrices, investedAmount)
    resultBuyHold = sim_buy_hold(importedPrices, investedAmount)
    resultHighLow, buyAmountHighLow, _ = sim_high_low(importedPrices, investedAmount, 30, 1.0)
    resultRSI, buyAmountRSI, _ = sim_rsi(importedPrices, investedAmount, 14, 1.0)

    ## Calculate invested Amount
    investedBuyHold = investedAmount
    investedDCA = investedAmount * len(resultDCA)
    investedHighLow = investedAmount * buyAmountHighLow
    investedRSI = investedAmount * buyAmountRSI

    ## Strategy dict
    strategies = [
        {"name": "Buy and Hold", "result": resultBuyHold, "invested": investedBuyHold},
        {"name": "DCA", "result": resultDCA, "invested": investedDCA},
        {"name": "High and Low", "result": resultHighLow, "invested": investedHighLow},
        {"name": "RSI", "result": resultRSI, "invested": investedRSI},
    ]

    for s in strategies:
        calcReturn = calculated_return(s["result"], s["invested"])
        print(f"{s['name']}: {calcReturn:.4f}%")        

