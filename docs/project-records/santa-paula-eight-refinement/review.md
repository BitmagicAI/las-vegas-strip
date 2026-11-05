# Santa Paula: eight-building frontage refinement

PR #515, issues #174/#175. This is a limited frontage correction; all eight buildings remain refinement-deferred. Reference provenance, inferred dimensions and design decisions are in [research.md](research.md).

## Per-building changes

- 1807: three-row unit/address board, gray painted stair metal with vertical infill and a slender landing-roof post.
- 1811: stair metal now uses the pale painted finish; original tree retained.
- North olive building (modeled 1703): two-rail frontage fence with heavier interval posts.
- Blue/cream 1707: two-rail frontage fence with heavier interval posts.
- Gray 1711: pale metal fence with pointed caps, two rails and interval posts.
- Cream gable (modeled 1715): removed the unsupported fence across its open parking frontage.
- Charcoal gable (modeled 1721): removed the unsupported fence across its open parking frontage.
- Purple/white south building (modeled 1725; satellite label 1727): lower two-rail fence with interval posts. Address discrepancy retained.

## Preservation and scope

Both source collision JSON hashes unchanged; all five existing 1807 tree nodes retained. No roads, map ownership, runtime optimization code, existing interiors or other buildings intentionally changed. Shared venue/version/LOD data were regenerated for this group; unrelated Gold Coast and Wyndham LOD differences were restored. The first capture was canceled to correct the sign position before any staging; one completed grouped bake was installed. No public interior established by the references. Third-party photographs are linked only; committed images show the original game geometry.

## Local validation

Baseline: seven matched neutral-daylight views; 1,454 support samples, 40 CPU stair legs and 40 installed keyboard legs passed. Sixteen endpoint images inspected; north return endpoints 1 and 5 face a nearby wall, retained with their position/height checks rather than presented as clear outward views. Performance is static at 960×540, DPR 1, ultra, 900-frame warm-up plus streaming quiet and 60 settle frames, 180 timed frames per view; not a driving benchmark or sustained 60 fps evidence.

After installation, all 40 keyboard legs passed again and all 16 endpoint images were inspected. Seven identical-camera daylight views were inspected before and after. Nine dev smoke stops were placed, with zero failed requests, page errors or console errors. Typecheck, three runtime tests, both model optimization checks, bake freshness, asset-pack integrity and block-record review pass; public check reports zero failures and 11 existing warnings. 91/92 city cells stayed byte-identical; only cell-2_-5 changed. The repeated warm performance diagnostic passed; final Git LFS audit is recorded in lfs-audit.json.

## Remaining discrepancies

Original approximate roof/window proportions, roof-service equipment, side/rear door positions and gallery/stair layouts remain. Olive frontage door and gray entry/gallery arrangement differ from the generic modeled front. Gardens remain sparse; tree/shrub placement, chain-link fence detail, gate layouts and frontage heights require further work. No residential interior, complete site circulation or driving benchmark claim.

## For the release step

CDN availability and the published-game check belong to the owner's release step. No CDN assets uploaded, publishing performed or release/main changes made.

### Initial matched performance discrepancy

The north-row front measured p95 20.8→31.1ms (+49.52%) after the original 900-frame warm-up. Other six matched views improved in this run. This sample is retained in performance.json; it cannot be described as a passing performance comparison. A browser-only exact-old-assets A/B diagnostic ran after then before, with 1,800-frame warm-up and ten 180-frame windows. Median window p95 was 18.0ms before and 17.9ms after (−0.56%); each after window was 17.7–18.2ms. Required north GLB and cell interceptions were verified. No sustained increase appeared in that warmer diagnostic, but it does not explain or erase the initial spike or guarantee startup behavior. No live assets were reverted.

## Matched views

| View | Before | After |
|---|---|---|
| santa-paula-1807-1811 front | [before](../../../public/review/santa-paula-eight-refinement/before/santa-paula-1807-1811-front.png) | [after](../../../public/review/santa-paula-eight-refinement/after/santa-paula-1807-1811-front.png) |
| santa-paula-1807-1811 roof | [before](../../../public/review/santa-paula-eight-refinement/before/santa-paula-1807-1811-roof.png) | [after](../../../public/review/santa-paula-eight-refinement/after/santa-paula-1807-1811-roof.png) |
| santa-paula-1807-1811 court | [before](../../../public/review/santa-paula-eight-refinement/before/santa-paula-1807-1811-court.png) | [after](../../../public/review/santa-paula-eight-refinement/after/santa-paula-1807-1811-court.png) |
| santa-paula-north-row front | [before](../../../public/review/santa-paula-eight-refinement/before/santa-paula-north-row-front.png) | [after](../../../public/review/santa-paula-eight-refinement/after/santa-paula-north-row-front.png) |
| santa-paula-north-row south | [before](../../../public/review/santa-paula-eight-refinement/before/santa-paula-north-row-south.png) | [after](../../../public/review/santa-paula-eight-refinement/after/santa-paula-north-row-south.png) |
| santa-paula-north-row roof | [before](../../../public/review/santa-paula-eight-refinement/before/santa-paula-north-row-roof.png) | [after](../../../public/review/santa-paula-eight-refinement/after/santa-paula-north-row-roof.png) |
| santa-paula-north-row gallery | [before](../../../public/review/santa-paula-eight-refinement/before/santa-paula-north-row-gallery.png) | [after](../../../public/review/santa-paula-eight-refinement/after/santa-paula-north-row-gallery.png) |
