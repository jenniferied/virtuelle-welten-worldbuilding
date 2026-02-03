# Houdini Terrain Conform Workflow

Terrain-Anpassung für Straßen und Gebäude auf HeightFields.

## Übersicht

Multi-Pass Workflow um HeightField-Terrain an Straßen-Ribbons und Building-Footprints anzupassen:

1. **Pass 1**: Straßen conform (links/rechts level, Längsneigung erhalten)
2. **Pass 2**: Buildings conform (pro Building eine Höhe)
3. **Pass 3**: Optional Blur für weiche Kanten

---

## Straßen-Workflow

### Schritt 1: Proxy Ribbons aus Centerlines

```
Centerlines (auf Terrain-Höhe) ──► Attribute Wrangle ──► Proxy Ribbons
```

```vex
// Run Over: Primitives
// Input 0: Centerlines (mit @width, @name)

int pts[] = primpoints(0, @primnum);
int n = len(pts);
if (n < 2) return;

float width = f@width * chf("width_mult");
string name = s@name;
vector up = {0, 1, 0};

int left[], right[];

for (int i = 0; i < n; i++) {
    vector pos = point(0, "P", pts[i]);

    vector dir = {0, 0, 0};
    if (i > 0) dir += normalize(pos - point(0, "P", pts[i-1]));
    if (i < n-1) dir += normalize(point(0, "P", pts[i+1]) - pos);
    dir = length(dir) > 0.001 ? normalize(dir) : {1, 0, 0};

    vector side_offset = normalize(cross(dir, up)) * width * 0.5;

    push(left, addpoint(0, pos - side_offset));
    push(right, addpoint(0, pos + side_offset));
}

for (int i = 0; i < n-1; i++) {
    int pr = addprim(0, "poly", left[i], right[i], right[i+1], left[i+1]);
    setprimgroup(0, "ribbon_" + name, pr, 1);
    setprimattrib(0, "name", pr, name);
}

setprimgroup(0, "centerlines", @primnum, 1);
```

**Parameter:**
- `width_mult`: Ribbon-Breite Multiplikator (1.0 = original @width)

**Wichtig:** Die Centerline-Höhe wird für links UND rechts verwendet → automatisch level!

### Schritt 2: Terrain an Ribbons anpassen (Volume Wrangle)

```
Proxy Ribbons ─────────────────────────┐
                                       ▼
HeightField ──► Volume Wrangle ──► Angepasstes Terrain
```

```vex
// Volume Wrangle
// Volumes to Write to: height
// Input 0: HeightField
// Input 1: Proxy Ribbons

vector pos_2d = set(@P.x, 0, @P.z);

int hit_prim;
vector uv;
float dist = xyzdist(1, pos_2d, hit_prim, uv);

float threshold = chf("threshold");

if (dist < threshold) {
    vector ribbon_pos = primuv(1, "P", hit_prim, uv);
    @height = ribbon_pos.y - chf("drop");
}
```

**Parameter:**
- `threshold`: Maximale Distanz (sollte > Terrain-Höhe sein, z.B. 500-1000)
- `drop`: Absenkung der Straße (z.B. 0.1m)

**Problem:** `xyzdist` misst 3D-Distanz. Mit `pos_2d` bei Y=0 und Ribbons bei Y=50+ ist die Distanz immer groß!

### Alternative: Raycast-Methode (präziser)

```vex
// Volume Wrangle
// Volumes to Write to: height
// Input 0: HeightField
// Input 1: Proxy Ribbons

vector ray_start = set(@P.x, 10000, @P.z);
vector ray_dir = {0, -1, 0};

vector hit_pos;
vector hit_uvw;
int hit_prim = intersect(1, ray_start, ray_dir * 20000, hit_pos, hit_uvw);

if (hit_prim >= 0) {
    @height = hit_pos.y - chf("drop");
}
```

Diese Methode trifft nur Punkte die direkt über/unter einem Ribbon-Polygon liegen.

---

## Building-Workflow

### Schritt 1: Buildings auf einheitliche Höhe bringen

Buildings kommen oft schief vom Ray-Projection. Erst auf eine Höhe pro Building setzen:

```vex
// Run Over: Primitives
// Input 0: Building Polygons (via Ray auf Terrain projiziert)

int pts[] = primpoints(0, @primnum);
int n = len(pts);

float minH = 1e9;
float maxH = -1e9;
float sum = 0;

foreach(int pt; pts) {
    vector pos = point(0, "P", pt);
    minH = min(minH, pos.y);
    maxH = max(maxH, pos.y);
    sum += pos.y;
}

float avgH = sum / n;

// 0 = min, 0.5 = avg, 1 = max
float blend = chf("height_mode");
float target = lerp(minH, maxH, blend);

foreach(int pt; pts) {
    vector pos = point(0, "P", pt);
    pos.y = target;
    setpointattrib(0, "P", pt, pos);
}

f@building_height = target;
```

**Parameter:**
- `height_mode`: 0 = unterster Punkt, 0.5 = Mitte, 1 = höchster Punkt

### Schritt 2: Terrain an Buildings anpassen

```vex
// Volume Wrangle
// Volumes to Write to: height
// Input 0: HeightField
// Input 1: Building Polygons (mit @building_height)

vector ray_start = set(@P.x, 10000, @P.z);
vector ray_dir = {0, -1, 0};

vector hit_pos;
vector hit_uvw;
int hit_prim = intersect(1, ray_start, ray_dir * 20000, hit_pos, hit_uvw);

if (hit_prim >= 0) {
    @height = hit_pos.y - chf("drop");
}
```

---

## Weiche Kanten (Blur)

Nach dem Conform harte Kanten mit HeightField Blur glätten:

```
Volume Wrangle (Conform) ──► HeightField Blur
                                   │
                                   ├── Blur Layer: height
                                   ├── Radius: 2-5m
                                   └── Iterations: 2-3
```

### Nur Kanten blurren (mit Maske)

```
Buildings/Ribbons ──► HeightField Mask by Object ──► HeightField Blur (mask erweitern)
                            │
                            └── Blur Radius: 5-10m

HeightField (nach Conform) ──► HeightField Blur
                                    │
                                    ├── Blur Layer: height
                                    ├── Mask Layer: mask
                                    └── Radius: 3-5m
```

---

## Troubleshooting

### Volume Wrangle tut nichts
1. **Volumes to Write to** = `height` eintragen
2. **Run Over** = Volumes
3. Test: `@height = 0;` - wird Terrain flach?

### xyzdist findet nichts
- Problem: 3D-Distanz inkludiert Y-Differenz
- Lösung 1: Großen Threshold verwenden (500+)
- Lösung 2: Raycast-Methode mit `intersect()` verwenden

### @density vs @height
- Bei **Volumes to Write to** = leer → `@density`
- Bei **Volumes to Write to** = `height` → `@height`

---

## Node-Struktur Übersicht

```
                    ┌─────────────────────────────────────┐
                    │         STRASSEN-PASS               │
                    │                                     │
Centerlines ──► Proxy Ribbons Wrangle ──┐                │
                    │                    │                │
                    │                    ▼                │
                    │            Volume Wrangle ◄── HeightField
                    │                    │                │
                    └────────────────────┼────────────────┘
                                         │
                    ┌────────────────────┼────────────────┐
                    │         BUILDING-PASS              │
                    │                    ▼                │
Buildings ──► Height Wrangle ──► Volume Wrangle          │
                    │                    │                │
                    └────────────────────┼────────────────┘
                                         │
                                         ▼
                                  HeightField Blur
                                         │
                                         ▼
                                   Final Terrain
```
