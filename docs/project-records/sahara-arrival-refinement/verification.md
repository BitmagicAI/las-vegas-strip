Refine SAHARA's arrival ceiling with an original closed crown and dark underside inset, based on supplier photographs and Google aerial review. This is a scoped refinement; the wider resort remains incomplete.

### SAHARA
- Give the former flat ring a closed 0.30 m crown and static metallic inset; extend hanging rods into it and remove only crossing central beam segments.
- Preserve outer roof, surrounding beams, basin, roads, towers, existing interiors, labels and collision. Correct the earlier roof-oculus interpretation: inspected references support a continuous closed roof.
- Inferred radii, heights and material finish are documented in `docs/project-records/sahara-arrival-refinement`. Geometry is original; no third-party imagery included.

### Verification
- Level optimization and WebP pass: PASS, 3.18 → 1.04 MiB.
- bitmagic check: PASS.
- Arrival test: PASS, 4,096 roof samples, 195 drive clearances, closed basin, zero failures.
- West arc test: 107 samples, zero new obstructions; two existing road-edge contacts explicitly retained, not a full-route pass.
- Actual installed walking: PASS, all 12 forward/return segments; both endpoint captures inspected.
- Four matching neutral-daylight views inspected, front first. Initial crossing-beam defect fixed on this branch. P95 baseline → corrected: front 18.2 → 19, arrival 18.5 → 17.7, canopy 19.1 → 19, feature 19.7 → 19 ms. Initial canopy 29 ms outlier retained; cause unproven, not reproduced. No speedup or 60fps claim.
- Source preservation: PASS, only two existing arrival material groups changed, two added; labels and collision identical.
- review.py: PASS, 289 records.
- check-public.py: PASS, zero failures; three existing email warnings.
- check-runtime-glbs.py --changed origin/next: PASS, one optimized GLB.
- bake-city.mjs check: PASS; exactly one shared bake.
- asset-pack.py check: PASS, 1,930 present, zero missing or unoptimized.
- smoke-clone.mjs against local bitmagic dev: PASS, nine stops; zero failed requests, page errors, console errors or unplaced stops.
- git diff --check: PASS.

### Asset scope
New Git LFS bytes: **1,520,248** across SAHARA GLB, LOD cell `cell-1_-4.bin`, and LOD manifest. **184/186** geographic/LOD cell files byte-identical; collision files unchanged. Two unrelated Gold Coast/Wyndham LOD blocks drifted during the bake and were restored byte-for-byte without recapture or rebake. Asset manifest and scoped task/record metadata updated; no runtime code changes, roads, foliage or other buildings edited.

### Decisions for the owner
Keep the roof closed and use a reversible static dark metallic inset; no dynamic mirror or new lights. Exact canopy shape, display columns, entrance details, landscaping, secondary pools and broader public circulation remain unfinished and recorded.

### For the release step
CDN upload and published cold-load checks happen before next merges to main. No upload, publishing or release performed.

Closes #36 (explicit issue closure after merging to next).
