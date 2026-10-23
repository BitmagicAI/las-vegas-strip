# Venetian canal detail, Harrah’s and LINQ façades — 9 October 2026

This local pass is installed and visually inspected. It replaces the canal’s generic pool treatment and placeholder boats, corrects the pavilion’s bank alignment, and revises Harrah’s/LINQ tower and Strip frontage geometry. Venetian’s ground-floor palazzo glazing and signage were also refined. It is not evidence of photo-perfect or complete resort reconstruction.

[Comparison board](venetian-gondola-frontages-2026-10-09/comparison.html) · [Source register](venetian-gondola-frontages-2026-10-09/sources.json) · [Installed asset hashes](venetian-gondola-frontages-2026-10-09/installed-assets.json)

## Installed changes

- **Canal water:** distinct physical material, small moving ripples, angle-dependent reflection and restrained teal body colour. Ultra reflects actual surrounding buildings and boats at half resolution every other frame; lower tiers retain animated water and sky reflection. A reversed-depth-aware oblique clipping plane prevents the mirrored camera from seeing the underside of terrain. The initial black-water result was rejected and corrected in game.
- **Pavilion:** all four sides and the roof share the shoreline tangent; the entire 4.8 m base now sits on the dry quay. Rotation and offset derive from the mapped bank edge, rather than a guessed world-axis alignment.
- **Gondolas:** original approximately 10.1 m open, asymmetric hulls with smooth lacquer, raised foredeck/stern, planked flooring, red buttoned seating, gold scrolls, gunwale fasteners, six-tooth ferro, stern ornament, forcola, oar and mooring rope. Fine ornaments use near-detail groups. No boat controls or boat animation were added. Boat placement clears the existing navigation test envelope; nearby poles exclude the hull footprint.
- **Harrah’s:** both mapped hotel towers use white walls, separate recessed dark windows, mullions, sills and crown bands. Blank end walls carry the hotel name. The curved Strip marquee follows the mapped western frontage, with clipped diagonal bands, large arches, glazing, cornices and sculpted globe/scroll silhouettes. Ground-level shops have framed glazing and door fittings. Roof service details are batched.
- **LINQ:** blue window fields within broad white frames replace the previous generic tower grid. The street front uses stepped hexagon-clad volumes, a recessed High Roller display, a central canopy, vertical light bars and shop glazing. The frontage volume is joined at its concave corners; individual long survey edges are clipped to its actual extent. The High Roller geometry is retained. Promenade visibility is separated from guest-tower visibility.
- **Venetian street level:** ground-floor glazing, door recesses, mullions, handles and Madame Tussauds banners on the adjoining palazzo. This is an incremental street detail pass, not a replacement of every individual shop.

## Visual inspection

![Final installed canal water and gondola](venetian-gondola-frontages-2026-10-09/canal-final-installed.png)

Actual installed game, Ultra. Arches, buildings and mooring poles appear in the reflected view. In-game water differs from the offline Cycles renderer shown below.

![Detailed gondola, offline Blender review](venetian-gondola-frontages-2026-10-09/gondola-detail-offline.png)

The final close review also removed a mooring pole passing through the hull. Separate rendered checks cover [pavilion alignment](venetian-gondola-frontages-2026-10-09/pavilion-alignment-offline.png), [Harrah’s aerial](venetian-gondola-frontages-2026-10-09/harrahs-facade-aerial-offline.png) and [LINQ aerial](venetian-gondola-frontages-2026-10-09/linq-facade-aerial-offline.png).

![Harrah’s installed Strip frontage](venetian-gondola-frontages-2026-10-09/harrahs-installed.png)

![LINQ installed Strip frontage](venetian-gondola-frontages-2026-10-09/linq-installed.png)

![Venetian installed street level](venetian-gondola-frontages-2026-10-09/venetian-street-installed.png)

Rejected intermediate evidence is retained for traceability: `canal-ultra-installed.png` shows the terrain-occlusion bug, while `canal-first-installed.png` shows the initial Lowest-quality check. Neither is the final water result. First LINQ renders exposed protruding return panels and floating side walls; both were corrected before the final export.

## Validation and performance

- TypeScript typecheck passed.
- City-inclusive route regression: **9,904 checks, 284 virtual rooms, zero failures**.
- Venetian water clearance: **231 samples**, 10.4 × 2.7 × 2.9 m test envelope, zero blocked samples.
- Plaza: **602 checks and five rail rays**, zero failures. Rialto: **686 samples**, zero failures.
- Surface audit: zero overlap on the four checked independent surface pairs; zero legacy bridge triangles in replacement corridors. This is a targeted audit, not proof that every surface across the resort is free of overlap.
- Reflection clipping: **30 numerical probes** across normal/reversed WebGPU depth and three camera heights passed.
- Final local WebGPU CLI verification **passed**: settled in 4.1 s, 59 fps at the default spawn, 3,034 physics bodies. This startup smoke test is distinct from the three stationary façade measurements. Archived as `verification.txt` and `verification.json`.

The existing local Chrome profiler used Ultra, 1280 × 720, DPR 1, three seconds per warmed stationary view. No before baseline was captured and this was not a driving or cold streaming test. No page errors were reported.

| View | FPS | Frame p50 / p90 | GPU p50 / p90 | Draws |
| --- | ---: | ---: | ---: | ---: |
| Canal | 60 | 16.7 / 16.7 ms | 7.76 / 9.76 ms | 175 |
| Harrah’s | 60 | 16.7 / 16.7 ms | 6.10 / 7.83 ms | 335 |
| LINQ | 60 | 16.7 / 16.7 ms | 15.64 / 16.75 ms | 485 |

The LINQ view has less GPU headroom than the other two. These results do not establish 60 fps at a larger display resolution. [Raw measurements and camera coordinates](venetian-gondola-frontages-2026-10-09/performance.json).

| Exterior GLB | Groups | Triangles | Raw | Installed WebP + Meshopt |
| --- | ---: | ---: | ---: | ---: |
| Venetian / Palazzo | 181 | 1,327,102 | 97.21 MiB | 27.12 MiB |
| Harrah’s | 41 | 121,964 | 10.06 MiB | 2.86 MiB |
| LINQ / High Roller | 197 | 298,279 | 28.82 MiB | 9.94 MiB |

These counts include the existing resort geometry in each asset, not only new additions. Source hashes match the optimized install manifest. Batching, near-detail groups, tower ownership, PBR and optimized asset selection are retained. Harrah’s old high-rise render meshes are hidden by `DRAWN_ELSEWHERE`; its original collision ownership and guest interiors remain. No lights were added to the runtime light set. No unrelated road, physics, foliage or interior regeneration was performed.

## Reference evidence and remaining discrepancies

The [Venetian’s official gondola photographs](https://www.venetianlasvegas.com/resort/attractions/gondola-rides.html) informed the boat’s hull, seating, prow and rowing fittings. [Caesars’ Harrah’s gallery](https://newsroom.caesars.com/Property-Fact-Sheets/Harrahs-Las-Vegas/) informed the white hotel/window treatment and striped marquee. [Caesars’ LINQ gallery](https://newsroom.caesars.com/Property-Fact-Sheets/The-LINQ-Hotel--Experience/) informed blue hotel panels and hexagonal street cladding. These were inspected as reference images; no reference photograph became an unlicensed game texture. The creator’s supplied aerial is archived in the comparison board.

Mapped footprints and prior tower heights were retained. Canopy heights, sign dimensions, window schedules and roof equipment placement are photo-fitted estimates, not a survey. The LINQ front screen is estimated at 29.5 m with a 26 m central recess. Harrah’s tower heights remain the prior mapped 109 m and 72 m; LINQ remains 63 m. Source image capture dates are unknown, so current temporary signage is not established.

Exact brand lettering, individual tenant fronts, sculptural ornament, façade weathering, complete roof services and landscaped grounds remain approximate. Venetian’s palazzo façade still needs closer architectural matching. Existing interiors are preserved and are not a map-faithful rebuild. Outdoor gondola water remains separate from Level 2 indoor canals, following the creator’s explicit choice. The full-resort completion gates remain open/failed rather than being relabeled complete. Overnight automation remains paused.

## Rebuild entry points

- `tools/strip-landmarks/build_venetian_exterior.py`
- `tools/strip-landmarks/build_harrahs_exterior.py`
- `tools/strip-landmarks/build_linq_exterior.py`
- `tools/strip-landmarks/review_canal_detail.py`
- `tools/strip-landmarks/review_facades.py -- harrahs|linq`

Export only the selected resort through the established Blender exporter, run both optimization variants for that one exterior, then install it. The optimizer accepts one substring in `--only`; comma-separated selectors are not supported there.
