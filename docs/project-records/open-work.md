# Open implementation and refinement work

Status at 2026-10-05. Detailed resort JSON records remain authoritative; this is an
index of work that must not disappear when the active block changes.

## Active — Bellagio

Complete-block exterior pass: fit each structure separately; integrate arrival,
lake-facing low buildings, restaurant patios, pool gardens, conservatory roof,
service facades and bridge/public paths. Record physical elevations and create
walkable connections. Preserve existing detailed guest templates and correct
visibility/collision ownership. The first mapped geometry pass is installed. See the Bellagio record for evidence.

North lakefront follow-up: mapped water basin and terrain cut; varied pavilions,
hipped tiled roofs, arched mullioned glazing, stone balconies, four rotundas and
connecting glazed vaults; shoreline rocks/planting and scalloped Strip promenade.
The bridge enclosure/exit were corrected and the sanctuary relocated to dry
ground. Still refine exact pavilion plans, metric facade heights, shop-specific
ornament/signage, bridge-facing architecture, contemporary landscaping and full
fountain machinery/show. The reference is not yet matched at photographic detail.

Remaining: re-register the old casino/guest cores, verify measured public elevations,
refine lobby finishes and flower ceiling, restaurant-specific fit-out and remaining
terraces, pool cabanas/whirlpools/planting, all service facades, every return route,
and cold-load/memory/performance comparison. No full-completion claim.

## Deferred by creator — Cosmopolitan refinement

- Complete the western connection and private bungalow terrace treatment.
- Confirm eastern bridge continuity and adjacent block ownership.
- Refine crowns, balcony/room alignment, shopfronts, pool tiers and roof services.
- Corroborate estimated public elevations; detail lift/escalator machinery.
- Complete matching reference/game views and all public route/return walks.
- Measure cold transitions, residency and memory, and a comparable performance
  baseline. Warm samples alone are not a complete performance acceptance test.
- Resolve all remaining issues in `tools/resort-blocks/cosmopolitan.json` before
  calling the block fully complete.

## Queued

Paris, then Planet Hollywood; thereafter remaining resort blocks one at a time.
Each includes its smaller frontage buildings, all exterior levels, entrances,
recognizable immediate interiors, public patios/decks and connections.

## Historical requests to retain for regression/polish

Existing project plans and source should be consulted before assuming these are
unfinished: resort-specific streamed corridors/rooms; reference-led entrances and
lobbies; Bellagio stair headroom/pop-in/performance; door camera occlusion; loading
feedback; inactive-tab suspension; jeep exit/camera/ground clearance; complete
road/sidewalk/landscape separation; pedestrian bridge interiors and exits; facade
ownership/z-fighting; distant skyline and haze; Sphere interior/video exterior;
Excalibur/NYNY identity and rideable coaster. These are past requests, not verified
new defects. Preserve their tests and evidence during each architectural pass.

## Repository handoff

Research archive and notes are Git-visible. A clean-clone runnable package still
needs explicit handling of runtime files currently under ignored `build/`, source
survey data and build dependencies. No publish/upload/push is authorized by this
record-keeping request.

### Bellagio lakefront performance observation

Final follow-up startup check passed but reported 24 fps during simultaneous live game QA. Warm promenade sample: 27.3ms median / 31.2ms p95, 1,126 draw calls and 4.58M visible triangles. Profile the complete active scene and compare the earlier baseline before reducing architectural detail. No performance acceptance claimed.

### Metrics-guided optimization queue

On-screen diagnostics are installed; see `scene-performance.md`. At the Bellagio
lakefront: 1,124 renderer draws / 4.37M triangles, of which the new lakefront is
52 draws / 0.94M triangles. Prioritize bridge concourse static trim/material reuse
(181 draws; 168 small meshes), character visibility/LOD (168 draws), city/road
submissions (~407–413 draws), and guest stair/door visibility outdoors (14 draws).
Check legacy collision residency against measured physics CPU time; over 3,000
colliders alone is not proof of a solver bottleneck. Texture/material atlasing can
reduce lakefront batches while preserving detail. These optimizations are recorded
for a subsequent pass and are not claimed implemented by the diagnostics work.


### City performance implementation (2026-10-05)

The prior metrics-guided batching queue is now implemented: compatible opaque city
blocks and the Bellagio village are atlased/merged; bridge trim is batched; distant
characters skip rendering; scale-aware full/coarse/culled block LOD is active.
The lakefront sample is 146 draws versus 1,124, and the village is 2 versus 52,
with all 939,350 nearby village triangles retained. See `city-lod-performance.md`.

**60 FPS acceptance remains open.** Pinned High at 3010×1544 measured 47.14 mean
FPS in one saved run and 36–39 in later runs with large render spikes. Profile
the complete render/post-processing path and shader/GC behavior. Do not present
median-only FPS or automatic quality reductions as success. Confirm long driving
routes, cold transitions and resource lifetime after this architecture change.

### City batching / LOD follow-up — 2026-10-05

- Implemented: architectural batches, shared full-resolution atlases/materials,
  prebuilt coarse geometry, scale-aware block selection/culling, shadow batching,
  small entrance/vehicle ranges and late engine-door registration.
- Measured: lakefront 1124 → 146 draws; village 52 → 2 with original near geometry.
  Bridge additional detail pass: 422 → 174 draws. See city-lod-performance.md.
- Still open: sustained 60 FPS at full-resolution High. Dense bridge remained
  ~17–18 FPS; lakefront controlled High sample 47.14 mean FPS, later 36–39.
  Profile complete render passes and GPU time; distinguish shader/light work,
  transparency/overdraw, shadows, post-processing and runtime compilation/GC.
  Do not assume triangle count or physics bodies explain this gap.
- Preserve the existing visual quality while profiling. Do not silently lower
  resolution, lighting or shadows to label the target achieved.
- Further acceptance: controlled driving loop and cold streamed transitions;
  resort-specific coarse silhouette review; memory ownership under repeated level
  reloads. Exact source geometry currently remains for collision/ground queries.

- 2026-10-06: Replace Bellagio arrival trees with generated realistic asset, then build LODs/instances and retain crown clearance. Generation blocked by exhausted Pro allowance and unapproved spark spending; no charge incurred. Exact garage floor/ceiling measurements remain unverified (authored3.4m spacing/.32m slab).


### Streaming stalls — 2026-10-06 (fixed; remainder)

Driving-near-buildings pauses are fixed (see `streaming-stalls-2026-10-06/README.md`). Rule to
keep: **never add, remove or hide a light after boot** (`SiteLights`, `tests/site-lights.test.mjs`).
Remaining: first-time shader builds when a landmark interior streams in on foot (0.4 to 0.7 s
behind the loading panel; consider time-slicing or a quiet preload as a vehicle slows toward an
entrance); skinned NPC materials near Paris build on first sight; the level's one shadow-casting
spot light and `AfterlightShadows.source.visible` still change the light set on building
entry/exit (one rebuild each; making them constant adds a shadow lookup to every outdoor lit
fragment, a visual/cost call for the creator). Several older tests fail for unrelated reasons
(listed in that README).
