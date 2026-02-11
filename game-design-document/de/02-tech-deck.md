# Tech Deck

## Entwicklungsumgebung

| | Mac Workstation | PC Workstation |
|---|---|---|
| **Hardware** | MacBook Pro M1 Max, 64 GB RAM | Intel i9-13900K, RTX 3090, 64 GB RAM |
| **Software** | Unreal 5.7, Houdini 20, Houdini Engine | Unreal 5.7, Houdini 20, Houdini Engine |
| **Versionierung** | Perforce (Helix Core) via Digital Ocean Server |

## Unreal Engine Assets

### Lighting & Wetter

| Asset | Entwickler | Einsatz | Link |
|-------|-----------|---------|------|
| Ultra Dynamic Sky | Everett Gunther | In-Game Beleuchtung & Wetter | [Fab](https://www.fab.com/listings/84fda27a-c79f-49c9-8458-82401fb37cfb) |
| EasySnow | William Faucher | Cinematic Schnee | [Fab](https://www.unrealengine.com/marketplace/en-US/product/easysnow) |

**Ultra Dynamic Sky** bietet ein vollständiges Himmel- und Wettersystem mit:

- Tag/Nacht-Zyklus mit einem einzigen Time-of-Day-Parameter
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

- **Eye Matching:** Die OSM-Daten habe ich eingeladen und visuell an das Terrain angepasst. Als Referenz dienten Straßen in Tälern und an Berghängen. Mittels Transform-Nodes wurden die Daten so verschoben und skaliert, bis sie exakt auf dem Terrain auflagen.

**Schritt 3: Terrain-Aufbereitung für Unreal**

Das Heightfield wurde für den Echtzeit-Einsatz dramatisiert – Höhenunterschiede verstärkt, um die visuelle Wirkung bei flachen Kamerawinkeln zu verbessern.

- **Nanite-Konvertierung:** Ursprünglich als Unreal Landscape importiert, dann auf Hi-Res Nanite Geometry umgestellt (HeightField Convert). Nanite erhält feine Details auch in der Ferne, wo traditionelle LODs bereits degradieren. Das Terrain wurde in 9 Tiles aufgeteilt.

- **Textur-Generierung:** Diffuse- und Roughness-Maps über den Labs Maps Baker erstellt. COPs wurde getestet, erzeugte jedoch schwarze Artefakte auf den Texturen.

- **Batch-Processing:** TOPS (Task Operator Network) verarbeitet alle Tiles parallel – sowohl Texturen als auch FBX-Geometrie-Export.

**Schritt 4: Multipass Terrain-Anpassung**

Das Heightfield wurde in mehreren Durchläufen an die Stadt-Infrastruktur angepasst:

1. **District-Anpassung:** Grobe Nivellierung der Wohngebiete
2. **Straßen-Projektion:** Einschnitte für Hauptstraßen
3. **Gebäude-Fundamente:** Lokale Planierung unter Gebäude-Footprints

## Straßen-System

### OSM-Extraktion

Aus den OpenStreetMap-Daten wurden verschiedene Straßentypen extrahiert und klassifiziert:

| Typ | Beschreibung | Behandlung |
|-----|-------------|------------|
| `major_big` | Hauptverkehrsstraßen (breit) | Asphalt-Geometrie mit Bordsteinen |
| `major_small` | Nebenstraßen (schmal) | Asphalt-Geometrie mit Bordsteinen |
| `mud` | Unbefestigte Wege | Ribbon-Geometrie |

### Geometrie-Vereinfachung

Parallele OSM-Straßen (z.B. Fahrbahnen mit Mittelstreifen) wurden über eine Pipeline aus Fuse, Resample und PolyPath zu einzelnen Curves konsolidiert.

### Custom Road Tool

Das Labs Road Generator Tool erwies sich als instabil. Stattdessen wurde ein eigenes System entwickelt:

- Ribbon-Geometrie entlang der Curve
- Bordstein-Extrusion über gezieltes PolyExtrude mit Inset
- Intersection-Handling über Point und Primitive Wrangles: Intersection Points wurden identifiziert, zuerst major-Straßen verarbeitet, dann Mud-Ribbons gegen major-Geometrie geschnitten

### Beleuchtung

Entlang der `major_big` und `major_small` Straßen wurden Straßenlaternen prozedural verteilt.

## Garagen

Gebäude unter 5 Metern Höhe aus den OSM-Daten wurden als Garagen interpretiert:

- Einfache Box-Geometrie aus Building-Footprints extrudiert
- Material-Variation über Attribute Create (verschiedene Unreal-Materials)
- Lightpoints über den Garagentoren für nächtliche Beleuchtung

## Gebäude-Generator

Für Gebäude über 5 Meter wurde die **Buildings from Patterns**-Node eingesetzt.

### Komponenten

Prozedurale Generierung modularer Building-Elemente, mit zukünftigen Variationen im Blick:

- Fassaden mit Fenster-Rastern
- Balkone und Eingänge
- Dachgeometrie

### Fenster-Beleuchtung

Ursprünglicher Ansatz: Point Lights hinter jedem Fenster. Problem: ~10.000 Light-Instances – für Unreal nicht praktikabel.

Lösung: Emissive Material Planes hinter den Fensteröffnungen. Gleicher visueller Effekt, minimaler Performance-Impact.

*Zukünftige Erweiterung: Logik zur Steuerung von Fensterfarbe und -zustand (beleuchtet / gedimmt / aus).*

### Fundamente

Da das Terrain trotz Multipass-Anpassung nicht perfekt plan unter allen Gebäuden lag, wurden automatische Fundamente generiert, die Unebenheiten kaschieren.

## Unreal Engine Integration

### Asset-Import

| Methode | Assets |
|---------|--------|
| TOPS/FBX | Nanite Terrain Tiles, Texturen |
| Houdini Engine/HDA | Gebäude, Straßen, Garagen, Laternen |

### Vegetation

PCG (Procedural Content Generation) für Baumplatzierung. Die Bäume wurden mit der EasySnow Material Function von William Faucher versehen.

### Post-Processing

- **Pixelation:** Custom Post Process Material für stilisierten Look
- **Color Grading:** LUT auf dem Post Process Volume

### Zusätzliche Assets

- **Train Station:** Prefab im sowjetischen Stil für die Opening-Szene
- *Fahrzeuge: Mit EasySnow Material Function vorbereitet, Scattering ausstehend*
