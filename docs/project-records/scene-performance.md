# Scene performance diagnostics

Implemented 2026-10-05. The top-left **Performance** panel is available during normal gameplay and local review. Click its header to collapse/expand; the choice persists. Expanded mode samples mesh submissions once per second and updates text twice per second. Collapsed mode retains FPS/draw totals and stops scene inventory scans and mesh instrumentation. It adds no animation loop; existing inactive-tab suspension applies.

## Reading the counters

- **Objects loaded / meshes:** scene graph nodes and mesh nodes, including hidden objects. A group is an object; an instanced mesh remains one mesh.
- **Enabled / drawn:** enabled meshes have visible ancestors, a matching camera layer and a visible material. This does not mean they pass the frustum or are unoccluded. Drawn meshes actually produced main-camera draw submissions in the sampled frame.
- **Draw calls / triangles:** renderer counters at main-scene completion. WebGPU uses `drawCalls`, not lifetime `calls`. Triangles include repeated instances and renderer passes included in that counter. These are submitted triangles, not visible pixels or Blender polygon counts.
- **Component breakdown:** actual main-camera mesh callback counter deltas, including material groups and instancing. Shadow/other passes can make overall renderer totals larger. The table shows the eight largest components; snapshots include all rows. Totals and rows update at different intervals.
- **Small:** submitted mesh objects with fewer than 100 base-geometry triangles. A heavily instanced mesh can be small by this definition but contain many instances.
- **Resources:** unique scene geometry/material identities; GPU geometry/texture counts are renderer-managed allocations, not byte estimates.
- **Lights:** visible positive-intensity lights on a camera layer, not all fixtures or all lights affecting a pixel.
- **Physics world:** all rigid bodies/colliders, not merely the active resort loader. A large static body count alone does not establish expensive physics.
- **Interiors:** separately shows submitted tagged interior geometry, enabled legacy interior batches, resident public interiors and guest stair/corridor/room instances. Doors and room-number signs have explicit guest ownership. Mixed indoor/outdoor bridge concourses have their own component. Unclassified objects remain in Other.
- **CPU:** game update and main-scene render submission spans. Neither is GPU timing or complete frame CPU time. Frame median/p95 covers up to 240 recent rendered intervals; long suspension gaps reset the frame window.

**Save metrics snapshot** downloads JSON containing all component rows, camera position, backend, streaming state, physics totals, sample time, CPU/frame percentiles and counter scope. Inventory scans were about 1–3 ms once per second in the sampled scene. Profiling itself has a cost; collapse the panel for a lighter comparison.

## Lakefront findings

Aerial review at player coordinates (−3,45.24,283), WebGPU:

| Component | Main-view draws | Triangles / details |
|---|---:|---|
| Overall renderer | 1,124 | 4,365,814 |
| Bellagio lakefront | 52 | 939,350; 22 loaded materials |
| OSM city / roads | approximately 407–413 | approximately 2.32–2.39M |
| Bridge concourses | 181 | 27,614; 168 small meshes |
| Characters | 168 | 199,260 |
| Legacy city / resort shells | 127 | approximately 176.85K |
| Bellagio exterior / arrival (excluding lakefront) | 54 | approximately 509.92K |
| Public entrance doors | 36 | 432 |

No public interiors were resident at the settled lakefront view. Tagged guest interior geometry still submitted 14 draws / 1,448 triangles. No legacy interior batches were enabled. All-world physics remained at 3,076 bodies / 3,085 colliders. Those are residency counts, not measured solver cost.

The village is already batched and is not the largest draw-call source. Getting its 22 materials into a handful of draws requires texture atlases/material consolidation or a different batching representation. Preserve visual detail and spatial culling. Bridge concourses are a particularly clear candidate for shared materials and merged/instanced static trim. Characters need distance/visibility review; their parts currently account for many submissions. Measure these independently before changing quality.

## Validation and limits

`bitmagic check` and `bitmagic verify` passed. Focused regression test: `node --experimental-transform-types --experimental-loader ./tools/geographic-strip/test-loader.mjs tools/test-scene-metrics.mjs` passed. It covers hidden parents/layers, shared assets, backend counter differences, grouped instancing and callback cleanup, plus collapsed mode.

Startup verification reported 24 fps during simultaneous live-game testing. This is a diagnostic pass, not a performance acceptance claim. Geometry, material quality and draw distance have not been reduced.

## Saved evidence

- [In-game panel](scene-performance.png)
- [Downloaded lakefront snapshot](scene-performance-lakefront.json)
- [WebGPU startup verification](scene-performance-verification.json)

The export button was exercised in Chrome and the downloaded JSON preserved here. Header collapse/expand also worked in the live game. Final isolated live QA after verification ended was roughly 42–47 fps at this fixed aerial view; this is a host/view observation, not a general performance guarantee.
