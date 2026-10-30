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
- Source generator: PASS, 54,379 triangles, no numerical warning.
- Blender GLB export: PASS.
- Front/roof/annex source renders personally inspected. Initial crossed roof ribs were corrected with shared inset-corner hip geometry, then the annex render rechecked.
- Source collision: 353 triangles; 45 arrival-ramp floor samples have support; no obstruction at body height; largest adjacent height change 0.003m. This is source geometry evidence, not an installed walk.
- Level optimization: PASS, approximately 5.19 MiB to 2.03 MiB. WebP pass invoked; no embedded textures to convert. Installer dry-run selects the candidate successfully.
- No actual optimized installation: the old branch installer auto-stages the city-wide runtime set, so it is deferred until infrastructure coordination. No shared city files or runtime snapshots changed. Git LFS bytes added: zero.

## Remaining
- Validate mapped alignment against matching installed views after the cell split permits installation; the source preview is not installed evidence.
- Refine roof vents/end elevations, site paving joins, gate/court dimensions and planting against additional references. Heights, bay spacing, pool positioning and unseen elevations remain estimates.
- Confirm the identity/operation of the south building; ownership or hotel affiliation is not asserted.
- Public interior only with current/as-built evidence (the brochure is not sufficient).
- Optimized installation, targeted collision replacement, route integration, matching front-first probes, full PR gates, current city bake and LFS accounting after infrastructure coordination. PR remains draft.
