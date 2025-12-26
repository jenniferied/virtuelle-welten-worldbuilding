# Worldbuilding Bible

Magazine-style PDF generation für die Worldbuilding-Dokumentation.

## Format

- **Größe:** A3 Querformat (420mm × 297mm)
- **Ränder:** 0.75 inch (19.05mm)
- **Pipeline:** Markdown → Pandoc → LaTeX → LuaLaTeX → PDF

## Verzeichnisstruktur

```
worldbuilding-bible/
├── de/                    # Deutsche Markdown-Quellen
│   ├── 00-cover.md
│   ├── 01-einfuehrung.md
│   └── ...
├── figures/               # Bilder und Diagramme
├── csv/                   # Datendateien
├── export/                # Generierte PDFs
├── template-latex.tex     # LaTeX-Vorlage
└── README.md
```

## Build

```bash
make worldbuilding
```

## Typografie

| Element | Schrift |
|---------|---------|
| Fließtext | Lora 10pt |
| Überschriften | Source Serif 4 Italic |
| Code/Metadaten | JetBrains Mono |

## Spezielle Boxen

```markdown
::: {.lead}
Einleitungstext in größerer Schrift.
:::

::: {.sidebar}
#### Seitenleiste
Zusätzliche Informationen.
:::

::: {.infobox}
Wichtige Hinweise.
:::

::: {.warning}
Warnungen oder kritische Informationen.
:::
```

## Spalten-Layouts

```markdown
::: {.columns-2}
Inhalt in zwei Spalten...
:::

::: {.columns-3}
Inhalt in drei Spalten...
:::
```
