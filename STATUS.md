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

**`src/strategies/high_low.py`** — FERTIG, Datei/Funktion heißen `high_low.py`/`sim_high_low` (nicht `hoch_tief.py`, Julian hat sich für englische Namen entschieden). **Update 24. Juli:** gibt jetzt DREI Werte zurück statt zwei (dritter Wert = `investedOverTime`, laufende Summe des investierten Betrags pro Tag, für den "Investiert vs. Portfolio-Wert"-Chart in `app.py` gebraucht):
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
    invested = 0
    investedOverTime = []
    portfolioValue = []

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
```
**Konzept (von Julian selbst festgelegt, da Projektbeschreibung "definierten" Tief-/Hochpunkt nicht konkret vorgibt):** Tiefpunkt = niedrigster Schlusskurs im Rolling-Fenster (`lookBackWindow` Tage, Standard 30) — funktioniert automatisch für JEDE Aktie/jeden Preisbereich. Kauft bei JEDEM Tiefpunkt-Tag nach (akkumuliert Shares, kein "nur kaufen wenn nicht schon investiert"-Gate), verkauft `userPercent` des Bestands bei jedem Hochpunkt-Tag. **Wichtig, da Rückgabewert sich geändert hat:** alle Aufrufe (`backtest.py`, `app.py`) müssen DREI Werte entgegennehmen, z.B. `result, buyAmount, investedSeries = sim_high_low(...)` — wo der dritte Wert nicht gebraucht wird (z.B. in `backtest.py`), einfach `_` als Platzhalter-Name nehmen.

**`src/strategies/rsi.py`** — FERTIG, von Julian sehr selbstständig gebaut (RSI-Berechnung neu, Kauf/Verkauf-Schleife bewusst von `high_low.py` übernommen/angepasst, da gleiches Muster). **Update 24. Juli:** analog zu `high_low.py` jetzt auch mit `investedOverTime` als drittem Rückgabewert:
```python
import pandas as pd

def sim_rsi(prices: pd.DataFrame, investAmount: float, period: int, userPercent: float) -> pd.Series:
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
    invested = 0
    investedOverTime = []
    portfolioValue = []

    for date in prices.index:
        price = prices["Close"][date]
        low = rsi[date] < 30
        high = rsi[date] > 70
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
```
`period` (Standard-Idee: 14, wird in `app.py` als Autofill-Wert mit Nutzer-Änderungsoption verwendet) ist Parameter, kein Fixwert. Kauf bei RSI < 30 (überverkauft), Verkauf von `userPercent` des Bestands bei RSI > 70 (überkauft).

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

**24. Juli — weitere Fortschritte:**

5. **Plotly-Grafiken (Task 5, FERTIG):** Drei Charts im Einzel-Test-Bereich — Kursverlauf (`px.line(prices, x=prices.index, y="Close", ...)`), Portfolio-Wert über Zeit, und ein kombinierter "Investiert vs. Portfolio-Wert"-Chart (zwei Series in einem `pd.DataFrame` kombiniert, dann `px.line(df)` zeichnet automatisch pro Spalte eine Linie mit Legende).
6. **Strategien-Vergleichs-Chart (FERTIG):** Eigener Abschnitt mit eigenem Button ("Strategien vergleichen"), führt alle 4 Strategien mit denselben Einstellungen aus, zeigt Rendite (%, nicht absolute Euro-Werte — wichtige Design-Entscheidung, siehe unten) aller 4 in einem Chart. Erfüllt Funktion 2 der Original-Projektbeschreibung ("Vergleich von Investmentstrategien") — ist also PFLICHT-Feature, keine Kür.
   - **Wichtiger Design-Punkt (von Julian selbst erkannt):** Absolute Portfolio-Werte zwischen Strategien zu vergleichen ist unfair, weil jede Strategie unterschiedlich VIEL Geld über die Zeit investiert (Buy&Hold nur einmal, DCA/High-Low/RSI wiederholt). Lösung: Vergleich über Rendite in % (`(result - investedSeries) / investedSeries * 100`), nicht über Euro-Beträge.
   - **Bug, der auftrat und gefixt wurde:** Formel initial falsch geschrieben als `(result / invested) - invested * 100` statt `(result - invested) / invested * 100` — durch Punkt-vor-Strich kam faktisch nur `-invested*100` raus, daher absurde Werte wie -10000%. Gefixt.
   - **Zweites Problem, gefixt:** DCA hat nur monatliche Datenpunkte, die anderen drei täglich — beim Kombinieren in einem DataFrame entstehen dadurch `NaN`-Lücken (Plotly zeichnet bei `NaN` keine Linie → DCA sah "unsichtbar" aus). Fix: `compareData = compareData.ffill()` (forward-fill, trägt letzten bekannten Wert bis zum nächsten echten Wert weiter) — macht aus DCA eine Treppenstufen-Linie statt Lücken.

Aktueller `app.py`-Code (Stand nach allen bisherigen Punkten):
```python
from src.data_loader import load_price_data
from src.strategies.buy_hold import sim_buy_hold
from src.strategies.dca import sim_dca
from src.strategies.high_low import sim_high_low
from src.strategies.rsi import sim_rsi
import streamlit as st
from streamlit_searchbox import st_searchbox
import yfinance as yf
import plotly.express as px
import pandas as pd

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
    fig = px.line(prices, x=prices.index, y="Close", title="Kursverlauf", labels={"x": "Datum", "y": "Aktien Wert(€)"})
    st.plotly_chart(fig)
    # if/elif je nach strategy: result, invested(Series) berechnen (buy_hold/dca extern, high_low/rsi liefern investedSeries direkt mit)
    calcReturn = (result.iloc[-1] - invested) / invested * 100
    fig2 = px.line(x=result.index, y=result, title="Portfolio Wert(€)", ...)
    st.plotly_chart(fig2)
    portfolioData = pd.DataFrame({"invested": investedSeries, "portfolioValue": result})
    fig3 = px.line(portfolioData, title="Investiert und Portfolio Wert(€)", ...)
    st.plotly_chart(fig3)
    st.write(f"Rendite: {calcReturn:.2f}%")

if st.button("Strategien vergleichen"):
    comparePrices = load_price_data(ticker, str(startDate), str(endDate))
    # alle 4 Strategien ausführen, je invested-Series berechnen/entgegennehmen
    # returnX = (resultX - investedX) / investedX * 100 pro Strategie
    compareData = pd.DataFrame({"Buy and Hold": returnBuyHold, "DCA": returnDCA, "High and Low": returnHighLow, "RSI": returnRSI})
    compareData = compareData.ffill()
    figCompare = px.line(compareData, title="Strategien vergleichen | Rendite(%)")
    st.plotly_chart(figCompare)
```

**Bekannte kleine Baustelle:** Zeilen mit auskommentiertem alten Code (aus Iterationen) sollten noch aufgeräumt werden, kein Blocker.

## Umbau auf Multipage-App — FERTIG (25. Juli)

`app.py` ist jetzt kein Monolith mehr, sondern reiner Router. Neue Struktur (Ordner `sites/`, bewusst auf Projekt-ROOT-Ebene, NICHT in `src/`, und bewusst NICHT `pages/` genannt, um Streamlits ältere Auto-Page-Detection nicht zu triggern):

```
sites/home.py     — Platzhalter-Startseite (Task "Homepage mit Marktübersicht" ist separat noch offen)
sites/single.py   — Einzelportfolio-Test (der alte "Test starten"-Bereich, 1:1 übernommen)
sites/compare.py  — Strategien-Vergleich (der alte "Strategien vergleichen"-Bereich, 1:1 übernommen)
```

`app.py` (neuer kompletter Inhalt):
```python
import streamlit as st

home = st.Page("sites/home.py", title="Home")
single = st.Page("sites/single.py", title="Einzelportfolio")
compare = st.Page("sites/compare.py", title="Vergleichen")

pg = st.navigation([home, single, compare])
pg.run()
```

**Wichtig, von Julian selbst korrekt umgesetzt:** Jede Seite läuft unabhängig (kein automatisches Teilen von Variablen zwischen Seiten), deshalb hat `single.py` UND `compare.py` jeweils ihre EIGENE Kopie der `search()`-Funktion + `ticker`/`startDate`/`endDate`/`strategy`/`investAmount`-Widgets. `session_state`-basiertes Teilen bewusst auf später verschoben (Einfachheit vor Eleganz für jetzt).

**Bug gefunden + gefixt (25. Juli):** `search()` nutzte `entry['shortname']` mit eckigen Klammern — crashte mit `KeyError: 'shortname'`, weil manche `yf.Search()`-Treffer (ETFs, Indizes, Futures) diesen Key gar nicht haben. Da `st_searchbox` bei JEDEM Tastenanschlag neu sucht, führte das dazu, dass der Vorschlags-Dropdown beim Tippen plötzlich verschwand und nicht wiederkam. Fix (von Julian selbst getippt, nach Hinweis auf `.get()` statt `[...]`):
```python
dispResults.append((f"{entry.get('shortname', entry.get('longname', 'Die eingabe ist fehlerhaft'))} - {entry['symbol']}", entry['symbol']))
```
`.get(key, fallback)` gibt einen Fallback zurück statt zu crashen, wenn der Key fehlt — hier verschachtelt: erst `shortname` versuchen, sonst `longname`, sonst Fehlertext. In BEIDEN Dateien (`single.py`, `compare.py`) angewendet. Getestet, funktioniert jetzt sauber durchgängig beim Tippen.

**Multipage-Umbau ist damit inhaltlich fertig und getestet.** Verbleibt: Task "Homepage mit Marktübersicht" (separat, unten) und Git-Commit.

## Homepage mit Marktübersicht — FERTIG (31. Juli)

`sites/home.py` ist jetzt kein Platzhalter mehr. Enthält:

1. **S&P500-Chart** (`^GSPC`, 30 Tage) in einer Box (`st.container(border=True)`), platziert in `st.columns(2)` damit die Box nicht die volle Seitenbreite einnimmt.
2. **Top 6 Gewinner** und **Top 6 Verlierer** (letzte 30 Tage), berechnet aus einer festen `tickerList` (20 bekannte Aktien verschiedener Branchen). Für jeden Ticker wird die Prozent-Veränderung berechnet (`(letzterKurs - ersterKurs) / ersterKurs * 100`), alle Ergebnisse als `(ticker, percent, pricesSeries)`-Tupel in einer Liste gesammelt, dann mit `sorted(..., key=lambda x: x[1], reverse=True)` bzw. ohne `reverse` sortiert und mit Slicing (`[:6]`, `[:3]`, `[3:6]`) in zwei Dreier-Reihen aufgeteilt. Jede Aktie bekommt eine eigene Box mit Mini-Chart + `st.markdown(f"#### {ticker} | {percent:.2f}%")`.
3. **`st.set_page_config(layout="wide")`** wurde in `app.py` (dem Router, NICHT in `home.py`!) ergänzt, weil Streamlit das nur einmal und nur im Entry-Point-File erlaubt — nötig, damit 3 Chart-Boxen nebeneinander genug Platz haben.

**Neue Konzepte, die dabei gelernt/angewendet wurden:** `sorted()` mit `key=lambda x: x[1]` (nach zweitem Tupel-Element sortieren), List-Slicing (`liste[:6]`, `liste[3:6]`), `zip()` um zwei Listen (Spalten + Daten) parallel zu durchlaufen, `st.columns()`/`st.container(border=True)` verschachtelt für Karten-Layout, `st.set_page_config(layout="wide")`.

**Kleine offene Kosmetik (kein Blocker):** Im "Top gefallen"-Block sind Variablennamen/Kommentare noch Kopien vom Gewinner-Block (z.B. `colGain` statt `colLoss`, Kommentar sagt "Top gainers") — funktioniert einwandfrei, nur verwirrend beim Lesen/Erklären. Irgendwann umbenennen.

**Damit ist auch der letzte "Kür"-Punkt (Task #2) fertig — das Projekt hat jetzt ALLE Pflicht-Features UND die zusätzlichen Homepage/Multipage-Ideen von Julian umgesetzt.**

## UI-Feinschliff — `single.py`/`compare.py` (1./2. August)

Beide Seiten wurden nach Fertigstellung nochmal überarbeitet:

- **Spalten-Layout:** Start-/Enddatum nebeneinander, Strategie-Dropdown schmal (eigene Spalte, Rest leer gelassen), `Investitionsbetrag`/`Zeitraum`/`Verkaufsanteil` in einer gemeinsamen 3er-Reihe (`st.columns(3)`) — inkl. der Erkenntnis, dass Widgets aus VERSCHIEDENEN `if`/`elif`-Zweigen trotzdem in denselben, vorher einmal erstellten Spalten landen können (`with col:` muss nicht direkt nach `st.columns()` stehen).
- **Standard-Datumswerte:** `value=date.today() - timedelta(days=182)` (Start, ~6 Monate zurück) / `value=date.today()` (Ende) — `timedelta` kennt nur Tage, keine Kalendermonate, `182` ist eine bewusste Annäherung.
- **Kurze Labels + `help=`-Tooltips:** lange Label-Texte (mit Tippfehlern) wurden gekürzt (z.B. `"Zeitraum(Tage)"`, `"Verkaufsanteil(%)"`), die ausführliche Erklärung wandert in den `help=`-Parameter der Widgets.
- **Intro-Texte** unter jedem Seitentitel ergänzt (Home, Einzelportfolio, Vergleichen) — kurz, sachlich, erklären den Zweck der jeweiligen Seite.
- **Echter Bug gefunden + gefixt in `compare.py`:** `sim_high_low`/`sim_rsi` bekamen weiterhin feste Werte (`30, 1.0` / `14, 1.0`) übergeben, obwohl jetzt echte `lookBackTime`/`userPercent`-Eingabefelder mit Tooltips angezeigt wurden — die Eingabe hatte also gar keine Wirkung. Gefixt, beide Aufrufe nutzen jetzt die Variablen.
- **Bewusste Design-Entscheidung (nach kurzer Diskussion):** `lookBackTime`/`userPercent` bleiben in `compare.py` GETEILT (ein Wert für High-Low UND RSI), nicht pro Strategie getrennt — sonst könnte man eine Strategie durch großzügigere Parameter künstlich besser aussehen lassen als die andere, was dem Fairness-Prinzip des Vergleichs widerspricht (gleiche Logik wie die frühere Entscheidung, in % statt absoluten Euro-Werten zu vergleichen).

## Beide Kosmetik-Punkte — FERTIG (2. August)

- **`dca.py`:** `resample("MS")` (labelte immer mit Monatsanfang) ersetzt durch `filtered.groupby(filtered.index.to_period("M")).head(1)` — behält jetzt das ECHTE Kaufdatum (z.B. der 15./16.) als Index, Werte unverändert korrekt. Neue Konzepte dabei: `.to_period("M")`, `.groupby(...).head(1)`.
- **`home.py`:** "Top gefallen"-Block umbenannt (`colGain`→`colLoss`, `topGainChart`→`topLossChart`, passende Kommentare) — inkl. eines kleinen Bugs, der beim Umbenennen entstand (die `zip(colGain, ...)`-Aufrufe wurden zuerst vergessen mit umzustellen, dadurch wären die Verlierer-Charts in den alten Gewinner-Spalten gelandet) — gefunden und gefixt.

**Damit ist die Code-Basis jetzt wirklich 100% fertig — keine offenen technischen Punkte mehr, nur noch Git-Commit + Doku/Präsentation (Monat 6).**

## Nächste Schritte

1. Git-Commit fällig — seit dem letzten Commit: komplette Homepage, `st.set_page_config(layout="wide")`, UI-Feinschliff auf `single.py`/`compare.py`, Bugfix in `compare.py`, DCA-Datumsfix, `home.py`-Umbenennung.
2. Julian hat Prüfer wegen Abgabetermin/Format kontaktiert (23. Juli) — Antwort noch ausstehend (Stand 2. August).
3. **Nächster großer Schritt:** Monat 6 laut Original-Fahrplan — Feinschliff, Dokumentation (separates Dokument!) und Präsentationsvorbereitung. Umfang hängt noch von der Antwort des Prüfers ab.
4. **Idee für später:** Julian würde nach Projekt-Abschluss das Tool zum Lernen nochmal in React (mit eigener API-Schicht) oder in Swift/SwiftUI nachbauen wollen — explizit NICHT fürs Schulprojekt, rein zum Selbstlernen danach.
