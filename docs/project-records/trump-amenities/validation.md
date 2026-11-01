Corrects the earlier Trump International pool's estimated 51 m length to the official 110 ft (33.528 m), and adds reference-supported deck amenities.

## Trump International

- Replace three old pool nodes and 81 collision triangles within the old pool bounds; preserve 14 tower/podium/arrival nodes and 140 existing collision triangles.
- Infill the old pool ends, retain inferred 11 m width and existing elevation, and add a navy tower-side awning, 26 loungers, five parasols, seven palms, planted south border and rail.
- The [official pool photograph](https://res.cloudinary.com/trump-hotels/image/upload/v1790864417/KHaydenTrumpLVPool3_kd2cso_ddco09.jpg) and Google aerial support the arrangement. Furniture counts, width and elevation remain inferred. February 2026 Street View was checked; arrival refinement remains deferred.
- 6,219 authored triangles, zero degenerates; 889 added collision triangles.

## Checks

- bitmagic check and three applicable tests PASS.
- 1,476 packed deck-route samples PASS, zero unsupported floors; 45 existing arrival clearance samples PASS.
- Eight bidirectional normal movement segments PASS; all eight endpoint captures personally inspected.
- Level and WebP optimization installed; changed-runtime check PASS (one GLB).
- review.py and check-public.py PASS; existing public contact warning only.
- One bake, freshness and package check PASS: 1,928 present, zero missing/unoptimized.
- Four matching final daylight views personally inspected. Median 16.6–16.7 ms; p95 front/pool/arrival/overview 17.3/17.3/17.5/19.3 ms versus baseline 17.3/17.3/17.4/27.5 ms. Local fixed-camera sample, not city-wide performance proof.
- Smoke PASS: nine stops placed; zero failed requests, page errors or console errors.

## Scope and storage

Only pool/deck asset, supporting tools/records and task metadata. Roads, guest interiors, tower geometry, shared shaders and foliage sources unchanged. One shared bake; four LFS objects add **1,043,272 bytes**. 276/278 cell files byte-identical; only baked cell 0,-2 and its manifest change. Venue data unchanged.

## Decisions for the owner

Use official pool length while retaining uncertain width/elevation. Cabana interiors, complete planted enclosure, entry facade and crown proportions, and interior-to-pool connections remain deferred. No whole-block or photorealistic completion claim.

## For the release step

CDN upload and published cold-load validation before next merges to main. No publishing or external asset upload performed.

Closes #45
