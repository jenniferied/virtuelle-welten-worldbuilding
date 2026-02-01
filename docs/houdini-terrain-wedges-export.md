# Houdini: Terrain Wedges Export für Unreal

**Stand**: 2026-01-31
**Versionen**: Houdini 21.0, Unreal Engine 5

## Ziel

Großes Heightfield-Terrain in 8 radiale Wedges splitten für:
- Frustum Culling (Teile hinter Kamera werden nicht gerendert)
- World Partition / Streaming
- Einfacheres Handling im Editor

## Workflow Übersicht

```
[Heightfield] → [HeightField Convert] → [Piece Wrangle] → [8x Blast] → [File Cache/ROP FBX]
                                              ↓
                                    [Labs Maps Baker] → Texturen
```

## Schritt 1: Heightfield zu Polygonen

**HeightField Convert SOP**
- Output: Polygons
- LOD: Nach Bedarf (mit Nanite kann höher sein)

## Schritt 2: Radiale Pieces zuweisen

**Primitive Wrangle** (Run Over: Primitives):

```vex
vector center = getbbox_center(0);  // oder {0,0,0} wenn zentriert
vector pos = @P - center;
float angle = atan2(pos.z, pos.x) + 3.14159;  // 0 bis 2*PI
angle += 0.3927;  // 22.5° Offset (Cuts nicht auf Landscape-Kanten)
i@piece = int((angle / 6.28318) * 8) % 8;
```

**Visualisierung** (optional, zum Debuggen):

```vex
vector colors[] = {
    {1,0,0}, {1,0.5,0}, {1,1,0}, {0,1,0},
    {0,1,1}, {0,0,1}, {0.5,0,1}, {1,0,1}
};
@Cd = colors[i@piece];
```

## Schritt 3: Pieces separieren

**Pro Piece ein Blast SOP:**
- Piece 0: Group = `@piece!=0` (löscht alles außer Piece 0)
- Piece 1: Group = `@piece!=1`
- etc.

Oder: **Partition SOP** → Rule: `piece_$PIECE` → dann **Split SOP**.

## Schritt 4: Texturen baken

### Color/Diffuse

Wenn `@Cd` aus Heightfield-Layern kommt:

**Labs Maps Baker SOP**
- Resolution: 8192 x 8192 (oder 4096)
- UV Attribute: `uv`
- Export Diffuse: ON
- Diffuse Attribute: `Cd`
- Output: `$HIP/tex/terrain_diffuse.png`

### Roughness aus Masken

**Attribute Wrangle** vor dem Baken:

```vex
// Masken lesen (Namen anpassen)
float snow = point(0, "snow", @ptnum);
float rock = point(0, "rock", @ptnum);
float sediment = point(0, "sediment", @ptnum);
float debris = point(0, "debris", @ptnum);

// Roughness-Werte
float snow_rough = 0.2;      // glatt, eisig
float rock_rough = 0.85;     // rau
float sediment_rough = 0.5;  // mittel
float debris_rough = 0.7;    // ziemlich rau

// Blenden
@roughness = snow * snow_rough
           + rock * rock_rough
           + sediment * sediment_rough
           + debris * debris_rough;

@roughness = clamp(@roughness, 0, 1);
@Cd = set(@roughness, @roughness, @roughness);
```

Dann nochmal Labs Maps Baker mit diesem `Cd`.

### Typische Roughness-Werte

| Material | Roughness |
|----------|-----------|
| Eis/Schnee | 0.1 - 0.3 |
| Nasser Fels | 0.4 - 0.5 |
| Trockenes Sediment | 0.5 - 0.6 |
| Schutt/Kies | 0.7 - 0.8 |
| Rauer Fels | 0.8 - 0.95 |

## Schritt 5: Export

**ROP FBX Output** oder **File Cache SOP**
- Format: FBX
- Pfad: `$HIP/geo/terrain_wedge_0.fbx` etc.
- Convert Units: ON (für Unreal-Scale)

## Nanite Hinweise

Mit Nanite:
- Höhere Poly-Count okay (Nanite handled LOD)
- **Normal Maps aus Geo nicht nötig** — Geo hat bereits das Detail
- Für Mikro-Detail: Tiling Detail Normals im Unreal Material

## Unreal Material Setup

**Master Material** (`M_Mountain`):
- Diffuse Texture Parameter
- Roughness Texture Parameter
- AO Texture Parameter
- Tiling Parameter

**Material Instance** (`MI_Mountain`):
- Gebakte Texturen zuweisen
- Alle 8 Wedges können dasselbe Instance nutzen

## Gemeinsame vs. Separate Texturen

| Approach | Pro | Contra |
|----------|-----|--------|
| Eine shared Texture | 1 Material, weniger Draw Calls | Weniger Auflösung pro Piece |
| Separate Texturen | Volle Auflösung, besseres Streaming | Mehr Materials, mehr Speicher |

Für Distant Terrain: Shared Texture oft ausreichend.

## Transform vom Cropped Landscape übernehmen

Falls Landscape mit Match Size transformiert wurde:

**Copy Transform SOP**
- Input 1: Full Terrain (zu transformieren)
- Input 2: Matched Landscape (Referenz)

Oder Match Size Parameter referenzieren:
```
ch("../matchsize1/tx")
ch("../matchsize1/ty")
etc.
```

## Loch für Landscape ausschneiden

**Delete SOP** mit Bounding Box die Landscape-Größe matched.
Oder **Boolean SOP** mit Box subtract.

## Light Leak Prevention

Extruded "Skirt" am inneren Rand:
1. **Group SOP** → Boundary Edges
2. **PolyExtrude SOP** → nach unten extrudieren

Verhindert sichtbare Lücken zwischen Landscape und Surrounding Terrain.
