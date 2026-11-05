# Wyoming / Perception baseline

2026-11-05: all six front-first neutral daylight baseline images inspected. Wyoming billboard rear is plain, storefront security grilles modeled; palms stylized. Perception angular graphics and bollards modeled, palms stylized, wider dark ground remains. No geometry edits.

Matching960x540DPR1ultra,900warm+streamquiet60settle,180samples. Wyoming p95front18.7/roof19.9/storefront19.3ms; Perception front24.3/roof19.1/plaza18.9ms. Retain slowfront result; do not claim sustained60fps.

New reproducible .8m grid with .35m footprint inset:662Wyoming+1035Perception=1697roofsupport samples pass. Perception recessed plant zone ray starts6.8m, remainingroof7.7m; Wyoming4.7m. Oldignored294/395sets unavailable; no oldcount reproduction claim.24CPUgroundlegs pass; actualbaseline pending.

Fresh reference leads, not yet visually inspected:
- [PERCEPTION 2022 operator press release](https://www.prnewswire.com/news-releases/now-open-las-vegas-first-permanent-digital-art-museum-perception-301567891.html). Historical opening does not verify current operation.
- [Motorcycle directory](https://www.ironhorsehelmets.com/nevada-motorcycle-dealers) associates Show Bike Performance with17E Wyoming; directory is not current official tenancy/branding proof.
- Search surfaced get-perception.vercel.app/museum.html; provenance not verified, do not treat as official without corroboration.
Next inspect dated Maps/StreetView and official photographs after GPU walking baseline finishes. No invented signs or interior layouts.

## Fresh visual inspection — 2026-11-05

Actual baseline: all 24 legs reached; four endpoint images inspected and preserved with actual-walk.json.

Wyoming [August 2024 Street View](https://www.google.com/maps/@?api=1&map_action=pano&pano=gao6napHRodosDbGOBBT_Q&heading=0&pitch=3) shows exposed vertical ribs and edge framing across the billboard rear, white storefront, red fascia/yellow cap, and shaggy palms. Camera address 140 E is not the target address. [Satellite](https://www.google.com/maps/@36.15231,-115.15310,21z/data=!3m1!1e3) confirms long flat roof, rear equipment and billboard along south edge. Satellite capture date unavailable. No current official tenancy photographs established; historical signage remains unverified.

Perception [October 2026 Street View](https://www.google.com/maps/@?api=1&map_action=pano&pano=fu2OLMNcKqp_eCU5K8F61A&heading=270&pitch=4) now resolves newer imagery than the older record's January 2025 view: black cylindrical bollards have inclined closed caps and white bands; gravel court, tall palms and angular graphics remain. Camera address 2738 is not the museum address. [Satellite](https://www.google.com/maps/@36.13825,-115.16150,20z/data=!3m1!1e3) shows the central recessed equipment court, west parking, wide east gravel plaza and palm row; capture date unavailable.

The operator's June 14 2022 press release links [501 Studios official photo archive](https://drive.google.com/drive/folders/1XyrZ24KMuRGWiDJIYKqAvl_hXMztlWRC). Visually inspected “PERCEPTION Las Vegas Exterior” (5.4 MB, archive modification July 20 2022, not asserted capture date). It confirms angular facade, large yellow fields, palms and slanted bollard caps. Its graphic layout and richer planting remain only approximately represented. No reference media copied into repository. Interior exhibit descriptions do not establish a continuous measured public floor plan; no invented interior added.

## Decisions for the owner

Add visual-only rear billboard stiffeners at inferred .75 m spacing, .055 m width/.08 m depth, within the existing 18 m by 2.5 m panel; retain all original braces. Correct Perception bollard upper .20 m to a closed inclined cap, inferred .16 m radius and .16 m rise across its diameter; keep existing positions, bands, hidden collision and pedestrian surfaces. These reversible details preserve all other unresolved landscaping, site, tenancy, interior and driving gaps. No full-block completion claim.
