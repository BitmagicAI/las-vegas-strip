# Venetian outdoor canal clearance — October 9, 2026

Installed locally and visually inspected. The outdoor bridge repair is functional geometry, not a claim that the complete resort now meets the requested photorealism.

## Layout decision and evidence

The creator explicitly selected **preserve the real layout** after clarification. Indoor gondola rides remain on the separate Level 2 Grand Canal Shoppes network; no invented exterior-to-interior water connection was added. The [official gondola page](https://www.venetianlasvegas.com/resort/attractions/gondola-rides.html) lists indoor and outdoor locations separately. The saved official map and level graph are in `venetian-floorplans-2026-10-09.md` and `tools/resort-blocks/venetian-public-layout.json`.

The creator's close Google Earth view is saved as `venetian-water-clearance-2026-10-09/user-water-reference.png`. OSM ways115776193/180831029 anchor the horizontal banks; the archived raw source is `venetian-exterior-2026-10-09/canal-osm-reference.json`. OSM excludes the covered plaza footprint from its water polygon, so the water surface now explicitly continues under the bridge.

## Geometry changed

- Replaced the solid T-plaza crossing with a raised, arched span. Walking surface, inlaid paving, balustrades and collision follow the same grade. Water datum0.31m, deck crest4.15m, central soffit3.60m; all elevations are estimates, not survey data.
- Rotated and repositioned the north side wing along the diagonal mapped bank. The north channel is now approximately5m wide at the small covered crossing, instead of being partly occupied by the old wing.
- Added the small north bridge with an actual arched opening and soffit; no water-level wall across the opening.
- Raised the south stair landing across its canal branch and cut an arch under it. Cut the boat passage through both faces of the adjacent south wing while preserving its separate upper pedestrian entrance.
- Preserved the separate indoor layout, the Rialto road span and unrelated roads/runtime/lighting. Only Venetian exterior was re-exported and reoptimized.

## Inspection and verification

Four combined city + exterior + interior Blender renders were opened and inspected, including both water-level views, the aerial and the Rialto/stair junction. Two optimized installed game views were then opened, inspected and saved:

![Installed main arch](venetian-water-clearance-2026-10-09/main-arch-installed.png)

![Installed north channel](venetian-water-clearance-2026-10-09/north-passage-installed.png)

![Combined aerial](venetian-water-clearance-2026-10-09/canal-water-aerial-combined.png)

The dark area under the bridge in the offline render was checked against mesh elevations: there is no above-water plate. In-game water continues visibly through the opening.

| Check | Result |
|---|---|
| Boat envelope, visible architecture plus collision |231samples,0blocked|
| Boat test envelope |10.4m long ×2.7m wide;2.9m above water|
| Plaza and portal walking probes |602passed|
| Balustrade rays |5passed|
| Rialto/stair/road headroom probes |686passed|
| Full city-inclusive routes |9,904passed|
| Four prior independent surface-overlap pairs |0m² overlap|
| Removed legacy bridge geometry |0triangles reintroduced|
| Type check |passed|
| Local WebGPU startup verification |passed,4.1s/60fps at spawn; not a route benchmark|

The water regression was first run against the previous geometry and failed211/251samples. The initial rebuilt version failed25/251: the south wing's rear collision face was still present, and the main crossing probe continued into shoreline mooring poles after leaving the bridge. The final231sample route ends after the entire envelope clears the bridge, before that shoreline turn. Both south wall openings were repaired. Test route metadata and reports are saved beside this report.

Final exterior:172groups,1,247,094triangles (about1.5% above previous1,229,034);95.09MiB original→26.25MiB WebP/meshopt asset. Source and installed hashes are saved. The optimizer's four shared dependency symlinks were repaired after their source project moved from `arcade-tycoon` to `games/cabinet-fever`; no downloads were needed.

## Remaining limitations

This is an air-clearance test, not a playable gondola simulation. Underwater ground is still shallow; realistic canal depth has not been reconstructed. No full keyboard traversal or resort-route performance comparison was completed. Horizontal channel outlines are map-based, while bridge elevations and exact architectural profiles remain estimated. The broad plaza currently uses one large arch; the reference's full multi-arch section and detailed terminal treatment remain to be reconstructed. The surrounding facade, sculpture, landscaping and interiors still have the broader documented fidelity issues. Whole-resort visual gate remains **failed**. Overnight automation remains **paused**.
