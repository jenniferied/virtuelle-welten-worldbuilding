# Houdini: Mud-Straßen an Major-Straßen beschneiden

**Datum:** 2026-02-06
**Status:** In Progress
**Houdini Version:** 21.0

## Ziel

Mud-Straßen (ribbons, edge_left, edge_right, intersections) sollen an Major-Straßen beschnitten werden. Rein attributbasiert mit vertikalem Ray-Test, ohne Boolean-Operationen.

## Workflow-Übersicht

```
[mud_ribbons + edges + intersections]          [major_ribbons + major_intersections]
              │                                              │
              ▼                                              ▼
┌────────────────────────────────────┐        ┌──────────────────────────────┐
│ Resample (Subdivide für Präzision) │        │ (unverändert als Input 1)    │
└────────────────────────────────────┘        └──────────────────────────────┘
              │                                              │
              └──────────────────┬───────────────────────────┘
                                 ▼
                   ┌─────────────────────────────────┐
                   │ Point Wrangle                   │
                   │ → vertikaler Ray-Test           │
                   │ → removepoint() wenn inside     │
                   └─────────────────────────────────┘
```

## VEX Code

### 1. Mud an Major beschneiden (Point Wrangle)

```vex
// Point Wrangle - Run Over: Points
// Input 0: mud (ribbons + edges + intersections)
// Input 1: major (ribbons + intersections)

vector ray_origin = set(@P.x, 10000, @P.z);
vector ray_dir = {0, -1, 0};

vector hit_pos, hit_uvw;
int hit = intersect(1, ray_origin, ray_dir * 20000, hit_pos, hit_uvw);

if(hit >= 0) {
    removepoint(0, @ptnum, 1);
}
```

**Funktionsweise:**
- Schießt einen vertikalen Ray von oben (Y=10000) nach unten durch jeden Punkt
- Wenn der Ray die major-Geometrie trifft → Punkt liegt "unter" major → wird gelöscht
- Der dritte Parameter `1` bei `removepoint()` entfernt auch degenerierte Prims

### 2. Major Edges beschneiden (Point Wrangle)

Schneidet "Löcher" in major_edge_left/right wo mud-Straßen anschließen:

```vex
// Point Wrangle - Run Over: Points
// Input 0: major_edge_left + major_edge_right
// Input 1: mud ribbons

vector ray_origin = set(@P.x, 10000, @P.z);
vector ray_dir = {0, -1, 0};

vector hit_pos, hit_uvw;
int hit = intersect(1, ray_origin, ray_dir * 20000, hit_pos, hit_uvw);

if(hit >= 0) {
    removepoint(0, @ptnum, 1);
}
```

### 3. Mud Edges Cleanup (Point Wrangle)

Splittet mud edges wo sie major edges berühren:

```vex
// Point Wrangle - Run Over: Points
// Input 0: mud_edge_left + mud_edge_right
// Input 1: major_edge_left + major_edge_right

float dist = xyzdist(1, @P);

if(dist < chf("threshold")) {  // z.B. 0.01
    removepoint(0, @ptnum, 1);
}
```

## Bekannte Probleme

### Polylines überbrücken Lücken

**Problem:** `removepoint()` löscht Punkte, aber bei Polylines (edges) bleibt das Prim bestehen und "überbrückt" die Lücke zwischen den verbleibenden Punkten.

**Symptom:** Nach dem Löschen sind die edge-Linien nicht mehr resampled, sondern eine gerade Linie über die Lücke.

**Lösungsansätze:**

#### A) Detail Wrangle (langsam bei vielen Prims)

```vex
// Detail Wrangle - Run Over: Detail
// Input 0: edges (mit @inside Attribut vom Point Wrangle)

int num_prims = nprimitives(0);

for(int pr = num_prims - 1; pr >= 0; pr--) {
    int pts[] = primpoints(0, pr);
    if(len(pts) < 2) continue;

    int segment[];
    foreach(int pt; pts) {
        if(point(0, "inside", pt) == 0) {
            append(segment, pt);
        } else {
            if(len(segment) >= 2) {
                addprim(0, "polyline", segment);
            }
            segment = {};
        }
    }
    if(len(segment) >= 2) {
        addprim(0, "polyline", segment);
    }
    removeprim(0, pr, 0);
}

// Orphans löschen
for(int pt = npoints(0) - 1; pt >= 0; pt--) {
    if(point(0, "inside", pt) == 1) {
        removepoint(0, pt);
    }
}
```

#### B) Node-basiert (schneller)

1. **Point Wrangle:** `@inside` markieren (nicht löschen)
2. **Convert Line SOP:** Jede Edge wird eigenes Prim
3. **Primitive Wrangle:**
```vex
int pts[] = primpoints(0, @primnum);
int in0 = point(0, "inside", pts[0]);
int in1 = point(0, "inside", pts[1]);

if(in0 == 1 || in1 == 1) {
    removeprim(0, @primnum, 1);
}
```
4. **Join SOP:** Verbindet Segmente wieder

#### C) Edges nach dem Schneiden neu generieren (empfohlen)

Statt edges separat zu schneiden:
- Nur die mud ribbons schneiden (funktioniert zuverlässig)
- Edges DANACH aus den geschnittenen ribbons generieren (PolyExpand2D, Offset, Sweep)
- Bürgersteige entstehen automatisch korrekt

## VEX Funktionen Referenz

| Funktion | Beschreibung |
|----------|--------------|
| `intersect(input, origin, dir, hit_pos, hit_uvw)` | Ray-Test gegen Geometry, returned Prim-Index oder -1 |
| `xyzdist(input, pos)` | Kürzeste Distanz zur Geometry |
| `removepoint(input, ptnum, remove_prims)` | Löscht Punkt, optional auch degenerierte Prims |
| `removeprim(input, primnum, remove_points)` | Löscht Prim, optional auch unbenutzte Punkte |
| `primpoints(input, primnum)` | Array der Punkt-Indices eines Prims |
| `addprim(input, type, pts[])` | Erstellt neues Prim aus Punkt-Array |

## Wichtige Einstellungen

- **Resample vor dem Wrangle:** Length 0.05-0.1 für präzisen Cut
- **Input 1 muss Flächen haben:** `intersect()` braucht Polygone mit Area, nicht nur Linien
- **Ray-Höhe:** 10000 sollte über allem Terrain liegen
- **Ray-Länge:** 20000 deckt auch tiefe Geometrie ab

## Nächste Schritte

- [ ] Entscheidung: Edges separat schneiden oder aus ribbons neu generieren
- [ ] Bürgersteig-Generierung aus geschnittenen ribbons testen
- [ ] Performance-Optimierung bei vielen Prims
