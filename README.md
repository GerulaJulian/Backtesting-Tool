# Backtesting-Tool für Anlagestrategien

BRP-Projekt von Julian Gerula. Simuliert und vergleicht Investmentstrategien (DCA, Hoch-/Tiefpunkt, Buy&Hold, RSI) anhand historischer Kursdaten.

## Setup

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Projektstruktur

```
src/
  data_loader.py     -> Kursdaten laden (yfinance)
  backtest.py         -> Simulations-Engine
  strategies/          -> Eine Datei pro Investmentstrategie
notebooks/             -> Explorative Analysen / Tests
data/                  -> Lokal gecachte Kursdaten (nicht in git)
app.py                  -> Streamlit-Einstiegspunkt
```

## Status

Monat 1 - Einarbeitung in die Bibliotheken.
