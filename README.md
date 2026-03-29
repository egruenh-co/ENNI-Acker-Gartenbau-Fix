# ENNI Acker-Gartenbau Fix

Konvertiert **GARTENBAU**-Schläge in ENNI-XML-Dateien (Dube-Export) nach **ACKER-GARTENBAU**, damit eine Zwischenfrucht/Gründüngung (HERBSTANSAAT) dokumentiert werden kann.

**Nur Schläge mit tatsächlicher Herbstansaat werden umgebaut.** Schläge ohne Herbstansaat bleiben als GARTENBAU erhalten.

## Hintergrund

In ENNI gibt es zwei Gartenbau-Nutzungsarten:

| Nutzungsart | Anbauten | HERBSTANSAAT |
|---|---|---|
| **GARTENBAU** | 2 (Vorfrucht + Gartenbaukultur) | ❌ nicht erlaubt |
| **ACKER-GARTENBAU** | 3 (Vorfrucht + Herbstansaat + Gartenbaukultur) | ✅ erlaubt |

Dube exportiert Gartenbau-Schläge immer als `GARTENBAU`. Wenn zwischen Vorfrucht und Gartenbaukultur eine Zwischenfrucht/Gründüngung stand, muss die Nutzungsart auf `ACKER-GARTENBAU` umgestellt werden.

## Was das Script macht

Im **Standardmodus** prüft das Script pro GARTENBAU-Schlag, ob Düngungen aus dem Vorjahr unter dem GARTENBAU- oder Vorfrucht-Anbau vorliegen. Nur wenn ja (= Herbstansaat-Indikator), wird der Schlag umgebaut. Alternativ können Schlagnummern explizit per `--schlagnummern` angegeben oder mit `--alle` alle Schläge umgebaut werden.

Pro betroffenen Schlag:

1. **Nutzungsart** von `GARTENBAU` auf `ACKER-GARTENBAU` ändern
2. **Bezugszeitraum der Vorfrucht** korrigieren (Dube exportiert fälschlich das aktuelle Jahr statt des Vorjahres)
3. **HERBSTANSAAT-Anbau** als Lfd=2 einfügen (ZFrucht028 = Gründüngung ohne Leguminosen)
4. **GARTENBAU-Anbau** von Lfd=2 auf Lfd=3 hochsetzen
5. **Düngungen aus dem Vorjahr** von GARTENBAU nach HERBSTANSAAT verschieben
6. **Anbauten** nach lfd-nr sortieren

### Anbaustruktur vorher (Dube-Export)

```
Lfd=1  FK=GARTENBAU-VORFRUCHT-ACKERBAU  BZ=2025  ← fehlerhaft
Lfd=2  FK=GARTENBAU                     BZ=2025
```

### Anbaustruktur nachher

```
Lfd=1  FK=GARTENBAU-VORFRUCHT-ACKERBAU  BZ=2024  ← korrigiert
Lfd=2  FK=HERBSTANSAAT                  BZ=2024  ← neu eingefügt
Lfd=3  FK=GARTENBAU                     BZ=2025
```

## Installation

Voraussetzung ist **Python 3.7 oder neuer**. Es werden keine externen Pakete benötigt (nur Python-Standardbibliothek).

---

### Windows

#### 1. Python installieren

1. Öffne <https://www.python.org/downloads/> und klicke auf **Download Python 3.x.x**.
2. Starte die heruntergeladene `.exe`-Datei.
3. **Wichtig:** Setze den Haken bei **"Add python.exe to PATH"**, bevor du auf *Install Now* klickst.
4. Nach der Installation prüfen — öffne die **Eingabeaufforderung** (`Win + R` → `cmd` → Enter):
   ```
   python --version
   ```
   Es sollte z. B. `Python 3.12.3` erscheinen.

#### 2. Script herunterladen

**Variante A – als ZIP (ohne Git):**

1. Öffne <https://github.com/egruenh-co/ENNI-Acker-Gartenbau-Fix> im Browser.
2. Klicke auf den grünen **Code**-Button → **Download ZIP**.
3. Entpacke die ZIP-Datei in einen beliebigen Ordner, z. B. `C:\Users\MeinName\ENNI-Fix`.

**Variante B – mit Git:**

Falls Git bereits installiert ist (oder von <https://git-scm.com/downloads/win> installiert wird):

```
git clone https://github.com/egruenh-co/ENNI-Acker-Gartenbau-Fix.git
cd ENNI-Acker-Gartenbau-Fix
```

#### 3. Script ausführen

Öffne die **Eingabeaufforderung** und wechsle in den entpackten Ordner:

```
cd C:\Users\MeinName\ENNI-Fix\ENNI-Acker-Gartenbau-Fix-main
python fix_acker_gartenbau.py ENNI_Export.xml
```

---

### macOS

#### 1. Python installieren

macOS bringt seit Catalina kein vorinstalliertes Python 3 mehr mit. Prüfe zuerst im **Terminal** (`Programme → Dienstprogramme → Terminal`):

```bash
python3 --version
```

Falls Python nicht vorhanden ist:

1. Öffne <https://www.python.org/downloads/macos/> und lade das macOS-Installationspaket herunter.
2. Öffne die `.pkg`-Datei und folge dem Installationsassistenten.

#### 2. Script herunterladen

**Variante A – als ZIP (ohne Git):**

1. Öffne <https://github.com/egruenh-co/ENNI-Acker-Gartenbau-Fix> im Browser.
2. Klicke auf den grünen **Code**-Button → **Download ZIP**.
3. Entpacke die ZIP-Datei (Doppelklick im Finder).

**Variante B – mit Git:**

Git ist auf macOS oft schon vorhanden. Falls nicht, installiert der Befehl `git` automatisch die Xcode Command Line Tools. Im Terminal:

```bash
git clone https://github.com/egruenh-co/ENNI-Acker-Gartenbau-Fix.git
cd ENNI-Acker-Gartenbau-Fix
```

#### 3. Script ausführen

```bash
cd ~/Downloads/ENNI-Acker-Gartenbau-Fix-main   # oder der Ordner, in den entpackt wurde
python3 fix_acker_gartenbau.py ENNI_Export.xml
```

> **Hinweis:** Unter macOS heißt der Befehl `python3` (nicht `python`).

---

### Linux (Debian/Ubuntu)

#### 1. Python installieren

Die meisten Linux-Distributionen haben Python 3 vorinstalliert. Prüfe im Terminal:

```bash
python3 --version
```

Falls nicht vorhanden:

```bash
sudo apt update
sudo apt install python3
```

#### 2. Script herunterladen

**Variante A – als ZIP (ohne Git):**

1. Öffne <https://github.com/egruenh-co/ENNI-Acker-Gartenbau-Fix> im Browser.
2. Klicke auf den grünen **Code**-Button → **Download ZIP**.
3. Entpacke mit: `unzip ENNI-Acker-Gartenbau-Fix-main.zip`

**Variante B – mit Git:**

```bash
sudo apt install git          # falls git nicht vorhanden
git clone https://github.com/egruenh-co/ENNI-Acker-Gartenbau-Fix.git
cd ENNI-Acker-Gartenbau-Fix
```

#### 3. Script ausführen

```bash
cd ENNI-Acker-Gartenbau-Fix-main   # oder ENNI-Acker-Gartenbau-Fix bei git clone
python3 fix_acker_gartenbau.py ENNI_Export.xml
```

## Verwendung

```bash
# Standardmodus: nur Schläge mit Vorjahr-Düngungen umbauen (= Herbstansaat erkannt)
python fix_acker_gartenbau.py ENNI_Export.xml

# Nur bestimmte Schläge umbauen (explizite Schlagnummern)
python fix_acker_gartenbau.py ENNI_Export.xml --schlagnummern 9,12

# Alle GARTENBAU-Schläge umbauen (ohne Herbstansaat-Prüfung)
python fix_acker_gartenbau.py ENNI_Export.xml --alle

# Ausgabe in separate Datei
python fix_acker_gartenbau.py ENNI_Export.xml -o ENNI_Export_fixed.xml

# Dry-Run (nur anzeigen, nichts schreiben)
python fix_acker_gartenbau.py ENNI_Export.xml --dry-run

# Ohne Backup
python fix_acker_gartenbau.py ENNI_Export.xml --no-backup

# Anderes Vorjahr (z.B. für Düngejahr 2026)
python fix_acker_gartenbau.py ENNI_Export.xml --bz-vorjahr 2025
```

### Optionen

| Option | Beschreibung |
|---|---|
| `input` | Pfad zur ENNI-XML-Eingabedatei (Dube-Export) |
| `-o`, `--output` | Pfad zur Ausgabedatei (Standard: Eingabedatei wird überschrieben) |
| `--schlagnummern` | Nur diese Schläge umbauen (Komma-getrennt, z.B. `9,12,15`). Umbau erfolgt ohne Herbstansaat-Prüfung, HERBSTANSAAT wird mit Standard-Gründüngung angelegt. |
| `--alle` | Alle GARTENBAU-Schläge umbauen (ohne Herbstansaat-Prüfung) |
| `--no-backup` | Kein `.bak`-Backup der Eingabedatei anlegen |
| `--bz-vorjahr` | Bezugszeitraum Vorjahr (Standard: aus XML `<bezugsjahr>` ermittelt) |
| `--dry-run` | Nur anzeigen, was geändert würde |

### HERBSTANSAAT-Standardwerte

Der eingefügte HERBSTANSAAT-Anbau wird immer mit folgenden Werten angelegt — auch bei `--schlagnummern` ohne vorhandene Düngungen:

| Feld | Wert |
|---|---|
| Fruchtart | `ZFrucht028` (ZF Gründüngung ohne Leguminosen) |
| Aussaattermin | `bis 15.09.` |
| Ernterückstand | `ABGEFROREN` |
| Ertrag | `300` dt/ha |

Diese Werte können nach dem Import in ENNI angepasst werden.

### Erkennungslogik (Standardmodus)

Ohne `--schlagnummern` oder `--alle` erkennt das Script automatisch, ob ein Schlag eine Herbstansaat hatte:

1. Prüfe, ob unter dem **GARTENBAU-Anbau** Düngungen aus dem Vorjahr liegen
2. Prüfe, ob unter der **Vorfrucht** Düngungen aus dem Vorjahr liegen
3. Nur wenn mindestens eine Vorjahr-Düngung gefunden → **Umbau auf ACKER-GARTENBAU**
4. Sonst → Schlag bleibt als **GARTENBAU** erhalten

## Nach dem Umbau

Die erzeugte XML-Datei kann in ENNI importiert werden.

## Hinweis

- Das Script wurde anhand von ENNI-Export-Dateien aus **Myfarm24/Dube** getestet. Bei Export-Dateien aus anderen Quellen können Abweichungen im XML-Format auftreten.
- Das Bezugsjahr wird automatisch aus dem XML-Element `<bezugsjahr>` ermittelt (Vorjahr = Bezugsjahr - 1). Mit `--bz-vorjahr` kann es manuell überschrieben werden.

## Lizenz

MIT – siehe [LICENSE](LICENSE).
