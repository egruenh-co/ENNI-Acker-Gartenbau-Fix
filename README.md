# ENNI Acker-Gartenbau Fix

Konvertiert **GARTENBAU**-Schläge in ENNI-XML-Dateien (Dube-Export) nach **ACKER-GARTENBAU**, damit eine Zwischenfrucht/Gründüngung (HERBSTANSAAT) dokumentiert werden kann.

## Hintergrund

In ENNI gibt es zwei Gartenbau-Nutzungsarten:

| Nutzungsart | Anbauten | HERBSTANSAAT |
|---|---|---|
| **GARTENBAU** | 2 (Vorfrucht + Gartenbaukultur) | ❌ nicht erlaubt |
| **ACKER-GARTENBAU** | 3 (Vorfrucht + Herbstansaat + Gartenbaukultur) | ✅ erlaubt |

Dube exportiert Gartenbau-Schläge immer als `GARTENBAU`. Wenn zwischen Vorfrucht und Gartenbaukultur eine Zwischenfrucht/Gründüngung stand, muss die Nutzungsart auf `ACKER-GARTENBAU` umgestellt werden.

## Was das Script macht

Pro GARTENBAU-Schlag:

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

```bash
git clone https://github.com/egruenh-co/ENNI-Acker-Gartenbau-Fix.git
cd ENNI-Acker-Gartenbau-Fix
```

Python 3.7+ wird benötigt. Es gibt keine externen Abhängigkeiten (nur Python-Standardbibliothek).

## Verwendung

```bash
# Grundaufruf (überschreibt Eingabedatei, legt .bak-Backup an)
python fix_acker_gartenbau.py ENNI_Export.xml

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
| `--no-backup` | Kein `.bak`-Backup der Eingabedatei anlegen |
| `--bz-vorjahr` | Bezugszeitraum für Vorfrucht und Herbstansaat (Standard: `2024`) |
| `--dry-run` | Nur anzeigen, was geändert würde |

## Nach dem Umbau

Die erzeugte XML-Datei kann in ENNI importiert werden. Die HERBSTANSAAT-Standardwerte (ZFrucht028, Gründüngung ohne Leguminosen, Aussaat bis 15.09., Ernterückstand ABGEFROREN, Ertrag 300) können nach dem Import in ENNI angepasst werden.

## Lizenz

MIT – siehe [LICENSE](LICENSE).
