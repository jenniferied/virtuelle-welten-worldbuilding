# Dystopian District

Worldbuilding Bible und Game Design Document für das Fach Virtuelle Welten.

**Thema:** Eine dystopische, sowjetisch inspirierte Schneemetropole mit korrupten Versionen sowjetischer Zeichentrickfiguren.

## Projektstruktur

```
├── assets/
│   ├── fonts/          # Schriftarten (Lora, Open Sans, etc.)
│   └── logos/          # TH OWL + MP Logos
│
├── worldbuilding-bible/
│   ├── de/             # Deutsche Markdown-Kapitel
│   ├── figures/        # Bilder und Diagramme
│   ├── csv/            # Datendateien
│   ├── export/         # Generierte PDFs
│   └── template-latex.tex
│
├── game-design-document/
│   ├── de/             # Deutsche GDD-Kapitel
│   ├── figures/        # GDD-Diagramme
│   ├── export/         # Generierte PDFs
│   └── template-gdd.tex
│
├── scripts/            # Build-Automatisierung
├── Makefile
└── README.md
```

## Build-Befehle

```bash
# Alle Dokumente bauen
make all

# Worldbuilding Bible (A3 Querformat)
make worldbuilding

# Game Design Document (A4 Hochformat)
make gdd

# Aufräumen
make clean
```

## Voraussetzungen

- **LuaLaTeX** (via MacTeX oder TeX Live)
- **Pandoc**
- **Python 3**

### Installation (macOS)

```bash
brew install --cask mactex
brew install pandoc
```

## Schriftarten

| Verwendung | Schriftart |
|------------|------------|
| Fließtext | Lora 10pt |
| Überschriften | Source Serif 4 Italic |
| Sans-Serif | Open Sans |
| Monospace | JetBrains Mono |

## Lizenz

Internes Projekt für TH OWL.
