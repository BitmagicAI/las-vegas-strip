# Proposal: immutable base city with building replacements

Status: proposed for owner review, **not approved or implemented** (2026-10-29).

## Problem

The current scoped installers remove placeholder triangles from city-meshes.json and city-colliders.json. Re-exporting city.glb, repacking collision and rebaking the combined LOD changes large Git LFS objects for each building pass. Batching buildings reduces the frequency but does not remove this cost.

## Recommended design

Keep a versioned base city immutable. During a one-time migration, generate a compact ownership index from the original survey and source geometry: stable OSM building ID to visual triangle ranges, collision triangle ranges and LOD ownership. Roads, terrain and shared surfaces have separate ownership and cannot be disabled by a building replacement.

Each authored building ships its own optimized exterior/interior GLBs, collision data, local LOD and metadata. A small replacement manifest maps its survey ID to these assets. Before constructing render batches or physics colliders, the loader excludes the base ranges for active replacements. Exclusion must also apply to distant geometry and shadows, so the gray shell cannot return at distance. An absent or invalid replacement fails the asset-pack check; runtime fallback restores both the original visible shell and its collision together rather than producing an invisible obstacle or empty hole.

The existing city LOD bake uses combined source plans and signatures. Replace that dependency with independently versioned building/district bake records: replacing one building invalidates only its local record and affected district. Stable source IDs, rather than source-array position, must identify records. Keep the current material sharing, compact vertex formats, lazy near geometry and CPU-buffer release. Do not add per-frame filtering or a shader variant per building.

A PR adding a building then changes only its assets, manifest/metadata and small local LOD records. It does not rewrite city.glb or the base collision file. Shared roads are handled separately through explicit district maintenance, not through a building claim.

## Migration and safeguards

1. Inventory what ownership survives in the current source geometry and how the 98 merged replacements are represented. Do not infer ownership only from bounding boxes; adjacent shells and shared walls need deterministic attribution.
2. Generate and validate the one-time base/ownership data on a dedicated approved infrastructure PR. Preserve the currently published look and collision. Record the one-time LFS bytes separately from ongoing per-building savings.
3. Add manifest-driven filtering before batching and collision construction; create local bake records and dependency hashes. Preserve the current path behind an A/B switch during verification.
4. Verify one isolated building and a district with neighboring replacements at near/far distances, with shadows and collision. Validate fallback, duplicate/conflicting IDs, shared walls, uninstall/rollback, cold-load stalls and memory.
5. Compare identical cameras and real walking/vehicle routes, shader counts, p50/p95 frames, network bytes and peak memory. Run all current release gates and fresh-clone smoke tests before enabling the new default.

## Risks and decision

Ownership may require a one-time re-export because the present GLB groups are not necessarily separable by building. Filtering faces changes batch signatures; local LOD storage must ship with this change, not as an unrelated later optimization. Whole-base downloads remain until a separate streaming/tile proposal is approved. Per-building assets must still be batched to avoid a draw-call explosion.

Approval requested for this design direction and a separately scoped migration PR. No implementation is included in the Westwood/Highland content batch. Until approved, that batch uses the existing pipeline and regenerates the shared files once.
