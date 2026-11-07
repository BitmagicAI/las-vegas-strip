# Scoped implementation and decisions — PR541

The tower crown now slopes inward 2.2 m between inherited elevations 123 and 128 m. Original white dormer cheeks and projecting caps replace flat window-only treatment. The cornice sits at the foot of the slope. Maximum tower height, mapped footprint, hotel interiors and parent collision ownership remain inherited; exact roof heights and raised wing ends are deferred.

The podium pool terrace gains eight original dark fabric chaises with light metal frames, supported by the official fifth-floor pool photo. Dimensions and spacing are inferred: approximately 0.7 m wide, 1.9 m long including reclined back, 0.44 m seat height. They occupy z≈988–990, clear of the verified z=992 walk and pool water. No new lights, textures or runtime systems.

Raw Grand Chateau collision is byte-identical before/after. Roof support audit: 31 samples, zero failures. Furniture is decorative and does not establish a new public route. The erroneous north canopy, roof pool, arrival hall, safety enclosure, connected deck access and full landscaping remain explicitly unresolved. This is a crown and furniture refinement, not whole-block completion.

Build: 15,899 triangles, 17 batches. Level optimizer passed bounds/node/validator checks, 953,368 → 270,200 bytes. WebP pass ran and found no image slots; it correctly retained the level output. One shared city bake; 91 of 92 cells byte-identical, only cell-0_1 changed. Gold Coast and Wyndham nondeterministic LOD changes were restored from HEAD bytes. Initial preservation guard expected a model-key block, rejected the tower source key, and was corrected to cover the two Grand Chateau blocks; no second bake was needed. No roads or neighboring authored models changed.

The task board generator ran; unrelated accumulated board/summary changes were excluded, keeping only the Grand Chateau task entry. Baseline PNGs were moved from the documentation tree into public/project-records after the public-file check rejected that location; these are our game renders, not third-party photos. Links are in capture-links.json.

Installed matching views, performance and actual walks remain separate evidence. Do not treat the local collision test as full circulation proof.

Initial installed crown review rejected the dormer returns: facade frames can run opposite the survey edge, and negative local depth projects outward. Corrected cap/cheek positions use the matching reversed edge coordinate and return inward. Initial six-view captures/timings retained in after-initial; corrective build/bake and final evidence required. Initial p95 pool 35.3ms vs29.9 baseline and crown27.9 vs18.8 need final matching measurement before any performance claim.

Corrective stage initially refused the regenerated collision JSON timestamp until pack-data refreshed its binary; bytes remained unchanged. The stale-data guard was satisfied before final staging/checks.

Final optimized size: 269372 bytes. Final corrective bake/stage complete; 91/92 cells byte-identical against original HEAD. Final eleven local checks,12walklegs and nine-stop smoke pass.
