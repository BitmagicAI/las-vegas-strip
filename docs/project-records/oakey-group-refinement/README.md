# Oakey group — bounded exterior refinement

Luv-It has original low-poly scrollwork on both existing south window grilles. ARCO has a recessed visual soffit with two shallow longitudinal beams. Both models preserve the previous collision geometry, materials, labels and surrounding layout. Oakey Shops geometry is unchanged; fresh reference and installed walkway review preserve its outstanding survey/interior work.

This is a detail pass, not a photorealistic or whole-block completion claim. Reference observations, inferred dimensions and decisions are in references.md. No third-party pixels were copied into geometry or textures.

## Verification so far

- Original generated JSON equals preserved main-checkout JSON; collision arrays and labels unchanged.
- Luv-It: 1,819 to 2,587 authored triangles; optimized 956,720 to 303,284 bytes. Texture-free model, WebP pass correctly skips it.
- ARCO: 3,499 to 3,523 authored triangles; optimized with WebP from 2,172,128 to 492,068 bytes. Original two texture/material definitions retained before optimization.
- One grouped bake; 91 of 92 city cells byte-identical. Only cell-2_-5.bin changed. Known unrelated Gold Coast/Wyndham LOD drift restored before staging.
- Thirteen local checks passed, including 87 Luv-It, 541 ARCO and 77 Shops support/headroom samples. Runtime asset check, bake check, staged pack check and Bitmagic check/reload passed.
- Baseline real-input walks: 18 legs passed. Repeated 18 legs passed after changing endpoint camera direction to avoid a window-filling screenshot; original evidence retained.
- Six matched daylight/performance baseline and candidate views, plus a supplemental under-canopy camera, inspected. Candidate runner initially retained an old final assertion; saved request counters confirm both candidate GLBs loaded. Assertion corrected and supplemental run passed.

Installed seven daylight views and six walk endpoint/return captures inspected;18afterlegs and9smokestops passed. Performance control/repeat retained; original control was also slower than the early baseline. Archive and LFS accounting are finalized before merge.

## Out of scope and release step

Roads, existing interiors, shared runtime code, city ownership and Shops geometry remain unchanged. Exact sign graphics, site paving, rear utility layouts, surveyed dimensions and interiors remain in the three block records. CDN and published-game checks belong to the owner's release step. No CDN upload, publication, main merge, release or settings change is authorized here.

Final LFS audit: 11,101,747 new bytes across 33 unique objects absent from origin/next, including generated captures and models.
