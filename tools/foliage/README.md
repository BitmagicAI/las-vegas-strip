# Resort botanical foliage

Bellagio arrival garden now uses Poly Haven CC0 assets rather than polygon crowns.

Sources (download manifests with URL/checksum retained under sources/):
- https://polyhaven.com/a/tree_small_02 — Rico Cilliers. Broadleaf ornamental tree, bark/leaf PBR textures.
- https://polyhaven.com/a/grass_medium_01 — Rico Cilliers, Rob Tuytel. Small grass tuft variant.
- https://polyhaven.com/license — CC0-1.0.

Rebuild from project root:
1. `python3 tools/foliage/download_sources.py`
2. Blender `--background --python tools/foliage/prepare_assets.py -- tree tools/foliage/sources/tree_small_02/tree_small_02_1k.gltf`
3. Same command with `grass tools/foliage/sources/grass_medium_01/grass_medium_01_1k.gltf`.
4. Blender `--background --python tools/foliage/make_impostor.py`.
5. Run `tools/foliage/place_lawn.py` with project Shapely/numpy Python environment.

Outputs: public/foliage GLBs, asset proofs, manifests and deterministic placement JSON.
Tree LODs: 250,000 / 13,139 / 6 triangles, 85/220/650m cell distances.
Grass LODs: 833 / 100 triangles; full placement density at medium detail; 18/55m distances.
37 trees, 177,044 tuft placements. Instances are grouped into 40m tree cells and 10m lawn cells, shared geometry/materials. Distance changes checked every 180ms with hysteresis. Grass stays inside authored lawn polygons inset 0.8m; maximum tuft horizontal radius including scale is below 0.8m. Existing terrain collision is retained. Tree crowns remain within previous 4m clearance radius.

This pass covers Bellagio's south arrival garden only. Other resorts and older lakefront trees still need the same migration. Source species is a visual ornamental stand-in, not a verified Bellagio botanical species. Wind animation and additional species remain future refinements. LawnMaterial supplies a matte, fine textured turf base at all distances; grass blades also suppress environment reflections.

Asset Forger was attempted once per asset first. Both jobs lost service worker instances and failed after internal resubmits; no model resulted and world.json was unchanged. Local CC0 source assets are the fallback, not claimed as generated results.

## Upright grass correction
The imported scrub-like tuft is no longer used for lawn. Rebuild grass with `blender --background --python tools/foliage/build_lawn_blades.py`. It creates opaque, tapered upright blades with green vertex-color variation, 18–32cm height before instance variation, 72 triangles/patch near and8 far. No alpha overdraw. Placements now use0.18m jittered spacing, uniform0.85–1.05 scale, 13cm boundary inset, no taller perimeter band and no horizontal stretching. 363425 patch placements;12m cells and14/36m detail distances. Matte textured ground remains at distance. Earlier source imports retained for provenance only.
