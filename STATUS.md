# Projekt-Status (für Claude)

Diese Datei existiert, damit eine neue Claude-Session sofort weiterhelfen kann, egal ob der Chatverlauf verloren geht oder das Gerät wechselt.

## Wichtigstes Prinzip dieses Projekts

Dies ist ein **BRP-Schulprojekt** (Backtesting-Tool für Anlagestrategien). Julian MUSS den Code selbst verstehen und (später) präsentieren/erklären können. Deshalb: **Claude schreibt hier keinen Projekt-Code, sondern ist Tutor** — Konzepte erklären, kleine Schritte vorgeben, Julian tippt selbst, Claude reviewt. Nur Setup/Tooling (venv, git, Ordnerstruktur, diese Status-Datei) darf Claude direkt übernehmen.

Julian ist Anfänger, wird schnell überwältigt bei zu vielen neuen Konzepten auf einmal — immer NUR EIN Konzept/EINE Zeile auf einmal einführen, mit Zwischen-Checks. Bei Selbstzweifeln ("ich bin ein Depp" etc.) gegensteuern, nicht bestätigen — er kriegt Sachen tatsächlich selbst raus, das soll man ihm auch sagen.

Stand 22. Juli 2026: Mac-Migration (von Windows) ist erledigt und Julian arbeitet jetzt komplett auf dem MacBook weiter.

## Mac-Setup — ERLEDIGT

Python 3.9.6 (Apple/Xcode Command Line Tools), `venv` neu erstellt (`python3 -m venv venv`, `source venv/bin/activate`), `pip install -r requirements.txt` erfolgreich, Git-Historie ist beim Zip/Unzip erhalten geblieben (`git log --oneline` zeigt alle alten Commits). VS Code installiert, Python-Extension drauf, Projektordner offen. Autocomplete/Ghost-Text/Accessibility-Signals-Sounds wurden in den VS-Code-Settings deaktiviert (`editor.quickSuggestions`, `editor.suggestOnTriggerCharacters`, `editor.inlineSuggest.enabled`, `editor.accessibilitySupport`).

## Bisheriger technischer Fortschritt

**`src/data_loader.py`** — FERTIG, inkl. Bugfix von heute:
```python
import pandas as pd
import yfinance as yf

def load_price_data(ticker: str, start: str, end: str):
    df = yf.download(ticker, start=start, end=end)
    df.columns = df.columns.get_level_values(0)
    return df

if __name__ == "__main__":
    stockData = load_price_data("AAPL", "2024-01-01", "2025-01-01")
```
**Wichtiger Bugfix (heute gefunden):** `yfinance` gibt neuerdings MultiIndex-Spalten zurück (z.B. `('Close', 'AAPL')` statt nur `'Close'`). Dadurch war `df["Close"]` ein einspaltiger DataFrame statt einer Series, was später in JEDER Strategie zu Fehlern führte (`KeyError: 0` bei `portfolioValue[0]` in `calculated_return`, weil DataFrame-Indexierung anders funktioniert als Series-Indexierung). Fix zentral hier mit `df.columns = df.columns.get_level_values(0)` — betrifft/profitiert automatisch ALLE Strategien, da alle über `data_loader.py` laden.

**`src/strategies/buy_hold.py`** — FERTIG, von Julian selbst geschrieben:
```python
import pandas as pd

testPrices = pd.DataFrame({"Close": [100, 110, 90, 120]})

def sim_buy_and_hold(testPrices: pd.DataFrame, investAmount: float) -> pd.Series:
    startPrice = testPrices["Close"].iloc[0]
    shares = investAmount / startPrice
    portfolioValue = testPrices["Close"] * shares
    return portfolioValue

if __name__ == "__main__":
    simRes = sim_buy_and_hold(testPrices, 1000)
    print(simRes)
```
**Noch offen:** Wurde bisher NUR mit den eigenen Fake-Testdaten (`testPrices` oben im Modul) getestet, NIE über `backtest.py` mit echten `yfinance`-Daten. Sollte als nächstes kurz nachgeholt werden (jetzt, wo `data_loader.py` den MultiIndex-Bug gefixt hat, sollte es einfach funktionieren) — guter, schneller Erfolgserlebnis-Schritt, bevor es an die nächste Strategie geht.

**`src/strategies/dca.py`** — FERTIG, heute komplett von Julian selbst geschrieben (inkl. `cumsum()` als neues Konzept):
```python
import pandas as pd

def sim_dca(prices: pd.DataFrame, invest_amount: float) -> pd.Series:
    filtered = prices["Close"][prices.index.day >= 15]
    buyDate = filtered.resample("MS").first()
    sharesPerMonth = invest_amount / buyDate
    cumSumShares = sharesPerMonth.cumsum()
    portfolioValue = cumSumShares * buyDate
    return portfolioValue
```
**Bekannte Eigenart (kein Blocker):** `resample("MS")` beschriftet Zeilen mit dem Monatsanfang (z.B. "2024-01-01"), auch wenn der zugrundeliegende Wert vom 15./16. stammt. Werte stimmen, Datums-Label ist nur kosmetisch irreführend.

**`src/backtest.py`** — aktueller Stand, mit DCA erfolgreich getestet (echte AAPL-Daten, Ergebnis 22.45% Rendite über 2024, manuell nachgerechnet und korrekt):
```python
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
    print(f"Portfolio Value: {result}€\nReturn: {percentReturn}%")
```
**Wichtiger Konzept-Bugfix (heute, von Julian selbst gefunden nach Anstoß):** `calculated_return` hat ursprünglich automatisch `portfolioValue[0]` (den ersten Wert der Series) als "investierten Betrag" angenommen — das passt für `buy_hold` (einmalige Investition), aber NICHT für DCA, wo jeden Monat neu investiert wird. Ergebnis war eine absurde Rendite von 1369%. Fix: `calculated_return` bekommt den investierten Gesamtbetrag jetzt als expliziten zweiten Parameter (`investedAmount`) übergeben, statt ihn selbst zu raten. Der Aufrufer (hier `__main__`) berechnet vorher selbst, wie viel insgesamt investiert wurde (`investedAmount * len(result)` bei DCA, oder einfach der einmalige Betrag bei `buy_hold`).

**Wichtiges Scope-Konzept, das dabei besprochen wurde:** Eine Funktion sieht NIE automatisch Variablen von außerhalb (auch nicht, wenn die Variable "vorher" im Code steht) — sie sieht nur ihre eigenen Parameter und selbst-definierte Variablen. Werte müssen explizit als Parameter übergeben werden.

**`src/strategies/rsi.py`, `src/strategies/hoch_tief.py`** — NOCH NICHT ERSTELLT.

## Architektur (bereits mit Julian besprochen)

```
app.py (User Interface, Monat 5 — noch nicht angefangen)
   ↓ ruft auf
backtest.py (Vergleichs-/Rechen-Logik, Monat 4 — in Arbeit)
   ↓ ruft auf
strategies/buy_hold.py, dca.py, rsi.py, hoch_tief.py (einzelne Strategien)
   ↓ nutzt
data_loader.py (holt Kursdaten via yfinance)
```
Wichtig: Strategie-Dateien in `src/strategies/` laden NIE selbst Daten, sie bekommen `prices` immer als Parameter. Datenladen passiert nur in `backtest.py`.

## Nächste Schritte

1. Kurzer Erfolgs-Schritt: `sim_buy_and_hold` auch mit echten AAPL-Daten über `backtest.py` testen (analog zu DCA), inkl. `calculated_return(result, investAmount)` — bei buy_hold ist der investierte Betrag einfach der einmalige Betrag, kein `len()`-Umweg nötig.
2. Nächste Strategie angehen: `rsi.py` oder `hoch_tief.py` (Julian fragen, was er zuerst machen will).
3. Später: Datums-Label-Kosmetikfehler bei DCA fixen, falls für die Präsentation echte Kaufdaten angezeigt werden sollen (kein Blocker aktuell).
