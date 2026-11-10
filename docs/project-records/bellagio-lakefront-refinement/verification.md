# Bellagio north-village ornament pass

Five existing pavilion frames receive original shallow stone ornament. This is a bounded refinement, not full Bellagio completion. Research and inferred dimensions are in [research.md](research.md); matching game images are in [captures.md](captures.md).

| Pavilion center X/Z (metres) | Cornice dentils | Framed oval medallions |
|---|---:|---:|
| -146 / 245 | 104 | 2 |
| -119 / 237 | 86 | 2 |
| -90 / 230 | 84 | 2 |
| -52 / 201 | 38 | 0 |
| -39 / 190 | 36 | 1 |

The existing Via Bellagio circulation mask excludes conflicting decoration. End-wall medallions avoid long-face shop signs. The pass adds 10,112 triangles in one material group, using the existing stone material. All 265 original mesh groups and 42 labels are retained exactly; authored and runtime collision remain byte-identical. The separate PR537 arcade and curved roofs are preserved.

The selective export was optimized with level and WebP passes before installation (both exit 0). The installed GLB is 49,160,292 bytes; the raw source is 139,568,644 bytes. The revision changed; see revision.json. One shared bake changed only the lakefront-village LOD block. Known unrelated Gold Coast/Wyndham bake differences were restored. 91 of 92 cells remain byte-identical; only cell--1_0 changed.

All 11 local checks pass: typecheck; block review; public-file check; city LOD, lighting-resize and site-lights tests; independent facade-support audit; changed-GLB optimization check; bake freshness; asset-pack check; reload. The initial review failed on a missing historical source access date; the dated owner-reference metadata was repaired and review passed. The support audit projects every new vertex onto exactly one retained coplanar facade. All 10 before and 10 after movement legs pass; four after endpoint/return images were inspected. These walks cover the north promenade and casino approach, not an escalator ascent or full public-interior route. Nine-stop dev smoke passes with zero failed requests, page errors, console errors or unplaced stops.

Three neutral daylight before/after views use identical cameras, names, viewport and settings; exterior front is first. Closer west/east views show cornice detail while the distant silhouette stays stable. Existing bay/proportion/dome discrepancies and reversed-looking shop signs remain recorded.

## Performance limits

All values below are p50/p95 milliseconds, same 960×540 DPR1 ultra settings, 900 warm-up frames, streaming idle, 60 settling frames and 180 timed frames. No concurrent GPU probe ran.

| View | Earlier original baseline | Installed after | Contemporary original control |
|---|---:|---:|---:|
| Front | 20.9 / 26.9 | 39.0 / 45.7 | 39.9 / 49.3 |
| East | 23.3 / 40.9 | 36.6 / 46.1 | 36.4 / 50.6 |
| West | 29.7 / 48.8 | 48.7 / 57.2 | 58.0 / 71.0 |

The initial apparent slowdown required investigation. Browser-only routes then served the original optimized GLB and original cell, with three GLB and one cell replacements confirmed. The control image visibly restores the undecorated facade. That original control also slowed substantially. Installed medians are within 1% or lower and p95 lower than this contemporary control. This does not establish an improvement: machine/session variation remains, and full-block 60fps, cold-load and guest-return acceptance remain open.

## Decisions and release boundary

Keep the reversible additive details and existing massing, signs, circulation and interiors. Historic photographs support permanent ornament forms, not current tenant identities. Ornament measurements are inferred. All broader gaps and pending gates remain in bellagio.json, with explicit reasons in remaining. CDN, published-game and owner-dependent checks belong to the release step; no publishing, upload, release, main merge or repository setting change is part of this pass.
