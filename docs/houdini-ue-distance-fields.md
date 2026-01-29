# Houdini → Unreal: Mesh Distance Fields

**Stand**: 2026-01-29
**Versionen**: Houdini 21, Houdini Engine, Unreal 5.7

## Problem

Mesh Distance Fields werden bei Houdini Engine Bakes nicht korrekt generiert:
- Setting "Generate Mesh Distance Field" wird nicht automatisch aktiviert
- Wenn aktiviert, ist das Distance Field invertiert (Partikel kollidieren innen statt außen)
- UE 5.7 wird offiziell noch nicht von Houdini Engine unterstützt (nur bis 5.6)

## Was funktioniert

### Attribute Wrangle (Detail)

```vex
i@unreal_uproperty_bGenerateMeshDistanceField = 1;
f@unreal_uproperty_DistanceFieldResolutionScale = 2.0;
```

Aktiviert das Setting, aber Distance Field bleibt invertiert.

### Workaround: OBJ/FBX Export

1. Houdini: File → Export → OBJ/FBX
2. Unreal: Import mit "Generate Mesh Distance Field" aktiviert
3. Nach Import: Mesh im Content Browser → Rechtsklick → Reload

**Ergebnis**: Distance Field funktioniert korrekt.

## Batch-Fix für Houdini Engine Bakes (Python)

Falls Houdini Engine genutzt wird, nach dem Bake in Unreal ausführen:

```python
import unreal

path = "/Game/HoudiniOutput"  # Pfad anpassen
assets = unreal.EditorAssetLibrary.list_assets(path, recursive=True)

for asset_path in assets:
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if isinstance(asset, unreal.StaticMesh):
        asset.set_editor_property("generate_mesh_distance_field", True)
        unreal.EditorAssetLibrary.save_asset(asset_path)
```

Danach: Meshes im Content Browser selektieren → Rechtsklick → Reload

## Was nicht funktioniert

- `s@unreal_uproperty_bGenerateDistanceFieldAsIfTwoSided` → Kein Effekt
- Plugin Settings → Distance Field Resolution Scale → Aktiviert nicht "Generate"
- Reverse SOP / Facet SOP / Normals flippen → Ändert nichts an Invertierung
- Mobility auf Static setzen → Kein Effekt

## Fazit

Houdini Engine + UE 5.7 + Distance Fields = Bug. Für produktiven Einsatz OBJ/FBX Export nutzen oder Bug an SideFX melden.
