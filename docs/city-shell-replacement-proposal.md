# Decision: split shared city assets by existing 800 m cells

Status: **implementation started in task #436 from main 288e2ac after PR #433 merged**. Owner decision: 2026-10-29; start authorized 2026-10-30. No infrastructure implementation was included in the building PR.

## Decision and scope

The earlier proposal for an immutable base, ownership index, replacement manifest, runtime exclusion and new local LOD system is **not approved**. Do not implement it.

Instead, split the shared assets along the 800 m cells already used by city.glb:

- Export one city GLB per cell, and partition city-colliders.bin and city-lod.bin along the same cells.
- Preserve the existing face-removal installers, cell/material batching, shaders and bake logic. A building change should rewrite only the cells it touches.
- Preserve unchanged cell bytes exactly so Git LFS stores no new object for them. Prove this with a rebuild that changes nothing.

The owner's sizing at approval was about 90 cells: largest compressed GLB 8.5 MB, median 0.75 MB, compared with 104 MB for the combined file. These are planning figures to verify during implementation, not measured results of a completed split.

## Sequence and coordination

1. Finish and merge the Westwood/Highland building batch using the existing pipeline, including its current shared files and verification gates.
2. Start a separate infrastructure task and PR from the then-current origin/main after #433 merges. Follow the repository claim and PR process.
3. While the split PR is open, continue researching and authoring buildings, but **do not install those buildings into the shared city files**: the installers and split both rewrite those files.
4. Resume installations against the merged split pipeline once it is verified and merged.

## Required evidence before ready

- A no-change rebuild produces byte-identical cell assets. Compare hashes and report any non-cell metadata changes separately.
- Identical named cameras produce the same pictures, including near/far transitions. Collision and actual walking/driving routes remain equivalent.
- No new stalls. Compare matching performance runs and report variability, not only the best run.
- A cold load of the published game is no slower. Many small requests may require grouping cells; measure before choosing grouping and retain the cell-local change benefit. The present task does not authorize publishing; arrange published validation with the owner when needed.
- Report the new Git LFS bytes caused by one representative building change before and after splitting, separately from the one-time migration cost.
- Run the existing repository release gates, including optimization/WebP, current bake, asset-pack validation and fresh-clone smoke/walk checks.

## Current content-batch baseline

Westwood/Highland's staged runtime changes total **147,718,816 new LFS bytes**, of which **4,307,668 bytes** are its two buildings' own models and collision. This is a two-building batch baseline, not the required controlled one-building before/after experiment. Its shared city GLB was regenerated once. The split has not been implemented or benchmarked.

## Implementation checkpoint — 2026-10-30

Claim #436 confirmed for janiverse; branch `task/infra-city-cell-split` starts from `288e2ac`. The read-only baseline audit (`tools/city-cells/audit.py`) confirms 92 existing cell keys, 921 mesh nodes and 5,946,306 triangles in the optimized 109,697,888-byte city GLB. SHA-256: `38e14b86f84980ae8efcaa5697b82c64f9bb4febd67affae7c8c87ec6fb07511`. Detailed local baseline: `.bitmagic/city-cells/baseline.json`.

Collision residency is currently 160 m; preserve those individual records while packaging them under 800 m parent cells. Keep the special `base` visual cell explicit. LOD data also contains other city parts: preserve their part/block identifiers and existing simplification rules. Runtime loading, cell export, collision/LOD partitioning, deterministic rebuild tests and performance comparisons are pending. No runtime assets have changed.

### Export prototype verified — 2026-10-30

`export_city.py --cells --preserve-surfaces` now exports the existing batches into separate GLBs without modifying the combined runtime files. Two Blender runs produced identical hashes for all 92 source GLBs. This is pre-optimization evidence; optimized no-op hashes and render equivalence remain pending. Splitting after whole-city compression was rejected during local prototyping because shared buffer streams duplicated unrelated data.

`tools/city-cells/pack-collision.mjs` packages the unchanged 160 m records under 91 parent cells using the existing codec. Two runs produced identical files: 13,056,416 bytes in total. `check-collision.mjs` verifies all 1,516 records against the committed collision pack: exact decoded positions and the same ordered, oriented triangles. The codec may cyclically rotate a triangle at stream boundaries, without changing winding or geometry. Actual runtime walking is still pending. No LFS assets or runtime loaders have changed.

### LOD and optimization checkpoint — 2026-10-30

`tools/city-cells/lod-files.mjs` partitions the geographic VLOD blocks without decoding/re-simplifying them. All 631 existing blocks retain their bytes; repeated packaging is identical, and a simulated single-city-block change affects only its cell file (`test-lod-files.mjs`: PASS). The prototype retains non-geographic parts together in `other-parts.bin`; their spatial packaging still needs resolution before final integration.

All 92 cell GLBs passed the existing level optimizer: combined candidates 109,926,564 bytes. The WebP pass was invoked and correctly skipped these textureless files. Candidates are not installed or staged. Runtime loaders, optimized no-op rebuild, render equivalence, release checks, cold-load/stall measurements and controlled building-change LFS evidence remain pending.

### Runtime A/B preparation — 2026-10-30

Added a localhost-only `?cityCells=on` path for cell GLBs and collision packs; the default and published paths remain combined. Local candidates are installed using `install-optimized.mjs --only=geographic-strip/cells/ --no-stage`; no release snapshot or LFS assets changed. Type check passed. A composite collision index retains the existing 160 m residency behavior.

Forced re-optimization reproduced identical bytes for all 92 optimized GLBs. Offline decoded comparison passes for all 932 nodes (including 11 empty nodes), with original transforms, metadata, vertex attributes, oriented triangles and material factors. Node order must match Blender's natural name ordering, not alphabetical or scene insertion order; the manifest now records it and the offline check asserts the complete original order.

Initial same-camera before/after screenshots at Lexi were personally inspected and look consistent, but reported mesh/triangle totals differed (325 / 4,461,515 versus 324 / 4,458,549). This is unresolved runtime-equivalence evidence, not a pass. One follow-up was interrupted after concurrent source edits could invalidate its live-reload session; a fresh stable comparison is required. No cold-load or no-stall claim.

### Spatial LOD and deterministic runtime census — 2026-10-30

`node tools/bake/bake-city.mjs cells` now packages the existing LOD without simplification. Non-geographic blocks use their captured bounding-box centers to select the existing 800 m grid; their part/key identities stay unchanged. The current 631 blocks fit in 92 files (20,277,754 bytes), including `base`, with no `other-parts` file. Tests verify exact block bytes, repeatability, isolated one-block changes, negative coordinates and rejection of missing/truncated metadata. This is local output; release integration remains pending.

Using `bake=capture` makes the near batches eager, eliminating lazy-residency timing from the comparison. Matched baseline and split runs both report 535 meshes / 10,117,295 triangles, with identical geographic capture statistics (160 blocks). Canonicalizing codec-permitted cyclic triangle rotation reduces six differing block/level hashes to three, all in cell -2,5. Per-attribute comparison is in progress; do not treat the remaining difference as verified equivalent. Existing default runtime and LFS files remain unchanged.


The residual -2,5 difference was traced to a timestamp boundary, not changed source geometry: its source mtime was 17:14:26.999814 UTC, while Node served `Last-Modified: 17:14:27 GMT`. The optimized-loader comparison floored the fractional manifest timestamp before the server's millisecond rounding, falsely loading the unoptimized source for that one cell. `OptimizedGlb.ts` now rounds to milliseconds before comparing whole seconds. HEAD checks pass for all 92 cells, and the type check passes. The post-fix eager scene comparison is pending below; this narrow loader correction is an explicit infrastructure touch outside packaging.

Post-fix eager comparison **passes**: all 480 oriented block/level hashes, 1,484 vertex-attribute hashes, capture statistics and census counts match the baseline. Evidence: `.bitmagic/city-cells/capture-attributes-before` versus `capture-timestamp-fixed`. The earlier discrepant results are retained as diagnostic history.

The localhost opt-in now loads the 92 spatial LOD files (four requests at a time). Runtime recombination preserves all 759 decoded batches exactly and rejects duplicate identities (`test-lod-loader.mjs`: PASS). Existing city LOD tests and type check pass. The installed opt-in front view was captured and visually inspected after this integration (`lod-runtime-after/front.png`); no obvious difference from the baseline view. This does not substitute for the pending route, cold-load, stall, release-manifest, full no-op pipeline and controlled building-change LFS gates. PR remains draft; no new LFS data is staged.

### Bounded loading and release selection — 2026-10-30

Visual and collision requests now run in groups of four, retaining manifest order before the established node-order sort. Three fresh-browser WebGPU runs per path at the same Lexi front camera produced median readiness **22.183 s combined / 21.850 s split**. Median post-readiness p95 frame time was **33.3 ms for both**; observed maximum post-readiness frame gaps were **166.8 / 166.7 ms**. These short local runs show similar performance, not a guarantee of no new stalls or published-CDN cold-load acceptance. They include startup/UI overhead and shared-machine variability. Raw evidence: `.bitmagic/city-cells/load-{before,after}-{1,2,3}`; reproduce the summary with `node tools/city-cells/report-load.mjs`. The last installed front capture was visually inspected. Type check passes.

`asset-pack.py --city-cells` selects 278 cell files/manifests in place of exactly the three combined assets, leaving the rest of the release inventory unchanged. The normal selection excludes experimental cell GLBs even when the local optimizer manifest contains them. Release cell manifests are generated separately under `.bitmagic/release/cell-manifests` with sizes/hashes of the selected optimized bytes; authoring manifests stay unchanged. `test-release-inventory.py` passes selection, exact selected-byte hashes and no-op checks. Nothing has been staged into runtime-assets or published. The source/export/bake default transition, final snapshot/fresh-clone checks, routes and real one-building LFS experiment remain outstanding.

### Default pipeline migration — 2026-10-30

The working branch now defaults to cells across export, optimization inventory, collision packing, runtime loading, bake packaging and release selection. Combined outputs remain explicit local comparison options only. Collision packaging checks source content and output hashes; all 1,516 decoded records still match the original. Bake validation checks all packaged LOD hashes. The first integrated bake captured 309 parts / 759 batches. A subsequent normal exporter/level+WebP optimizer/install/collision rebuild and bake check left **all 370 source/runtime cell files and manifests byte-identical** (`noop-integrated-result.log`). The unchanged bake remained current; prior forced encoder runs separately proved optimized output determinism.

The migration snapshot contains 278 new files/manifests, leaves 1,636 runtime assets unchanged and removes exactly the three combined files. **One-time new Git LFS bytes: 143,331,940 (278 objects).** This is migration cost, not the pending controlled one-building comparison. Release inventory: 1,914 present, zero missing/unoptimized. Changed runtime GLB gate: all 92 pass. Type check, existing LOD tests, collision equivalence, LOD recombination, release-inventory check, block review and public-file checks pass (one existing email-address warning). `smoke-clone.mjs --shots` against the current dev checkout passed all nine stops, with zero failed requests, page errors, console errors or unplaced stops; the Sphere approach image was inspected. This is current-checkout smoke coverage, not yet an independently populated clone or a walked collision route.

Still required before ready: independent fresh-clone installation, wider matched cameras/actual routes, controlled one-building LFS delta, and published-CDN cold-load/stall evidence. The CDN map still describes the old release. Publishing or CDN upload remains outside this task's authorization; no such action has been taken. Keep PR draft.
