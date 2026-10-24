# How it was made

1. **The map.** OpenStreetMap footprints, heights and roads, and Clark County pavement data, became streets and box
   buildings (`tools/strip-survey/`, `tools/geographic-strip/`).
2. **The buildings.** Agents compared each building with Google Earth views, then rebuilt it in Blender from public
   photographs and published resort maps. A block record notes each source and every gap still open
   (`tools/resort-blocks/`).
3. **The interiors.** Lobbies, casinos, corridors and rooms were laid out from published floor plans and photographs
   (`tools/strip-landmarks/`, `tools/highrises/`, `tools/level/`).
4. **Checking.** Every pass was compared against its references and walked. Collision was audited, and frame time
   measured before and after.

The history is in `docs/project-records/`.
