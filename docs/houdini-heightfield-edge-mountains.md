# Houdini: Heightfield Edge Mountains

**Stand**: 2026-01-31
**Versionen**: Houdini 21.0

## Problem

Berge am Rand eines Heightfields sollen extremer/höher sein als in der Mitte. `HeightField Mask by Feature` hat keinen "Boundary Distance" Modus — die verfügbaren Modi sind:

- Slope (Neigung)
- Height (Höhe)
- Curvature (Krümmung/Peaks/Valleys)
- Direction (Ausrichtung)
- Occlusion (Verschattung)

## Lösung

Zwei-Schritt-Workflow: Erst Edge-Maske per VEX erstellen, dann Höhe skalieren.

### Schritt 1: Edge-Maske erstellen

**Volume Wrangle** nach dem Heightfield, läuft auf `height` Primitive:

```vex
// Heightfield Bounds ermitteln
vector bbox_min = getbbox_min(0);
vector bbox_max = getbbox_max(0);
vector bbox_size = bbox_max - bbox_min;

// Position auf 0-1 normalisieren
float u = (@P.x - bbox_min.x) / bbox_size.x;
float v = (@P.z - bbox_min.z) / bbox_size.z;

// Distanz vom Zentrum (0 in Mitte, ~0.7 an Ecken)
float dist = length(set(u, v) - set(0.5, 0.5));

// Auf 0-1 remappen (inner/outer für Falloff anpassen)
float inner = ch("inner");  // z.B. 0.3
float outer = ch("outer");  // z.B. 0.5
float mask = fit(dist, inner, outer, 0, 1);
mask = clamp(mask, 0, 1);

@mask = mask;
```

Parameter hinzufügen:
- `inner`: Wo Maske beginnt (0 = ab Mitte, 0.3 = ab 30% Radius)
- `outer`: Wo Maske = 1 erreicht (0.5 = bei 50% Radius voll)

### Schritt 2: Höhe skalieren

**Option A: Volume Wrangle** (mehr Kontrolle)

Weiterer Volume Wrangle, läuft auf `height`:

```vex
float mask_val = volumesample(0, "mask", @P);
float multiplier = ch("lift");  // z.B. 2.0 = doppelte Höhe am Rand

@height *= 1 + mask_val * (multiplier - 1);
```

**Option B: HeightField Layer** (non-destructive)

1. `heightfield_layer` Node hinzufügen
2. **Layer**: `height`
3. **Mode**: `Scale`
4. **Mask Layer**: `mask`
5. **Scale**: z.B. 2.0

## Wichtige VEX-Funktionen

| Funktion | Zweck |
|----------|-------|
| `getbbox_min(0)` | Minimum der Bounding Box |
| `getbbox_max(0)` | Maximum der Bounding Box |
| `volumesample(0, "layer", @P)` | Wert aus anderem Layer lesen |
| `fit(val, omin, omax, nmin, nmax)` | Wert remappen |
| `clamp(val, min, max)` | Wert begrenzen |

## Hinweise

- `HeightField Distort by Layer` ist für horizontale Verzerrung, nicht für Höhenskalierung
- Bei Volume Wrangle auf korrektes Primitive achten (`height` vs `mask`)
- Maske mit HeightField Visualize prüfen bevor Höhe skaliert wird
