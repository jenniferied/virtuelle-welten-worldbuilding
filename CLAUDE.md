# ПАНЕЛЬКИ / Virtuelle Welten Worldbuilding

Master Medienproduktion project for "Virtuelle Welten" course with Adrian Meyer at TH OWL.

## Project Structure

```
worldbuilding-bible/     # A3 landscape worldbuilding bible (German)
game-design-document/    # A4 portrait Prozessdokumentation (German)
wip/                     # Work-in-progress Houdini project files
  houdini/               # Houdini project
    VirtuelleWeltenAbgabe.hipnc  # Main HIP file
    assets-cars/         # Vehicle assets (Blender/FBX)
  neryungi/              # Terrain and OSM data for Neryungri, Russia
    AP_18737_*/          # ALOS PALSAR DEM/radar data
    planet_*.osm*        # OpenStreetMap extracts
  screenshots-progress/  # Development progress screenshots
  screenshots-assets/    # Asset reference screenshots
assets/                  # Logos and shared assets
scripts/                 # Python build scripts
fonts/                   # Typography (Molot, Futura, PT Sans)
```

## Build Commands

```bash
make worldbuilding   # Build worldbuilding bible PDF
make gdd            # Build game design document PDF
make all            # Build both documents
make clean          # Remove build artifacts
```

## Houdini Project

- **Main file**: `wip/houdini/VirtuelleWeltenAbgabe.hipnc`
- **Location**: Neryungri (Нерюнгри), Yakutia, Russia
- **Geodata**: OSM buildings/roads, ALOS PALSAR DEM terrain

## Large Files Note

Some assets exceed GitHub's 100MB limit:
- `YugoKoral55.blend` (291MB)
- `YugoKoral55.fbx` (137MB)

Consider Git LFS for these files, or keep them local.
