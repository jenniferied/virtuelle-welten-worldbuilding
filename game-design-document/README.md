# Game Design Document

PDF-Generierung für das Spieldesign-Dokument.

## Format

- **Größe:** A4 Hochformat
- **Ränder:** 2.54cm (1 inch)
- **Pipeline:** Markdown → Pandoc → LaTeX → LuaLaTeX → PDF

## Verzeichnisstruktur

```
game-design-document/
├── de/                    # Deutsche Markdown-Quellen
│   ├── 00-frontmatter.md
│   ├── 01-uebersicht.md
│   └── ...
├── figures/               # GDD-Diagramme
├── export/                # Generierte PDFs
├── template-gdd.tex       # LaTeX-Vorlage
└── README.md
```

## Build

```bash
make gdd
```

## Kapitelstruktur

Empfohlene Kapitel für das GDD:

1. `00-frontmatter.md` - Titelseite und Metadaten
2. `01-uebersicht.md` - Spielübersicht und Konzept
3. `02-gameplay.md` - Gameplay-Mechaniken
4. `03-charaktere.md` - Charaktersystem
5. `04-welt.md` - Weltdesign
6. `05-kampf.md` - Kampfsystem
7. `06-systeme.md` - Weitere Spielsysteme
8. `07-ui-ux.md` - Benutzeroberfläche
9. `08-technisch.md` - Technische Spezifikationen

## YAML Frontmatter

```yaml
---
title: "Dystopian District"
author:
  - "Name"
date: "Dezember 2025"
version: "0.1"
status: "Entwurf"
platform: "PC"
engine: "Unreal Engine 5"
toc: true
---
```
