# Excalibur public approach arcade

Issue32 / PR453, from next4b47fb0. Original geometry fitted to linked official gallery, aerial and April2025 Street View. Official property map was inspected for circulation only; no reference pixels or plans redistributed.

The old generator promoted mapped five-metre approach features to ten-metre conical turrets. Ten selected features are now owned by `excalibur_arcade.py`: mapped centres, estimated square piers, shallow pointed openings, tan masonry trims, low crenellated side walls, flat ceiling and inset panels. Existing ground route and bridge surfaces stay unchanged. This is a flat-datum architectural approximation, not a rebuilt moving walkway or surveyed elevation. Whole-block landscaping, tower detailing, station circulation and south elevation remain deferred with reasons in the block record.

The existing 47,762 frontage triangles and 19 groups remain intact. A targeted index-only installer removes 5,256 obsolete low turret faces from the high-rise file; other nodes, transforms, extras, triangle counts and bounds are audited. The full architecture builder skips the same ten IDs so they do not return on a rebuild. No new runtime light, shader or interior.

## Rebuild

Use the existing `build_excalibur_frontage.py` then export only `excaliburFrontage-exterior` through `tools/strip-landmarks/export.py`. The full south-strip builder already skips the replaced IDs. For an existing high-rise GLB, run `node tools/city-exteriors/install-excalibur-arcade.mjs` once against the original model; the installer refuses a repeat with no faces to remove. Backups are in `.bitmagic/city-exterior-backups/excalibur-arcade/`.

Optimize both `highrises/exteriors.glb` and `excaliburFrontage-exterior.glb` individually with level and WebP passes, pack the frontage collider and install with `--no-stage`. Inspect and walk before one city bake, then stage/check. Existing high-rise/city collision is unchanged; new pier/wall/ceiling collision belongs to the frontage.

## Evidence

- `research.json`: primary links and observations, initial camera correction.
- `geometry.json`: finite geometry and retained frontage/collision audit.
- `replacement-report.json`, `highrise-preservation.json`: precise replacement scope and optimized output checks.
- Matching baseline: `build/city-exteriors/excalibur-arcade-before-final`; initial `before` has two obstructed cameras and is not the comparison baseline.
- Final installed captures, normal walking, performance, bake and package checks are still pending. Do not treat this source checkpoint as completion.

## Final elevated-view correction

The first final elevated view revealed 480 old crenellation faces outside the original removal radii. Removal radii expanded by0.45m to cover their box corners, without reaching neighboring features. A second local bake is required to correct this before merge; only the final corrected runtime assets will be staged for commit, so no extra LFS asset version is uploaded. Initial after captures are superseded by the corrected final captures.
