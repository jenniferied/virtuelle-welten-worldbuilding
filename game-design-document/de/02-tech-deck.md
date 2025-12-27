# Tech Deck

## Entwicklungsumgebung

```
┌─────────────────────┐                              ┌─────────────────────┐
│   MAC WORKSTATION   │                              │   PC WORKSTATION    │
│                     │                              │                     │
│  MacBook Pro M1 Max │                              │  Intel i9-13900K    │
│  64 GB RAM          │                              │  RTX 3090           │
│                     │                              │  64 GB RAM          │
│  ┌───────────────┐  │                              │  ┌───────────────┐  │
│  │ Unreal 5.5+   │◄─┼──────┐                ┌─────►┼──│ Unreal 5.5+   │  │
│  └───────────────┘  │      │                │      │  └───────────────┘  │
│  ┌───────────────┐  │      │                │      │  ┌───────────────┐  │
│  │ Houdini Engine│──┼──────┘                └──────┼──│ Houdini Engine│  │
│  └───────────────┘  │                              │  └───────────────┘  │
│  ┌───────────────┐  │                              │  ┌───────────────┐  │
│  │ Houdini       │  │                              │  │ Houdini       │  │
│  └───────────────┘  │                              │  └───────────────┘  │
│  ┌───────────────┐  │                              │  ┌───────────────┐  │
│  │ P4V Client    │  │                              │  │ P4V Client    │  │
│  └───────────────┘  │                              │  └───────────────┘  │
│                     │                              │                     │
└──────────┬──────────┘                              └──────────┬──────────┘
           │                                                    │
           │              ┌─────────────────────┐               │
           │              │   DIGITAL OCEAN     │               │
           │              │                     │               │
           └──────────────┤  Perforce Server    ├───────────────┘
                          │  (Helix Core)       │
                          │                     │
                          │  ┌───────────────┐  │
                          │  │ Depot         │  │
                          │  │ - //depot/... │  │
                          │  └───────────────┘  │
                          │                     │
                          └─────────────────────┘
```

### Workflow

1. **Entwicklung** erfolgt auf beiden Workstations parallel
2. **Assets** werden via Perforce synchronisiert
3. **Große Binärdateien** (Texturen, Meshes) nutzen Perforce-Locking
4. **Houdini Digital Assets** werden zentral versioniert

## Unreal Engine Assets

### Lighting & Wetter

| Asset | Entwickler | Einsatz | Link |
|-------|-----------|---------|------|
| Ultra Dynamic Sky | Everett Gunther | In-Game Beleuchtung & Wetter | [Fab](https://www.fab.com/listings/84fda27a-c79f-49c9-8458-82401fb37cfb) |
| EasySnow | William Faucher | Cinematic Schnee | [Fab](https://www.unrealengine.com/marketplace/en-US/product/easysnow) |

**Ultra Dynamic Sky** bietet ein vollständiges Himmel- und Wettersystem mit:

- Tag/Nacht-Zyklus mit einem einzigen Time-of-Day-Parameter
- Ultra Dynamic Weather für Blizzard, leichten Schneefall, Gewitter
- Volumetrische 3D-Wolken und dynamische Aurora
- Echtzeit-Simulation basierend auf Breitengrad/Längengrad

**EasySnow** wird für Cinematics eingesetzt wegen:

- Realistische 3D-Schneeflocken (keine 2D-Sprites)
- Jede Flocke ist ein 3D-Modell basierend auf echten Schneeklumpen
- Optimiert für Lumen und Pathtracing
- Schwerer Schneefall bis leichte Flöckchen einstellbar

### Geodaten

Der Fokus liegt auf der authentischen Rekonstruktion sibirischer Industrielandschaften durch die Kombination von hochpräzisen Geländedaten und prozeduralem Weltenbau.

#### Standortauswahl

Ich habe mehrere russische Städte recherchiert, die aufgrund ihrer topografischen Besonderheiten und industriellen Prägung (sowjetischer Funktionalismus) in Frage kamen:

| Stadt | Geografische Spezialität | Sowjet-Architektur | Koordinaten | Einwohner |
|-------|-------------------------|-------------------|-------------|-----------|
| **Nerjungri** | Riesige terrassierte Kohlemine; Hanglage in der Taiga | Hoch (Strenges 70er-Gitter; Panelkas) | 56.67, 124.72 | 58.000 |
| Dalnegorsk | Enges Gebirgstal; Mine direkt in Wohngebiete geschnitten | Mittel (Grittiger Industriestil) | 44.56, 135.03 | 33.000 |
| Petropawlowsk | Pazifikbucht; unmittelbare Nähe zu 3000m Vulkanen | Hoch (Berghang-Plattenbau) | 53.02, 158.65 | 180.000 |
| Norilsk | Putorana-Plateau; extreme Industrielandschaft im Permafrost | Extrem (Dystopische Hochdichte-Raster) | 69.35, 88.20 | 175.000 |
| Magadan | Meeresenge; Kolyma-Gebirge; isolierte Hafenlandschaft | Mittel (Sowjet-Klassizismus & Betonblocks) | 59.56, 150.80 | 90.000 |
| Wiljutschinsk | Militärbasis; direkte Lage am Vulkan-Fuß | Mittel (Militärisch-starre Anordnung) | 52.93, 158.41 | 22.000 |

Ich habe mich für **Nerjungri** entschieden – die terrassierte Kohlemine bietet eine einzigartige Topografie, und die strenge 70er-Jahre-Panelka-Architektur passt perfekt zur ПАНЕЛЬКИ-Ästhetik.

#### Workflow

**Schritt 1: Bereich definieren & Datenakquise**

Zuerst habe ich das [Bounding Box Tool](https://boundingbox.klokantech.com/) verwendet, um die exakten Grenzen für Nerjungri festzulegen. Diese Box diente als einheitlicher Referenzrahmen für alle Datenexporte.

- **Terrain-Daten:** Die Höhendaten habe ich über [ASF Data Search (Vertex)](https://search.asf.alaska.edu/) bezogen. Ich wählte das ALOS PALSAR Produkt (RTC - Hi-Res Terrain Corrected). Die Auflösung von 12,5 Metern ermöglicht es, die feinen Stufen des Tagebaus physikalisch korrekt abzubilden.

- **Stadt-Daten:** Über den [BBBike Extract Service](https://extract.bbbike.org/) habe ich die OpenStreetMap-Daten (Gebäude, Straßen, Schienen) im .osm-Format exportiert, basierend auf der zuvor definierten Bounding Box.

**Schritt 2: Houdini-Integration & Alignment**

- **Manueller Skalierungs-Fix:** Nach dem Import über die HeightField File-Node habe ich das Grid Spacing manuell auf 12,5 gesetzt. Das stellt sicher, dass die Landschaftsdimensionen in Houdini exakt dem realen Maßstab (1 Unit = 1 Meter) entsprechen.

- **Zentrierung:** Das gesamte Terrain habe ich auf den Ursprung (0,0,0) verschoben, um Rechenfehler bei großen Koordinaten zu vermeiden.

- **Eye Matching:** Die OSM-Daten habe ich eingeladen und visuell an das Terrain angepasst. Als primäre Referenz dienten die Schleifenstraßen des Tagebaus. Da die Straßen in OSM präzise digitalisiert sind, habe ich sie mittels Transform-Nodes so verschoben und skaliert, bis sie exakt auf den Krater-Terrassen des 12,5m-Terrains auflagen.
