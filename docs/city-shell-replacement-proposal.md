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
