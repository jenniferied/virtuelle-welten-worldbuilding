# Houdini Session Protokoll — 2026-02-06

Fenster-Generierung, Garage-Wrangle Fixes, Wand-Selektion.

---

## 1. Sowjetische Wohnbaustile (Recherche)

Drei Haupt-Epochen für Worldbuilding-Referenz:

| Stil | Zeitraum | Merkmale |
|------|----------|----------|
| **Stalinki** | 1930er–1950er | Neoklassisch, hohe Decken (2.8–3.2m), Stuck, Säulen, massiv |
| **Khrushchyovki** | späte 1950er–1960er | Billig, Plattenbau, 2.5m Decken, ~5m² Küche, max 5 Stockwerke |
| **Brezhnevki** | 1960er–1980er | Höher (9–17 Stockwerke), Aufzüge, größere Wohnungen, besser isoliert |

---

## 2. Fenster-Generierung (Konzept)

### Ansatz: Edge Dissolve für Fensterformen

- **Grid SOP** → Subdivide → ergibt + Muster an Kreuzungen
- **Dissolve SOP** → Edge entfernen → + wird zu T-Form
- Edge-Spezifikation im Group-Feld: `p4-6` (Punkt 4 zu Punkt 6)
- Mehrere Edges: `p4-6 p3-7` (space-separated)

### Alternative Ansätze

1. **Profil-basiert**: Curve SOP (Fenster-Querschnitt) → PolyExtrude → Copy to Points
2. **Boolean**: Solid Wall → Box-Cutouts per Copy to Points → Boolean Subtract
3. **PolyExtrude Inset**: Merged Polygon selektieren → PolyExtrude mit negativem Distance + Inset für Rahmen

---

## 3. Garage Türen Wrangle — Bugfixes & Features

### 3.1 Bugfix: Pfeiler-zwischen-Türen Loop

```vex
// VORHER (Bug): setzte Attribut auf falsches Primitive
setprimattrib(0, "is_wall", pr_right, 1);

// NACHHER (Fix): korrektes Primitive
setprimattrib(0, "is_wall", pr, 1);
```

### 3.2 Attribut-Umbenennung

`lgth_pnt` → `light_pnt` (konsistenterer Name)

### 3.3 Point-Attribut auf neuen Punkten im Primitive Wrangle

**Problem:** `setpointattrib` auf Punkte die mit `addpoint` im selben Primitive Wrangle erstellt werden ist unzuverlässig — deferred Writes überschreiben sich.

**Lösung:**
```vex
// Ganz oben im Wrangle (vor allen returns):
addpointattrib(0, "light_pnt", 0);

// Bei der Zuweisung — expliziter "set" Modus:
setpointattrib(0, "light_pnt", light_pt, 1, "set");
```

**Alternative:** Separater Point Wrangle danach mit `pointprims()`:
```vex
if(len(pointprims(0, @ptnum)) == 0)
    i@light_pnt = 1;
```

> **Hinweis:** `numprimitivesfor` und `primitivesforpoint` existieren NICHT in VEX.
> Die korrekte Funktion ist `pointprims(geometry, ptnum)` → gibt int-Array zurück.

### 3.4 Licht-Rotation

Neuer Parameter `light_rotation` (Vector3) rotiert die Licht-Normalen im lokalen Wand-Koordinatensystem:

```vex
vector local_x = wall_dir;    // horizontal entlang Wand
vector local_y = {0, 1, 0};   // vertikal
vector local_z = wall_N;      // weg von Wand

matrix3 rot = ident();
rotate(rot, radians(light_rot.x), local_x);  // hoch/runter
rotate(rot, radians(light_rot.y), local_y);   // links/rechts
rotate(rot, radians(light_rot.z), local_z);   // roll

vector light_N = wall_N * rot;
```

---

## 4. Wand-Selektion (Group by Normal)

### Problem

"Alle Seitenwände selektieren" funktioniert NICHT mit Group SOP → Normal Tab, weil ein einzelner Direction-Vektor + Spread Angle nur einen Kegel definiert — nicht alle horizontalen Richtungen gleichzeitig.

### Lösung: Attribute Wrangle

```vex
// Primitive Wrangle
if(abs(@N.y) < 0.5)
    setprimgroup(0, "walls", @primnum, 1);
```

> **Hinweis:** Group Expression SOP mit `abs(@N.y) < 0.3` kann Point-Normals statt Prim-Normals lesen — Wrangle ist zuverlässiger.

### Debug: Normals visualisieren

```vex
// Zeigt Normal-Richtung als Farbe: R=X, G=Y, B=Z
v@Cd = abs(@N);
```

- Grün = nach oben/unten (Boden/Decke)
- Rot/Blau = seitlich (Wände)
- Schwarz = keine Normals vorhanden

### Fehlende Wände

Falls einzelne Wände trotz korrektem Threshold fehlen: Group-Feld auf dem Wrangle-Node prüfen — ein alter Gruppen-Filter kann Primitives überspringen.

---

## Aktualisierte Output-Attribute

| Attribut | Typ | Beschreibung |
|----------|-----|--------------|
| `is_garage_wall` | int (prim) | 1 = Garage-Wand |
| `is_door` | int (prim) | 1 = Tür-Face |
| `is_wall` | int (prim) | 1 = Wand-Face (generiert) |
| `light_pnt` | int (point) | 1 = Licht-Punkt |

---

## VEX Learnings

- `addpointattrib()` vor `setpointattrib()` wenn Attribute in Primitive Wrangles auf neuen Punkten gesetzt werden
- `"set"` als 5. Parameter bei `setpointattrib` verhindert Merge-Konflikte
- `pointprims(0, @ptnum)` ist die korrekte Funktion für "welche Prims nutzen diesen Punkt"
- Group Expression kann Point-Normals statt Prim-Normals lesen → Wrangle bevorzugen
- Dissolve SOP Edge-Syntax: `p4-6` (Punkt-Punkt mit p-Prefix)

---

## 5. Blast SOP mit Attribut-Expressions

### Syntax für Integer-Attribute

```
@lgth_pnt==0    // Alles mit Wert 0 selektieren
@lgth_pnt==1    // Alles mit Wert 1 selektieren
@lgth_pnt!=1    // Alles OHNE Wert 1 selektieren
```

### Delete Non Selected

- **ON**: Löscht alles was NICHT im Group-Feld steht
- **OFF**: Löscht alles was IM Group-Feld steht

**Beispiel:** "Behalte nur `lgth_pnt==1`":
- `@lgth_pnt==1` mit Delete Non Selected **ON**
- ODER `@lgth_pnt==0` mit Delete Non Selected **OFF**

### Wichtig: Group Type muss zum Attribut passen

Wenn Blast nichts oder alles löscht:
1. Prüfen ob Attribut auf **Points** oder **Primitives** liegt (Spreadsheet)
2. **Group Type** in Blast auf denselben Typ setzen

---

## 6. Foreach Loop — Attribut-Debugging

### Problem: Attribut existiert im Loop, aber Blast danach findet nichts

**Debug-Check:** Null SOP nach Foreach End → Spreadsheet öffnen → Attribut vorhanden?

Falls Attribut fehlt: Im **Foreach End** unter "Attributes from Pieces" das Attribut listen oder `*` setzen.

Falls Attribut vorhanden: Group Type in Blast prüfen (siehe oben).

---

## 7. Unreal Engine — Lighting Limits

### Statische Lights (gebacken)
- Praktisch unbegrenzt (tausende möglich)
- Kosten nur Lightmap-Speicher und Bake-Zeit

### Dynamische Point Lights
| Rendering | Limit |
|-----------|-------|
| Deferred | ~100-500 sichtbare gleichzeitig |
| Forward | Hard limit 8-16 pro Objekt |
| Lumen (UE5) | ~50-100 bevor Performance einbricht |

### Performance-Strategie für viele Lichter
- **Emissive Materials + Bloom** statt echte Lights für Deko
- Wenige echte Lights + viele Fake-Emissives
- Statisch baken wo möglich

---

## 8. Houdini Engine — Blueprint Instancing in Unreal

### Blueprint per Attribut instanziieren

**Attribute Create SOP:**

| Feld | Wert |
|------|------|
| Name | `unreal_instance` |
| Class | Point |
| Type | String |
| String Value | `/Game/Blueprints/BP_StreetLight` |

Oder als **Wrangle:**
```vex
s@unreal_instance = "/Game/Blueprints/BP_StreetLight";
```

### Hierarchical Instanced Static Mesh (HISM)

Für tausende Meshes mit einem Draw Call:

| Attribut | Typ | Wert |
|----------|-----|------|
| `unreal_instance` | String | `/Game/Meshes/SM_StreetLight` |
| `unreal_hierarchical_instancer` | Integer | `1` |

### Hinweis zu Lights in Blueprints

Lights in Blueprints werden trotzdem einzeln gespawnt — kein Instancing möglich. Strategie:
1. Mesh instanziieren (HISM)
2. Nur nächste Lights zur Kamera aktiv
3. Rest mit Emissive faken
