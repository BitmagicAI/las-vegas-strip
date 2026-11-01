# New York–New York south arrival island

Issue31 / PR454, based on next76bfd7c. Official property map and gallery, Google aerial and January2025 Street View were inspected; links and observations are in research.json. Original geometry only; no third-party reference imagery redistributed.

The previously empty forecourt island receives an estimated34x6.2m low lawn mound, south-facing flower NYNY strokes, red curb, rear low fence, upright shrubs, desert leaves and stones. Two broadleaf trees use existing CC0 Poly Haven tree_small_02 source meshes from tools/foliage/models, with the established three-level tree metadata, using tree-0 near and tree-2 far (source files unchanged). Plant species/counts and all heights are fitted estimates, not survey measurements.

All ten old source groups /6,717 triangles and existing labels and collision prefix are preserved exactly. Added authored landscaping has7,738 valid triangles and448 collision triangles (tree visual meshes counted separately in exported GLB). The canopy, pavilion, roads, dense legacy coaster supports and interiors are preserved. No new lights or runtime shaders are introduced.

Rebuild with build_nyny_arrival.py and export_nyny_landscape.py, pack the arrival collider and venues records, level+WebP optimize and install nynyArrival-exterior.glb. Inspect before the single final city bake and asset stage. Shared source foliage is unchanged; do not rebuild its runtime copies.

Baseline four matching views: build/city-exteriors/nyny-landscape-before. Initial installed preview inspected; final corrected close views are in progress. Twelve normal walking segments passed around both ends of the island and back; all four endpoint captures inspected. Static clearance1398samples passed;199ground samples are supplied by runtime terrain/roads and are verified by normal walking. Existing canopy864support samples passed. Initial path atz1638 grazed old columns; the path was moved toz1636 before walking. Whole-resort architecture, rear pool, typography and accurate paving remain deferred; no photoreal completion claim.
