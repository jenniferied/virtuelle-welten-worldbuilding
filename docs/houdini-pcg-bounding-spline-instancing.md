# Houdini PCG Bounding Splines & Building Instancing

Protokoll: PCG Bounding Splines aus Houdini nach Unreal bringen + Buildings als separate Instanzen ausgeben.

---

## 1. PCG Bounding Spline aus Houdini (via Houdini Engine)

### Ansatz A: HoudiniPCGTranslator Plugin (empfohlen)

Community-Plugin für direkte PCG-Datenübertragung ohne Datei-Export.

- **Repo:** https://github.com/AdrianPanGithub/HoudiniPCGTranslator
- **Voraussetzung:** UE 5.6+
- **Unterstützte PCG-Typen:** PCGPointData, PCGSplineData, PCGDynamicMeshData (UE 5.5+)

#### Node Graph

```
Curve SOP → Resample SOP → Attrib Wrangle → Output (null)
```

#### Curve SOP

- Primitive Type: `Polygon`
- Kurve im Viewport zeichnen (G = Draw Mode)
- **Kurve schließen** — Startpunkt klicken, Shift+Enter, oder Close Curve Button

#### Resample SOP

- Maximum Segments: `20`–`50` (für Bounding reicht das)
- Oder Maximum Segment Length: `1.0`

#### Attrib Wrangle (Run Over: Points)

```vex
// Geschlossene Spline = Bounding Region
i@curve_closed = 1;

// Tangenten automatisch berechnen
int prev = (@ptnum - 1 + npoints(0)) % npoints(0);
int next = (@ptnum + 1) % npoints(0);
vector p_prev = point(0, "P", prev);
vector p_next = point(0, "P", next);
vector tangent = normalize(p_next - p_prev);
float tangent_scale = distance(p_prev, p_next) * 0.33;

v@unreal_spline_point_arrive_tangent = tangent * tangent_scale;
v@unreal_spline_point_leave_tangent  = tangent * tangent_scale;

// PCG Tags zum Filtern im PCG Graph
s[]@unreal_pcg_tags = array("BoundingSpline");
```

#### Unreal-Seite (mit HoudiniPCGTranslator)

1. Plugin in `Plugins/` Ordner installieren
2. PCG Graph → HDA Node → HDA auswählen
3. Output ist `PCGSplineData` → in Spline Sampler Node verdrahten
4. Spline Sampler: Shape = `Spline`, Sampling Mode = `Interior`
5. Alles downstream wird innerhalb der Houdini-Kurve begrenzt

### Ansatz B: Labs Unreal Spline (JSON-basiert)

1. Labs Unreal Spline SOP nach dem Wrangle anhängen
2. JSON exportieren
3. In Unreal: JSON in Blueprint mit Spline Component importieren
4. Blueprint Actor im Level platzieren
5. PCG: Get Spline Data oder als PCG Component Input verwenden

### Ansatz C: Einfach in Unreal machen

Für handplatzierte Bounding Regions ist Unreal's eingebauter PCG Spline/Volume Actor der schnellste Weg:

1. PCG Volume oder PCG Spline Actor ins Level ziehen
2. Spline-Punkte direkt im Viewport bearbeiten
3. Im PCG Graph als Input verwenden

**Houdini lohnt sich nur wenn:** die Boundary prozedural generiert wird, von anderen Houdini-Daten abhängt, oder viele Regions auf einmal erzeugt werden müssen.

### Skalierung

Houdini = Meter, Unreal = Zentimeter. Entweder Kurve in Houdini ×100 skalieren oder Houdini Engine die Transformation überlassen (macht es normalerweise automatisch).

---

## 2. Buildings als einzelne Instanzen (nicht merged Mesh)

### Problem

Ohne Pack werden alle Buildings im For Each Loop zu einem einzigen merged Static Mesh zusammengefasst.

### Lösung: Pack SOP im For Each Loop

```
For Each Begin → [Building Logic] → Pack SOP → For Each End
```

Der **Pack SOP** vor dem For Each End ist der Schlüssel. Jede Loop-Iteration erzeugt ein eigenes Packed Primitive → Houdini Engine macht daraus separate Static Meshes in Unreal.

### Performance-Vergleich

| Ansatz | Draw Calls | Memory | Culling | Wann nutzen |
|--------|-----------|--------|---------|-------------|
| ISM (Packed Prims, default) | 1 pro Mesh-Typ | Shared | Per-Cluster | Gleiches Mesh oft wiederholt |
| HISM (hierarchisch) | 1 pro Mesh-Typ | Shared | Per-Instance LOD | Gleiches Mesh + LODs nötig |
| Split Actors (`unreal_split_attr`) | 1 pro Building | Dupliziert | Per-Actor | Jedes Building einzigartig |
| Merged Mesh | 1 total | Ein großer Blob | Alles oder nichts | Nie für Buildings |

### Fazit

- **Jedes Building ist unique Geometry** (Pattern-Generator) → Pack SOP → separate Meshes. Unreal kann einzeln cullen, Nanite funktioniert per-Mesh.
- **Gleiche Buildings wiederholt** → Packed Prims + Copy to Points mit "Pack and Instance" AN → automatisch ISM, ein Draw Call pro Typ.
- **Nanite:** Niemals HISM forcen (`unreal_hierarchical_instancer`), Nanite handled LOD selbst.

### Wenn Buildings identisch sind (Bonus)

Houdini Engine erkennt identische Packed Prims automatisch und erzeugt `InstancedStaticMeshComponent`. Voraussetzung: identische Topologie (gleiche Punkt-/Prim-Anzahl).

### Splitting per Attribut (Alternative)

Falls feingranulare Kontrolle nötig:

```vex
// Wrangle auf Points NACH Copy to Points
i@id = @ptnum;
s@unreal_split_attr = "id";
```

Erzeugt separate Components pro Building. `unreal_split_instances` ist seit Houdini 20.5 deprecated.

---

## Relevante Houdini Engine Attribute (Referenz)

| Attribut | Typ | Zweck |
|----------|-----|-------|
| `unreal_instance` | string | Pfad zu UE Asset für Instancing |
| `unreal_split_attr` | string | Attributname zum Aufteilen der Instancer |
| `unreal_force_instancer` | int | Instancer auch bei Einzelkopie erzwingen |
| `unreal_hierarchical_instancer` | int | HISM forcen (nicht mit Nanite) |
| `unreal_foliage` | int | In UE Foliage-System integrieren |
| `i@curve_closed` | int | Geschlossene Spline |
| `v@unreal_spline_point_arrive_tangent` | vector | Eingehende Tangente |
| `v@unreal_spline_point_leave_tangent` | vector | Ausgehende Tangente |
| `s[]@unreal_pcg_tags` | string array | PCG Tags zum Filtern |

## Quellen

- SideFX PCG Overview: https://www.sidefx.com/docs/houdini/unreal/pcg/index.html
- HoudiniPCGTranslator: https://github.com/AdrianPanGithub/HoudiniPCGTranslator
- Labs PCG Export: https://www.sidefx.com/docs/houdini/nodes/sop/labs--pcg_export-1.0.html
- Houdini Engine Instancers: https://www.sidefx.com/docs/houdini/unreal/instancing.html
- Houdini Engine Attributes: https://www.sidefx.com/docs/houdini/unreal/attributes.html
- Export Splines Houdini↔Unreal: https://www.sidefx.com/contentlibrary/export-splines-between-houdini-and-unreal/
