# City batching and scale-aware LOD

Implemented locally on 2026-10-05. This pass implements the requested draw-call and
LOD architecture. **Steady 60 FPS is not yet achieved in the dense High-quality test views.** The renderer still has
large frame-time spikes; the following evidence distinguishes draw reduction
from frame-rate acceptance.

## What changed

- Static architecture is grouped by resort/property or 160 m geographic cell.
  Compatible opaque materials share a mesh and shader; base color, roughness,
  metallic and emission factors become vertex attributes. Bitmap color textures
  use full-resolution atlases with repeated UVs and gutters. The lakefront village
  is two submissions, retaining its original 939,350 detailed triangles.
- Each block has prebuilt full and coarse meshes. Coarse meshes cluster vertices
  and use texture-average colors, preserving surveyed envelopes, roof lines and
  setbacks instead of substituting unrelated generic boxes. No geometry is rebuilt
  on an LOD transition.
- Selection measures distance to the block's bounds. Default full-detail range is
  180–900 m according to height; ordinary low-rise blocks disappear beyond at least
  1,200 m. OSM cells use 240 m full / 2,400 m cutoff. Tall blocks (>45 m) and explicit
  skyline properties retain a coarse silhouette at all distances within camera range.
  Twelve-percent hysteresis, 180 ms throttling and a 1 m camera movement threshold
  prevent repeated switching and per-window work. The editor camera also selects LOD.
- Exact source geometry remains available to the ground-surface index. Colliders,
  entrances and streamed interiors keep their existing ownership/lifetime. Shadow
  silhouettes are separately batched by spatial cell and cannot select the visible
  scene LOD. Original transforms/parents/materials are restored on disposal.
- Bridge-concourse architecture and door trim share geometry/materials. Distant
  characters skip render/animation beyond 180 m, excluding the player. Transparent
  surfaces and unsupported shader/map pipelines retain their separate render path.
- Shader/material/atlas reuse spans blocks, with reference-counted disposal. This
  fixed an initial shader-warmup regression (98.3 s down to 15.5 s in startup tests).
- WebGPU city batches use the installed Three clustered-lighting node. Point-light
  influence is culled by screen/depth region; no scene lights are deleted. Shadowed
  lights retain the normal path. More than 64 non-shadowed point lights falls back
  to the normal light list rather than silently dropping lights. WebGL uses the
  normal path. Light-list work is shared once per frame/camera, not per building.
- The panel reports LOD block counts, mean-based FPS, quality and drawing-buffer
  size. Mean FPS now includes stutters that the earlier reciprocal-median display
  hid. Expanded diagnostics still add measurable cost; collapse for lighter runs.

## Repeatable lakefront measurements

Player (-3, 45.24, 283), camera (-3, 46.787, 283), fixed aerial bookmark.

| Measure | Original diagnostics | Batched / LOD sample |
|---|---:|---:|
| Renderer draw calls | 1,124 | 146 |
| Submitted triangles | 4,365,814 | 3,265,756 |
| Lakefront village draws | 52 | 2 |
| Village triangles | 939,350 | 939,350 |
| Bridge-concourse draws | 181 | 25 |
| Main-scene CPU render median | 11.3 ms | 4.0 ms |

The final detailed sample has 345 blocks: 39 full, 233 coarse, 73 culled. Renderer
counts include shadow/other passes covered by Three's counters. No public interiors
are resident at the settled aerial view; legacy interior batches are disabled.

`city-lod-high-clustered.json` records pinned **High**, **3010×1544**, 240 samples:
**47.14 mean FPS**, 21.21 ms mean, 17.2 ms median, 44.1 ms p95. Later samples were
36–39 mean FPS with ~117 ms p95, including after collapsing the inventory panel.
The original baseline did not record resolution/quality, and an intermediate
sample had automatically fallen to Lowest. Those runs are not a controlled FPS
comparison. A fixed-High unclustered observation was only 8–11 FPS; clustered
lighting substantially helped it, but did not establish the 60 FPS target.

The engine overlay attributed a later worst spike to **render 144 ms**, compared
with physics 2.8 ms and game/genre 1.2 ms. The panel's CPU render measurement is only
the main-scene submission span, not the whole render/post-processing path or GPU
hardware time. Chrome Task Manager showed the test game's renderer using ~609%
CPU. An initial suspicion of an unrelated tab was disproved. A native stack sample
lacked enough symbols to assign the load to a specific function. No user's tabs
or processes were terminated.

## Validation and limits

- Typecheck passed after material compatibility hardening.
- City regression: batching, PBR factors, world transforms, exact grounding,
  hidden-parent handling, hysteresis, scale rules, editor/shadow separation,
  shadow triangle counts, shared-material lifetime and restoration passed.
- Ground surfaces: 457 checks and 100 eviction cycles passed.
- Hotel transitions: 1,391 checks, sky/seam ownership, door camera collision and
  loading-paint barrier passed.
- Scene metrics: backend counters, instancing/groups, hooks and compact mode passed.
- Final startup verification passed: WebGPU, stable after 4.033 s, playing,
  engine-reported 60 FPS at the starting area, no warnings/failures. See
  `city-lod-verification-final.json`. This is not the dense aerial stress view.

This is not a memory-reduction claim: exact source geometry is retained for
collision/ground queries alongside batched buffers and coarse geometry. Coarse
LOD is deliberately less detailed and may require resort-specific art refinement.
Moving doors and transparent surfaces cannot all be folded into the static draw.

## Outstanding acceptance work

Obtain sustained 60 FPS with controlled camera, resolution and quality; profile the
full render path (including post-processing, shadow work, shader compilation and
GC), and verify a representative driving route plus cold streamed transitions.
The remaining render spikes must not be blamed on triangle count, physics-body
count or other tabs without evidence. Full-resolution High is currently below target.

## Evidence

- `scene-performance-lakefront.json`: original draw-count baseline.
- `city-lod-lakefront.json`, `city-lod-lightweight.json`: intermediate batching runs.
- `city-lod-shared-auto.json`: shared-material run; automatic quality was Lowest.
- `city-lod-high-clustered.json`: explicit pinned-High sample with resolution.
- `city-lod-high-final.png`: final full-detail aerial appearance (metrics collapsed).
- `city-lod-verification-first.json`: initial warmup regression, retained honestly.
- `city-lod-verification-shared.json`: passing shared-material startup check.

Core files: `CityBatches.ts`, `CityAtlas.ts`, `CityLod.ts`, `CityShadows.ts`,
`CityLighting.ts`, `DoorTrim.ts` and the geographic/landmark integration points.
New blocks should provide a stable architectural key to `CityLod`; keep animated
parts, interiors, collision and ground-query registration outside the static batch.

## Small entrance details and bridge follow-up

`CityDetailRanges` groups existing entrance doors and guest ground cores into
160 m cells, with a 240 m range and 12% hysteresis. Selection runs at most every
200 ms after camera movement; it never rediscovers individual pieces per frame.
Identity wrappers preserve each original object's animation and visibility,
physics ownership and parent coordinate system. Late engine door pivots register
through `WorldGroup` child-add events, after their fitting/positioning microtask.
The parked jeep/charger and coaster cars have separate 250 m / 300 m visual
ranges; occupied vehicles remain visible. Large hotel silhouettes are unaffected.

The fixed bridge approach initially used 422 calls. Existing-detail culling
reduced this to 265; asynchronous door registration reduced it further to **174**.
The final view retains 5.12M submitted triangles, 33 full blocks, 237 coarse and
75 culled. The initially missed legacy-door group fell from 111 to 20 main-view
calls. Settled High observations at 3010×1656 were still roughly **17–18 FPS** at
the closed glass door. Opening it and walking inside reached roughly 25–27 FPS;
that is a different view, not a before/after claim. These measurements explicitly
do **not** establish 60 FPS. Do not infer that the draw reduction alone fixed the
remaining full rendering cost, or that the glass is the sole cause.

Live route check: normal interaction opened the bridge door; five seconds of
normal movement crossed from (-68.44,6.07,172.10) to (-68.36,6.10,181.29), remaining
grounded. Automated tests also cover later door registration, fitting transforms,
subscription teardown, exact ground queries and hotel/door-camera transitions.
No runtime scan was added for each new small building. Full driving and cold
interior transition performance acceptance remains outstanding.

Evidence: `city-lod-bridge-before.json`, `city-lod-bridge-after.json` (265-call
intermediate sample), and `city-lod-bridge-final.json` (late-door fix).

Final bridge export: **17.71 mean FPS**, **56.45 ms mean / 53.7 ms median / 165.5 ms
p95** over 240 frames. Game update median/p95: **1.2/1.6 ms**. Main-scene CPU
submission median/p95: **4.5/6.5 ms**. The large unmeasured remainder requires
whole-pipeline profiling; the export is not GPU timing. See
`city-lod-bridge-final.json` and `city-lod-bridge-final.png`.


## Driving-past stalls: light set, interior gate, quiet collision (2026-10-06)

Long pauses (1 to 8 s) when driving near buildings were shader rebuilds, not loading of
geometry. Streaming a landmark interior in or out added, hid or removed four point lights;
three.js puts the id of every visible light in the cache key of every lit shader, so each
change rebuilt every lit program in view (15 to 86, 12 to 50 ms each). Fixed by a constant
shared light pool (`SiteLights`), by not streaming interiors, entrance previews or concourses
for a passing player (`PassingDetector`), and by running ahead-of-need collision loads in the
background (`StreamingWork` `background`). Scripted two-pass drive of the Strip: frames over
1 s went from 6 to 0, the longest from 2.9 s (8.4 s once) to 0.4 s, seconds spent in frames
over 250 ms from 12.5 to 0.4; a real jeep driven by key presses had no frame over 83 ms.
This is a hitch fix; it does **not** claim 60 FPS (mean frame in the headless probe at
640x360 was 17 ms). Evidence, method and what remains:
`streaming-stalls-2026-10-06/README.md` and `runs.json`.
