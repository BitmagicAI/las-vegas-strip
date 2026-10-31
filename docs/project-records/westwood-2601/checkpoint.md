# 2601 Westwood — source authoring checkpoint

Issue #435 assigned to janiverse, verified 2026-10-30. Branch starts at main 288e2ac. Source-only work while city-cell PR #437 remains open; do not run a shared-city installer or bake.

## References inspected
- [Owner property page](https://lvbuildings.com/2601-westwood-property/)
- [Owner aerial](https://lvbuildings.com/wp-content/uploads/2023/08/Westwood-Property-44-1.jpg): long hotel bar beside freeway, site taper and sign pylon. Yellow marketing overlay obscures surface colours.
- [Owner floor plan](https://lvbuildings.com/wp-content/uploads/2023/08/floorr-plan-Westwood-1.jpg): three floors, central longitudinal corridor, end stairs, central arrival and irregular pool. Plan image alone does not establish current interior finishes.
- [November 2021 Street View](https://www.google.com/maps/@36.1423359,-115.1714865,3a,75y,309.03h,90t/data=!3m4!1e1!3m2!1stnZRf7widER9VhzM2QIiIg!2e0): cream facade, salmon vertical round-headed panels with pale trim, paired windows/PTAC grilles, tile eaves, centre canopy and ramp.
- [2023 brochure](https://lvbuildings.com/wp-content/uploads/2023/08/Hotel-Property-Info.pdf). Proposed restaurant/patio illustrations are not evidence of existing interiors.

## Source pass, 2026-10-30
Both claimed mapped buildings now have original exterior source geometry. Main hotel: three-storey arch relief, paired windows and grilles, continuous tiled roof skirt, canopy, broad arrival ramp and low flanking walls. South building: three-storey grey facade, pale arches, paired windows and tiled roof. Pool court: irregular basin, coping, water, perimeter privacy wall and open gate.

The brochure page 3 visibly specifies **236 by 41 feet** (71.933 by 12.497 metres). The main wall bar now uses those dimensions at the mapped centre/heading instead of the approximately 19m-deep coarse Microsoft footprint. This is a reference-based correction, not a surveyed alignment; the before/after installed overlap check remains mandatory. The south building retains its mapped footprint. Its Street View appearance was inspected by rotating the same November 2021 panorama toward the pool and south building; rear and end repetition remains inferred.

The original plan labels the central ground-floor lobby as proposed. It therefore does not establish a built public interior. No speculative public lobby or proposed restaurant has been added. Further current/as-built interior evidence is needed.

### Local checks
- Source generator: PASS, 54,403 triangles, no numerical warning.
- Blender GLB export: PASS.
- Front/roof/annex source renders personally inspected. Initial crossed roof ribs were corrected with shared inset-corner hip geometry, then the annex render rechecked.
- Source collision: 353 triangles; 45 arrival-ramp floor samples have support; no obstruction at body height; largest adjacent height change 0.003m. This is source geometry evidence, not an installed walk.
- Level optimization: PASS, approximately 5.20 MiB to 2.03 MiB. WebP pass invoked; no embedded textures to convert. Installer dry-run selects the candidate successfully.
- No actual optimized installation: the old branch installer auto-stages the city-wide runtime set, so it is deferred until infrastructure coordination. No shared city files or runtime snapshots changed. Git LFS bytes added: zero.

## Remaining
- Validate mapped alignment against matching installed views after the cell split permits installation; the source preview is not installed evidence.
- Refine roof vents/end elevations, site paving joins, gate/court dimensions and planting against additional references. Heights, bay spacing, pool positioning and unseen elevations remain estimates.
- Confirm the identity/operation of the south building; ownership or hotel affiliation is not asserted.
- Public interior only with current/as-built evidence (the brochure is not sufficient).
- Optimized installation, targeted collision replacement, route integration, matching front-first probes, full PR gates, current city bake and LFS accounting after infrastructure coordination. PR remains draft.

### Deck-edge regression pass
The previous courtyard polygon stopped 0.50m short of the hotel wall. A new source check reproduced 49 missing floor samples along this edge before the fix. The deck now overlaps the wall by 0.05m; all 49 samples pass, alongside the original 45 ramp samples and body-height clearance. The repeatable check is `tools/strip-landmarks/check_westwood_2601.py`. Export, roof source render and level/WebP optimizer were repeated successfully after the correction.

Added `tools/city-exteriors/probe-westwood-2601.js` with matching front/roof/annex views. Each camera position was checked against mapped building footprints and heights; none lies within a mapped building. This does not replace an actual installed capture/occlusion check. The probe has not been run against installed Westwood content.

### Pylon and drainage pass
Re-inspected the owner's aerial placement reference. Added the two-legged sign pylon beside the hotel's freeway-side end, with the brochure's 100 ft overall height and 40 x 30 ft display faces. Leg dimensions, exact footing position and screen depth are inferred; the dark screen does not reproduce an advertisement or assert its current content. Added two front downpipes and brackets based on the previously inspected street view. Roof source render inspected after export; sign is separate from the hotel shell.

Current source: 54,723 triangles, 449 collision triangles. All 94 floor samples and arrival body clearance still pass. GLB export and level optimization pass: 5,475,408 source bytes to 2,146,316 optimized bytes. WebP invoked (no embedded textures); installer dry-run passes. Actual installation and installed alignment/performance remain pending; no LFS bytes added.

### Planting pass
Added five fan palms at the pool court and front facade using the existing original `courtyard_525.palm` helper. Their presence is supported by the inspected November 2021 Street View; exact heights, positions and circular planting rims are inferred. No foliage source models changed, and no remote plant assets were downloaded. The front source render was inspected after rebuilding.

Current result: 63,293 source triangles, 509 collision triangles; 94 floor samples and arrival body clearance PASS. Blender export PASS. Level optimizer 6,332,828 → 2,514,464 bytes; WebP invoked (textureless); installer dry-run PASS. Actual installation, public interior evidence, end-elevation refinement and all installed gates remain pending. The shared city is untouched.

### North-end reference pass
Inspected a further [February 2020 Street View panorama](https://www.google.com/maps/@36.1426339,-115.1712835,3a,75y,306h,90t/data=!3m4!1e1!3m2!1sba0gpHmaaTcW7rlwo1ugzg!2e0). This shows ochre masonry at the north end, a tall stair-window strip, smaller windows, ground-floor service doors and a screened utility cabinet with protective posts. Added original geometry for these features only on the observed end; positions and dimensions remain estimates. Date differs from the November 2021 frontage reference.

Added matching north-end source/probe camera, retaining front first. Personally inspected the exported north-end render. Current source 71,789 triangles; collision 581 triangles. All 94 floor samples and body clearance PASS. Export PASS; level optimization 7,091,648 → 2,779,684 bytes; WebP pass and installer dry-run PASS. No actual installation, shared-city changes or new Git LFS bytes. Final installed alignment and route/performance gates remain pending.

### Pool circulation and geometry-cost pass
Added a source route from the pool gate to the hotel deck. Clearance checks now sample a 0.6 m wide body at three heights through the gate and along the route, with 120 additional deck floor samples (214 total). All pass. A temporary probe shifted onto the solid wall correctly failed; original metadata was restored and the check passed again. These are source tests, not installed walks or proof of street support outside the court.

Replaced hidden masonry-joint box faces with coplanar outward strips, removing 6,670 triangles without altering collision. Exported north-end render inspected: coursing retained. Source now 65,119 triangles; collision 581. Export, level optimization (6.20 MiB to 2.45 MiB), WebP pass and installer dry-run pass. No installation/shared bake/upload. Next: installed alignment and source-to-city integration after #437; remaining uncertain elevations and current interior evidence remain recorded.

### Source acceptance record and pool view
Added tools/resort-blocks/westwood-2601.json as a source-only queued record, without changing the active queue or implying installation. It consolidates both mapped IDs, issue/PR, dated source evidence, component status, dimensions still inferred, named camera views and all remaining installed gates. Added the same pool-gate camera to the source review and future installed probe, front still first; personally inspected the exported view and visible opening/deck.

Targeted record validation PASS; check-public.py PASS with the existing inventory email warning. Full review.py is blocked in this spare worktree by missing legacy local reference images (Cosmopolitan/Bellagio/Paris and other records), not a Westwood record failure. Task board generation ran; its unrelated Lexi-only index changes were discarded. No model geometry, runtime, shared city or LFS change this pass. PR remains draft.

### South-building stairwell correction
Followed November 2021 Street View south through panoramas DMkPgfJ90sLeyIuZ7kGUtw and 9SfTBZn0Nrrsh5NjQYOSgQ. The street-facing short end is pale masonry with a full-height open steel stairwell and closed ground gate, not repeated blind arches. Cut the shell and collision at that end, added original switchback flights/landings/rails and gated frontage. Stair dimensions and landing arrangement inferred; no public access or installed walk is claimed. Added matching annex-stair camera and personally inspected final exported view after correcting the end finish.

Source 67,701 triangles, collision 1,747; 214 existing route floor samples and body clearance PASS. Blender export, level optimization, WebP pass and installer dry-run PASS. No city installation or shared bake. A focused current-interior search found only renovation/proposed-layout marketing and historical listings, so public interior remains unauthored rather than invented. References and uncertainty saved in the building record.

### Read-only installation preflight
Added preflight_westwood_2601.py to compare authored shell footprints and above-ground collision projections against all 6,766 mapped building footprints, excluding only the two claimed IDs. No neighbouring-building overlap over 0.05 square metres found. All six named camera origins are outside mapped building volumes. Saved placement-report.json. This is not road alignment, runtime occlusion, collision equivalence or an installed walk; those gates remain pending while #437 is open. No generated geometry or shared city files changed.
