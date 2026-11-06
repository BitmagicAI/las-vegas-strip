# Shake Shack — installed sign refinement

The front now includes an original raised burger outline beside the existing letters. It adds 588 triangles and one material batch. Installed GLB: 78,903 → 79,491 triangles; 1,081,272 → 1,095,328 bytes. The earlier record’s 45,911-triangle count was stale and is corrected here.

All 43 existing source GLB nodes remain unchanged before optimization. All 273 collision triangles and the installed collision binary remain unchanged. Only LOD cell -1_1 changed; the other 91 cells are byte-identical. Unrelated Gold Coast and Wyndham LOD differences from the shared bake were restored.

| View | Before | After | p95 ms before → after |
|---|---|---|---|
| Front | [before](before/shake-shack-front.png) | [after](after/shake-shack-front.png) | 24.0 → 17.3 |
| Terrace | [before](before/shake-shack-terrace.png) | [after](after/shake-shack-terrace.png) | 39.9 → 39.6 |
| North | [before](before/shake-shack-north.png) | [after](after/shake-shack-north.png) | 17.6 → 18.4 |
| Roof | [before](before/shake-shack-roof.png) | [after](after/shake-shack-roof.png) | 25.1 → 19.2 |

Identical cameras, neutral daylight, ultra, 960×540, DPR 1; 900 warm frames, streaming quiet, 60 settling frames, 180 timed frames. Each pair was visually inspected. No measured view regressed over 10%, but the terrace remains slow. This small addition does not establish a performance improvement, full driving benchmark, or sustained 60 fps.

Actual installed keyboard movement passed all 14 ramp/terrace/stair legs in both directions. The independent CPU walk passed 14 legs and all 185 support samples passed. These checks validate the existing outdoor route; they do not establish access to a new interior.

## Decisions for the owner

Use an original tubular emblem, with inferred dimensions of 1.3m × .86m, preserving the existing canopy, letters and all other frontage geometry. Keep the approximate upper mass, north glazing, missing landscape, adjacent Tom’s and dining interior explicitly deferred. Official interior photographs support finishes but do not resolve a measured circulation plan.

## For the release step

CDN and published-game checks are not performed locally. Nothing was uploaded, published, released or merged to main.
