# ROADMAP: Virtuelle Welten — ПАНЕЛЬКИ

> *Soviet-inspired eternal winter — worldbuilding for dark fantasy CRPG*

## Projekt-Übersicht

30-Sekunden-Cinematic in Soviet-inspired eternal winter. Houdini + Unreal Engine 5.

---

## Literature Review (2026-01-22) ✅

| Domain | Papers | Downloaded | Missing | Status |
|--------|--------|------------|---------|--------|
| Worldbuilding Theory | 13 | 6 | 7 | ✅ Search + download |
| Game Narrative | 11 | 5 | 6 | ✅ Expanded (was 0!) |
| Conlangs & Culture | 7 | 4 | 3 | ✅ Search + download |
| Soviet Architecture | 12 | 5 | 7 | ✅ **NEW DOMAIN** |
| **Total** | **43** | **20** | **23** | |

**Downloaded (20):**
- *Worldbuilding Theory (6):* Wolf 2012, Zaidi 2019, Rauscher 2020, Dunne 2017, WorldBuildingFramework 2019, Maleki 2024
- *Game Narrative (5):* Jenkins 2004, Tarnowetzki 2015, VirtualEnvironmentDesign 2014, IntechOpen 2025, AAU Storyworlds
- *Conlangs & Culture (4):* Brierly 2016, Coker 2021, Secondary Belief 2019, Diva Dynamic
- *Soviet Architecture (5):* Malaia 2020, Zarecor 2010, SeizingDomesticity 2020, SHS Khrushchevka 2019, ACSA Transfers 2016

**Folder Structure:**
```
literature-review/
├── papers/
│   ├── worldbuilding-theory/   # (6 papers)
│   │   ├── tier1-core/
│   │   ├── tier2-important/
│   │   └── tier3-reference/
│   ├── game-narrative/         # (5 papers) ← EXPANDED
│   │   ├── tier1-core/
│   │   └── tier2-important/
│   ├── conlangs-culture/       # (4 papers)
│   └── soviet-architecture/    # (5 papers) ← NEW
│       ├── tier1-core/
│       └── tier2-important/
├── papers-index.md
└── outputs/
```

**iCloud:** `~/Library/Mobile Documents/com~apple~CloudDocs/papers/virtuelle-welten-worldbuilding/`

**Key Books to Acquire:**
- Wolf (2012): Building Imaginary Worlds — "Bible of imaginary worlds"
- Tolkien (1947): On Fairy-Stories — Sub-creation theory
- Juul (2005): Half-Real — Games/fiction theory
- Peterson (2015): The Art of Language Invention — Conlang methodology
- Meuser & Zadorin (2016): Toward a Typology of Soviet Mass Housing — DOM Publishers (panelki reference)

**PDF Download Strategy:**
1. **Author websites** — search `[author] [title] PDF site:[university].edu`
2. **University repositories** — DiVA, NCUR, Signum, WWU Cedar
3. **Conference sites** — DiGRAA, ICCC proceedings
4. **Journal of Futures Studies** — jfsdigital.org (open access)
5. **Game AI Pro** — gameaipro.com (free chapters)
6. **University proxy** — for ACM, Springer, Routledge (TH OWL library → EZproxy)

---

## Game Systems (Pending)

### Custom Logo
| Task | Status |
|------|--------|
| ПАНЕЛЬКИ Logo erstellen | ⬜ |

### Time System
| Task | Status |
|------|--------|
| Time of Day implementieren | ⬜ |
| Day of Week System | ⬜ |
| NPC-Routinen an Tageszeit koppeln | ⬜ |
| UI für Zeit-Anzeige | ⬜ |

### Weather System
| Task | Status |
|------|--------|
| Cold/Snowiness Parameter | ⬜ |
| Weather Impact auf NPC-Routinen | ⬜ |
| Bei Kälte: Leute bleiben zuhause, schlechtere Laune | ⬜ |
| Weather UI | ⬜ |

### Economy System
| Task | Status |
|------|--------|
| Panelrubel-Währung implementieren | ⬜ |
| NPC-Geld-Tracking (jeder NPC hat Budget) | ⬜ |
| Player-Geld-Tracking | ⬜ |
| Kaufen/Verkaufen-Mechanik | ⬜ |
| Simples Inventar-System | ⬜ |
| Economy UI (Geld-Anzeige, Shop-Interface) | ⬜ |

---

## Aktive Aufgaben

### Houdini

| Task | Status |
|------|--------|
| Building Generator fertigstellen | 🔄 |
| UVs für Buildings generieren | ⬜ |
| Texturierung-Lösung finden | ⬜ |
| Bug: Lights spawnen nicht am World Origin (UE) | ⬜ |
| Light Control System (on/off, Farben) | ⬜ |
| Set Dressing | ⬜ |
| Labs Street Generator verstehen & nutzen | ⬜ |

### Unreal Engine 5

| Task | Status |
|------|--------|
| Rendering & Lighting finalisieren | ⬜ |
| Layout-Verbesserungen | ⬜ |

### Process Document (ehem. GDD)

| Task | Status |
|------|--------|
| PCG-Nutzung dokumentieren | ⬜ |
| Pixel Style Post-Process dokumentieren | ⬜ |
| Snow Master Material + Snow System dokumentieren | ⬜ |
| Day-Night Cycle dokumentieren | ⬜ |
| Plugins dokumentieren (UltraDynamicSky, EasySnow) | ⬜ |
| Houdini Engine Pipeline dokumentieren (Landscape, Buildings) | ⬜ |
| Wall Partition dokumentieren | ⬜ |
| Substrate Materials, Nanite, Lumen dokumentieren | ⬜ |
| Planned Features vs. Done trennen | ⬜ |

### Worldbuilding Bible

| Task | Status |
|------|--------|
| Content-Arbeit (TBD) | ⬜ |
| Layout-Tweaks | ⬜ |

---

## Worldbuilding Agents (2026-01-22) ✅

Academic frameworks from literature review encoded into Claude Code agents.

**Architecture:**
```
panelki (orchestrator)
    ├── worldbuild-analyst  (Zaidi/Wolf frameworks)
    ├── faction-developer   (systematic faction design)
    ├── lore-checker        (Tolkien consistency)
    └── location-designer   (Jenkins environmental storytelling)
```

**Skills (framework knowledge):**
| Skill | Source | Purpose |
|-------|--------|---------|
| `zaidi-foundations` | Zaidi 2019 | Seven Foundations systematic analysis |
| `wolf-subcreation` | Wolf 2012 | Transnarrative, canonicity circles |
| `jenkins-environmental` | Jenkins 2004 | Evocative/enacted/embedded/emergent spaces |
| `tolkien-belief` | Brierly 2016 | Secondary Belief consistency |
| `panelki-world-rules` | 04-die-welt.md | Canonical ПАНЕЛЬКИ rules |

**Usage:**
```
"Use the panelki agent"           # Start orchestrated session
"Have worldbuild-analyst analyze economic system"  # Direct invocation
"Check this for consistency"      # Auto-delegates to lore-checker
```

**Files:**
```
.claude/
├── agents/
│   ├── panelki.md              # Orchestrator
│   ├── worldbuild-analyst.md
│   ├── faction-developer.md
│   ├── lore-checker.md
│   └── location-designer.md
└── skills/
    ├── zaidi-foundations/
    ├── wolf-subcreation/
    ├── jenkins-environmental/
    ├── tolkien-belief/
    └── panelki-world-rules/
```

---

## Tech Stack

| Kategorie | Tools |
|-----------|-------|
| DCC | Houdini (+ Houdini Engine) |
| Engine | Unreal Engine 5 |
| Plugins | UltraDynamicSky, EasySnow |
| Features | Nanite, Lumen, Substrate Materials, PCG |
| Data | ALOS DEM Terrain, OSM Buildings |

---

## Erledigt

- [x] Grundstruktur Worldbuilding Bible (8 Kapitel)
- [x] Houdini Terrain Pipeline
- [x] Houdini Building Generator (Grundversion)
- [x] UE5 Projekt Setup
- [x] Snow System Grundlagen

---

*Last updated: 2026-01-22 (literature expansion: 10→20 papers)*
