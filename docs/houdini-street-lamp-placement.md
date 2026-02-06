# Houdini: Straßenlaternen-Placement entlang Edges

Protokoll: Laternen entlang von Straßenkanten (edge_left/edge_right) platzieren mit VEX.

## Input-Anforderungen

- Polylines mit Prim-Attribut `name`: z.B. `major_big_edge_left`, `major_small_edge_right`
- Point-Attribut `street_dir` (vector3): Richtung zur Straßenmitte (-1 bis 1)
- Point-Attribut `street_name`: z.B. `major_big`, `major_small`

## Komplette VEX Wrangle

**Run Over: Primitives**

```vex
// ==== PARAMETER ====
float spacing = ch("spacing");
float offset = ch("offset");
float prevalence = ch("prevalence");
int seed = chi("seed");
float side_offset = ch("side_offset");
float outward_offset = ch("outward_offset");
float drop_down = ch("drop_down");
float rotation = ch("rotation");

// Spacing-Multiplier pro Street-Type
float mult_major_big = ch("mult_major_big");
float mult_major_small = ch("mult_major_small");

string name = prim(0, "name", @primnum);

int side = find(name, "_left") >= 0 ? -1 : 1;

int pts[] = primpoints(0, @primnum);
int num_pts = len(pts);

if (num_pts < 2) return;

// street_name vom Point lesen
string street_name = point(0, "street_name", pts[0]);

// Fallback: aus prim name extrahieren
if (street_name == "") {
    if (find(name, "major_big") >= 0) street_name = "major_big";
    else if (find(name, "major_small") >= 0) street_name = "major_small";
}

float spacing_mult = 1.0;
if (street_name == "major_big") spacing_mult = mult_major_big;
else if (street_name == "major_small") spacing_mult = mult_major_small;

float final_spacing = spacing * spacing_mult;

float total_length = 0;
float seg_lengths[];
vector positions[];

for (int i = 0; i < num_pts; i++) {
    vector p = point(0, "P", pts[i]);
    append(positions, p);
    if (i > 0) {
        float seg_len = distance(positions[i-1], positions[i]);
        append(seg_lengths, seg_len);
        total_length += seg_len;
    }
}

float current_dist = offset;
int lamp_id = 0;

while (current_dist < total_length) {

    float rand = rand(@primnum * 1000 + lamp_id + seed);
    if (rand <= prevalence) {

        float walked = 0;
        for (int i = 0; i < len(seg_lengths); i++) {
            if (walked + seg_lengths[i] >= current_dist) {
                float local_t = (current_dist - walked) / seg_lengths[i];
                vector pos = lerp(positions[i], positions[i+1], local_t);

                vector tan = normalize(positions[i+1] - positions[i]);

                vector sd0 = point(0, "street_dir", pts[i]);
                vector sd1 = point(0, "street_dir", pts[i+1]);
                vector street_dir = lerp(sd0, sd1, local_t);

                vector facing = normalize(street_dir) * side;

                vector up = {0, 1, 0};
                vector outward = normalize(cross(tan, up)) * side;

                pos += facing * side_offset;
                pos += outward * outward_offset;
                pos.y -= drop_down;

                // Rotation + 180° flip für gegenüberliegende Seite
                float base_rot = rotation;
                if (side == 1) base_rot += 180;

                float rad = radians(base_rot);
                vector n_rotated;
                n_rotated.x = tan.x * cos(rad) - tan.z * sin(rad);
                n_rotated.y = 0;
                n_rotated.z = tan.x * sin(rad) + tan.z * cos(rad);

                int pt = addpoint(0, pos);

                setpointattrib(0, "N", pt, normalize(n_rotated));
                setpointattrib(0, "up", pt, up);
                setpointattrib(0, "tangentu", pt, tan);
                setpointattrib(0, "outward", pt, outward);
                setpointattrib(0, "side", pt, side);
                setpointattrib(0, "street_name", pt, street_name);
                setpointattrib(0, "prim_name", pt, name);
                setpointattrib(0, "lamp_id", pt, lamp_id);

                break;
            }
            walked += seg_lengths[i];
        }
    }

    current_dist += final_spacing;
    lamp_id++;
}

removeprim(0, @primnum, 1);
```

## Parameter-Interface

| Name | Label | Type | Range | Default |
|------|-------|------|-------|---------|
| `spacing` | Basis-Abstand | Float | 1-50 | 15 |
| `offset` | Start-Offset | Float | 0-20 | 0 |
| `prevalence` | Häufigkeit | Float | 0-1 | 0.9 |
| `seed` | Seed | Int | 0-999 | 42 |
| `side_offset` | Side Offset | Float | -5 bis 5 | 0 |
| `outward_offset` | Nach Außen | Float | -5 bis 5 | 0.5 |
| `drop_down` | Drop Down | Float | 0-10 | 0 |
| `rotation` | Rotation | Float | -180 bis 180 | 0 |
| `mult_major_big` | Major Big Spacing | Float | 0.5-3 | 1.0 |
| `mult_major_small` | Major Small Spacing | Float | 0.5-3 | 1.5 |

## Unreal Engine Blueprint Spawning

Nach der Laternen-Wrangle:

```vex
// RUN OVER: Points

string street = s@street_name;

if (street == "major_big") {
    s@unreal_instance = "/Game/Blueprints/Lamps/BP_Lamp_Large";
} else if (street == "major_small") {
    s@unreal_instance = "/Game/Blueprints/Lamps/BP_Lamp_Medium";
} else {
    s@unreal_instance = "/Game/Blueprints/Lamps/BP_Lamp_Small";
}
```

### Wichtige Unreal-Attribute

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `unreal_instance` | String (Point) | Blueprint/StaticMesh Pfad |
| `unreal_split_instances` | Int (Detail) | 1 = separate Actors |
| `unreal_level_path` | String (Prim) | Sublevel für Actor |

---

## Zusatz: Gruppen kombinieren für Bevel

### Schnittmenge (AND)
```
extrudeSide extrudeFront
```

### Oder (OR)
```
extrudeSide | extrudeFront
```

### NOT
```
!extrudeSide
```

### Side die Front berührt (VEX)

```vex
// RUN OVER: Primitives

if (!inprimgroup(0, "extrudeSide", @primnum)) return;

int touching = 0;
int pts[] = primpoints(0, @primnum);

foreach (int pt; pts) {
    int prims[] = pointprims(0, pt);
    foreach (int pr; prims) {
        if (pr != @primnum && inprimgroup(0, "extrudeFront", pr)) {
            touching = 1;
            break;
        }
    }
    if (touching) break;
}

if (touching) {
    setprimgroup(0, "side_touching_front", @primnum, 1);
}
```

---

## Zusatz: Straßennetzwerk Inset-Methoden

### Option 1: PolyExpand2D (Beste für Centerlines)
```
Centerlines → PolyExpand2D (Offset = Straßenbreite/2)
```

### Option 2: VDB Offset (für existierende Ribbons)
```
Ribbons → VDB from Polygons → VDB Reshape SDF (Erode) → Convert VDB
```

### Option 3: Labs Straight Skeleton
```
Ribbons → Labs Straight Skeleton 2D
```
