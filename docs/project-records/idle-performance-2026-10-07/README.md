# Idle frame rate: foliage at 5 fps, 20-40 fps standing still (2026-10-07)

Owner report (summary): the game ran at 5 fps with foliage and trees on, and at 20 to 40 fps standing still with them off; profile it.

Owner comment during the profile (summary): use no JS arrays at runtime (and almost never elsewhere): their overhead is large.

Profile first (sections 1-3), then the fixes (section 4, same day). Numbers are from headless Chrome 153 (WebGPU on Metal) on the
owner's Mac (M5 Max), at the spawn point (-60, 0.4, 540) with no input. The owner's real window was
reproduced: 1505×772 CSS px at devicePixelRatio 2, so a 3010×1544 drawing buffer with 4× MSAA. Data:
[runs.json](runs.json), [full-res-summary.txt](full-res-summary.txt), [grass-summary.txt](grass-summary.txt),
[memory-summary.txt](memory-summary.txt).

## 1. Foliage: the grass, not the trees

GPU time per frame comes from WebGPU timestamp queries.

| Scenario at spawn | FPS | GPU ms/frame (p50) |
|---|---:|---:|
| Foliage on | 25 | 60 |
| Tree shadows off | 25 | 60 |
| Trees hidden | 26 | 62 |
| Grass hidden | 46 | 12.5 |
| Foliage off | 45 | 12.6 |
| Foliage off, half resolution | 55 | 7.2 |

The grass adds 0.88 M triangles but ~48 ms of GPU time per frame. Taken separately, and measured
without timestamp queries:

| Lawn variant | FPS |
|---|---:|
| Normal | 26.8 |
| Near grass (LOD0, ≤14 m) hidden | 39.7 |
| Far grass (LOD1) hidden | 31.5 |
| All grass drawn with an unlit basic material | 39.7 |
| No grass | 41.7 |

The cost is the lit PBR shader: MeshStandardMaterial with normal and emissive maps, the shadow-map
lookup and clustered point lights. It runs for every fragment of thin, overlapping blades, mostly in the
near grass. Rasterising the same blades with a cheap shader costs about 2 fps. The spawn camera looks
slightly upward. Standing in the lawn and looking level or down multiplies the grass coverage, which
matches the owner's 5 fps. The trees (LOD0: 250 k triangles each) cost nothing measurable from spawn.

**Correctness bug found on the way.** At boot, every lawn and tree group is hidden although the player
stands in the garden. They reappear only once the player moves far enough to change a cell's LOD, or
when the foliage checkbox is toggled. Cause: `GameEngineWarmup.warmUpSceneNow` records the objects that
are hidden, forces them visible, and restores them about 50 s later. `ResortFoliage.select` (and
`GroveLod`) chose LOD levels in between, so `cell.level` says "LOD0 shown" while the warm-up has hidden
the group again, and `select` skips cells whose level did not change. Trap log: `runs.json`
→ `foliageWarmupTrace`. The same pattern can affect any LOD system that caches the visibility it set
(`CityDetailRanges` caches `cell.visible`).

## 2. Foliage off: garbage-collection pauses on a nearly full process

Foliage off, standing still: 41-45 fps. Most frames take 16.7 ms, but 8-15% take 33-200 ms. Rendering
is not the cause: those frames have ~13 ms of rAF CPU and 9-20 ms of GPU time. A Chrome trace shows each
long frame is a **V8 full mark-compact inside the frame**.

- Standing still for 10 s: 56-86 mark-compacts (6-8 per second), 30-125 ms per pause (mean 43 ms),
  ~300 ms of main-thread pause per second. No cheap young-generation scavenges at all.
- Each collection frees only ~6 MB. The memory is live.
- V8's global accounting (JS heap + ArrayBuffers + native memory reported to V8) stands at 9.6 GB.
  Above 8 GB, V8 sets the next limit just above current use: the limit was 8,192 MB with 9.6 GB in use,
  or 7-26 MB above use. So every few MB allocated starts the next full collection. Reasons recorded:
  "global allocation limit reached" and "external memory pressure".
- Idle allocation is ~47 MB/s of JS objects, so a collection every ~100 ms of script time.

What fills the process (Chrome memory-infra dump of the game's renderer, plus a scene walk):

| Holder | Size |
|---|---:|
| ArrayBuffer partition (typed arrays) | 4.1 GB |
| — CPU copies of scene geometry (already uploaded to the GPU) | 3.0 GB |
| — of which city-batch vertex attributes (`batchAtlas`, `batchEmission`, `batchPbr`, `batchWrap`, `color`) | 1.45 GB |
| — largest owners: OSM Strip 1.1 GB, Paris 322 MB, Bellagio exterior 240 MB, lakefront 221 MB, Polo Towers 203 MB | |
| 2D canvases: the city texture atlases (`CityAtlas.makeCityAtlas`, up to 8192×4096 = 128 MB each, kept as `CanvasTexture.image` after upload) | 1.58 GB |
| V8 heap (JS objects) | 0.74 GB |
| malloc / GPU mapped memory | 0.64 / 0.47 GB |
| Texture ImageBitmaps in the scene | 0.38 GB |
| Rapier WebAssembly memory | 40 MB |

About 6.4 GB of V8's 9.6 GB is attributed above; the rest is native memory not yet broken down.
The GPU process separately holds ~7 GB (normal GPU memory, outside V8's accounting).

Experiments that rule things out:

- Dropping the CPU copy of every geometry attribute that has a GPU buffer (1.45 GB): usage went to
  8.2 GB, the limit to 8,192 MB, collections 86 → 68 per 10 s, 41 → 44 fps. Not enough on its own: the
  process is still above 8 GB.
- WebGPU timestamp readback (this probe's own instrument) adds collections. Without it there are still
  60 per 10 s, and all conclusions above hold.
- Pausing the Sphere video: 60 → 58 collections, 44 → 48 fps. Minor.
- Not the light set (no light changes while standing), not streaming jobs.

Top idle allocation sites (sampled, MB/s): `BuildingVisibility.contains`/`pointVisible` (per-call
`exteriorVoids.some` closures and `find` iterators, ~10), engine `PhysicsWorld.quarantineSanitizePass`
(walks every rigid body each substep, allocating translation/rotation objects, ~9.5; engine code,
read-only here), `SkylineDepth` sort comparator (1.5), `VegasCast.activityRouteClear` NPC raycasts (1.4 +
0.5), `StripLandmarks.update` (1.1), three.js render internals (~5).

## 3. Steady-state budget, foliage off, full resolution

- CPU in rAF ~12-13 ms per frame. Hot spots are spread: `updateMatrixWorld` 2.2 ms (every object's matrix,
  every frame), `_projectObject` culling 0.7 ms, object rendering ~2 ms.
- GPU ~12 ms: scene pass 7 ms (3010×1544, 4× MSAA), post/output 5 ms, shadow map 0.8 ms. Half
  resolution: 7 ms.
- Both fit the 16.7 ms frame. The 60 fps cap only drops frames the GC has already delayed.

## Fix candidates, in order of effect (none implemented)

1. **Grass material**: a cheap lawn shader (no normal/emissive/roughness maps, no clustered point lights,
   a single sun term, at most one shadow tap), plus fewer, wider near blades. Measured ceiling: grass
   at near the no-grass frame rate.
2. **Get the renderer process well under V8's 8 GB global mark** (target ≤ 6 GB):
   - release city-atlas canvases after upload (or bake atlases offline as compressed textures): −1.6 GB;
   - pack city-batch factors as a small per-vertex material index into a table instead of four
     float vec4s per vertex: −1+ GB of CPU memory and the same in GPU memory;
   - drop CPU geometry copies after upload where nothing reads them (ground index and colliders keep
     their own data): up to −3 GB.
3. **Idle garbage** (owner's rule: no JS arrays, no per-frame array/closure churn): flatten the
   visibility zones into typed arrays and test them with loops; reuse scratch objects in the skyline sort,
   NPC route checks and StripLandmarks. Report the engine's per-substep sanitize pass upstream.
4. **Warm-up / LOD desync**: LOD systems should re-apply visibility from their level rather than trust a
   cached level (or re-select after the warm-up finishes).
5. Optional: render scale below devicePixelRatio 2 on Retina (half resolution measured 55 vs 45 fps,
   foliage off).

## Tools

- `node tools/probe-idle.mjs --name <run> [--viewport 1505x772 --dpr 2] [--scenarios a,b] [--trace a,b]
  [--profile] [--no-timestamps] [--trace-foliage]`: standing-still scenarios with frame interval, rAF
  CPU, per-pass GPU time, Chrome trace (GC and long tasks), CPU profile.
- `node tools/probe-memory.mjs --name <run>`: Chrome memory-infra breakdown, scene geometry and texture
  accounting by owner, idle allocation by site.

Both are local-only, use one headless Chrome and close it in `finally`. Output goes to `build/probe/`.

## 4. Implemented (2026-10-07, same session)

Owner request (summary): do steps 1 to 3, use the most efficient vertex formats, and optimize every GLB with the asset-optimization skill.

All numbers: headless Chrome, WebGPU, 3010×1544 at DPR 2, `?quality=ultra` pinned (the engine's
auto tier dropped to High mid-run in early captures, so those were re-taken).

### Results

| Measure | Before | After |
|---|---:|---:|
| First person in the garden (spawn, eye level) | 5.5 fps | 60 fps (vsync cap) |
| Among the trees | 6.2 fps | 60 fps |
| West view (jeep and charger close up) | 7.6 fps | 45.9 fps |
| Standing still, foliage on (spawn camera) | 23-25 fps, worst frame 583 ms | 60 fps, worst 16.8 ms |
| Standing still, foliage off | 41-45 fps, frames up to 500 ms | 60 fps, one 33 ms frame in 30 s |
| Strip, Paris, skyline views | 48-53 fps | 60 fps |
| Full garbage collections, 10 s standing still | 56-86 (30-125 ms each) | 0 |
| Young collections | 0 | 8-15 (about 1 ms each) |
| Render-loop CPU per frame | 12-13 ms | 7.7-8.6 ms |
| V8 heap / typed arrays / canvases | 0.70 / 4.04 / 1.58 GB | 0.34 / 1.07 / 0.08 GB |
| City geometry kept on the CPU | 3.0 GB | 0.6 GB |
| Idle allocation | 47 MB/s | 21 MB/s |
| Runtime GLB downloads (441 files) | 1,862 MB | 764 MB |
| Jeep drive, 1,480 m on the Strip | | 16.7 ms mean, one 100 ms frame, none over 250 ms |

`bitmagic verify` passed (settled in 4.0 s, 60 fps; earlier sessions recorded it failing at Play
detection with the menu at ~30 fps).

### What changed

1. **Foliage.** Garden trees and lawn keep their standard materials (identical look: lawn mean
   colour equal within 0.1 of a grey level) but are lit by a fixed list: the focused sun with its
   shadow, the hemisphere and the ambient light (`ResortFoliage.ts`). No point light reaches the
   garden (nearest 88 m away, range ≤ 24 m); a load-time warning fires if that ever changes. The
   engine's start-up warm-up restored stale visibility under four LOD systems, leaving the garden
   (and potentially city blocks) hidden until the player moved: `ResortFoliage`, `GroveLod`,
   `CityLod` and `CityDetailRanges` now re-assert the visibility their level implies and pause during
   the warm-up. Leaf cut-outs use `alphaTestNode` + `maskShadowNode` (see the churn note below).
2. **Memory.** City batches: 88 → 32 bytes a vertex (40 for glossy/metal buckets, which keep float
   normals), surface factors in one shared table texture (`citySurfaceTable`), built straight into
   typed arrays; coarse LODs built with numeric cluster keys; CPU copies of batches, coarse LODs and
   shadow batches released once the GPU holds them (`CpuGeometryRelease.ts`, per attribute, index
   kept, paused during warm-up); merged source meshes drop their geometry; city atlases upload as
   they are built and free their canvases; `GroundSurfaceIndex` rewritten on flat typed arrays with
   its own copy of walkable triangles (it used to pin the source vertex buffers).
3. **Idle garbage.** `BuildingVisibility` zones precompiled into `Float64Array` tables (differential
   test: 577,600 zone tests and 15,200 visibility states identical to the original), the state
   computed once per update; NPC route checks cached and allocation-free; `StripLandmarks.update`,
   hotel transforms and NPC activity timing without per-frame closures or destructuring; render-list
   comparators return -1/0/1 (a fractional result is boxed on every comparison).
4. **GLBs.** The optimizing-assets skill's `optimize-glb.mjs` (CLI 0.1.81, unpatched; offline tools
   reused from Arcade Tycoon, no download): `level` preset for architecture, interiors and hotels,
   `code-driven` for the jeep and train, `hero-prop` without KTX2 for the trees. Float positions,
   int8 normals, 16-bit UVs where they fit, meshopt, separate layouts. Copies live in
   `build/optimized/` with a manifest; `glbUrl()` serves a copy only while its source is unchanged
   (size and modification time), so pipelines that regenerate or patch the originals keep working.
   A meshopt decoder shim (`GltfDecoders.ts`) covers every loader. Visual A/B on ten fixed views:
   mean difference ≤ 0.13 grey levels where the camera settled identically.

### Tried and rejected (measured)

- Scene-wide clustered lighting (three's `ClusteredLighting` for every material): measured slower on the
  layered lawn (spawn 7.6 → 4 fps) and reverted. Correction (2026-10-08): that A/B swapped
  `renderer.lighting` at runtime, which three r185 does not apply cleanly, so the result is not reliable.
  Installed at boot, clustered lighting runs the full-list garden at 60 fps. The engine's batched
  lighting is the better path; see `lighting-analysis-2026-10-08`.
- A Lambert lawn with world-up normals: fast, but the lawn lost the low sun's warmth (red channel
  127 → 95). Rejected for the look; the standard material with the fixed light list is exact.
- snorm16 normals for glossy batches: camouflage blotches on the Paris balloon. Float instead.
- Fewer, wider grass blades: not needed once shading was fixed; the lawn stays as approved.

### Found on the way

- Making the trees visible exposed a three r185 trait: the shadow pass copies each caster's
  `alphaTest` onto one shared material whose version bumps whenever it switches between zero and
  non-zero, so every shadow caster rebuilt its pipeline key every frame (~92 a frame, ~45 MB/s).
- three r185's `MeshStandardNodeMaterial.copy()` drops `alphaTest`.

### Not done (decisions for the creator)

- Characters (9): only a texture-only WebP variant is possible (their required sparse-correctives
  extension blocks the encoder); they load from registered bitmagic.ai URLs, so using it needs new
  asset uploads and an up-close face review.
- The published level asset (`level-vegas`, remote) and the 15 placeholder stubs (not smaller).
- Indices stay on the CPU (~0.3 GB), per the engine's rule about re-bound geometry.
- Remaining idle allocation is mostly three's render bookkeeping and the engine's per-substep
  physics sanitize pass (~3.5 MB/s; engine code, read-only here).
- An optional lossy WebP-texture variant (hotels 298 → 117 MB) exists in `.bitmagic/optimize/` and
  is not installed: it needs its own A/B.

## 5. Lossy WebP textures (installed, 2026-10-07)

Owner request (summary): use the lossy textures, and keep a backup of the originals.

- Installed `--variant=webp-textures` (colour and emissive maps lossy WebP q90 at their own size,
  ORM maps lossless WebP, normal maps kept): 450 runtime GLBs, **1,864 → 522 MB** on disk (the lossless
  optimized set was 764 MB). Nine placeholder stubs the lossless pass could not shrink now shrink.
  Characters excluded (remote registered assets, faces not reviewed).
- Backups (`~/Development/GitFork/_backups/`): `vegas-afterlight-2026-10-07-glb-originals`
  (all 465 original runtime GLBs at their project paths, SHA256SUMS, 1.9 GB; the game never modified
  them, they also remain in place) and `vegas-afterlight-2026-10-07-glb-optimized-lossless` (the
  previously installed lossless set, 765 MB, with restore instructions).
- Switch back to lossless textures: `node tools/optimize/install-optimized.mjs --variant=level`.
- A/B against the lossless set on 15 views (10 street, Bellagio/Caesars/Cosmopolitan corridors, a
  Bellagio bedroom, the Wynn lobby; the corridors had the lowest per-texture PSNR, 32.6-34 dB): 13
  views 42-63 dB PSNR with no pixel off by more than 16; the two lower ones (skyline, Cosmopolitan
  corridor) are a camera offset (edges only), and a full-resolution crop of the corridor carpet shows
  the same fibre detail. GPU memory is unchanged (textures decode to the same size); frame rates
  unchanged within noise. Capture script: `sh tools/capture-texture-ab.sh <prefix>`.
- Found while capturing: hotel interiors run 20-33 fps at 3010×1544 even with few triangles (Caesars
  corridor 54k). Not investigated yet.
