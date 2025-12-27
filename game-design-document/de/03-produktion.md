# Produktion

Dieses Kapitel dokumentiert den Produktionsablauf für ПАНЕЛЬКИ im Rahmen des Kurses "Virtuelle Welten". Es definiert die technische Pipeline, die Arbeitsphasen und die Abgabe-Anforderungen.

## Kursstruktur

### Block I – Grundlagen

**Inhalte:**

- Intro / World Building Fundamentals
- Team Findung / grobe Konzept Entwicklung
- **Houdini Terrain Tools Intro** – Prozedurale Environments und Landscapes
- **Houdini Building Generator** – Modulare Fab Building Assets
- **Houdini Engine für Unreal Intro** – Effiziente Geometrie-Portierung

**Ziel:** Technische Grundlagen für prozedurale Weltgenerierung verstehen und anwenden.

### Block II – Verfeinerung

**Inhalte:**

- Feedback & Hilfestellungen
- Houdini Szenen-Debugging / Optimierung
- **Unreal Engine Set Dressing** – Details, Props, Leben
- **Unreal Engine Lighting** – Atmosphäre, Stimmung
- **Unreal Engine Rendering** – Finale Ausgabe

**Ziel:** Technische Assets zu einer stimmungsvollen Szene zusammenführen.

## Eigenarbeit-Phasen

### Eigenarbeit I

**Aufgaben:**

- World Bible / Concept Art fertigstellen
- Houdini: Terrain Generation
- Houdini: Building Generation
- Unreal Engine: Import und Layout

**Deliverables:**

- Funktionierendes Houdini-Setup für Terrain
- Funktionierendes Houdini-Setup für Gebäude
- Grundlegendes Unreal-Level mit importierten Assets

### Eigenarbeit II

**Aufgaben:**

- Unreal Engine: Set Dressing
- Unreal Engine: Lighting Setup
- Unreal Engine: Rendering Pipeline
- Finales Video erstellen

**Deliverables:**

- Vollständig eingerichtete Szene
- Finales 30-Sekunden-Video

## Technische Pipeline

### Schritt 1: Terrain Generation (Houdini)

**Input:**

- Heightmap-Daten (real oder prozedural)
- Parameter für Größe, Detail, Variation

**Output:**

- Terrain-Mesh für Unreal
- UV-Koordinaten für Landscaping

**Tools:** Houdini Terrain Tools

### Schritt 2: Building Generation (Houdini)

**Input:**

- OpenStreetMap-Daten oder prozedurale Layouts
- Building-Parameter (Höhe, Typ, Variationen)
- Modulare Assets (Fenster, Balkone, Türen)

**Output:**

- Gebäude-Meshes mit LODs
- Materialzuweisungen
- Collision-Geometrie

**Tools:** Houdini Building Generator, Modular Fab Assets

### Schritt 3: Unreal Import (Houdini Engine)

**Prozess:**

1. Houdini Digital Assets (HDAs) erstellen
2. HDAs in Unreal laden
3. Parameter in Unreal anpassen
4. Assets kochen/generieren

**Vorteile:**

- Nicht-destruktiver Workflow
- Schnelle Iteration
- Parameter-Kontrolle in Unreal

### Schritt 4: Set Dressing (Unreal)

**Elemente:**

- Props (Bänke, Laternen, Spielgeräte)
- Vegetation (Bäume, Büsche)
- Details (Müll, Spuren, Leben)

**Methoden:**

- Manuelles Placement
- Foliage System für Vegetation
- Decals für Details

### Schritt 5: Lighting & Rendering (Unreal)

**Lighting:**

- Directional Light (Sonne/Mond)
- Sky Light (Ambient)
- Point/Spot Lights (Laternen, Fenster)
- Volumetric Fog

**Rendering:**

- High Quality Screenshots
- Movie Render Queue
- Post-Processing

## Abgabe-Anforderungen

### Cinematic Video

| Aspekt | Anforderung |
|--------|-------------|
| Format | Video (MP4, H.264) |
| Länge | Minimum 30 Sekunden |
| Shots | Minimum 5 verschiedene Einstellungen |

### Shot-Planung

| Shot | Beschreibung | Tageszeit | Dauer |
|------|-------------|-----------|-------|
| 1 | Establishing – Skyline | Dämmerung | ~8s |
| 2 | Innenhof – Detail | Tag | ~6s |
| 3 | Straße – Bewegung | Nacht | ~6s |
| 4 | Fenster – Intimität | Nacht | ~5s |
| 5 | Der Fremde | Dämmerung | ~5s |

*Anpassungen möglich je nach Fortschritt und kreativer Vision.*

## Scope-Definition

### Was wird gebaut

**Muss (MVP):**

- 1 detaillierter Innenhof
- Umgebende Gebäude (Houdini-generiert)
- Grundlegende Straßenszene
- Tag/Nacht-Lichtstimmung
- Schnee-Environment

**Sollte:**

- Straßenbahn (statisch oder animiert)
- Mehr Gebäudevariationen
- Aurora-Effekt
- Atmosphärische Partikel (Schneefall)

### Was wird NICHT gebaut

**Außerhalb des Scope:**

- Spielbare Charaktere
- Interaktive Gameplay-Elemente
- Vollständiger Bezirk
- Innenräume
- KI/NPCs

**Begründung:** Der Fokus liegt auf Environment Art und Cinematic Präsentation, nicht auf spielbarem Content.

## Meilensteine

| Meilenstein | Beschreibung |
|-------------|--------------|
| **M1** | World Bible Complete – Alle Kapitel geschrieben, Referenzmaterial organisiert |
| **M2** | Houdini Pipeline Ready – Terrain + Building Generator funktionieren |
| **M3** | Base Level Complete – Assets importiert, Grundlayout steht |
| **M4** | Final Polish – Set Dressing, Lighting finalisiert |
| **M5** | Abgabe – 30s Video, Bible PDF, GDD PDF |
