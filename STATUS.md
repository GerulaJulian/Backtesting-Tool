# Projekt-Status (für Claude)

Diese Datei existiert, damit eine neue Claude-Session sofort weiterhelfen kann, egal ob der Chatverlauf verloren geht oder das Gerät wechselt.

## Wichtigstes Prinzip dieses Projekts

Dies ist ein **BRP-Schulprojekt** (Backtesting-Tool für Anlagestrategien). Julian MUSS den Code selbst verstehen und (später) präsentieren/erklären können. Deshalb: **Claude schreibt hier keinen Projekt-Code, sondern ist Tutor** — Konzepte erklären, kleine Schritte vorgeben, Julian tippt selbst, Claude reviewt. Nur Setup/Tooling (venv, git, Ordnerstruktur, diese Status-Datei) darf Claude direkt übernehmen.

Julian ist Anfänger, wird schnell überwältigt bei zu vielen neuen Konzepten auf einmal — immer NUR EIN Konzept/EINE Zeile auf einmal einführen, mit Zwischen-Checks. Bei Selbstzweifeln ("ich bin ein Depp" etc.) gegensteuern, nicht bestätigen — er kriegt Sachen tatsächlich selbst raus, das soll man ihm auch sagen.

Stand 23. Juli 2026: Mac-Migration (von Windows) ist erledigt und Julian arbeitet jetzt komplett auf dem MacBook weiter. Original-Projektbeschreibung liegt jetzt vor (`Projektbeschreibung_Backtesting-Tool.pdf`, 18. März 2026) — wichtigste Punkte unten unter "Original-Projektvorgaben".

## Original-Projektvorgaben (aus der PDF)

- **Ziel:** Backtesting-Tool, Nutzer wählt Aktie/ETF, Zeitraum, Strategie → Tool zeigt erzielte Rendite. Auch Strategien-Vergleich soll möglich sein.
- **Wichtige Regel:** Simulation darf NIE in Zeitpunkte außerhalb des gewählten Zeitraums schauen (kein Lookahead-Bias). Aktuell automatisch eingehalten, weil `load_price_data` nur den gewählten Zeitraum lädt — im Hinterkopf behalten bei neuen Features.
- **Strategien-Definitionen laut Vorgabe:**
  - DCA/Sparplan: fixer Betrag an festgelegtem Zeitpunkt (z.B. 15. jeden Monats) — ✅ entspricht `sim_dca`
  - Hoch-/Tiefpunkt: kaufen bei definiertem Tiefpunkt, verkaufen bei definiertem Hochpunkt — **"definiert" ist NICHT genau vorgegeben**, Julian muss selbst eine konkrete Regel festlegen (z.B. Rolling-Min/Max über X Tage). Noch zu klären.
  - Buy&Hold: einmaliger Kauf, kein Verkauf — ✅ entspricht `sim_buy_hold`
  - RSI: Standard-Zeitraum 14 Tage, Kauf bei RSI < 30, Verkauf bei RSI > 70
- **Technologien laut Vorgabe:** Python, yfinance (statt Polygon.io, kostenfrei), Pandas, **Plotly** explizit für interaktive Grafiken, **Streamlit** fürs Webinterface.
- **Monats-Fahrplan laut Vorgabe:** Monat 1 Bibliotheken lernen, Monat 2 Konzept + 1 Strategie/1 Aktie, Monat 3 mehr Aktien/Strategien, Monat 4 Strategien-Vergleich, Monat 5 UI/Frontend, Monat 6 Feinschliff + **Dokumentation** (separates Dokument, nicht nur Präsentation!) + Präsentationsvorbereitung.
- **BRP-Prüfungsformat (allgemein, unbedingt mit Betreuer/Prüfer bestätigen):** schriftliche Arbeit i.d.R. mind. 6 Wochen vor Prüfungstermin abzugeben, mündliche Präsentation nur ca. 5-7 Minuten + Diskussion (max. 15 Min. gesamt). Julian hat sich vorgenommen, Prüfer wegen genauem Abgabetermin/Format zu kontaktieren.

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
**Update:** Funktion wurde von Julian zu `sim_buy_hold` umbenannt (kürzer). Erfolgreich mit echten AAPL-Daten über `backtest.py` getestet: **35.56% Rendite über 2024** (plausibel, da AAPL 2024 stieg und Buy&Hold in einem Bullenmarkt DCA meist schlägt, weil DCA einen Teil des frühen Anstiegs verpasst).

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

**`src/backtest.py`** — UMGEBAUT (23. Juli) auf echte Vergleichs-Struktur (Liste von Dictionaries + Schleife), ersetzt die alten Wegwerf-Testblöcke pro Strategie. Alle drei fertigen Strategien laufen jetzt nebeneinander und werden einheitlich verglichen:
```python
from data_loader import load_price_data
from strategies.buy_hold import sim_buy_hold
from strategies.dca import sim_dca
from strategies.high_low import sim_high_low
import pandas as pd

def calculated_return(portfolioValue: pd.Series, investedAmount: float) -> float:
    CalcReturn = (portfolioValue.iloc[-1] - investedAmount) / investedAmount * 100
    return CalcReturn

if __name__ == "__main__":
    investedAmount = 1000
    importedPrices = load_price_data("AAPL", "2024-01-01", "2025-01-01")

    resultDCA = sim_dca(importedPrices, investedAmount)
    resultBuyHold = sim_buy_hold(importedPrices, investedAmount)
    resultHighLow, buyAmount = sim_high_low(importedPrices, investedAmount, 30, 1.0)

    investedBuyHold = investedAmount
    investedDCA = investedAmount * len(resultDCA)
    investedHighLow = investedAmount * buyAmount

    strategies = [
        {"name": "Buy and Hold", "result": resultBuyHold, "invested": investedBuyHold},
        {"name": "DCA", "result": resultDCA, "invested": investedDCA},
        {"name": "High and Low", "result": resultHighLow, "invested": investedHighLow},
    ]

    for s in strategies:
        calcReturn = calculated_return(s["result"], s["invested"])
        print(f"{s['name']}: {calcReturn:.4f}%")
```
**Ergebnis mit echten AAPL-2024-Daten (alle plausibel):** Buy and Hold 35.56%, DCA 22.45%, High/Low 6.84% (niedriger, weil die Strategie bei jedem Hochpunkt komplett verkauft und dadurch Teile vom weiteren Anstieg verpasst — macht in einem Bullenmarkt wie 2024 Sinn).
**Wichtiger Konzept-Bugfix (heute, von Julian selbst gefunden nach Anstoß):** `calculated_return` hat ursprünglich automatisch `portfolioValue[0]` (den ersten Wert der Series) als "investierten Betrag" angenommen — das passt für `buy_hold` (einmalige Investition), aber NICHT für DCA, wo jeden Monat neu investiert wird. Ergebnis war eine absurde Rendite von 1369%. Fix: `calculated_return` bekommt den investierten Gesamtbetrag jetzt als expliziten zweiten Parameter (`investedAmount`) übergeben, statt ihn selbst zu raten. Der Aufrufer (hier `__main__`) berechnet vorher selbst, wie viel insgesamt investiert wurde (`investedAmount * len(result)` bei DCA, oder einfach der einmalige Betrag bei `buy_hold`).

**Wichtiges Scope-Konzept, das dabei besprochen wurde:** Eine Funktion sieht NIE automatisch Variablen von außerhalb (auch nicht, wenn die Variable "vorher" im Code steht) — sie sieht nur ihre eigenen Parameter und selbst-definierte Variablen. Werte müssen explizit als Parameter übergeben werden.

**`src/strategies/high_low.py`** — FERTIG (23. Juli), Datei/Funktion heißen `high_low.py`/`sim_high_low` (nicht `hoch_tief.py`, Julian hat sich für englische Namen entschieden):
```python
import pandas as pd

def sim_high_low(prices: pd.DataFrame, investAmount: float, lookBackWindow: int, userPercent: float) -> pd.Series:
    rollingMin = prices["Close"].rolling(lookBackWindow).min()
    rollingMax = prices["Close"].rolling(lookBackWindow).max()
    isLowest = prices["Close"] == rollingMin
    isHighest = prices["Close"] == rollingMax

    sharesAmount = 0
    cashAmount = 0
    buyAmount = 0
    portfolioValue = []

    for date in prices.index:
        price = prices["Close"][date]
        low = isLowest[date]
        high = isHighest[date]
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
```
**Konzept (von Julian selbst festgelegt, da Projektbeschreibung "definierten" Tief-/Hochpunkt nicht konkret vorgibt):** Tiefpunkt = niedrigster Schlusskurs im Rolling-Fenster (`lookBackWindow` Tage, Standard 30) — funktioniert automatisch für JEDE Aktie/jeden Preisbereich. Kauft bei JEDEM Tiefpunkt-Tag nach (akkumuliert Shares, kein "nur kaufen wenn nicht schon investiert"-Gate), verkauft `userPercent` des Bestands bei jedem Hochpunkt-Tag. `userPercent` ist bereits als Parameter vorbereitet (aktuell testweise fest auf `1.0` = 100%), damit später in `app.py` nur noch echter Nutzer-Input durchgereicht werden muss statt die Funktion umzubauen. Gibt ein Tupel zurück `(portfolioValue, buyAmount)` — `buyAmount` = Anzahl tatsächlicher Käufe, wird für die Rendite-Berechnung gebraucht (Gesamtinvestition = `investAmount * buyAmount`).

**`src/strategies/rsi.py`** — FERTIG (23. Juli), von Julian sehr selbstständig gebaut (RSI-Berechnung neu, Kauf/Verkauf-Schleife bewusst von `high_low.py` übernommen/angepasst, da gleiches Muster):
```python
import pandas as pd

def sim_RSI(prices: pd.DataFrame, investAmount: float, period: int, userPercent: float) -> pd.Series:
    diff = prices["Close"].diff()
    gain = diff.clip(lower=0)
    avgGain = gain.rolling(period).mean()
    loss = -diff.clip(upper=0)
    avgLoss = loss.rolling(period).mean()
    rs = avgGain / avgLoss
    rsi = 100 - (100 / (1 + rs))

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
```
`period` (Standard-Idee: 14, wird später in `app.py` als Autofill-Wert mit Nutzer-Änderungsoption verwendet) ist Parameter, kein Fixwert. Kauf bei RSI < 30 (überverkauft), Verkauf von `userPercent` des Bestands bei RSI > 70 (überkauft) — exakt gleiche Kauf/Verkauf-Schleifen-Struktur wie `high_low.py`, nur andere Bedingung.

**ALLE VIER Kernstrategien aus der Projektbeschreibung sind jetzt fertig und im Vergleich integriert (Monat 4 inhaltlich abgeschlossen).** Ergebnis mit echten AAPL-2024-Daten: Buy and Hold 35.56%, DCA 22.45%, High/Low 6.84%, RSI 4.90% — plausible Reihenfolge (aktivere Strategien verpassen in einem Aufwärtstrend immer wieder Teile vom Anstieg durchs Ein-/Aussteigen).

## Architektur (bereits mit Julian besprochen)

```
app.py (User Interface, Monat 5 — IN ARBEIT, siehe unten)
   ↓ nutzt direkt (NICHT über backtest.py, siehe Import-Hinweis unten)
strategies/buy_hold.py, dca.py, rsi.py, high_low.py (einzelne Strategien)
   ↓ nutzt
data_loader.py (holt Kursdaten via yfinance)

backtest.py (eigenständiges Vergleichs-Skript/Testumgebung, läuft separat via `python3 src/backtest.py`)
```
Wichtig: Strategie-Dateien in `src/strategies/` laden NIE selbst Daten, sie bekommen `prices` immer als Parameter. Datenladen passiert nur in `data_loader.py`/`app.py`/`backtest.py`.

**Wichtiger Import-Stolperstein (gelöst):** `app.py` liegt AUSSERHALB von `src/`, `backtest.py` liegt INNERHALB. `backtest.py`s eigene Imports (`from data_loader import ...`) funktionieren nur, wenn es direkt als Skript läuft (`python3 src/backtest.py`), NICHT wenn es von `app.py` aus importiert würde. Lösung: `app.py` importiert komplett eigenständig direkt mit `src.`-Präfix (`from src.data_loader import load_price_data`, `from src.strategies.buy_hold import sim_buy_hold` etc.) und hat eine eigene kleine `calculated_return`-Logik inline — KEIN Import von `backtest.py` nötig. `backtest.py` bleibt unverändert nutzbar als schnelles Test-/Vergleichsskript im Terminal.

## `app.py` — Fortschritt (23. Juli, IN ARBEIT)

Streamlit-UI wird schrittweise gebaut, Task-Liste dazu läuft im Cowork-Tool. Bisher fertig:

1. **Streamlit-Grundgerüst** — läuft mit `streamlit run app.py` (NICHT `python3 app.py`!).
2. **Eingabeformular** — Datum (Start/Ende), Strategie-Dropdown, Investitionsbetrag; bei `High and Low`/`RSI` zusätzlich `lookBackTime` und `userPercent` (als `/100` umgerechnet, da UI in % zeigt aber Funktionen Bruchzahl 0-1 erwarten).
3. **Verknüpfung mit Strategie-Funktionen** — Button ("Test starten") lädt Daten, ruft je nach gewählter Strategie die passende `sim_*`-Funktion auf (if/elif auf den Dropdown-Text), berechnet Rendite. Getestet und mit `backtest.py`-Ergebnissen exakt abgeglichen (z.B. RSI: 4.90% in beiden identisch).
4. **Ticker-Namenssuche mit Live-Vorschlägen** — nutzt `yfinance.Search(...).quotes` (Feld `symbol` = Ticker) KOMBINIERT mit der Zusatz-Bibliothek `streamlit-searchbox` (`pip install streamlit-searchbox`, `from streamlit_searchbox import st_searchbox`) für echtes Tippen-ohne-Enter-Verhalten. Eigene `search()`-Funktion gibt Liste von `(Anzeigetext, Ticker-Symbol)`-Tupeln zurück, `st_searchbox()` übernimmt den Rest. Funktioniert einwandfrei (getestet mit "App" → Live-Vorschläge AppLovin/Apple/Applied Materials etc.).

Aktueller `app.py`-Code (Stand nach Punkt 4, gekürzt um Kommentare):
```python
from src.data_loader import load_price_data
from src.strategies.buy_hold import sim_buy_hold
from src.strategies.dca import sim_dca
from src.strategies.high_low import sim_high_low
from src.strategies.rsi import sim_rsi
import streamlit as st
from streamlit_searchbox import st_searchbox
import yfinance as yf

st.title("Backtesting-Tool")

def search(searchTerm):
    if not searchTerm:
        return []
    searchResults = yf.Search(searchTerm).quotes
    dispResults = []
    for entry in searchResults:
        dispResults.append((f"{entry['shortname']} - {entry['symbol']}", entry['symbol']))
    return dispResults

ticker = st_searchbox(search, placeholder="Unternehmen suchen", key="tickerSearch")
startDate = st.date_input("Startdatum")
endDate = st.date_input("Enddatum")
strategy = st.selectbox("Strategie", ["Buy and Hold", "DCA", "High and Low", "RSI"])
investAmount = st.number_input("Investitionsbetrag(€)", min_value=0.0, value=100.0)

if strategy == "High and Low":
    lookBackTime = st.number_input("...", min_value=0, value=30)
    userPercent = st.number_input("...", min_value=0, max_value=100, value=50)
    userPercent = userPercent / 100
elif strategy == "RSI":
    lookBackTime = st.number_input("...", min_value=0, value=14)
    userPercent = st.number_input("...", min_value=0, max_value=100, value=50)
    userPercent = userPercent / 100

if st.button("Test starten"):
    prices = load_price_data(ticker, str(startDate), str(endDate))
    # if/elif je nach strategy, ruft passende sim_*-Funktion auf, berechnet calcReturn
    # zeigt Rendite mit st.write an
```

**Bekannte kleine Baustelle:** Zeilen mit auskommentiertem alten Code (aus Iterationen) sollten noch aufgeräumt werden, kein Blocker.

## Nächste Schritte

1. **`app.py` Task 5 — Plotly-Grafiken:** Kursverlauf + Portfolio-Value über Zeit als interaktive Charts (Hover-Details), wie in der Projektbeschreibung gefordert.
2. **`app.py` Task 6 — Homepage:** optionale Startseite mit S&P500/Top-Gewinnern (Julians eigene Idee, nice-to-have).
3. Git-Commit für den heutigen Fortschritt nicht vergessen (`rsi.py`, `high_low.py`, `backtest.py`-Umbau, `app.py`-Fortschritt — sehr viel seit dem letzten Commit).
4. Später: Datums-Label-Kosmetikfehler bei DCA fixen, falls für die Präsentation echte Kaufdaten angezeigt werden sollen (kein Blocker aktuell).
5. Julian hat Prüfer wegen Abgabetermin/Format kontaktiert (23. Juli) — Antwort abwarten und hier nachtragen sobald da.
