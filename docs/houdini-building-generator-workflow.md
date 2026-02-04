# Houdini Building Generator Workflow

Prozedurales Dach-Raising, Garage-Wände und Tür-Generierung für OSM Buildings.

## Übersicht

```
[Building from Patterns]
    → [Extrude Wände] (für Dicke)
    → [Point Wrangle: Dach Raising]
    → [Primitive Wrangle: Garage Wall Erkennung]
    → [Primitive Wrangle: Garage Türen]
    → [Labs Auto UV]
```

---

## 1. Dach Raising (Point Wrangle)

**Run over:** Points
**Group:** ceiling (oder tempCeiling)

```vex
float ridge_height = chf("ridge_height");
float target_angle = chf("roof_direction");
vector target_dir = set(cos(radians(target_angle)), 0, sin(radians(target_angle)));

int prims[] = pointprims(0, @ptnum);
if(len(prims) == 0) return;
int prim = prims[0];

int pts[] = primpoints(0, prim);
int num_pts = len(pts);

if(num_pts < 3) return;

if(num_pts == 4) {
    vector p0 = point(0, "P", pts[0]);
    vector p1 = point(0, "P", pts[1]);
    vector p2 = point(0, "P", pts[2]);
    vector p3 = point(0, "P", pts[3]);

    float len01 = length(p1 - p0);
    float len12 = length(p2 - p1);
    float len23 = length(p3 - p2);
    float len30 = length(p0 - p3);

    float pair_A = len01 + len23;
    float pair_B = len12 + len30;

    vector centroid = (p0 + p1 + p2 + p3) / 4;

    int raise_pt_a, raise_pt_b;

    if(pair_A > pair_B) {
        vector mid01 = (p0 + p1) / 2;
        vector mid23 = (p2 + p3) / 2;

        if(dot(mid01 - centroid, target_dir) > dot(mid23 - centroid, target_dir)) {
            raise_pt_a = pts[0]; raise_pt_b = pts[1];
        } else {
            raise_pt_a = pts[2]; raise_pt_b = pts[3];
        }
    } else {
        vector mid12 = (p1 + p2) / 2;
        vector mid30 = (p3 + p0) / 2;

        if(dot(mid12 - centroid, target_dir) > dot(mid30 - centroid, target_dir)) {
            raise_pt_a = pts[1]; raise_pt_b = pts[2];
        } else {
            raise_pt_a = pts[3]; raise_pt_b = pts[0];
        }
    }

    if(@ptnum == raise_pt_a || @ptnum == raise_pt_b) {
        @P.y += ridge_height;
    }
}
else {
    // Nicht-Quad Fallback: längste Edge finden
    float max_len = 0;
    int best_a = pts[0], best_b = pts[1];

    for(int i = 0; i < num_pts; i++) {
        int pt_a = pts[i];
        int pt_b = pts[(i + 1) % num_pts];
        vector pa = point(0, "P", pt_a);
        vector pb = point(0, "P", pt_b);
        float len = length(pb - pa);

        if(len > max_len) {
            max_len = len;
            best_a = pt_a;
            best_b = pt_b;
        }
    }

    if(@ptnum == best_a || @ptnum == best_b) {
        @P.y += ridge_height;
    }
}
```

**Parameter:**
- `ridge_height`: 0-5m (Höhe des Dachfirsts)
- `roof_direction`: 0-360° (Ausrichtung aller Dächer)

---

## 2. Garage Wall Erkennung (Primitive Wrangle)

**Run over:** Primitives
**Group:** walls

```vex
float target_angle = chf("roof_direction");
float min_wall_length = chf("min_wall_length");
float other_side_percent = chf("other_side_percent");

vector target_dir = set(cos(radians(target_angle)), 0, sin(radians(target_angle)));

int pts[] = primpoints(0, @primnum);
if(len(pts) != 4) return;

float min_y = 1e9;
foreach(int pt; pts) {
    vector pos = point(0, "P", pt);
    if(pos.y < min_y) min_y = pos.y;
}

int bottom_pts[];
foreach(int pt; pts) {
    vector pos = point(0, "P", pt);
    if(pos.y < min_y + 0.01) append(bottom_pts, pt);
}

if(len(bottom_pts) != 2) return;

vector p0 = point(0, "P", bottom_pts[0]);
vector p1 = point(0, "P", bottom_pts[1]);
float wall_length = length(p1 - p0);

if(wall_length < min_wall_length) {
    i@is_garage_wall = 0;
    @Cd = {0.5, 0.5, 0.5};
    return;
}

vector wall_N = @N;
wall_N.y = 0;
wall_N = normalize(wall_N);

float facing = dot(wall_N, target_dir);

vector centroid = (p0 + p1) / 2;
float rand_val = random(centroid * 0.01);
int use_other = (rand_val < other_side_percent) ? 1 : 0;

int is_garage = 0;
if(use_other) {
    if(facing > 0.3) is_garage = 1;
} else {
    if(facing < -0.3) is_garage = 1;
}

if(is_garage) {
    i@is_garage_wall = 1;
    @Cd = {1, 0.5, 0};
} else {
    i@is_garage_wall = 0;
    @Cd = {0.5, 0.5, 0.5};
}
```

**Parameter:**
- `roof_direction`: 0-360° (gleicher Wert wie Dach!)
- `min_wall_length`: 4.0m (Minimum für Garage-Wand)
- `other_side_percent`: 0-1 (z.B. 0.1 = 10% auf anderer Seite)

---

## 3. Garage Türen (Primitive Wrangle)

**Run over:** Primitives
**Group:** @is_garage_wall==1

```vex
if(i@is_garage_wall != 1) return;
if(abs(@N.y) > 0.3) return;

float door_width = chf("door_width");
float door_height = chf("door_height");
float door_spacing = chf("door_spacing");
float margin = chf("margin");
float light_height = chf("light_height");
float min_wall_width = chf("min_wall_width");

int pts[] = primpoints(0, @primnum);
if(len(pts) != 4) {
    setprimattrib(0, "is_garage_wall", @primnum, 0);
    setprimattrib(0, "Cd", @primnum, {0.5, 0.5, 0.5});
    return;
}

vector wall_N = @N;

float min_y = 1e9, max_y = -1e9;
foreach(int pt; pts) {
    vector pos = point(0, "P", pt);
    if(pos.y < min_y) min_y = pos.y;
    if(pos.y > max_y) max_y = pos.y;
}

int bottom_pts[], top_pts[];
foreach(int pt; pts) {
    vector pos = point(0, "P", pt);
    if(pos.y < min_y + 0.01) append(bottom_pts, pt);
    else if(pos.y > max_y - 0.01) append(top_pts, pt);
}

if(len(bottom_pts) != 2 || len(top_pts) != 2) return;

vector bl = point(0, "P", bottom_pts[0]);
vector br = point(0, "P", bottom_pts[1]);
if(length(br - bl) < 0.01) return;

vector wall_dir = normalize(br - bl);

if(dot(br - bl, wall_dir) < 0) {
    int temp = bottom_pts[0];
    bottom_pts[0] = bottom_pts[1];
    bottom_pts[1] = temp;
    bl = point(0, "P", bottom_pts[0]);
    br = point(0, "P", bottom_pts[1]);
}

vector tl = point(0, "P", top_pts[0]);
vector tr = point(0, "P", top_pts[1]);
vector tl_flat = tl; tl_flat.y = bl.y;
if(length(tl_flat - bl) > length(tl_flat - br)) {
    int temp = top_pts[0];
    top_pts[0] = top_pts[1];
    top_pts[1] = temp;
}

float wall_width = length(br - bl);
float wall_height = max_y - min_y;

if(wall_width < min_wall_width || wall_width < door_width + 2*margin) return;
if(wall_height < door_height + 0.1) return;

float usable_width = wall_width - 2 * margin;
int num_doors = int(floor((usable_width + door_spacing) / (door_width + door_spacing)));
if(num_doors < 1) return;

float total_doors_width = num_doors * door_width + (num_doors - 1) * door_spacing;
float start_offset = (wall_width - total_doors_width) / 2;

float door_top_y = min_y + door_height;

removeprim(0, @primnum, 0);

int pt_door_bottom[], pt_door_top[];

for(int i = 0; i < num_doors; i++) {
    float door_left = start_offset + i * (door_width + door_spacing);
    float door_right = door_left + door_width;
    float door_center = door_left + door_width / 2;

    vector base_l = bl + wall_dir * door_left;
    vector base_r = bl + wall_dir * door_right;
    vector base_c = bl + wall_dir * door_center;

    int pbl = addpoint(0, set(base_l.x, min_y, base_l.z));
    int pbr = addpoint(0, set(base_r.x, min_y, base_r.z));
    int ptl = addpoint(0, set(base_l.x, door_top_y, base_l.z));
    int ptr = addpoint(0, set(base_r.x, door_top_y, base_r.z));

    setpointattrib(0, "N", pbl, wall_N);
    setpointattrib(0, "N", pbr, wall_N);
    setpointattrib(0, "N", ptl, wall_N);
    setpointattrib(0, "N", ptr, wall_N);

    append(pt_door_bottom, pbl);
    append(pt_door_bottom, pbr);
    append(pt_door_top, ptl);
    append(pt_door_top, ptr);

    // Tür-Face
    int pr = addprim(0, "poly", pbl, pbr, ptr, ptl);
    setprimattrib(0, "N", pr, wall_N);
    setprimattrib(0, "is_door", pr, 1);

    // Licht-Punkt über der Tür
    vector light_pos = set(base_c.x, door_top_y + light_height, base_c.z);
    int light_pt = addpoint(0, light_pos);
    setpointattrib(0, "N", light_pt, wall_N);
    setpointattrib(0, "lgth_pnt", light_pt, 1);
}

// Oberes N-gon
int upper_ngon[];
append(upper_ngon, top_pts[0]);
for(int i = 0; i < len(pt_door_top); i++) {
    append(upper_ngon, pt_door_top[i]);
}
append(upper_ngon, top_pts[1]);

int pr_upper = addprim(0, "poly", upper_ngon);
setprimattrib(0, "N", pr_upper, wall_N);
setprimattrib(0, "is_wall", pr_upper, 1);

// Linker Pfeiler
int pr_left = addprim(0, "poly", bottom_pts[0], pt_door_bottom[0], pt_door_top[0], top_pts[0]);
setprimattrib(0, "N", pr_left, wall_N);
setprimattrib(0, "is_wall", pr_left, 1);

// Rechter Pfeiler
int last = len(pt_door_bottom) - 1;
int pr_right = addprim(0, "poly", pt_door_bottom[last], bottom_pts[1], top_pts[1], pt_door_top[last]);
setprimattrib(0, "N", pr_right, wall_N);
setprimattrib(0, "is_wall", pr_right, 1);

// Pfeiler zwischen Türen
for(int i = 0; i < num_doors - 1; i++) {
    int idx = i * 2 + 1;
    int pr = addprim(0, "poly", pt_door_bottom[idx], pt_door_bottom[idx+1], pt_door_top[idx+1], pt_door_top[idx]);
    setprimattrib(0, "N", pr, wall_N);
    setprimattrib(0, "is_wall", pr_right, 1);
}
```

**Parameter:**
- `door_width`: 2.5m
- `door_height`: 2.5m
- `door_spacing`: 1.0m (Abstand zwischen Türen)
- `margin`: 0.5m (Rand links/rechts)
- `light_height`: 0.3m (Höhe des Licht-Punkts über Tür)
- `min_wall_width`: 4.0m

---

## 4. Hilfs-Wrangles

### Punkte filtern (z.B. nach module_name)

```vex
if(find(s@module_name, "Window") < 0) {
    removepoint(0, @ptnum);
}
```

### Nach oben zeigende Faces löschen

```vex
if(@N.y > 0.9) {
    removeprim(0, @primnum, 1);
}
```

---

## 5. UVs

```
[Finale Geometrie] → [Labs Auto UV]
```

Alternativ für Triplanar-Materials in Unreal: Keine UVs nötig.

---

## Output-Attribute

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `is_garage_wall` | int (prim) | 1 = Garage-Wand |
| `is_door` | int (prim) | 1 = Tür-Face |
| `is_wall` | int (prim) | 1 = Wand-Face |
| `lgth_pnt` | int (point) | 1 = Licht-Punkt |

---

## Notizen

- `roof_direction` muss in beiden Wrangles (Dach + Garage) gleich sein
- Gebäude mit komplexen Shapes (Nicht-Quads) werden mit Fallback behandelt
- Türen werden nur auf langen Wänden erstellt
- `other_side_percent` verteilt manche Garagen auf die andere lange Seite
