# Carpets Galore and Rexford courtyard refinement

Two mapped structures; scoped exterior detail pass, not full-block completion. Matched verification, performance investigation and nine-stop smoke check passed.

Carpets Galore: four small roof-mounted sign flood housings above the two west fascia runs, with non-emitting faces and existing materials. North pale-blue painted finish reviewed under neutral daylight. Rexford: a thin outer roof lip follows the existing rounded footprint. All dimensions are inferred; see research.md for dated references and decisions.

One grouped bake, level plus WebP optimization for both models. No runtime lights, roads or interiors changed. Both source collisions retain their exact baseline hashes. Unrelated Gold Coast and Wyndham LOD regeneration restored;91/92 cell binaries remain byte-identical, onlycell2_-5 changes. Shared cell manifest and asset pack are the necessary out-of-scope data touches.

Before and after:1378 source support/headroom samples,12CPUgroundlegs,6CPUstairs and18actual installed keyboard walk legs pass. All7matched daylight views and6afterwalk endpoint images inspected. The existing Blender rail validity warning produced no missing rails in the installed court/gallery/stair views. Typecheck,3regressiontests, recordreview, optimization2/2, bake freshness and assetpack1930present pass. Public-content check0failures,11existingwarnings. Smoke:9/9 stops placed,0failed requests/page errors/console errors. New Git LFS16,244,597bytes in41uniqueobjects across all own commits, including baseline, after and A/B proofs.

## Performance discrepancy retained

960×540,DPR1,ultra;900warmframes,streaming quiet+60settle,180samples/view. Carpets aerial initialp95 increased48.3%; the other6views remain within10% or improve. Five-window browser-only original-asset A/B completed, intercepting all three baseline assets without changing live files. The aerial spike was not sustained: median17.5→18.6ms (+6.29%), with after windows18.3–18.9ms. All seven median p95 comparisons stay below10%; north has one21.6ms window, retained in the raw results. All14A/B screenshots inspected. This supports a short timing spike in the initial aerial sample, not a persistent48.3% geometry cost. No sustained60fps, perimeter driving, coldtransition, GPUspan or residency claim.

|Building/view|Beforep95ms|Afterp95ms|
|---|---:|---:|
|carpets-galore front|18.3|17.8|
|carpets-galore carpets-north|25.1|19.8|
|carpets-galore carpets-aerial|18.0|26.7|
|rexford-courtyard-1701 front|17.5|17.9|
|rexford-courtyard-1701 rexford-court|18.4|19.0|
|rexford-courtyard-1701 rexford-gallery|17.9|18.9|
|rexford-courtyard-1701 rexford-aerial|34.2|19.6|

## Decisions for the owner

Keep these small facade details reversible; preserve existing entrances, gallery and private-room boundaries. Parking layout, planting, precise lettering/weathering, textured corner and unsupported interiors remain explicitly deferred. Dated2021/2026 imagery does not establish all current conditions or surveyed dimensions.

## For the release step

CDN and published-game checks, and owner review of inferred dimensions. No publishing or CDN upload performed.

## Matched views

### carpets-galore-front

![Before](../../../public/review/carpets-rexford-refinement/before/carpets-galore-front.png)

![After](../../../public/review/carpets-rexford-refinement/after/carpets-galore-front.png)

### carpets-galore-carpets-north

![Before](../../../public/review/carpets-rexford-refinement/before/carpets-galore-carpets-north.png)

![After](../../../public/review/carpets-rexford-refinement/after/carpets-galore-carpets-north.png)

### carpets-galore-carpets-aerial

![Before](../../../public/review/carpets-rexford-refinement/before/carpets-galore-carpets-aerial.png)

![After](../../../public/review/carpets-rexford-refinement/after/carpets-galore-carpets-aerial.png)

### rexford-courtyard-1701-front

![Before](../../../public/review/carpets-rexford-refinement/before/rexford-courtyard-1701-front.png)

![After](../../../public/review/carpets-rexford-refinement/after/rexford-courtyard-1701-front.png)

### rexford-courtyard-1701-rexford-court

![Before](../../../public/review/carpets-rexford-refinement/before/rexford-courtyard-1701-rexford-court.png)

![After](../../../public/review/carpets-rexford-refinement/after/rexford-courtyard-1701-rexford-court.png)

### rexford-courtyard-1701-rexford-gallery

![Before](../../../public/review/carpets-rexford-refinement/before/rexford-courtyard-1701-rexford-gallery.png)

![After](../../../public/review/carpets-rexford-refinement/after/rexford-courtyard-1701-rexford-gallery.png)

### rexford-courtyard-1701-rexford-aerial

![Before](../../../public/review/carpets-rexford-refinement/before/rexford-courtyard-1701-rexford-aerial.png)

![After](../../../public/review/carpets-rexford-refinement/after/rexford-courtyard-1701-rexford-aerial.png)

## Five-window A/B median p95

|View|Beforems|Afterms|Change|
|---|---:|---:|---:|
|front|18.9|19.0|0.53%|
|carpets-north|18.0|19.1|6.11%|
|carpets-aerial|17.5|18.6|6.29%|
|front|18.0|17.9|-0.56%|
|rexford-court|19.5|19.2|-1.54%|
|rexford-gallery|19.2|19.0|-1.04%|
|rexford-aerial|18.0|18.2|1.11%|
