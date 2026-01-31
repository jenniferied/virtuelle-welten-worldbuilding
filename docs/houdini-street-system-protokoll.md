# Houdini Street System — Protokoll

> Session: 2026-01-30

## Ziel
Prozedurales Straßensystem mit variablen Breiten, Kreuzungen, Bürgersteigen und Props.
Road Labs Tool broken → eigener VEX-basierter Workflow.

## Straßentypen

| Typ | Width | Priority | Farbe |
|-----|-------|----------|-------|
| major_big | 30m | 3 | dunkelgrau |
| major_small | 15m | 2 | mittelgrau |
| mud | 6m | 1 | braun |
| intersection | max | 4 | grau |

## Workflow: Flach arbeiten, dann auf Terrain projizieren

---

## Phase 1: Line Preparation

### 1.1 Width/Color/Priority setzen (Primitive Wrangle)

```vex
string name = s@name;

if (name == "major_big") {
    f@width = 30.0;
    v@Cd = set(0.2, 0.2, 0.2);
    i@priority = 3;
} else if (name == "major_small") {
    f@width = 15.0;
    v@Cd = set(0.4, 0.4, 0.4);
    i@priority = 2;
} else if (name == "mud") {
    f@width = 6.0;
    v@Cd = set(0.55, 0.4, 0.25);
    i@priority = 1;
} else {
    f@width = 4.0;
    v@Cd = set(0.6, 0.6, 0.6);
    i@priority = 0;
}
```

### 1.2 Mud Lines mit Major Streets verbinden (Point Wrangle)

Input 0: mud_lines, Input 1: major_lines

```vex
int prims[] = pointprims(0, @ptnum);
if (len(prims) == 0) return;
if (len(prims) > 1) return;

string name = prim(0, "name", prims[0]);
if (name != "mud") return;

int my_prim = prims[0];
int prim_pts[] = primpoints(0, my_prim);
int is_start = (prim_pts[0] == @ptnum);
int is_end = (prim_pts[len(prim_pts)-1] == @ptnum);

if (!is_start && !is_end) return;

// Proximity check: andere Punkte in der Nähe?
float fuse_dist = 0.5;
int nearpts[] = nearpoints(0, @P, fuse_dist);
if (len(nearpts) > 1) return;

// Tangenten-Richtung
int nb = neighbours(0, @ptnum)[0];
vector nb_pos = point(0, "P", nb);
vector dir = normalize(@P - nb_pos);

vector ray_start = @P + dir * 0.1;
vector hit_pos, hit_uvw;
int hit_prim;

// 1. Versuch: Major streets (Input 1), 50m
hit_prim = intersect(1, ray_start, dir * 50.0, hit_pos, hit_uvw);

if (hit_prim >= 0) {
    int new_pt = addpoint(0, hit_pos);
    int new_prim = addprim(0, "polyline", @ptnum, new_pt);
    setprimattrib(0, "name", new_prim, "mud", "set");
    setprimattrib(0, "width", new_prim, 6.0, "set");
    i@connected = 1;
    return;
}

// 2. Versuch: Self-intersection mit anderen mud lines (Input 0), 10m
hit_prim = intersect(0, ray_start, dir * 10.0, hit_pos, hit_uvw);

if (hit_prim >= 0 && hit_prim != my_prim) {
    int new_pt = addpoint(0, hit_pos);
    int new_prim = addprim(0, "polyline", @ptnum, new_pt);
    setprimattrib(0, "name", new_prim, "mud", "set");
    setprimattrib(0, "width", new_prim, 6.0, "set");
    i@connected = 2;
    return;
}

i@is_dead_end = 1;
```

### 1.3 Kurze Lines entfernen (Primitive Wrangle)

```vex
string name = s@name;
if (name != "mud") return;

int pts[] = primpoints(0, @primnum);
int npts = len(pts);

if (npts <= 2) {
    removeprim(0, @primnum, 1);
    return;
}

float total_length = 0.0;
for (int i = 0; i < npts - 1; i++) {
    vector p0 = point(0, "P", pts[i]);
    vector p1 = point(0, "P", pts[i+1]);
    total_length += distance(p0, p1);
}

float min_length = 5.0;
if (total_length < min_length) {
    removeprim(0, @primnum, 1);
}
```

### 1.4 Intersections/Endpoints markieren (Point Wrangle)

```vex
int ncount = neighbourcount(0, @ptnum);
i@ncount = ncount;
i@is_intersection = (ncount > 2) ? 1 : 0;
i@is_endpoint = (ncount == 1) ? 1 : 0;
i@is_middle = (ncount == 2) ? 1 : 0;
```

### 1.5 Max Width an Intersections (Point Wrangle)

```vex
if (i@is_intersection != 1) return;

int prims[] = pointprims(0, @ptnum);
float max_w = 0.0;
int max_priority = 0;

foreach (int pr; prims) {
    float w = prim(0, "width", pr);
    int p = prim(0, "priority", pr);
    if (w > max_w) max_w = w;
    if (p > max_priority) max_priority = p;
}

f@intersection_width = max_w;
i@intersection_priority = max_priority;
```

---

## Phase 2: Geometry Generation

### 2.1 Ribbon Expansion (Primitive Wrangle)

```vex
int pts[] = primpoints(0, @primnum);
int n = len(pts);
if (n < 2) return;

string name = s@name;
float width = f@width;
int priority = i@priority;

vector col = set(0.5, 0.5, 0.5);
if (name == "major_big") col = set(0.2, 0.2, 0.2);
else if (name == "major_small") col = set(0.4, 0.4, 0.4);
else if (name == "mud") col = set(0.55, 0.4, 0.25);

int left[];
int right[];
vector up = set(0.0, 1.0, 0.0);

for (int i = 0; i < n; i++) {
    vector pos = point(0, "P", pts[i]);

    vector dir = set(0.0, 0.0, 0.0);
    if (i > 0) {
        vector prev = point(0, "P", pts[i-1]);
        dir += normalize(pos - prev);
    }
    if (i < n - 1) {
        vector next = point(0, "P", pts[i+1]);
        dir += normalize(next - pos);
    }
    if (length(dir) < 0.001) dir = set(1.0, 0.0, 0.0);
    else dir = normalize(dir);

    vector side = normalize(cross(dir, up)) * width * 0.5;

    int pt_left = addpoint(0, pos - side);
    int pt_right = addpoint(0, pos + side);

    setpointattrib(0, "N", pt_left, up);
    setpointattrib(0, "N", pt_right, up);

    append(left, pt_left);
    append(right, pt_right);
}

for (int i = 0; i < n - 1; i++) {
    int newprim = addprim(0, "poly", left[i], right[i], right[i+1], left[i+1]);

    setprimattrib(0, "name", newprim, name, "set");
    setprimattrib(0, "width", newprim, width, "set");
    setprimattrib(0, "priority", newprim, priority, "set");
    setprimattrib(0, "Cd", newprim, col, "set");
}

// Edge-Lines für Bürgersteig
int left_line = addprim(0, "polyline", left);
int right_line = addprim(0, "polyline", right);

setprimattrib(0, "name", left_line, name + "_edge_left", "set");
setprimattrib(0, "name", right_line, name + "_edge_right", "set");

removeprim(0, @primnum, 1);
```

---

## Node Graph (aktueller Stand)

```
major_lines ─────────────────────────────────┐
                                             ↓
mud_lines → [Fuse] → [Point Wrangle] connect → [Merge]
                                             ↓
                                        [Fuse] 0.01
                                             ↓
                                   [Prim Wrangle] remove_short
                                             ↓
                                   [Prim Wrangle] set_width
                                             ↓
                                   [Attrib Promote] width → Point
                                             ↓
                                   [Point Wrangle] mark_intersections
                                             ↓
                                   [Point Wrangle] intersection_max_width
                                             ↓
                                   [Prim Wrangle] expand_to_ribbons
                                             ↓
                                        ribbons + edge_lines
```

---

## TODO

### Phase 2 (weiter)
- [ ] Intersection-Polygone generieren (Convex Hull oder N-Gon)
- [ ] Boolean Union für saubere Geometrie

### Phase 3: Details
- [ ] Bürgersteige aus Edge-Lines
- [ ] Crossings/Zebrastreifen
- [ ] Laternen, Ampeln, parkende Autos

### Phase 4: Terrain
- [ ] HeightField Mask für Flattening
- [ ] Ray SOP für Projection
- [ ] Hausflächen/Parzellen

---

## Notizen

- PolyExpand2D kann keine per-primitive Offsets → eigenes VEX
- Flach arbeiten (Y=0), am Ende auf Terrain projizieren
- Farben: Cd auf Primitives setzen, dann Attrib Promote zu Points
- Viewport: Display Options → Use Vertex/Point Color
