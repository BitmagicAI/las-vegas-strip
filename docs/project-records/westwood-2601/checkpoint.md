# 2601 Westwood — source authoring checkpoint

Issue #435 assigned to janiverse, verified 2026-10-30. Branch starts at main 288e2ac. Source-only work while city-cell PR #437 remains open; do not run a shared-city installer or bake.

## References inspected
- [Owner property page](https://lvbuildings.com/2601-westwood-property/)
- [Owner aerial](https://lvbuildings.com/wp-content/uploads/2023/08/Westwood-Property-44-1.jpg): long hotel bar beside freeway, site taper and sign pylon. Yellow marketing overlay obscures surface colours.
- [Owner floor plan](https://lvbuildings.com/wp-content/uploads/2023/08/floorr-plan-Westwood-1.jpg): three floors, central longitudinal corridor, end stairs, central arrival and irregular pool. Plan image alone does not establish current interior finishes.
- [November 2021 Street View](https://www.google.com/maps/@36.1423359,-115.1714865,3a,75y,309.03h,90t/data=!3m4!1e1!3m2!1stnZRf7widER9VhzM2QIiIg!2e0): cream facade, salmon vertical round-headed panels with pale trim, paired windows/PTAC grilles, tile eaves, centre canopy and ramp.
- [2023 brochure](https://lvbuildings.com/wp-content/uploads/2023/08/Hotel-Property-Info.pdf). Proposed restaurant/patio illustrations are not evidence of existing interiors.

## Implemented source study
Main building way/1018431840 only: mapped shell, original arch relief, three window tiers with mullions and grilles, tile skirt, arrival canopy/supports and closed entry glazing. 26,370 triangles before optimization. GLB/Blend remain ignored local outputs. No runtime files, collision packages, roads or city files changed. No third-party imagery committed.

## Outstanding
- Resolve mapped depth (~19m) versus brochure room-bar dimension (~12.5m); retain explicit uncertainty before installation.
- Verify annex way/276428208 elevations and its relation to the site; do not copy main hotel's pattern blindly.
- First front source render inspected: overall silhouette and arches read, but arrival/ramp/site remain incomplete. Replaced warning-prone oriented-envelope helper with explicit longest-edge projections; source generator now runs clean.
- Pool, ramp and site details; public lobby layout/finishes need further corroboration.
- Correct facade bay count and roof profile against additional angles; rear repetition and heights currently inferred.
- Optimizer plus WebP, collision/route checks, matching front-first probes, installation after infrastructure coordination, full PR gates, LFS accounting. Nothing is ready or claimed complete.
