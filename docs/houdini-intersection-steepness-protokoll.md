# Houdini Intersection & Terrain Protokoll

**Datum:** 2026-02-06
**Kontext:** Straßenkreuzungen, HeightField-Anpassungen, Smoothing

---

## 1. Intersection Create mit Steepness Compensation (v8)

**Problem:** Bei steilen Straßenübergängen entstanden überlappende NGons.

**Lösung:** Steepness Compensation erkennt steile Winkel und zieht Corner-Punkte näher zur sicheren Mitte.

### Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `corner_radius` | - | Radius für Corner-Kurven |
| `min_segments` | - | Minimum Corner-Segmente |
| `max_segments` | - | Maximum Corner-Segmente |
| `adaptivity` | - | Adaptive Segmentierung |
| `merge_threshold` | - | Cluster-Merge-Schwelle |
| `straight_threshold` | - | Gerade-Erkennung |
| `steepness_threshold` | 0.15 | Ab welchem Winkel Compensation greift |
| `steepness_falloff` | 0.5 | Übergangs-Kurve (höher = weicher) |

### Code (Point Wrangle)

```vex
// intersection_create Point Wrangle v8 (mit Steepness Compensation)
// Input 0: Intersection points (mit int_id)
// Input 1: Ribbon geometry (mit edge points)
// Input 2: Original cut lines (mit start_int_id, end_int_id, width)

int my_id = i@int_id;

// ===== PARAMETER =====
float corner_radius = chf("corner_radius");
int min_segments = chi("min_segments");
int max_segments = chi("max_segments");
float adaptivity = chf("adaptivity");
float merge_threshold = chf("merge_threshold");
float straight_threshold = chf("straight_threshold");
float steepness_threshold = chf("steepness_threshold");
float steepness_falloff = chf("steepness_falloff");

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

// ===== PHASE 5: POLYGON MIT ADAPTIVE CORNERS + STEEPNESS COMPENSATION =====
vector final_positions[];
int is_anchor[];
string final_street_names[];
int final_edge_sides[];
int corner_start_indices[];

for (int i = 0; i < count; i++) {
    int curr_idx = sorted_indices[i];
    int next_idx = sorted_indices[(i + 1) % count];

    vector pos_curr = edge_positions[curr_idx];
    vector pos_next = edge_positions[next_idx];

    string name_curr = edge_street_names[curr_idx];
    string name_next = edge_street_names[next_idx];

    vector dir_curr = edge_dirs[curr_idx];
    vector dir_next = edge_dirs[next_idx];

    int side_curr = edge_sides[curr_idx];
    int side_next = edge_sides[next_idx];

    int int_id_curr = edge_int_ids[curr_idx];
    int int_id_next = edge_int_ids[next_idx];

    // Anchor-Punkt
    push(final_positions, pos_curr);
    push(is_anchor, 1);
    push(final_street_names, name_curr);
    push(final_edge_sides, side_curr);

    // Selbe Straße?
    int same_street = 0;
    if (name_curr == name_next && int_id_curr == int_id_next) {
        float dir_dot = abs(dot(normalize(dir_curr), normalize(dir_next)));
        if (dir_dot > straight_threshold) {
            same_street = 1;
        }
    }

    if (same_street == 1) continue;

    push(corner_start_indices, len(final_positions) - 1);

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

    // ===== STEEPNESS COMPENSATION =====
    vector dir_curr_norm = normalize(dir_curr);
    vector dir_next_norm = normalize(dir_next);
    float edge_dot = dot(dir_curr_norm, dir_next_norm);

    float local_corner_radius = corner_radius;

    if (edge_dot < -steepness_threshold) {
        float steep_factor = fit(edge_dot, -1.0, -steepness_threshold, 0.0, 1.0);
        steep_factor = pow(steep_factor, steepness_falloff);

        vector safe_corner = (pos_curr + pos_next) * 0.5;
        safe_corner.y = (pos_curr.y + pos_next.y) * 0.5;

        corner_pt = lerp(safe_corner, corner_pt, steep_factor);
        local_corner_radius *= steep_factor;
    }

    // ===== OVERLAP PREVENTION =====
    if (len(final_positions) >= 2) {
        vector last_pos = final_positions[len(final_positions) - 1];
        vector prev_pos = final_positions[len(final_positions) - 2];

        vector edge_dir = normalize(last_pos - prev_pos);
        vector to_corner = corner_pt - last_pos;
        vector edge_normal = set(-edge_dir.z, 0, edge_dir.x);

        float side_check = dot(to_corner, edge_normal);
        vector to_centroid = centroid - last_pos;
        float centroid_side = dot(to_centroid, edge_normal);

        if (sign(side_check) != sign(centroid_side) && abs(side_check) > 0.01) {
            corner_pt = last_pos + to_corner - edge_normal * side_check;
            corner_pt = lerp(corner_pt, (pos_curr + pos_next) * 0.5, 0.5);
        }
    }

    // ===== MAX DISTANCE CLAMP =====
    float max_corner_dist = distance(pos_curr, pos_next) * 1.5;
    float actual_dist = distance(corner_pt, centroid);
    if (actual_dist > max_corner_dist) {
        vector dir_to_corner = normalize(corner_pt - centroid);
        corner_pt = centroid + dir_to_corner * max_corner_dist;
    }

    // Adaptive Corner Segments
    if (local_corner_radius > 0 && max_segments > 0) {
        vector dir_to_curr = normalize(pos_curr - corner_pt);
        vector dir_to_next = normalize(pos_next - corner_pt);

        float corner_dot = dot(dir_to_curr, dir_to_next);
        float corner_angle = acos(clamp(corner_dot, -1, 1));

        float sharpness = 1.0 - (corner_angle / PI);
        int adaptive_segs = int(lerp(float(min_segments), float(max_segments), sharpness * adaptivity + (1.0 - adaptivity) * 0.5));
        adaptive_segs = clamp(adaptive_segs, min_segments, max_segments);

        float dist_to_curr = distance(corner_pt, pos_curr);
        float dist_to_next = distance(corner_pt, pos_next);

        float eff_radius = local_corner_radius;
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
                push(final_street_names, "corner");
                push(final_edge_sides, -1);
            }
        } else {
            push(final_positions, corner_pt);
            push(is_anchor, 0);
            push(final_street_names, "corner");
            push(final_edge_sides, -1);
        }
    } else {
        push(final_positions, corner_pt);
        push(is_anchor, 0);
        push(final_street_names, "corner");
        push(final_edge_sides, -1);
    }
}

// ===== PHASE 6: BOUNDARY POLYGON =====
int nf = len(final_positions);
if (nf < 3) return;

int boundary_pts[];
vector up = set(0,1,0);

for (int i = 0; i < nf; i++) {
    int pt = addpoint(0, final_positions[i]);
    setpointattrib(0, "N", pt, up);
    setpointattrib(0, "is_anchor", pt, is_anchor[i]);
    setpointattrib(0, "cluster_id", pt, my_id);
    setpointattrib(0, "street_name", pt, final_street_names[i]);
    setpointattrib(0, "edge_side", pt, final_edge_sides[i]);
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

// ===== PHASE 7: CORNER CURVES =====
for (int i = 0; i < nf; i++) {
    if (is_anchor[i] != 1) continue;

    int next_anchor = -1;
    for (int j = 1; j < nf; j++) {
        int idx = (i + j) % nf;
        if (is_anchor[idx] == 1) {
            next_anchor = idx;
            break;
        }
    }

    if (next_anchor < 0) continue;

    string name_from = final_street_names[i];
    string name_to = final_street_names[next_anchor];
    int side_from = final_edge_sides[i];
    int side_to = final_edge_sides[next_anchor];

    if (name_from == name_to) continue;

    string side_str_from = (side_from == 0) ? "left" : "right";
    string side_str_to = (side_to == 0) ? "left" : "right";
    string from_edge = name_from + "_edge_" + side_str_from;
    string to_edge = name_to + "_edge_" + side_str_to;

    int curve_pts[];
    for (int j = 0; j <= nf; j++) {
        int idx = (i + j) % nf;
        push(curve_pts, boundary_pts[idx]);
        if (idx == next_anchor) break;
    }

    if (len(curve_pts) >= 2) {
        int curve_prim = addprim(0, "polyline", curve_pts);
        setprimattrib(0, "name", curve_prim, "corner_curve");
        setprimattrib(0, "Cd", curve_prim, set(0.7, 0.2, 0.8));
        setprimattrib(0, "int_id", curve_prim, my_id);
        setprimattrib(0, "from_edge", curve_prim, from_edge);
        setprimattrib(0, "to_edge", curve_prim, to_edge);
        setprimattrib(0, "from_street", curve_prim, name_from);
        setprimattrib(0, "to_street", curve_prim, name_to);
    }
}

i@intersection_status = 1;
i@final_count = nf;
```

---

## 2. Overlap Remove (Primitive Wrangle)

**Problem:** Trotz Steepness Compensation entstehen selten noch überlappende Polygone.

**Lösung:** Separates Wrangle das überlappende Intersection-Polygone erkennt und das kleinere löscht.

### Code (Primitive Wrangle, nach intersection_create)

```vex
// overlap_remove Primitive Wrangle
// Input 0: Intersection geometry (nach intersection_create)

string prim_name = s@name;
if (prim_name != "intersection") return;

int my_prim = @primnum;
vector my_center = @P;

int my_pts[] = primpoints(0, my_prim);
int my_ptcount = len(my_pts);
if (my_ptcount < 3) return;

vector my_min = set(1e9, 1e9, 1e9);
vector my_max = set(-1e9, -1e9, -1e9);
vector my_positions[];

for (int i = 0; i < my_ptcount; i++) {
    vector pos = point(0, "P", my_pts[i]);
    push(my_positions, pos);
    my_min = min(my_min, pos);
    my_max = max(my_max, pos);
}

// Fläche (Shoelace)
float my_area = 0;
for (int i = 0; i < my_ptcount; i++) {
    vector p0 = my_positions[i];
    vector p1 = my_positions[(i + 1) % my_ptcount];
    my_area += (p0.x * p1.z - p1.x * p0.z);
}
my_area = abs(my_area) * 0.5;

int num_prims = nprimitives(0);
int should_delete = 0;

for (int other = 0; other < num_prims; other++) {
    if (other == my_prim) continue;

    string other_name = prim(0, "name", other);
    if (other_name != "intersection") continue;

    int other_pts[] = primpoints(0, other);
    int other_ptcount = len(other_pts);
    if (other_ptcount < 3) continue;

    vector other_min = set(1e9, 1e9, 1e9);
    vector other_max = set(-1e9, -1e9, -1e9);
    vector other_positions[];

    for (int i = 0; i < other_ptcount; i++) {
        vector pos = point(0, "P", other_pts[i]);
        push(other_positions, pos);
        other_min = min(other_min, pos);
        other_max = max(other_max, pos);
    }

    // BBox Check
    if (my_max.x < other_min.x || my_min.x > other_max.x) continue;
    if (my_max.z < other_min.z || my_min.z > other_max.z) continue;

    // Edge Intersection Test
    int has_edge_intersection = 0;

    for (int i = 0; i < my_ptcount && has_edge_intersection == 0; i++) {
        vector a1 = my_positions[i];
        vector a2 = my_positions[(i + 1) % my_ptcount];

        for (int j = 0; j < other_ptcount && has_edge_intersection == 0; j++) {
            vector b1 = other_positions[j];
            vector b2 = other_positions[(j + 1) % other_ptcount];

            float d1x = a2.x - a1.x;
            float d1z = a2.z - a1.z;
            float d2x = b2.x - b1.x;
            float d2z = b2.z - b1.z;

            float cross = d1x * d2z - d1z * d2x;
            if (abs(cross) < 1e-8) continue;

            float dx = b1.x - a1.x;
            float dz = b1.z - a1.z;

            float t = (dx * d2z - dz * d2x) / cross;
            float u = (dx * d1z - dz * d1x) / cross;

            if (t > 0.01 && t < 0.99 && u > 0.01 && u < 0.99) {
                has_edge_intersection = 1;
            }
        }
    }

    // Point-in-Polygon Tests
    int my_center_in_other = 0;
    int other_center_in_my = 0;

    if (has_edge_intersection == 0) {
        int crossings = 0;
        for (int j = 0; j < other_ptcount; j++) {
            vector p1 = other_positions[j];
            vector p2 = other_positions[(j + 1) % other_ptcount];

            if ((p1.z <= my_center.z && p2.z > my_center.z) ||
                (p2.z <= my_center.z && p1.z > my_center.z)) {
                float t = (my_center.z - p1.z) / (p2.z - p1.z);
                float x_intersect = p1.x + t * (p2.x - p1.x);
                if (my_center.x < x_intersect) crossings++;
            }
        }
        my_center_in_other = (crossings % 2 == 1) ? 1 : 0;

        vector other_center = set(0,0,0);
        for (int j = 0; j < other_ptcount; j++) {
            other_center += other_positions[j];
        }
        other_center /= float(other_ptcount);

        crossings = 0;
        for (int j = 0; j < my_ptcount; j++) {
            vector p1 = my_positions[j];
            vector p2 = my_positions[(j + 1) % my_ptcount];

            if ((p1.z <= other_center.z && p2.z > other_center.z) ||
                (p2.z <= other_center.z && p1.z > other_center.z)) {
                float t = (other_center.z - p1.z) / (p2.z - p1.z);
                float x_intersect = p1.x + t * (p2.x - p1.x);
                if (other_center.x < x_intersect) crossings++;
            }
        }
        other_center_in_my = (crossings % 2 == 1) ? 1 : 0;
    }

    if (has_edge_intersection == 1 || my_center_in_other == 1 || other_center_in_my == 1) {
        float other_area = 0;
        for (int j = 0; j < other_ptcount; j++) {
            vector p0 = other_positions[j];
            vector p1 = other_positions[(j + 1) % other_ptcount];
            other_area += (p0.x * p1.z - p1.x * p0.z);
        }
        other_area = abs(other_area) * 0.5;

        if (my_area < other_area) {
            should_delete = 1;
            break;
        } else if (abs(my_area - other_area) < 0.001 && my_prim > other) {
            should_delete = 1;
            break;
        }
    }
}

if (should_delete == 1) {
    removeprim(0, my_prim, 1);
}
```

---

## 3. HeightField Adapt to Buildings (Volume Wrangle)

**Problem:** HeightField soll sich an Gebäude anpassen, mit adaptivem Threshold basierend auf Höhendifferenz.

**Lösung:** Gebäude auf Bodenniveau → kleiner Blur. Gebäude auf Stelzen → großer Blur/Übergang.

### Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `base_threshold` | 0.5 | Minimaler Einflussbereich |
| `max_threshold` | 5.0 | Maximaler bei Stelzen |
| `diff_scale` | 2.0 | Skalierung durch Höhendiff |
| `drop` | 0.1 | Absenkung unter Gebäude |
| `blur_strength` | 0.7 | Anteil Übergangszone |
| `blur_falloff` | 2.0 | Kurvenform |

### Code (Volume Wrangle, Volumes to Write: height)

```vex
// Input 0: HeightField
// Input 1: Building Polygons (mit @building_height)

float drop = chf("drop");
float base_threshold = chf("base_threshold");
float max_threshold = chf("max_threshold");
float diff_scale = chf("diff_scale");
float blur_strength = chf("blur_strength");
float blur_falloff = chf("blur_falloff");

float smooth_step(float edge0; float edge1; float x) {
    float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

int hit_prim;
vector uv;
vector sample_pos = set(@P.x, 1000, @P.z);
float dist = xyzdist(1, sample_pos, hit_prim, uv);

if (hit_prim < 0) return;

float building_h = prim(1, "building_height", hit_prim);
vector closest_pos = primuv(1, "P", hit_prim, uv);

float horiz_dist = distance(set(@P.x, 0, @P.z), set(closest_pos.x, 0, closest_pos.z));

float height_diff = abs(building_h - drop - @height);

float adaptive_threshold = base_threshold + height_diff * diff_scale;
adaptive_threshold = clamp(adaptive_threshold, base_threshold, max_threshold);

if (horiz_dist > adaptive_threshold) return;

float blend = horiz_dist / adaptive_threshold;
float blur_blend = pow(blend, blur_falloff);
blur_blend = smooth_step(0, 1, blur_blend);

float target_height = building_h - drop;
float core_size = 1.0 - blur_strength;

if (blend < core_size) {
    @height = target_height;
} else {
    float transition_blend = (blend - core_size) / blur_strength;
    transition_blend = smooth_step(0, 1, transition_blend);
    transition_blend = pow(transition_blend, blur_falloff);
    @height = lerp(target_height, @height, transition_blend);
}
```

---

## 4. Z-Smooth (Primitive Wrangle)

**Problem:** Primitives in Z-Achse smoothen, ohne Endpoints zu verändern.

### Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `iterations` | 10 | Mehr = glatter |
| `strength` | 0.5 | Stärke pro Iteration |

### Code (Primitive Wrangle)

```vex
int iterations = chi("iterations");
float strength = chf("strength");

int pts[] = primpoints(0, @primnum);
int num_pts = len(pts);

if (num_pts < 3) return;

float z_values[];
for (int i = 0; i < num_pts; i++) {
    vector pos = point(0, "P", pts[i]);
    push(z_values, pos.z);
}

for (int iter = 0; iter < iterations; iter++) {
    float new_z[];

    for (int i = 0; i < num_pts; i++) {
        if (i == 0 || i == num_pts - 1) {
            push(new_z, z_values[i]);
            continue;
        }

        float avg = (z_values[i - 1] + z_values[i + 1]) * 0.5;
        float smoothed = lerp(z_values[i], avg, strength);
        push(new_z, smoothed);
    }

    z_values = new_z;
}

for (int i = 1; i < num_pts - 1; i++) {
    int pt = pts[i];
    vector pos = point(0, "P", pt);
    pos.z = z_values[i];
    setpointattrib(0, "P", pt, pos);
}
```

---

## 5. HeightField Conform mit Blur (Volume Wrangle)

**Problem:** HeightField an Geometrie anpassen mit sanftem Übergang zum Original-Terrain.

### Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|--------------|
| `drop` | 0.1 | Absenkung |
| `blur_radius` | 5.0 | Übergangszone in Metern |
| `blur_falloff` | 2.0 | Kurvenform |

### Code (Volume Wrangle, Volumes to Write: height)

```vex
// Input 0: HeightField
// Input 1: Conform Geometry

float drop = chf("drop");
float blur_radius = chf("blur_radius");
float blur_falloff = chf("blur_falloff");

float smooth_step(float edge0; float edge1; float x) {
    float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}

vector ray_start = set(@P.x, 10000, @P.z);
vector ray_dir = {0, -1, 0};

vector hit_pos;
vector hit_uvw;
int hit_prim = intersect(1, ray_start, ray_dir * 20000, hit_pos, hit_uvw);

float original_height = @height;

if (hit_prim >= 0) {
    @height = hit_pos.y - drop;
    return;
}

if (blur_radius <= 0) return;

vector sample_pos = set(@P.x, 0, @P.z);
int closest_prim;
vector closest_uv;
float dist = xyzdist(1, sample_pos, closest_prim, closest_uv);

if (closest_prim < 0 || dist > blur_radius) return;

vector closest_pos = primuv(1, "P", closest_prim, closest_uv);
float target_height = closest_pos.y - drop;

float blend = dist / blur_radius;
blend = pow(blend, blur_falloff);
blend = smooth_step(0, 1, blend);

@height = lerp(target_height, original_height, blend);
```

---

## 6. HeightField Caching

**Problem:** Normaler File Cache gibt leeres Ergebnis bei HeightFields.

**Lösungen:**

| Methode | Format | Beschreibung |
|---------|--------|--------------|
| HeightField File Node | `.exr`, `.tiff` | Empfohlen, erhält alle Layers |
| File Cache | `.bgeo.sc` | Funktioniert für Volumes |
| File Cache | `.vdb` | Alternative für Volumes |
| Labs HeightField Quick Cache | auto | Falls Labs installiert |

**Wichtig:** Nicht `.abc` oder `.obj` verwenden - diese unterstützen keine Volumes.
