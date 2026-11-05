# South Commercial pair refinement

Two mapped structures364846558/559. Scoped original geometry changes: broader, lower-contrast standing seams on the main hip roof; diagonal painted hatching on the annex west access strip. All six matched neutral daylight views inspected. The roof change is partial: one plane reads more continuously, but opposite-plane dotted alias remains. No full-block or photorealism claim.

References and inferred dimensions are in research.md. Identity, detailed materials/entries, mature planting and interiors remain unsupported or incomplete. No roads, terrain, runtime code or existing interiors changed. Both source collision hashes unchanged. Shared cell manifest/asset pack and task records are the necessary out-of-scope touches; unrelated Gold Coast/Wyndham regenerated LOD changes restored.

One grouped bake; both GLBs level+WebP optimized.91/92 cell binaries byte-identical (onlycell--1_4 changed). Typecheck,3regressiontests, optimization2/2, bakefreshness, assetpack1930present, resortreview pass; publiccheck0failures11existingwarnings.

New reproducible2369roof-support samples pass before/after. The old ignored910/825samples were unavailable, so this count is not a reproduction claim. Original18CPUwalklegs passed but actualannexdiagonal cut a corner and stopped: failure JSON/images retained. Adding an explicit outer-corner waypoint produced20CPUlegs and20actualbaselinelegs passing with original endpoints/tolerances. All 20 actual after-walk legs pass; four endpoint captures inspected. Nine-stop dev smoke passes with zero failed requests, page errors or console errors.

## Matching performance

Same960×540DPR1ultra cameras/light,900warmframes,streamingquiet+60settle,180samples/view. Maximum p95 increase0.53%; short static samples do not establish sustained60fps, perimeter driving, cold stalls or residency.

|Building/view|Beforep95ms|Afterp95ms|
|---|---:|---:|
|south-commercial-364846558 front|19.0|18.8|
|south-commercial-364846558 roof|18.6|18.6|
|south-commercial-364846558 north|18.9|19.0|
|south-commercial-annex front|19.1|18.9|
|south-commercial-annex roof|19.0|18.5|
|south-commercial-annex east|26.2|18.8|

## Decisions for the owner

Retain reversible visual estimates and original circulation. Preserve unresolved aliasing instead of claiming a complete fix. No invented identity, signs or interior layout.

## For the release step

CDN/published-game checks and owner review of inferred dimensions. No publishing or CDN upload performed.

## Matched views

### south-commercial-364846558-front

![Before](../../../public/review/south-commercial-pair-refinement/before/south-commercial-364846558-front.png)

![After](../../../public/review/south-commercial-pair-refinement/after/south-commercial-364846558-front.png)

### south-commercial-364846558-roof

![Before](../../../public/review/south-commercial-pair-refinement/before/south-commercial-364846558-roof.png)

![After](../../../public/review/south-commercial-pair-refinement/after/south-commercial-364846558-roof.png)

### south-commercial-364846558-north

![Before](../../../public/review/south-commercial-pair-refinement/before/south-commercial-364846558-north.png)

![After](../../../public/review/south-commercial-pair-refinement/after/south-commercial-364846558-north.png)

### south-commercial-annex-front

![Before](../../../public/review/south-commercial-pair-refinement/before/south-commercial-annex-front.png)

![After](../../../public/review/south-commercial-pair-refinement/after/south-commercial-annex-front.png)

### south-commercial-annex-roof

![Before](../../../public/review/south-commercial-pair-refinement/before/south-commercial-annex-roof.png)

![After](../../../public/review/south-commercial-pair-refinement/after/south-commercial-annex-roof.png)

### south-commercial-annex-east

![Before](../../../public/review/south-commercial-pair-refinement/before/south-commercial-annex-east.png)

![After](../../../public/review/south-commercial-pair-refinement/after/south-commercial-annex-east.png)
