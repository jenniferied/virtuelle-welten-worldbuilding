# Build Scripts

Python-Skripte für die PDF-Generierung.

## Verfügbare Skripte

### build-worldbuilding.py

Baut die Worldbuilding Bible als A3-Querformat-PDF.

```bash
python scripts/build-worldbuilding.py
python scripts/build-worldbuilding.py --tex-only    # Nur TeX generieren
python scripts/build-worldbuilding.py --check-deps  # Abhängigkeiten prüfen
```

### build-gdd.py

Baut das Game Design Document als A4-PDF.

```bash
python scripts/build-gdd.py
python scripts/build-gdd.py --merge-only  # Nur Markdown zusammenführen
```

## Voraussetzungen

- Python 3.8+
- Pandoc
- LuaLaTeX (MacTeX oder TeX Live)
