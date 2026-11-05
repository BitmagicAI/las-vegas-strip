# Initial baseline review

All seven installed neutral daylight views inspected. Carpets Galore north wing is pale blue; warehouse vertical cladding is visible. West forecourt is bare and broad. Rexford shows simplified windows and screens, broad plain walls, gallery/rail/stairs and pool; rounded corner is untextured. No geometry changes selected yet.

Isolated static p95ms: Carpets front18.3,north25.1,aerial18.0; Rexford front17.5,court18.4,gallery17.9,aerial34.2. Do not hide the north/aerial slow views or claim sustained60fps. Match every camera after changes and investigate any regression.

[Carpets Galore official contact](https://www.carpetsgaloreflooring.com/contact) corroborates1601SMain address. [About page](https://www.carpetsgaloreflooring.com/about-us) is a candidate for official photographic review, still pending; text does not establish showroom geometry. No verified official Rexford property page found in initial search; dated Maps visual review remains necessary. No third-party images committed.

Baseline source checks1378support/headroom samples,12groundCPUlegs and6stairCPUlegs passed. In-memory source calls regenerated missing ignored samplefiles without saving geometry. Actual ground walk running; dedicated actual stair script uses the existing CPUroute and0.18ground/3.0gallery heights, pending run.

## Dated visual review and reversible scope (2026-11-05)

[Carpets west, January 2026](https://www.google.com/maps/@?api=1&map_action=pano&pano=sJyre5SSinRWeuLCglTtFw&heading=90&pitch=0) shows white fascia, blue lettering, broad paved forecourt, angled parking stripes and small roof-mounted flood housings. Add two compact non-emitting housings per west-facing sign frontage using existing materials. Brackets .08m wide, housing .42×.23×.24m; dimensions and spacing inferred. Parking layout remains deferred because its alignment to the existing apron/road boundary needs a separate measured site pass.

[Rexford corner, January 2021](https://www.google.com/maps/@?api=1&map_action=pano&pano=hoLANNC8dYsa0tC_XO1iEw&heading=240&pitch=0) shows mint walls, a rounded white textured corner, thin projecting roof lip, horizontal windows, mature planting and recessed entry. The date carousel offered January 2021 only at this panorama; no current-condition claim. Add a thin outer roof lip following the existing rounded footprint, 7cm beyond the existing roof edge, y6.08–6.18m. Dimensions inferred. Preserve existing entry, gallery, stairs and pool; exact entry position, wall texture and planting remain unresolved.

Official About gallery visually inspected: close-up carpet sample boards, a narrow hard-floor sample aisle with suspended tile ceiling/panel lighting, and carpet roll storage. These isolated views do not establish a connected showroom floor plan or entrance mapping. Public showroom interior remains deferred with that specific layout gap, not treated as complete. No official Rexford property photographs verified; differently addressed search results excluded. No third-party image data committed.

Baseline actual stairs passed all6legs; both endpoint captures inspected (upper gallery and ground return). Combined actual baseline is18legs.

Installed after review (first two views): four west sign housings visible above the two fascia runs; lettering remains unobstructed. North painted wing reads pale blue under the fixed neutral daylight, matching its intended painted finish. Bare forecourt, simplified advertising and cladding remain evident; no broader fidelity claim. Other five views, actual walks and smoke still pending.

All seven after views now inspected: aerial confirms four small west fixtures, unchanged roof equipment and L footprint; Rexford street/aerial shows continuous thin rounded roof rim; court/gallery rails and pool opening remain intact. Blender rail warning did not produce a visible missing rail in these views; no source rail changes made. First matched static aerial sample regressed48.3% (18.0→26.7ms) while the other six stayed within10% or improved. Preserve all samples and investigate using five-window original-asset browser A/B; not yet a passing performance gate.
