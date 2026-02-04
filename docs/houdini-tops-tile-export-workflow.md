# Houdini: TOPs Tile Export mit Height Field Tile Split

**Stand**: 2026-02-04 (aktualisiert)
**Session**: Texture Baking + TOPs @attribute Debugging
**Versionen**: Houdini 21.0
**Problem gelöst**: File Cache + PDG/TOPs Export

## Ziel

Height Field Terrain in 9 Tiles (3x3) splitten und parallel via TOPs als Mesh exportieren.

## Das Problem

Height Field Tile Split → Height Field Convert → TOPs Export produziert nur 1KB leere Dateien, obwohl:
- Wedge-Vorschau korrekte Tiles zeigt
- Manueller ROP-Cook funktioniert (4GB Dateien)
- Setup mit einfacher Geometrie (Cube + Mountain) funktioniert

## Ursache

**"Load from Disk" im File Cache wird von ROP-Prozessen falsch gelesen.**

Wenn PDG/TOPs den ROP triggert, wird der "Load from Disk" Status des File Cache nicht korrekt erkannt. Die Geometrie erscheint leer im ROP-Kontext.

Quellen:
- [CG Forge - File Cache 2.0](https://www.cgforge.com/blog/filecache-14097512)
- [Ronald Fong - File Cache and File nodes](https://ronald-fong.com/blog/create-file-cache-and-file-nodes-in-houdini/)

## Die Lösung

**Separaten File SOP verwenden statt "Load from Disk":**

```
[File SOP] → Height Field Tile Split → Height Field Convert → [Export]
     ↓
(liest Cache-Datei direkt)
```

### Schritt für Schritt

1. **File Cache**: Terrain einmal cachen, dann "Load from Disk" DEAKTIVIEREN (oder Node bypassen)

2. **File SOP einfügen** vor Height Field Tile Split:
   - Geometry File: Absoluter Pfad zur .bgeo.sc Datei
   - Pfad aus File Cache kopieren: Advanced → Output File

3. **Height Field Tile Split**:
   - Tile Count: 3 × 3
   - Extract Single Tile: ON
   - Tile Number: `` `@tilenum` `` (mit Backticks)

4. **Height Field Convert**:
   - Convert To: Polygons

5. **Attribute Delete** (optional, für sauberen Export):
   - Lösche unnötige Heightfield-Attribute

## TOPs Setup

```
[Wedge] → [ROP Fetch]
```

### Wedge TOP
- Wedge Count: 9
- Attribut: `tilenum` (Integer, 0-8)

### ROP Fetch / ROP Geometry Output
- Zeigt auf Geometry ROP im SOP-Netzwerk
- Output File: `$PDG_DIR/geo/tile_`@tilenum`.fbx`

## Export-Formate

| Format | Pro | Contra |
|--------|-----|--------|
| **FBX** | Beste Unreal-Kompatibilität, große Meshes | - |
| **OBJ** | Einfach | Kann bei großen Meshes korrupt werden |
| **GLTF/GLB** | Modern, kompakt | Weniger verbreitet |

**Empfehlung**: FBX für Unreal/Unity Export.

## Wichtige Erkenntnisse

1. **File Cache "Load from Disk"** funktioniert nicht zuverlässig mit PDG/TOPs
2. **File SOP** ist die robuste Alternative
3. **OBJ** kann bei sehr großen Meshes (4GB+) korrupt werden → FBX verwenden
4. **Wedge-Vorschau** ≠ ROP-Cook — verschiedene Evaluierungskontexte

## Debugging-Tipps

- Wenn nur 1KB Dateien entstehen: File Cache ist das Problem
- Test ohne Cache (dauert lang, aber beweist dass Setup stimmt)
- Geometry Spreadsheet prüfen: Sind Polygone da oder nur Volumes?
- Work Item Info checken: Stimmen die Pfade?

## Texture Baking in TOPs

### Das Problem mit Labs Baker

Labs Maps Baker und Labs Simple Baker haben Probleme mit TOPs/PDG:
- **Maps Baker**: ROP Fetch erkennt Output-Parameter nicht (`sOutputFile` manuell setzen hilft nicht immer)
- **Simple Baker**: Mantra-basiert, langsam, ähnliche TOPs-Probleme
- **COPs/Copernicus**: Schwarze Artefakte auf Höhen möglich

### Alternativen für Texture Baking

| Methode | Geschwindigkeit | TOPs-kompatibel | Hinweise |
|---------|-----------------|-----------------|----------|
| **Vertex Colors in FBX** | Instant | ✓ | Kein Baking nötig, Unreal liest direkt |
| **Bake Geometry Textures COP** | Schnell | ✓ (via ROP Image Output) | Kein Mantra, Custom Attributes |
| **Bake Texture ROP** | Langsam | ✓ | Mantra, aber zuverlässig |
| **Karma Texture Baker LOP** | Mittel | ✓ (via USD Render) | Modern, USD-basiert |

### Empfehlung: Vertex Colors exportieren

FBX exportiert Vertex Colors (`@Cd`) automatisch. In Unreal:

```
Material: Vertex Color Node → Base Color / Roughness
```

Kein Baking nötig — funktioniert gut für Terrain mit ausreichend Vertices.

## Roughness aus Height Field Layers

### Attribute Wrangle (nach Height Field Convert)

```vex
// Layer-Masken lesen
float snow = @snow;
float rock = @rock;
float sediment = @sediment;
float debris = @debris;

// Realistische Roughness-Werte
float snow_r = 0.15;      // Glatt, eisig
float rock_r = 0.85;      // Sehr rau
float sediment_r = 0.55;  // Mittel, erdig
float debris_r = 0.7;     // Rau, locker

// Gewichtetes Blending
float total = snow + rock + sediment + debris;
if (total > 0) {
    @roughness = (snow * snow_r + rock * rock_r + sediment * sediment_r + debris * debris_r) / total;
} else {
    @roughness = 0.5;
}

@roughness = clamp(@roughness, 0, 1);
```

### Roughness-Referenzwerte

| Material | Roughness | Begründung |
|----------|-----------|------------|
| Schnee/Eis (nass) | 0.1 - 0.2 | Reflektierend |
| Schnee (trocken) | 0.3 - 0.4 | Matter |
| Nasser Fels | 0.4 - 0.5 | Glänzend |
| Sediment/Erde | 0.5 - 0.6 | Matt |
| Schutt/Debris | 0.65 - 0.75 | Rau |
| Trockener Fels | 0.8 - 0.95 | Sehr rau |

### Roughness nach Cd für Baking

Falls du doch baken musst:

```vex
@Cd = set(@roughness, @roughness, @roughness);
```

## Bake Geometry Textures COP (Alternative)

Der moderne Ersatz für Labs Maps Baker:

```
[COP Network] → [Bake Geometry Textures] → [ROP Image Output]
```

- Schnell (kein Mantra)
- Bakt: Normal, AO, Curvature, Height, Thickness, Custom Attributes
- Für `@Cd`: Channels als separate Float-Attribute splitten

Quellen:
- [SideFX - Bake Geometry Textures](https://www.sidefx.com/docs/houdini/nodes/cop/bakegeometrytextures.html)

## Verwandte Docs

- [houdini-terrain-wedges-export.md](houdini-terrain-wedges-export.md) — Radiale Wedges für Frustum Culling
- [SideFX - File Cache](https://www.sidefx.com/docs/houdini/nodes/sop/filecache.html)
- [SideFX - ROP Fetch](https://www.sidefx.com/docs/houdini/nodes/top/ropfetch.html)
- [SideFX - Karma Texture Baker](https://www.sidefx.com/docs/houdini/nodes/lop/karmatexturebaker.html)

---

## Session 2026-02-04: @attribute Syntax & Texture Baking

### Das @tile Problem

**Symptom**: TOPs produziert nur 1KB/8KB Dateien, obwohl manueller Export funktioniert.

**Ursache**: `@tile` Attribut wird im `heightfield_tilesplit` nicht korrekt evaluiert.

#### Getestete Syntax-Varianten

| Syntax | Parameter-Typ | Ergebnis |
|--------|---------------|----------|
| `@tile` | Numerisch | ❌ Nicht evaluiert |
| `` `@tile` `` | Numerisch | ❌ Fehler |
| `detail("pfad/wedge1", "tile", 0)` | Numerisch | ⚠️ Teilweise |
| `pdgattribute("tile", 0)` | Numerisch | ⏳ Ungetestet |

**Empfehlung**: `pdgattribute("tile", 0)` statt `@tile` verwenden.

### Copernicus COPs Workflow (Houdini 21)

Für Texture Baking ohne Labs Baker:

```
[SOP Import] → [Rasterize Setup] → [Rasterize Geometry] → [File Output]
                  Space: UVs
                  UV Attribute: uv
```

**Problem entdeckt**: Schwarze Bereiche bei hohen Terrain-Bereichen.

- Nicht Steilheit-abhängig, sondern Höhe-abhängig
- "Face Visibility Culling: No Culling" hilft nicht
- UV Flatten behebt das Problem, ist aber sehr langsam

### Bake Geometry Textures COP

Moderner Ersatz, aber gleiches Problem:

```
[SOP Import] → [Bake Geometry Textures]
                 Tracing Mode: Single Mesh
                 Face Visibility Culling: No Culling
                 UV Attribute: uv
                 Custom Attributes: Cd (RGB)
```

**Schwarze Bereiche**: Auch hier Cutoff bei bestimmter Höhe. Ursache unklar.

### Labs Simple Baker (funktioniert)

Der einzige zuverlässig funktionierende Baker:

```
Labs Simple Baker
  Resolution: 2048
  ✓ Vertex Color
  ✓ Custom Channel: roughness
  Base Path: $HIP/tex/tile_`@tile`_$(CHANNEL).png
```

**Hinweis**: Langsam bei hochaufgelösten Meshes (Millionen Polygone).

### TOPs Node-Übersicht

| Node | Zweck | @attribute Support |
|------|-------|-------------------|
| **Wedge** | Work Items erstellen | Quelle der Attribute |
| **ROP Fetch** | ROP triggern | ⚠️ Kocht SOPs nicht neu |
| **ROP Geometry Output** | Geo direkt exportieren | ✓ Sollte funktionieren |
| **Geometry Import** | Geo in PDG laden | ✓ Kocht SOPs |
| **HDA Processor** | HDA mit Attributen kochen | ✓ Zuverlässig |

### Empfohlener Workflow

Bis @attribute zuverlässig funktioniert:

1. **Manuell exportieren** (9x, pro Tile)
2. **Oder**: Subnet → HDA wrappen → HDA Processor
3. **Oder**: Python Script das Parameter setzt und ROP triggert

### Vertex Colors als Alternative

FBX exportiert `@Cd` automatisch. In Unreal Material:

```
Vertex Color → Base Color
```

**Vorteile**: Kein Baking, instant, funktioniert zuverlässig
**Nachteile**: Auflösung = Vertex-Dichte

### Quellen (diese Session)

- [SideFX - Using PDG Attributes](https://www.sidefx.com/docs/houdini/tops/attributes.html)
- [SideFX - ROP Geometry Output](https://www.sidefx.com/docs/houdini/nodes/top/ropgeometry.html)
- [SideFX - Rasterize Setup](https://www.sidefx.com/docs/houdini/nodes/cop/rasterizesetup.html)
- [SideFX - Bake Geometry Textures](https://www.sidefx.com/docs/houdini/nodes/cop/bakegeometrytextures.html)
- [CGWiki - Houdini Tops](https://tokeru.com/cgwiki/HoudiniTops.html)
