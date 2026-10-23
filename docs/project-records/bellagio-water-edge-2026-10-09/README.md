# Bellagio water, shore overlap and roadside openings — 2026-10-09

Local repair installed and inspected in the running WebGPU game and editor. This is a targeted defect repair, not a claim that the resort is photorealistic or architecturally complete.

## Request and observed failures

The exact request is in `request.txt`, with the three creator screenshots saved as `user-1.png` through `user-3.png`. These show the outdoor Bellagio lake in **Editor** mode. The last screenshot faces the Paris balloon from the southern arrival/sidewalk join.

- Water time was advanced from the simulation update. The editor pauses that clock. Water now uses the engine's render ambience clock, which also supports paused gameplay and fixed-step recording.
- The screen-space planar mirror was reused on alternate frames while its sampling coordinates followed the new camera. Turning therefore sampled a stale camera image. Each visible mirror now renders for the current camera every displayed frame.
- Lake reflection distortion was ten times larger than the revised value, stretching repeated window grids into stripes. Distortion is now small, with four-sample MSAA, mip filtering and the existing soft reflection filter. The air/water Fresnel base is 0.0204. The reflected camera clips submerged geometry using the existing reversed-depth-aware clip plane.
- The lake bank, promenade slab and raised garden had coincident vertical faces. The repair cuts their overlapping render polygons at authoring time. It does not shift the road, grass, walkway or existing colliders.
- The city cut at x=-22 left open roadside cross-sections. New cap faces follow the existing city road/sidewalk heights. A narrow existing verge also lacked physical support after the terrain cut; three collision triangles now follow its already visible surface.
- Fountain rings/header pipes were modeled through/above the water. Their top is now 0.5 m below water (-1.6 m versus -1.1 m). This does not implement a fountain show.

## Installed comparison

All images below are actual game renders, not Blender beauty renders or generated illustrations.

| View | Before | Installed repair |
|---|---|---|
| Low lake view | [Before](before/still-0.png) | [Editor, still](after/editor-water-0.png) |
| Bank/railing | [Before](before/shore.png) | [Repaired shore](after/shore.png) |
| Roadside opening | Creator `user-3.png` | [Closed edge](after/roadside.png) |
| Looking into the lake | Creator `user-2.png` | [Water from above](after/water-above.png) |

`after/turn-0.png` through `turn-4.png` record different camera orientations. Two stationary frames are retained. Frame/clock assertions, rather than still images alone, verify continued animation and mirror refresh. High-tier images and `high-report.json` check the environment-reflection fallback without a planar mirror.

## Checks and scope

- TypeScript and `bitmagic check`: passed. Final `bitmagic verify --timeout 90000`: passed, no failures or warnings; playing at 60 fps after 4.1 s settle. The first default-timeout run stopped at the menu after a 38 s GPU warmup; its result is retained, and the longer startup allowance resolved it.
- 30 mathematical water clipping probes: passed (normal and reversed WebGPU depth).
- Real Ultra runtime, 2450×1550: **150 mirror renders / 150 frames** for each of gameplay, stationary editor, and rotating editor. Water time advances in all three.
- Warm Ultra frame median 16.6–16.7 ms, p95 18.2–18.6 ms. The turn sample includes a 49.6 ms maximum. These short local samples are not a full-city streaming or memory acceptance test; no controlled pre-change performance comparison was made.
- High tier, 1280×720: water time advances for all three modes; no planar reflection passes as intended. Median 16.6–16.7 ms, p95 17.5–17.6 ms.
- Authoring ownership audit: **0 m² remaining overlap** for all repaired ownership pairs; repeating the repair removes nothing further. First pass cut 108.47 m² from the bank/walk/garden intersections plus hidden railing caps. Exact reports are retained.
- Roadside physics: **1,240 floor rays and 31 cap rays pass** across the reported connection.
- 255 existing exterior groups unchanged; four existing groups altered plus two small cap groups. Thirty protected files unchanged, including world data, city GLB/collision, Bellagio interiors, routes and barriers. Original author collision is an exact retained prefix; appended canopy collision is preserved.
- Only `bellagioBlock-exterior` was exported. Raw GLB 132.09 MiB → optimized installed WebP GLB 46.43 MiB. Existing LOD/source grouping and optimizer pipeline retained.
- Full existing Bellagio route suite: 4,178 samples, **19 failures at “Sign interior stairs to arcade.”** Repeating it with the saved original collision produces the identical 19 failures (`baseline-routes.json` versus `route-audit.json`). These pre-existing stair issues remain open.

## Durable authoring and reproduction

`src/work/Game.ts` registers/unregisters the before-render water clock. `RealisticWater.ts` handles current-frame reflection, filtering and conservative distortion.

`tools/resort-blocks/bellagio_edge_ownership.py` supplies shared face ownership, roadside closures and narrow-verge support. The full builder calls it, and `repair_bellagio_lake_edge.py` applies it selectively to the cached exterior without rebuilding other buildings, lawns or roads. `export_bellagio.py -- --only bellagioBlock-exterior` preserves all other GLBs. See `BELLAGIO-BUILD.md` for the targeted commands.

Regression entry points:

```
node --import ./tools/ts-register.mjs tests/water-reflection-clip.test.mjs
node tools/resort-blocks/test-bellagio-water-edge.mjs
python3 tools/resort-blocks/test-bellagio-edge-geometry.py
node tools/probe-eval.mjs tools/resort-blocks/probe-bellagio-water.js --viewport 1225x775 --dpr 2 --out build/probe/water-edge/after
```

Python requires the project's existing NumPy/Shapely runtime. Evidence scripts allocate freely; runtime changes add no per-frame geometry, lights or JavaScript arrays. No publishing or uploads.
