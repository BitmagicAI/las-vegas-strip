# Historical Mirage public arrival

Issue #47 / PR #456, based on next 1ee00b7. December 2022 Street View establishes tropical hip pavilions, exposed timber rafters, pale beam grids and stone columns. Links and observations are in research.json. The official historical map is indexed as text but its live URL returns HTML; no PDF visual inspection is claimed.

Replace only the old arrival node and its exact 36 collision triangles. Preserve the other 24 nodes and 3,367 collision triangles, including hotel, lagoon, drive and all separate entrance/interior assets. Two low hip pavilions and original timber/stone detail fit the existing 17 × 28 m canopy footprint. Eaves 6.35 m, ridges 8.5 m, sections and roof subdivisions are inferred. Existing hotel structure supports the west edge; retain two eastern columns and avoid adding supports inside the hotel facade.

Four baseline and four preview daylight views personally inspected. The first hotel-side route intersected the existing angled building wall; moved the route into the clear covered lane. Updated packed-collision audit passes 807 samples with no missing floors. Six normal movement segments passed and all six endpoint captures were personally inspected. The final model removes only two unused hotel-side supports outside those paths; final packed collision still passes all 807 samples. Final source has 7,408 authored triangles and 120 collision triangles, replacing 36 old collision triangles. All four final packaged daylight views were personally inspected. One city bake and runtime optimization/bake/asset-pack checks pass. Four changed LFS objects total1,323,859bytes;276/278runtimecellfiles remain byte-identical.

The reference median separates a broader multi-lane arrival than the existing model. This pass preserves the road layout rather than introducing an unsupported partial road alteration. Median, complete entry circulation, lagoon/crater, rear gardens, mechanical details and facade refinements remain in the block record with reasons. This is a scoped canopy pass, not whole-resort completion.

Rebuild: retain the pre-pass mirageExterior GLB and collision JSON under .bitmagic/city-exterior-backups/mirage-arrival; run mirage_arrival.py, export_mirage_arrival.py in Blender, install-mirage-arrival.mjs, pack the collision, optimize level then WebP, and install. The installer always reads the saved base and cannot accumulate duplicate canopies.

All local step 7 checks must pass before merge. CDN upload and published cold-load validation belong to the owner release step.

Matching 960×540 ultra fixed-view measurements: final medians28.5/18.7/32.0/16.6ms versus29.1/19.7/32.4/16.6ms. Final p9543.7/34.8/48.2/30.5ms versus42.1/36.8/39.4/23.4ms; canopy and south-view tails are slower despite similar medians. No stable60fps or no-regression claim.

All local step 7 gates pass, including nine smoke stops with no request/page/console errors. Evidence archived locally; no publishing performed.
