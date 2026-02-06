# Houdini OSM Building Walls & Foundation

VEX-Wrangles für Wand-Bereinigung und Foundation-Generierung bei OSM-Buildings.

## Übersicht

```
[OSM Buildings]
    → [Extrude / Wall Modules]
    → [Primitive Wrangle: blast_non_connected] — äußere Ränder löschen
    → [Facet > Unique Points + Connectivity] — Buildings separieren
    → [Floor Plane + Primitive Wrangle: foundation] — Foundation-Gruppe
    → [Extrude SOP auf foundation-Gruppe]
```

---

## 1. Äußere Ränder löschen (Primitive Wrangle)

**Ziel:** Dünne Rand-Primitives an Z-Min/Z-Max entfernen, aber Vorder-/Rückwände (X-Richtung) erhalten.

**Run over:** Primitives

```vex
vector bmin = getbbox_min(0);
vector bmax = getbbox_max(0);

float tol = 0.001;

int pts[] = primpoints(0, @primnum);
int all_on_edge = 1;

foreach (int pt; pts) {
    vector pos = point(0, "P", pt);

    if (pos.z > bmin.z + tol && pos.z < bmax.z - tol) {
        all_on_edge = 0;
        break;
    }
}

// Nur löschen wenn am Z-Rand UND Normale NICHT in X-Richtung
if (all_on_edge && abs(@N.x) < 0.5)
    i@group_blast_non_connected = 1;
```

**Logik:**
- Prüft ob **alle** Punkte eines Prims am Z-Rand der BBox liegen
- Faces mit Normale in ±X (Vorder-/Rückwand) werden nie gelöscht
- Danach **Blast SOP** mit Gruppe `blast_non_connected`

**Iterationen:**
1. Erster Ansatz: nur Z-Boundary-Check → löschte auch Wandflächen
2. Z-Thickness-Check hinzugefügt → unnötig, da alle gleich ausgerichtet
3. "Alle Punkte am Rand"-Check → löschte immer noch Vorder-/Rückwand
4. Normal-Check (`abs(@N.x) < 0.5`) hinzugefügt → finale Lösung

---

## 2. OSM Buildings separieren

**Problem:** Connectivity gruppiert separate Buildings zusammen, weil Edges sich berühren.

**Lösung — Reihenfolge ist entscheidend:**
1. **Fuse SOP** (Punkte pro Gebäude mergen)
2. **Connectivity SOP** (class per Building)
3. **Facet SOP** → Unique Points (erst danach separieren)

**Falsche Reihenfolge** (Facet vor Connectivity) führt dazu, dass Buildings trotzdem als connected gelten.

**Alternative:** Falls OSM-Daten ein `@osm_id` oder `@name` Attribut haben, direkt danach splitten statt Connectivity.

---

## 3. Foundation-Generierung (Primitive Wrangle)

**Ziel:** Wenn die Höhendifferenz der gerayten Punkte einen Schwellenwert überschreitet, Floor Plane als Foundation-Gruppe markieren.

**Setup:**
- Input 0: Floor Plane
- Input 1: Resampled + Rayed + Sorted Points

**Run over:** Primitives

```vex
float threshold = ch("threshold");

vector bmin = getbbox_min(1);
vector bmax = getbbox_max(1);

float ydiff = bmax.y - bmin.y;

if (ydiff > threshold) {
    i@group_foundation = 1;
    f@height_diff = ydiff;
}
```

**Parameter:** `threshold` → Zahnrad → Create Spare Parameters für Slider

**Danach:** Extrude SOP auf Gruppe `foundation`, Distance: `-@height_diff`

---

## 4. Fehlerbehebung

### "Invalid attribute specification: no match for __sourcevtx"
- Attribute Delete sucht Attribute die nicht (mehr) existieren
- **Fix:** Pattern auf `__source*` ändern, oder Error-Level auf "Warn" setzen

### "Pattern expansion reached iteration limit of 1000"
- Compile Block oder For-Each Loop mit fehlerhaftem Pattern
- **Check:** compile_begin/compile_end Paare, For-Each Referenzen, Iteration-Limit testweise reduzieren
