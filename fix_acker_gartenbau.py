#!/usr/bin/env python3
"""
Umbau GARTENBAU → ACKER-GARTENBAU in ENNI-XML-Dateien (Dube-Export).

Dube exportiert Gartenbau-Schläge als Nutzungsart GARTENBAU. Wenn eine
Zwischenfrucht/Gründüngung (HERBSTANSAAT) dokumentiert werden soll, muss
die Nutzungsart auf ACKER-GARTENBAU umgestellt werden.

**Nur Schläge mit tatsächlicher Herbstansaat werden umgebaut.**
Erkennungslogik (Standardmodus):
  - Düngungen aus dem Vorjahr unter GARTENBAU- oder Vorfrucht-Anbau
    → Herbstansaat-Indikator → Umbau
  - Alternativ: explizit per --schlagnummern angeben
  - Oder: --alle für alle GARTENBAU-Schläge (ohne Prüfung)

Pro betroffenen Schlag wird:
  1. Nutzungsart von GARTENBAU auf ACKER-GARTENBAU geändert
  2. Bezugszeitraum der Vorfrucht (GARTENBAU-VORFRUCHT-ACKERBAU) korrigiert
     (Dube exportiert fälschlich das aktuelle Jahr statt des Vorjahres)
  3. Neuer HERBSTANSAAT-Anbau als Lfd=2 eingefügt
     (ZFrucht028 = Gründüngung ohne Leguminosen, Standardwerte)
  4. GARTENBAU-Anbau von Lfd=2 auf Lfd=3 hochgesetzt
  5. Düngungen aus dem Vorjahr von GARTENBAU nach HERBSTANSAAT verschoben
  6. Anbauten nach lfd-nr sortiert

Anbaustruktur vorher (GARTENBAU):
  Lfd=1  FK=GARTENBAU-VORFRUCHT-ACKERBAU  BZ=2025  (fehlerhaft)
  Lfd=2  FK=GARTENBAU                     BZ=2025

Anbaustruktur nachher (ACKER-GARTENBAU):
  Lfd=1  FK=GARTENBAU-VORFRUCHT-ACKERBAU  BZ=2024  (korrigiert)
  Lfd=2  FK=HERBSTANSAAT                  BZ=2024  (neu)
  Lfd=3  FK=GARTENBAU                     BZ=2025  (angepasst)
"""

import argparse
import shutil
import sys
import xml.etree.ElementTree as ET


def parse_args():
    parser = argparse.ArgumentParser(
        description="ENNI-XML: Gartenbau-Schläge auf Acker-Gartenbau umbauen"
    )
    parser.add_argument("input", help="Pfad zur ENNI-XML-Eingabedatei (Dube-Export)")
    parser.add_argument(
        "-o", "--output",
        help="Pfad zur Ausgabedatei (Standard: Eingabedatei wird überschrieben)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Kein Backup der Eingabedatei anlegen",
    )
    parser.add_argument(
        "--bz-vorjahr",
        help="Bezugszeitraum für Vorfrucht und Herbstansaat (Standard: aus XML ermittelt)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur anzeigen, was geändert würde, ohne Datei zu schreiben",
    )
    parser.add_argument(
        "--schlagnummern",
        help="Nur diese Schläge umbauen (Komma-getrennt, z.B. 9,12,15)",
    )
    parser.add_argument(
        "--alle",
        action="store_true",
        help="Alle GARTENBAU-Schläge umbauen (ohne Herbstansaat-Prüfung)",
    )
    return parser.parse_args()


def create_herbstansaat(anbauten, bz_vorjahr):
    """Neuen HERBSTANSAAT-Anbau als Lfd=2 erstellen."""
    herbst = ET.SubElement(anbauten, "anbau")
    ET.SubElement(herbst, "fruchtklasse").text = "HERBSTANSAAT"
    ET.SubElement(herbst, "anbau-im-fremdbetrieb").text = "false"
    ET.SubElement(herbst, "kulturfolge").text = "1"
    ET.SubElement(herbst, "lfd-nr").text = "2"
    ET.SubElement(herbst, "bezugszeitraum").text = bz_vorjahr
    return herbst


def move_vorjahr_duengungen(gb_anbau, herbst_anbau, bz_vorjahr):
    """Düngungen aus dem Vorjahr von GARTENBAU nach HERBSTANSAAT verschieben."""
    gb_duengungen = gb_anbau.find("duengungen")
    if gb_duengungen is None:
        return []

    to_move = []
    for d in gb_duengungen.findall("duengung"):
        ad = d.find("aufbringdatum")
        if ad is not None and ad.text.startswith(bz_vorjahr):
            to_move.append(d)

    if not to_move:
        return []

    herbst_duengungen = herbst_anbau.find("duengungen")
    if herbst_duengungen is None:
        herbst_duengungen = ET.SubElement(herbst_anbau, "duengungen")

    moved = []
    for d in to_move:
        ad = d.find("aufbringdatum").text
        bez = d.find("duenger-bezeichnung")
        bez_text = bez.text if bez is not None else "?"
        gb_duengungen.remove(d)
        herbst_duengungen.append(d)
        moved.append(f"{ad} {bez_text}")

    return moved


def sort_anbauten(anbauten):
    """Anbauten nach lfd-nr sortieren."""
    all_anbau = list(anbauten.findall("anbau"))
    for a in all_anbau:
        anbauten.remove(a)
    all_anbau.sort(key=lambda a: int(a.find("lfd-nr").text))
    for a in all_anbau:
        anbauten.append(a)


def has_vorjahr_duengungen(anbau, bz_vorjahr):
    """Prüft ob ein Anbau Düngungen aus dem Vorjahr hat."""
    duengungen = anbau.find("duengungen")
    if duengungen is None:
        return False
    for d in duengungen.findall("duengung"):
        ad = d.find("aufbringdatum")
        if ad is not None and ad.text and ad.text.startswith(bz_vorjahr):
            return True
    return False


def fix_schlag(schlag, bz_vorjahr, explicit_snr=None, force_all=False):
    """Einen GARTENBAU-Schlag auf ACKER-GARTENBAU umbauen.

    Umbau erfolgt nur wenn:
      - Schlagnummer in explicit_snr (falls angegeben), oder
      - force_all=True, oder
      - Düngungen aus dem Vorjahr unter GARTENBAU/Vorfrucht erkannt

    Returns:
        dict mit Ergebnis-Infos, oder
        None bei Skip/Fehler, oder
        'skipped' wenn keine Herbstansaat erkannt.
    """
    nutz = schlag.find("nutzungsart")
    sname = schlag.find("schlagname")
    snr_el = schlag.find("schlagnummer")
    if nutz is None or nutz.text != "GARTENBAU":
        return None

    name = sname.text if sname is not None else "?"
    snr = snr_el.text if snr_el is not None else "?"

    anbauten = schlag.find("anbauten")
    if anbauten is None:
        print(f"  WARNUNG: {name} hat keine Anbauten!", file=sys.stderr)
        return None

    # Finde Vorfrucht und Gartenbau-Anbau
    vorfrucht = None
    gartenbau = None
    for anbau in anbauten.findall("anbau"):
        fk = anbau.find("fruchtklasse")
        if fk is not None:
            if fk.text == "GARTENBAU-VORFRUCHT-ACKERBAU":
                vorfrucht = anbau
            elif fk.text == "GARTENBAU":
                gartenbau = anbau

    if vorfrucht is None or gartenbau is None:
        print(f"  WARNUNG: Schlag {snr} ({name}) - Vorfrucht oder Gartenbau fehlt!", file=sys.stderr)
        return None

    # ── Prüfung: Hat dieser Schlag eine Herbstansaat? ──
    if explicit_snr is not None:
        if snr not in explicit_snr:
            return "skipped"
    elif not force_all:
        if not (has_vorjahr_duengungen(gartenbau, bz_vorjahr)
                or has_vorjahr_duengungen(vorfrucht, bz_vorjahr)):
            return "skipped"

    # 1. Nutzungsart umcodieren
    nutz.text = "ACKER-GARTENBAU"

    # 2. BZ der Vorfrucht auf Vorjahr setzen
    bz_vf = vorfrucht.find("bezugszeitraum")
    old_bz = bz_vf.text if bz_vf is not None else "?"
    if bz_vf is not None:
        bz_vf.text = bz_vorjahr

    # 3. HERBSTANSAAT-Eintrag erstellen
    herbst = create_herbstansaat(anbauten, bz_vorjahr)

    # 4. GARTENBAU-Anbau: Lfd auf 3
    lfd_gb = gartenbau.find("lfd-nr")
    if lfd_gb is not None:
        lfd_gb.text = "3"

    # 5. Düngungen aus dem Vorjahr verschieben
    moved = move_vorjahr_duengungen(gartenbau, herbst, bz_vorjahr)

    # 6. Anbauten sortieren
    sort_anbauten(anbauten)

    return {
        "snr": snr,
        "name": name,
        "old_bz": old_bz,
        "moved_duengungen": moved,
    }


def main():
    args = parse_args()

    tree = ET.parse(args.input)
    root = tree.getroot()

    # Bezugsjahr ermitteln
    if args.bz_vorjahr:
        bz_vorjahr = args.bz_vorjahr
    else:
        bezugsjahr_el = root.find('.//bezugsjahr')
        if bezugsjahr_el is not None:
            bz_vorjahr = str(int(bezugsjahr_el.text) - 1)
        else:
            bz_vorjahr = '2024'
            print("WARNUNG: Kein <bezugsjahr> in XML gefunden, nehme 2024 als Vorjahr")

    # Schlagnummern-Filter
    explicit_snr = None
    if args.schlagnummern:
        explicit_snr = {s.strip() for s in args.schlagnummern.split(',') if s.strip()}
        print(f"Modus: Nur Schläge {', '.join(sorted(explicit_snr))}")
    elif args.alle:
        print("Modus: Alle GARTENBAU-Schläge (--alle)")
    else:
        print(f"Modus: Nur Schläge mit Vorjahr-Düngungen ({bz_vorjahr})")

    results = []
    skipped = 0
    for schlag in root.iter("schlag"):
        result = fix_schlag(schlag, bz_vorjahr, explicit_snr, args.alle)
        if result == "skipped":
            skipped += 1
            snr = schlag.find("schlagnummer")
            sname = schlag.find("schlagname")
            snr_t = snr.text if snr is not None else "?"
            name_t = sname.text if sname is not None else "?"
            print(f"  SKIP: Schlag {snr_t} ({name_t}) – keine Herbstansaat erkannt")
        elif result:
            results.append(result)

    # Ergebnisse ausgeben
    for r in results:
        dueng_info = ""
        if r["moved_duengungen"]:
            dueng_info = f"  Düngungen verschoben: {', '.join(r['moved_duengungen'])}"
        print(
            f"  OK: Schlag {r['snr']} ({r['name']}) → ACKER-GARTENBAU, "
            f"BZ Vorfrucht {r['old_bz']}→{bz_vorjahr}, "
            f"HERBSTANSAAT Lfd=2, GB Lfd=3"
        )
        if dueng_info:
            print(dueng_info)

    print(f"\n{len(results)} Schläge umgebaut, {skipped} übersprungen (keine Herbstansaat).")

    if args.dry_run:
        print("(Dry-Run – keine Datei geschrieben)")
        return

    output = args.output or args.input
    if not args.no_backup and output == args.input:
        backup = args.input + ".bak"
        shutil.copy2(args.input, backup)
        print(f"Backup: {backup}")

    tree.write(output, xml_declaration=True, encoding="UTF-8")
    print(f"Gespeichert: {output}")


if __name__ == "__main__":
    main()
