# North Strip corrections — 9 October 2026

This pass responds to the creator's lower Venetian z-fighting, incorrect LINQ/TI facades and missing Caesars shopping complex. These are targeted exterior corrections, not whole-resort or photorealistic sign-off. Installed game images and neutral daylight renders are in the adjacent `north-strip-corrections-2026-10-09/` folder.

## Changes and evidence

**Venetian:** the previous four-pair overlap test missed tower/podium ownership. The expanded audit found over 4,300 m² of coincident faces in just two tower/podium pairs. Author-time boolean subtraction now gives the podium ownership below its roof, cuts duplicate north-frontage trim and removes duplicate shop mullion faces. This edits render geometry, not physics or retained interior assets. All ten targeted independent surface pairs in the regression report are now zero within numerical tolerance. The wider diagnostic still reports other overlaps, including internal cap faces and pool-deck/interior pairs; it is not a blanket all-building z-fighting guarantee.

![Venetian installed aerial](north-strip-corrections-2026-10-09/venetian-after.png)

**LINQ:** real projecting three-sided blue glass bays replace the flat white window grid. Broad white structural ends/crown, blue reveals and horizontal base bands follow the creator's aerial reference. Existing mapped footprint, roof height, wheel, promenade, interiors and collisions remain. Window depth, exact bay schedule, signage scale and service-roof layout are photo-fitted approximations.

![LINQ installed aerial](north-strip-corrections-2026-10-09/linq-after.png)

**TI:** the mapped 112 m, three-wing tower now has red masonry, projecting white window surrounds, horizontal floor bands, blind blade ends and arched crown glazing. StripLandmarks owns the tower render; HighriseCity retains its collision and guest layout. The old generic visual tower is suppressed. The podium, ship and interiors are retained. A neutral roof material replaces the repetitive podium roof texture. Full arrival grounds, exact roof services and tenant detail still need a separate architectural pass. Reference: [CTBUH exterior photograph](https://www.skyscrapercenter.com/building/treasure-island-hotel-casino/14139), photo date unknown, inspected visually and not used as a game texture.

![TI installed aerial](north-strip-corrections-2026-10-09/ti-after.png)

**Forum Shops:** the mapped 60,014.95 m² shopping complex was excluded by the older Caesars replacement without actually being built. A new exterior restores the connected footprint, stepped roof tiers, parapets, skylights, service equipment and concave Roman Strip entrance. The main frontage owns its walls and trim; the map's column/stair micro-outlines are not extruded into full-height walls. The original city, roads, legacy Caesars and Colosseum assets are unchanged. This is an exterior-only venue: it will not request a nonexistent interior or add runtime lights. Existing Caesars geometry, including its approximate Colosseum, remains visibly less accurate than the reference.

The footprint is registered to [OSM way 34068416](https://www.openstreetmap.org/way/34068416). Its layout is corroborated by the [official Simon Terrace Level leasing plan](https://devbusiness.simon-ops.com/assets/mall/224/LEASING_PLAN/1145_FORUM%20SHOPS%20AT%20CAESARS_CurrentWebLeasePlan-T.pdf), dated June 2021 and archived locally. The plan is illustrative, not a construction survey. Roof tiers of 12.8, 16.8, 24.4 and 32 m, entrance curvature and ornament are photo estimates. The [street reference photograph](https://cdn.wallpapersafari.com/77/13/tN0arf.jpg) was inspected but is not licensed or embedded as a game texture. Small entrance-edge adjustments replace noisy map micro-outlines; the rest of the mapped perimeter stays in place.

![Forum Shops installed aerial](north-strip-corrections-2026-10-09/forum-after.png)

![Forum Shops installed street](north-strip-corrections-2026-10-09/forum-street-after.png)

Fine sculptural relief, statuary, tenant branding, a surveyed height schedule, complete landscaping and the shopping interior are not completed by this pass. Whole-site acceptance gates remain open; no resort is marked complete.

## Validation and method

- TypeScript check passes.
- Expanded Venetian regression passes ten independent surface-pair checks, and finds no old bridge triangles in the replacement corridors.
- Existing city-inclusive Rapier route suite: 9,904 checks, 284 virtual rooms, zero failures. Forum Shops has no interior routes and is excluded from the interior-file assumption; this suite does not imply its interior is walkable.
- New mall collision test: four sampled roof heights agree within 0.01 m; 217 sidewalk capsule samples clear; 994 collision triangles. Ornament has no per-detail collider.
- 33 protected interior/city files checked by SHA256, no changes. No road regeneration, uploads, commits or publishing. The overnight automation stays paused.
- Every revised exterior was inspected in the installed game and in neutral daylight. Aerial review uses the probe's explicit `--hold` mode to keep the player/camera airborne. Those captures are visual evidence, not traversal or fair performance measurements.
- The before/after stationary benchmark uses identical commands, 1280×720, DPR1, Ultra, three-second warm samples and no Blender render running. Two repeats are retained because CPU spans and draw counts varied as content streamed/unloaded. They establish 60 fps in the sampled views, not a controlled improvement in total CPU work. These views allow the normal player to fall to the existing ground. They are not a driving/streaming benchmark, and the report's `placed` field is the initial teleport position, not the settled player position.

See `performance-before.json`, `performance-after.json`, `asset-metrics.json`, `venetian-regression.json`, `venetian-overlap-after.json`, `forum-collision-audit.json`, `protected-after.json` and `build-fingerprint.json` in the evidence folder. Final WebGPU verification is recorded there as well. The original street review camera was occluded by neighboring geometry; the corrected game camera is `(42, 3, -363)`, yaw `1.816`, pitch `-0.20`. Its screenshot and camera report are archived separately. The source review view now uses that unobstructed position.

## Reproduction

Run only the targeted builders with the project's Python 3.12 (numpy/shapely): `build_venetian_exterior.py`, `build_linq_exterior.py`, `build_ti_exterior.py`, `build_forum_shops.py` under `tools/strip-landmarks/`. Export only their respective `*-exterior` assets with Blender `export.py`. Refresh the optimizer list for a newly added venue, then optimize and install each changed asset. No full level or road build is needed. The shared full landmark builder also calls the new exterior modules and Venetian ownership reconciliation for future reproducibility.

All generated files remain local. The four resort records retain prior open issues and gates.

## Stationary timing results

1280×720, DPR1, Ultra; three-second warm samples. CPU/GPU columns are medians in milliseconds.

| View | FPS before → after | CPU before → after | GPU before → after | Draws before → after |
|---|---:|---:|---:|---:|
| linq | 60 → 60 | 7 → 8.2 | 8.76 → 3.8 | 436 → 441 |
| ti | 60 → 60 | 6 → 6.4 | 7.97 → 3.57 | 158 → 96 |
| forum | 60 → 60 | 5.9 → 6.3 | 5.02 → 4.48 | 166 → 167 |

The LINQ CPU median increased from 7.0 to 8.2 ms in the final repeat. Scene residency varied notably for TI between repeats, so this is not a controlled CPU attribution. FPS remained 60 in all samples, but full street/streaming performance acceptance remains open. The final entrance facing/offset correction changes no topology or collision relative to this final benchmark.
