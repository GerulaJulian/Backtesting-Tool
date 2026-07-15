"""
Einfachste Strategie: Einmaliger Kauf am Anfang, Halten bis zum Ende.
Guter Startpunkt fuer Monat 2, um die Backtest-Engine zu testen.
"""

import pandas as pd


def simulate_buy_and_hold(prices: pd.DataFrame, invest_amount: float) -> pd.Series:
    """
    Simuliert Buy&Hold: kauft am ersten Tag fuer invest_amount, haelt bis zum Ende.

    Args:
        prices: DataFrame mit Spalte "Close", Index = Datum
        invest_amount: Investierter Betrag in Euro

    Returns:
        Series mit dem Depotwert pro Tag
    """
    start_price = prices["Close"].iloc[0]
    shares = invest_amount / start_price
    portfolio_value = prices["Close"] * shares
    return portfolio_value
