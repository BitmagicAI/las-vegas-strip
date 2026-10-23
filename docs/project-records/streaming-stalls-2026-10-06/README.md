# Long pauses when driving near buildings (2026-10-06)

User report and follow-up comments are quoted exactly in
[journal-2026-10-06.md](../journal-2026-10-06.md) ("Long pauses when driving near
buildings"). This folder holds the measurements. Everything here is local: headless Chrome
against the dev server, nothing published or uploaded.

## Cause

Every long stall coincided, to the millisecond, with the set of lit point lights in the scene
changing by exactly four (46 to 42 or 42 to 46). Those were the four PointLights that
`StripLandmarks` created when it streamed a landmark interior in, switched on and off with
`visible` as the player neared its entrances, and removed again on unload (`SphereVenue` did the
same for the Sphere). three.js hashes the id of every visible light into the shader cache key of
every lit material (`LightsNode.customCacheKey`), so each change invalidated and synchronously
rebuilt every lit shader in view: 15 to 86 programs at 12 to 50 ms each (node-graph build plus
`createShaderModule`), a 0.3 to 3 s freeze, 5 s once on a busy machine. The programs rebuilt were
mostly other buildings' (High Roller cabins, street surfaces, Caesars stone), not the interior that
had been loaded, which is why it felt like "driving near a building".

The engine states the rule ("constant-count light pooling; keeps the scene's light count stable to
avoid WebGPU shader recompiles"); `HotelStreaming` (8 lights), `GeographicPassages` (6) and the
engine's own pool (25) follow it. `StripLandmarks` and `SphereVenue` did not.

Why some stalls had no "Loading…" message: the loading panel belongs to the streaming queue. The
stall that came when a landmark was *unloaded* or its lights switched off (330 to 480 ms, 15 to 26
shader builds) happened outside any job, and the frames after a job hides its panel carried the
rest. About half of the long frames in the baseline had no job overlapping them.

## Ruled out, measured

- Garbage collection: V8 trace over a full drive, 70 scavenges, 231 ms in total, no mark-compact.
- Geometry and texture uploads, physics, the game's update, NPCs, navigation: about 1 ms each in the
  engine's own frame-spike log; the time is all in `render`.
- The machine being over-stressed: a heartbeat worker thread in the page never stalled (worst 52 ms
  over a whole drive) while the main thread stalled for seconds, and the same shader-build counts
  repeated at the same places on every run. Load stretches the stall (the same 44 builds took 1.6 s
  at load average 6 and 2.5 s at 16 to 22) but is not its cause.

## What changed

1. `src/work/SiteLights.ts`: one fixed pool of four lights created at boot, never added, removed or
   hidden, driven by intensity only. `StripLandmarks`, the three resort-block instances and
   `SphereVenue` borrow it. `tests/site-lights.test.mjs` guards the rule (only the three constant
   pools may create a point light; exactly one `SiteLights`).
2. `src/work/PassingDetector.ts`: a player moving faster than 9 m/s, or a vehicle faster than
   3.5 m/s, is "passing" and nothing about interiors is streamed for them: landmark and Sphere
   interiors, entrance previews (`BuildingVisibility`), bridge concourses. A vehicle that slows to a
   stop at an entrance, or anyone on foot, still gets the interior. Exterior collision still loads.
   `tests/passing-detector.test.mjs`, `tests/passing-previews.test.mjs`.
3. `StreamingWork.enqueue(..., {background:true})`: work the player does not need yet (the
   neighbouring city collision cells, a landmark's or high-rise's exterior collision more than 30 m
   away) runs without the loading panel and without holding the game; queueing the same key
   again without the flag upgrades it to a held job. `tests/streaming-background.test.mjs`.

## Results

Same route (the Strip road, z -240 to 1240, 1,480 m), same speed (20 m/s), two passes unless
noted. "Stalled" counts frames over 250 ms. Full numbers: [runs.json](runs.json).

| Run | frames > 100 ms | > 250 ms | > 1 s | longest | seconds stalled | held jobs |
|---|---|---|---|---|---|---|
| Before, 960x540 | 14 | 11 | 6 | 8.4 s | 19.9 | 19 (12.4 s) |
| Before, 640x360 | 19 | 12 | 6 | 2.9 s | 12.5 | 36 (14.1 s) |
| Before, busy machine | 42 | 15 | 6 | 5.1 s | 22.0 | 36 (25.3 s) |
| Constant lights only | 36 | 6 | 0 | 0.57 s | 2.2 | 36 (11.5 s) |
| + passing gate | 1 | 1 | 0 | 0.38 s | 0.4 | 29 (4.2 s) |
| + background collision | 1 | 1 | 0 | 0.40 s | 0.4 | 1 (0.7 s) |
| Real jeep, key presses, one pass | 0 | 0 | 0 | 0.08 s | 0 | 0 |

The one remaining frame over 250 ms is the scripted drive stopping at the LINQ entrance, which
correctly streams that interior behind the loading panel (0.4 to 0.7 s). The "constant lights only"
run still held 36 short jobs (100 to 170 ms each) and the pool existed four times in it (the three
resort-block instances each made their own); the later runs have one pool of four.

## Reproduce

```sh
node tools/probe-streaming.mjs --name run --laps 2 --viewport 640x360     # scripted drive, two passes
node tools/probe-streaming.mjs --name jeep --jeep --viewport 640x360       # the real jeep, key presses
node tools/probe-streaming.mjs --name gc --laps 2 --trace-gc               # with DEBUG=pw:browser, then tools/analyze-gc.py
node tools/probe-heap.mjs --name heap --drive                              # live heap by allocation site
```

`?probe` on a localhost page exposes `window.__afterlightProbe` (teleport, streaming history, the
renderer, the jeep). It is gated like the other local review parameters and never exists on a
published page. Reports land in `build/probe/` (not archived; `runs.json` here is the distillation).
Do not run two probes, or a probe and `bitmagic verify`, at once: each is a GPU-bound Chrome.

## Still open

- First-time shader builds for materials that really are new (a landmark interior's own materials,
  about 4 to 10 programs, 150 to 400 ms behind the loading panel on arrival; the skinned NPC
  materials near Paris, 35 to 40 ms each the first time they are seen).
- Entering or leaving the building that contains the level's one shadow-casting spot light changes
  the visible-light set (`BuildingVisibility` hides it with `visible`), as does
  `AfterlightShadows.source.visible`. Not seen on the drive; expect one rebuild per entry or exit.
  Making them constant costs a spot-shadow lookup in every lit fragment outdoors: a visual/cost
  decision, left alone.
- Interior streaming on arrival still holds the game behind the panel (0.4 to 0.7 s). It could be
  time-sliced, or preloaded quietly as the player slows toward an entrance and held only if they
  get there first.
- `tests/building-visibility.mjs` (fixture zones lack `geoTransform`), `tests/player-grounding`,
  `player-presentation`, `sanctuary`, `shadow-casters`, `supply-loop` and
  `tools/test-hotel-transitions.mjs` already failed before this work for unrelated reasons (stale
  fixtures, JSON import attributes under Node 25, a moved import).
