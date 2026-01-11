# Houdini Integration Skill

Document Houdini project, capture screenshots, and manage assets.

## Trigger
Run `/houdini` when:
- Need screenshots from HIP file for documentation
- Updating asset inventory
- Documenting workflow/nodes

## Project Files

### Main Houdini File
`wip/houdini/VirtuelleWeltenAbgabe.hipnc`

### Assets
- `wip/houdini/assets-cars/` - Vehicle models (Blender/FBX)
  - Mercedes.blend/fbx
  - YugoKoral55.blend/fbx (large - 291MB/137MB)

### Geodata
- `wip/neryungi/` - Terrain and city data
  - ALOS PALSAR DEM/radar data (AP_18737_*)
  - OpenStreetMap extracts (planet_*.osm*)

## Screenshot Management

### Progress Screenshots
Location: `wip/screenshots-progress/`
- Named by date: `YYYY-MM-DD_description.png`
- Document major milestones

### Asset Screenshots
Location: `wip/screenshots-assets/`
- Reference images for assets
- Before/after comparisons

## Documentation Tasks

### For Worldbuilding Bible
- Extract key renders for visual style chapter
- Document terrain generation workflow
- Show building/road placement from OSM

### For Process Documentation (GDD)
- Houdini→Unreal pipeline diagrams
- Node network screenshots
- Before/after terrain processing

## Limitations

**Note**: Claude cannot directly open or manipulate Houdini .hipnc files.

For screenshots:
1. User opens Houdini
2. Takes screenshots manually
3. Saves to appropriate folder
4. Claude can then reference/document them

Alternative: Use Houdini's batch rendering via command line (if HIP file has proper render setups):
```bash
hython -c "hou.hipFile.load('path/to/file.hipnc'); hou.node('/out/render').render()"
```
(Requires Houdini/hython installed and configured)

## MCP Integration

For Claude AI integration with Houdini, use the official MCP server:

**Repository:** [capoomgit/houdini-mcp](https://github.com/capoomgit/houdini-mcp)

This enables:
- Prompt-assisted 3D modeling
- Scene creation via natural language
- Simulation setup
- Procedural generation workflows

**Setup:** Follow the repository README to configure MCP connection between Claude and Houdini.

## Asset Inventory

| Asset | Format | Size | Notes |
|-------|--------|------|-------|
| VirtuelleWeltenAbgabe.hipnc | Houdini | ~50MB | Main project |
| Mercedes.blend | Blender | ~5MB | Reference car |
| YugoKoral55.blend | Blender | 291MB | Hero vehicle (LFS) |
| YugoKoral55.fbx | FBX | 137MB | Export for Unreal (LFS) |
