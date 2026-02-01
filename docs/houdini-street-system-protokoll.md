# Houdini Street System — Protokoll

> Session: 2026-01-30 → 2026-02-01

## Ziel
Prozedurales Straßensystem mit variablen Breiten, Kreuzungen, Bürgersteigen und Props.
Road Labs Tool broken → eigener VEX-basierter Workflow.

## Straßentypen

| Typ | Width | Priority | Farbe |
|-----|-------|----------|-------|
| major_big | 300m | 3 | rot |
| major_small | 25m | 2 | grün |
| mud | 12m | 1 | lila |
| intersection | - | 4 | gelb |

---

## Phase 1: Line Preparation

### 1.1 Width/Color/Priority setzen (Primitive Wrangle)

```vex
float width = 5.0;  // default

if (s@name == "major_big") {
    width = 300.0;
} else if (s@name == "major_small") {
    width = 25.0;
} else if (s@name == "mud") {
    width = 12.0;
}

f@width = width;
```

---

## Phase 2: Intersection Detection & Cutting

### 2.1 Mark Intersections (Point Wrangle)

```vex
int prims[] = pointprims(0, @ptnum);
if(len(prims) <= 2) return;

int prim_ids[] = {};
float w_arr[] = {};
vector dir_arr[] = {};

foreach(int pr; prims) {
    int pts[] = primpoints(0, pr);
    vector other_pos = @P;
    foreach(int pt; pts) {
        if(pt != @ptnum) {
            other_pos = point(0, "P", pt);
            break;
        }
    }
    vector dir = normalize(other_pos - @P);

    push(prim_ids, pr);
    push(w_arr, float(prim(0, "width", pr)));
    push(dir_arr, dir);
}

i[]@inter_prims = prim_ids;
f[]@inter_widths = w_arr;
v[]@inter_dirs = dir_arr;
i@int_id = @ptnum;
setpointgroup(0, "intersections", @ptnum, 1);
```

### 2.2 Intersection Start/Endpoint Logic (Primitive Wrangle)

```vex
int pts[] = primpoints(0, @primnum);
int n = len(pts);
if (n < 2) return;

int start_pt = pts[0];
int end_pt = pts[n-1];

int start_in_group = inpointgroup(0, "intersections", start_pt);
int end_in_group = inpointgroup(0, "intersections", end_pt);

i@start_int_id = start_in_group ? point(0, "int_id", start_pt) : -1;
i@end_int_id = end_in_group ? point(0, "int_id", end_pt) : -1;
```

### 2.3 Intersection Cut Out (Primitive Wrangle)

Mit per-Straßentyp Multiplikatoren.

```vex
float cut_multiplier = chf("cut_multiplier");
float cut_bias = chf("cut_bias");

float mult_major_big = chf("mult_major_big");
float mult_major_small = chf("mult_major_small");
float mult_mud = chf("mult_mud");

float my_width = f@width;
string my_name = s@name;
int my_start_int = i@start_int_id;
int my_end_int = i@end_int_id;

float type_mult = 1.0;
if (my_name == "major_big") {
    type_mult = mult_major_big;
} else if (my_name == "major_small") {
    type_mult = mult_major_small;
} else if (my_name == "mud") {
    type_mult = mult_mud;
}

int pts[] = primpoints(0, @primnum);
int npts = len(pts);
if (npts < 2) return;

vector prim_dir = normalize(point(0, "P", pts[npts-1]) - point(0, "P", pts[0]));

// Berechne Cut-Distanz für START
float start_cut = 0;
if (my_start_int >= 0) {
    int start_int_pt = -1;
    for (int i = 0; i < npoints(1); i++) {
        int check_id = point(1, "int_id", i);
        if (check_id == my_start_int) {
            start_int_pt = i;
            break;
        }
    }

    if (start_int_pt >= 0) {
        float other_widths[] = point(1, "inter_widths", start_int_pt);
        vector other_dirs[] = point(1, "inter_dirs", start_int_pt);

        for (int j = 0; j < len(other_dirs); j++) {
            vector other_dir = other_dirs[j];
            float other_w = other_widths[j];

            float cos_angle = abs(dot(-prim_dir, other_dir));
            if (cos_angle > 0.9) continue;

            float sin_angle = sqrt(1.0 - cos_angle * cos_angle);
            sin_angle = max(sin_angle, 0.2);

            float cut = ((other_w + my_width) * 0.5) / sin_angle;
            cut = cut * cut_multiplier * type_mult + cut_bias;
            start_cut = max(start_cut, cut);
        }
    }
}

// Berechne Cut-Distanz für END
float end_cut = 0;
if (my_end_int >= 0) {
    int end_int_pt = -1;
    for (int i = 0; i < npoints(1); i++) {
        int check_id = point(1, "int_id", i);
        if (check_id == my_end_int) {
            end_int_pt = i;
            break;
        }
    }

    if (end_int_pt >= 0) {
        float other_widths[] = point(1, "inter_widths", end_int_pt);
        vector other_dirs[] = point(1, "inter_dirs", end_int_pt);

        for (int j = 0; j < len(other_dirs); j++) {
            vector other_dir = other_dirs[j];
            float other_w = other_widths[j];

            float cos_angle = abs(dot(prim_dir, other_dir));
            if (cos_angle > 0.9) continue;

            float sin_angle = sqrt(1.0 - cos_angle * cos_angle);
            sin_angle = max(sin_angle, 0.2);

            float cut = ((other_w + my_width) * 0.5) / sin_angle;
            cut = cut * cut_multiplier * type_mult + cut_bias;
            end_cut = max(end_cut, cut);
        }
    }
}

// Positionen von Start und End Intersection
vector start_int_pos = point(0, "P", pts[0]);
vector end_int_pos = point(0, "P", pts[npts-1]);

if (my_start_int >= 0) {
    for (int i = 0; i < npoints(1); i++) {
        if (point(1, "int_id", i) == my_start_int) {
            start_int_pos = point(1, "P", i);
            break;
        }
    }
}
if (my_end_int >= 0) {
    for (int i = 0; i < npoints(1); i++) {
        if (point(1, "int_id", i) == my_end_int) {
            end_int_pos = point(1, "P", i);
            break;
        }
    }
}

// Punkte filtern
vector keep[];

foreach (int i; int pt; pts) {
    vector pos = point(0, "P", pt);

    int should_keep = 1;

    if (my_start_int >= 0 && start_cut > 0) {
        float dist_to_start = distance(pos, start_int_pos);
        if (dist_to_start < start_cut) {
            should_keep = 0;
        }
    }

    if (my_end_int >= 0 && end_cut > 0) {
        float dist_to_end = distance(pos, end_int_pos);
        if (dist_to_end < end_cut) {
            should_keep = 0;
        }
    }

    if (should_keep == 1) {
        append(keep, pos);
    }
}

removeprim(0, @primnum, 1);

if (len(keep) >= 2) {
    int newpts[];
    foreach (vector p; keep)
        append(newpts, addpoint(0, p));
    int newprim = addprim(0, "polyline", newpts);

    setprimattrib(0, "width", newprim, my_width);
    setprimattrib(0, "name", newprim, my_name);
    setprimattrib(0, "start_int_id", newprim, my_start_int);
    setprimattrib(0, "end_int_id", newprim, my_end_int);
}
```

**Parameter:**
- `cut_multiplier` (Float, default 1.0)
- `cut_bias` (Float, default 0.0)
- `mult_major_big` (Float, default 1.0)
- `mult_major_small` (Float, default 1.1)
- `mult_mud` (Float, default 1.3)

---

## Phase 3: Ribbon Generation

### 3.1 Ribbon (Primitive Wrangle)

```vex
int pts[] = primpoints(0, @primnum);
int n = len(pts);
if (n < 2) return;

string name = s@name;
float width = f@width;
int priority = i@priority;

int start_int_id = i@start_int_id;
int end_int_id = i@end_int_id;

vector col = set(0.5, 0.5, 0.5);
if (name == "major_big") col = set(0.9, 0.2, 0.2);
else if (name == "major_small") col = set(0.4, 1, 0.4);
else if (name == "mud") col = set(0.55, 0.4, 1);

int start_dead = point(0, "is_dead_end", pts[0]);
int end_dead = point(0, "is_dead_end", pts[n-1]);

int left[];
int right[];
vector up = set(0, 1, 0);

for (int i = 0; i < n; i++) {
    vector pos = point(0, "P", pts[i]);

    vector dir = set(0, 0, 0);
    if (i > 0) dir += normalize(pos - point(0, "P", pts[i-1]));
    if (i < n-1) dir += normalize(point(0, "P", pts[i+1]) - pos);
    if (length(dir) < 0.001) dir = set(1, 0, 0);
    else dir = normalize(dir);

    vector side = normalize(cross(dir, up)) * width * 0.5;

    int pt_left = addpoint(0, pos - side);
    int pt_right = addpoint(0, pos + side);

    setpointattrib(0, "int_id", pt_left, -1);
    setpointattrib(0, "int_id", pt_right, -1);

    setpointattrib(0, "N", pt_left, up);
    setpointattrib(0, "N", pt_right, up);

    if (i == 0 && start_dead == 0 && start_int_id >= 0) {
        setpointattrib(0, "int_id", pt_left, start_int_id);
        setpointattrib(0, "int_id", pt_right, start_int_id);
        setpointattrib(0, "edge_side", pt_left, 0);
        setpointattrib(0, "edge_side", pt_right, 1);
        setpointattrib(0, "street_name", pt_left, name);
        setpointattrib(0, "street_name", pt_right, name);
        setpointattrib(0, "street_width", pt_left, width);
        setpointattrib(0, "street_width", pt_right, width);
        setpointattrib(0, "street_dir", pt_left, -dir);
        setpointattrib(0, "street_dir", pt_right, -dir);
    }

    if (i == n-1 && end_dead == 0 && end_int_id >= 0) {
        setpointattrib(0, "int_id", pt_left, end_int_id);
        setpointattrib(0, "int_id", pt_right, end_int_id);
        setpointattrib(0, "edge_side", pt_left, 0);
        setpointattrib(0, "edge_side", pt_right, 1);
        setpointattrib(0, "street_name", pt_left, name);
        setpointattrib(0, "street_name", pt_right, name);
        setpointattrib(0, "street_width", pt_left, width);
        setpointattrib(0, "street_width", pt_right, width);
        setpointattrib(0, "street_dir", pt_left, dir);
        setpointattrib(0, "street_dir", pt_right, dir);
    }

    push(left, pt_left);
    push(right, pt_right);
}

for (int i = 0; i < n-1; i++) {
    int newprim = addprim(0, "poly", left[i], right[i], right[i+1], left[i+1]);
    setprimattrib(0, "name", newprim, name);
    setprimattrib(0, "width", newprim, width);
    setprimattrib(0, "priority", newprim, priority);
    setprimattrib(0, "Cd", newprim, col);
}

int left_line = addprim(0, "polyline", left);
int right_line = addprim(0, "polyline", right);
setprimattrib(0, "name", left_line, name + "_edge_left");
setprimattrib(0, "name", right_line, name + "_edge_right");
setprimattrib(0, "Cd", left_line, set(1, 0, 0));
setprimattrib(0, "Cd", right_line, set(0, 0, 1));

removeprim(0, @primnum, 1);
```

---

## Phase 4: Intersection Polygon Generation

### 4.1 Intersection Create v6 (Point Wrangle)

Vollständiges Wrangle mit:
- Topologie-basiertem Clustering (merged nahe Intersections)
- Radialem Sortieren
- Adaptive Corner Segments (Bezier-Kurven)
- Nur Boundary-Polygon (kein Center Fan)

**Inputs:**
- Input 0: Intersection points (mit int_id)
- Input 1: Ribbon geometry (mit edge points)
- Input 2: Original cut lines (mit start_int_id, end_int_id, width)

```vex
int my_id = i@int_id;

// ===== PARAMETER =====
float corner_radius = chf("corner_radius");
int min_segments = chi("min_segments");
int max_segments = chi("max_segments");
float adaptivity = chf("adaptivity");
float merge_threshold = chf("merge_threshold");
float straight_threshold = chf("straight_threshold");

// ===== PHASE 1: CLUSTER DETECTION =====
int cluster_ids[];
push(cluster_ids, my_id);

int num_prims = nprimitives(2);
int changed = 1;
int max_iter = 20;
int iter = 0;

while (changed == 1 && iter < max_iter) {
    changed = 0;
    iter++;

    for (int pr = 0; pr < num_prims; pr++) {
        int start_id = prim(2, "start_int_id", pr);
        int end_id = prim(2, "end_int_id", pr);

        if (start_id < 0 || end_id < 0) continue;

        int start_in_cluster = 0;
        int end_in_cluster = 0;

        foreach (int cid; cluster_ids) {
            if (cid == start_id) start_in_cluster = 1;
            if (cid == end_id) end_in_cluster = 1;
        }

        if (start_in_cluster == 0 && end_in_cluster == 0) continue;
        if (start_in_cluster == 1 && end_in_cluster == 1) continue;

        int pts[] = primpoints(2, pr);
        if (len(pts) < 2) continue;

        vector p0 = point(2, "P", pts[0]);
        vector p1 = point(2, "P", pts[len(pts)-1]);
        float line_length = distance(p0, p1);
        float line_width = prim(2, "width", pr);

        float threshold = line_width * merge_threshold;

        if (line_length < threshold) {
            if (start_in_cluster == 1 && end_in_cluster == 0) {
                push(cluster_ids, end_id);
                changed = 1;
            } else if (end_in_cluster == 1 && start_in_cluster == 0) {
                push(cluster_ids, start_id);
                changed = 1;
            }
        }
    }
}

int min_cluster_id = my_id;
foreach (int cid; cluster_ids) {
    if (cid < min_cluster_id) min_cluster_id = cid;
}

if (my_id != min_cluster_id) {
    i@cluster_id = min_cluster_id;
    i@is_cluster_leader = 0;
    return;
}

i@cluster_id = my_id;
i@is_cluster_leader = 1;
i@cluster_size = len(cluster_ids);

// ===== PHASE 2: EDGE-PUNKTE SAMMELN =====
vector edge_positions[];
vector edge_dirs[];
string edge_street_names[];
int edge_sides[];
int edge_int_ids[];

int total_pts = npoints(1);
for (int i = 0; i < total_pts; i++) {
    int pt_int_id = point(1, "int_id", i);
    if (pt_int_id < 0) continue;

    int in_cluster = 0;
    foreach (int cid; cluster_ids) {
        if (cid == pt_int_id) {
            in_cluster = 1;
            break;
        }
    }

    if (in_cluster == 0) continue;

    vector pos = point(1, "P", i);
    vector dir = point(1, "street_dir", i);
    string name = point(1, "street_name", i);
    int side = point(1, "edge_side", i);

    push(edge_positions, pos);
    push(edge_dirs, dir);
    push(edge_street_names, name);
    push(edge_sides, side);
    push(edge_int_ids, pt_int_id);
}

int count = len(edge_positions);
if (count < 3) return;

// ===== PHASE 3: CENTROID =====
vector centroid = set(0,0,0);
for (int i = 0; i < count; i++) {
    centroid += edge_positions[i];
}
centroid /= float(count);

// ===== PHASE 4: RADIALES SORTIEREN =====
float point_angles[];
for (int i = 0; i < count; i++) {
    vector dir = edge_positions[i] - centroid;
    float angle = atan2(dir.z, dir.x);
    push(point_angles, angle);
}

int sorted_indices[];
for (int i = 0; i < count; i++) {
    push(sorted_indices, i);
}

for (int i = 0; i < count - 1; i++) {
    for (int j = 0; j < count - 1 - i; j++) {
        if (point_angles[sorted_indices[j]] > point_angles[sorted_indices[j+1]]) {
            int tmp = sorted_indices[j];
            sorted_indices[j] = sorted_indices[j+1];
            sorted_indices[j+1] = tmp;
        }
    }
}

// ===== PHASE 5: POLYGON MIT ADAPTIVE CORNERS =====
vector final_positions[];
int is_anchor[];

for (int i = 0; i < count; i++) {
    int curr_idx = sorted_indices[i];
    int next_idx = sorted_indices[(i + 1) % count];

    vector pos_curr = edge_positions[curr_idx];
    vector pos_next = edge_positions[next_idx];

    string name_curr = edge_street_names[curr_idx];
    string name_next = edge_street_names[next_idx];

    vector dir_curr = edge_dirs[curr_idx];
    vector dir_next = edge_dirs[next_idx];

    int int_id_curr = edge_int_ids[curr_idx];
    int int_id_next = edge_int_ids[next_idx];

    push(final_positions, pos_curr);
    push(is_anchor, 1);

    // Selbe Straße? Mit einstellbarem Threshold
    int same_street = 0;
    if (name_curr == name_next && int_id_curr == int_id_next) {
        float dir_dot = abs(dot(normalize(dir_curr), normalize(dir_next)));
        if (dir_dot > straight_threshold) {
            same_street = 1;
        }
    }

    if (same_street == 1) continue;

    // Corner berechnen
    float dx = pos_next.x - pos_curr.x;
    float dz = pos_next.z - pos_curr.z;
    float cross_val = dir_curr.x * dir_next.z - dir_curr.z * dir_next.x;

    vector corner_pt;
    int valid_corner = 0;

    if (abs(cross_val) > 0.001) {
        float t = (dx * dir_next.z - dz * dir_next.x) / cross_val;
        corner_pt = pos_curr + t * dir_curr;

        float dist_curr = distance(set(corner_pt.x, 0, corner_pt.z), set(pos_curr.x, 0, pos_curr.z));
        float dist_next = distance(set(corner_pt.x, 0, corner_pt.z), set(pos_next.x, 0, pos_next.z));
        float total_dist = dist_curr + dist_next;

        if (total_dist > 0.001) {
            corner_pt.y = (pos_curr.y * dist_next + pos_next.y * dist_curr) / total_dist;
        } else {
            corner_pt.y = (pos_curr.y + pos_next.y) * 0.5;
        }

        float max_dist = distance(pos_curr, pos_next) * 2.5;
        if (distance(corner_pt, centroid) < max_dist && t > -0.5) {
            valid_corner = 1;
        }
    }

    if (valid_corner == 0) {
        corner_pt = (pos_curr + pos_next) * 0.5;
        corner_pt.y = (pos_curr.y + pos_next.y) * 0.5;
    }

    // Adaptive Corner Segments
    if (corner_radius > 0 && max_segments > 0) {
        vector dir_to_curr = normalize(pos_curr - corner_pt);
        vector dir_to_next = normalize(pos_next - corner_pt);

        float corner_dot = dot(dir_to_curr, dir_to_next);
        float corner_angle = acos(clamp(corner_dot, -1, 1));

        float sharpness = 1.0 - (corner_angle / PI);
        int adaptive_segs = int(lerp(float(min_segments), float(max_segments), sharpness * adaptivity + (1.0 - adaptivity) * 0.5));
        adaptive_segs = clamp(adaptive_segs, min_segments, max_segments);

        float dist_to_curr = distance(corner_pt, pos_curr);
        float dist_to_next = distance(corner_pt, pos_next);

        float eff_radius = corner_radius;
        eff_radius = min(eff_radius, dist_to_curr * 0.8);
        eff_radius = min(eff_radius, dist_to_next * 0.8);

        if (eff_radius > 0.01 && adaptive_segs > 0) {
            vector arc_start = corner_pt + dir_to_curr * eff_radius;
            vector arc_end = corner_pt + dir_to_next * eff_radius;

            arc_start.y = lerp(corner_pt.y, pos_curr.y, eff_radius / max(dist_to_curr, 0.001));
            arc_end.y = lerp(corner_pt.y, pos_next.y, eff_radius / max(dist_to_next, 0.001));

            for (int seg = 0; seg <= adaptive_segs; seg++) {
                float blend = float(seg) / float(adaptive_segs);

                float t0 = (1.0 - blend) * (1.0 - blend);
                float t1 = 2.0 * (1.0 - blend) * blend;
                float t2 = blend * blend;

                vector arc_pt = arc_start * t0 + corner_pt * t1 + arc_end * t2;

                push(final_positions, arc_pt);
                push(is_anchor, 0);
            }
        } else {
            push(final_positions, corner_pt);
            push(is_anchor, 0);
        }
    } else {
        push(final_positions, corner_pt);
        push(is_anchor, 0);
    }
}

// ===== PHASE 6: NUR BOUNDARY POLYGON =====
int nf = len(final_positions);
if (nf < 3) return;

int boundary_pts[];
vector up = set(0,1,0);

for (int i = 0; i < nf; i++) {
    int pt = addpoint(0, final_positions[i]);
    setpointattrib(0, "N", pt, up);
    setpointattrib(0, "is_anchor", pt, is_anchor[i]);
    setpointattrib(0, "cluster_id", pt, my_id);
    push(boundary_pts, pt);
}

int prim = addprim(0, "poly");
for (int i = 0; i < nf; i++) {
    addvertex(0, prim, boundary_pts[i]);
}
setprimattrib(0, "name", prim, "intersection");
setprimattrib(0, "source_int_id", prim, my_id);
setprimattrib(0, "cluster_size", prim, len(cluster_ids));
vector col = set(0.8, 0.8, 0.3);
setprimattrib(0, "Cd", prim, col);

i@intersection_status = 1;
i@final_count = nf;
```

**Parameter:**

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `corner_radius` | 5.0 | Radius der Bezier-Rundung |
| `min_segments` | 1 | Minimum Segmente pro Corner |
| `max_segments` | 5 | Maximum Segmente pro Corner |
| `adaptivity` | 0.7 | Wie stark Winkel die Segments beeinflusst |
| `merge_threshold` | 1.2 | Cluster-Erkennung für nahe Intersections |
| `straight_threshold` | 0.9 | Ab welchem Winkel Corner erstellt wird (0.99 für leichte Kurven) |

---

## Node Graph (aktueller Stand)

```
Lines (major + mud)
        ↓
   [Fuse] 0.01
        ↓
   [Prim Wrangle] set_width_priority
        ↓
   [Point Wrangle] mark_intersections
        ↓
   [Prim Wrangle] intersection_start_end_logic
        ↓
   ┌────┴────┐
   ↓         ↓
[Split]   [Split]
(intersections)  (non-intersections)
   ↓              ↓
[Blast]      [Facet] (unique points)
(points only)      ↓
   ↓         [Prim Wrangle] intersection_cut_out
   │              ↓
   │         [Conform to Terrain]
   │              ↓
   │         [Prim Wrangle] ribbon
   │              ↓
   └──────► [Point Wrangle] intersection_create
                  ↓
             [Divide] (Convex Polygons)
                  ↓
             [Ray] (Terrain Conform)
                  ↓
                DONE
```

---

## TODO

### Phase 5: Finishing
- [ ] 2D Boolean Cut (kleine Straßen unter großen entfernen)
- [ ] Height Blend (kleine Straßen an große anpassen)
- [ ] Bürgersteige aus Edge-Lines
- [ ] Terrain Flattening Mask

### Phase 6: Details
- [ ] Crossings/Zebrastreifen
- [ ] Laternen, Ampeln, parkende Autos
- [ ] Hausflächen/Parzellen

---

## Notizen

- VEX `push()` braucht explizit typisierte Variablen (nicht direkt `point()` Ergebnis)
- Intersection-Polygon: Nur Boundary, kein Center Fan (besser für Terrain-Konformität)
- Divide SOP nach intersection_create für saubere Triangulation
- `straight_threshold = 0.99` für Corners auch bei leichten Kurven
