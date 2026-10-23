# Venetian / Palazzo floor-map evidence and indoor reconstruction plan

Retrieved and visually reviewed on 2026-10-09. The creator requested floor maps to guide the exterior and future indoor construction. Existing indoor geometry is preserved in this exterior pass; it is not yet a reconstruction of these plans.

## Authoritative sources

1. [Official resort map, both properties, Levels 1 and 2](https://www.venetianlasvegas.com/content/dam/venetian/resort/map.pdf). Archived as `venetian-exterior-2026-10-09/official-resort-map-2026-10-09.pdf`; both pages rendered and visually inspected (`official-resort-map-1.png`, `official-resort-map-2.png`). Current download has no printed issue date visible. It includes Level 2M and a separate Palazzo lower-level inset. Diagrammatic visitor map, without scale or floor-to-floor heights.
2. [Official meeting floor plans](https://www.venetianlasvegas.com/content/dam/vlv/meetings/downloadable-pdfs/M_FloorPlans.pdf), linked from the resort's [meeting resources](https://www.venetianlasvegas.com/meetings/resources.html). Archived as `official-meeting-floorplans.pdf`. Sixteen pages: Level 1 plans pp1-4/capacities p5, Level 2 plans pp6-9/capacities p10, Level 3 p11/capacities p12, Level 4 p13/capacities p14, Level 5 Palazzo Ballroom p15/capacities p16. Page11 visually inspected: actual room divisions, foyers, circulation/vertical cores and a connection labeled to Grand Canal Shoppes. Dimensions/ceiling data are local to the named meeting rooms; they do not establish heights of the casino, hotel podium or pools.
3. [Official February 2026 pool maps](https://www.venetianlasvegas.com/content/dam/vlvweb/poolsandspas/pool-map.pdf), already archived as `pool-map-2026.pdf`. Separate Venetian main pools, South Tower Pool Garden and Palazzo decks, with the inter-deck walkway.
4. [Official Venetian Luxury King suite](https://www.venetianlasvegas.com/hotel/the-venetian/luxury-king-suite.html): current remodeled suite plan, 650 square feet (about 60.4m²), with a 130-square-foot bathroom. Plan archived and visually inspected as `venetian-luxury-king-floorplan.png`.
5. [Official Palazzo Luxury King suite](https://www.venetianlasvegas.com/hotel/the-palazzo/luxury-king-suite.html): 720 square feet (about 66.9m²), with a 130-square-foot bathroom. Plan archived and visually inspected as `palazzo-luxury-king-floorplan.png`. Exact image URLs are recorded in `suite-floorplan-sources.json`.

These are research references, not textures or imagery licensed for redistribution in the game. No source image was projected onto the architecture.

## What the plans establish

| Public area | Official label / connectivity | Reconstruction consequence |
| --- | --- | --- |
| Venetian lobby and casino | Level 1; arrivals by front desk and Armillary Sphere, casino farther inside; separate canal-front casino entry | Do not treat every canal-side doorway as the main hotel lobby. Preserve current access until replacement rooms and portals can be installed together. |
| Venetian to Palazzo | Level 1 route through Restaurant Row and Waterfall Atrium | Build connected interior zones, not disconnected resort boxes. Ground public route and upper shopping route need distinct graphs. |
| Grand Canal Shoppes | Level 2; bent canal with several crossings, St Mark's Square, branching retail streets and Waterfall Atrium connection | Existing straight 86m canal is a playable interpretation, not an accurate plan. Replacement needs traced branches, a square, bridges and area-based streaming. |
| Rialto / Scenic Overlook | On the Level 2 resort map at the Strip edge, with public vertical circulation near the frontage | Keep the bridge's upper entrance open. Reconcile upper gallery, outside overlook and stairs with the future indoor route graph. |
| Palazzo arrivals | Main front-desk route on Level 1; lower-level transport/retail inset | Separate arrivals and lower porte-cochere, with documented vertical connections. |
| Pools | Venetian North Tower floor 4; Palazzo floor 3; Venetian South Tower Pool Garden floor 10 | Hotel labels are not physical elevations. Register separate decks and vertical cores; retain provisional metre elevations until measured. |
| Convention connections | Convention Level 3 plan points to Grand Canal Shoppes; resort labels Shoppes Level 2 | Floor numbers differ by zone. Do not force one uniform building-wide floor numbering or invent a stair solely from the label mismatch. |

## Required indoor graph

- Ground: Venetian arrivals → front desk / Armillary Sphere → casino → Restaurant Row → Waterfall Atrium → Palazzo casino → Palazzo front desk / arrivals.
- Ground exterior branches: Clock Tower entry; canal-front casino entry; Waterfall Atrium street entry; Sands Avenue bridge entry; convention/ground-transport connection.
- Upper: Rialto → Scenic Overlook / frontage retail → branching Grand Canal streets → St Mark's Square; western retail spine → Waterfall Atrium upper gallery → Palazzo Shoppes / Wishing Tree → guest cores and north-side shops.
- Vertical: trace each lift/escalator symbol by floor, pair endpoints explicitly, then build playable stairs/lifts. Pool access must reach the correct tower and labeled deck. Level 2M pockets and Palazzo lower arrivals are separate spaces, not a global extra slab.

A compact machine-readable semantic graph accompanies this document in `tools/resort-blocks/venetian-public-layout.json`. It deliberately has no fabricated world-coordinate transform or measured heights.

## Reconciliation with current game

`tools/strip-landmarks/build.py` currently supplies a 37×65m frontal atrium, 88×62.4m casino, straight 86m upper canal and a well overlooking the casino. The code explicitly calls these interpretations. These dimensions and the well are not verified by the maps. The upper east terrace at [438.6,7.24,-734] and Rialto portal [225.85,6.24,-644] are current game anchors, not surveyed official-plan endpoints.

Next indoor construction should first register multiple map landmarks against mapped footprints and reference aerials. Trace all public areas at the same registration, fit each zone separately where the visitor diagram distorts geometry, and record residual errors. Derive a physical level schedule separately from floor names. Then replace one connected zone at a time, moving portals, colliders, visibility volumes, guest-core connections and route tests together. Preserve `InteriorLighting`, the fixed light pool, allocation-free runtime, optimized GLBs and existing streaming improvements.

## Guest suite evidence

Both official individual suite plans show an entrance beside the bathroom, a central sleeping area and a lounge by the window. The bathrooms show a private toilet, double vanity and separate bath/shower. These plans support those room relationships and the published total areas; they do not specify every linear dimension. The Venetian plan depicts the remodeled furnishings, including a curved sofa; the Palazzo plan has a different lounge arrangement. Treat the two as distinct templates. Sunken lounge details and accessible variants must be checked separately rather than applied to every room.

The suite plans are not full hotel-floor blueprints: corridors, stairs, service rooms and core placement still need evidence. No guest modules were regenerated in this pass. Before replacing them, reconcile the suite envelope with the existing tower bay spacing and keep every door opening, corridor, stair landing and streaming boundary functional.

## Remaining evidence gaps

Visitor maps give topology, not exact wall thickness, door width, ceiling shape, furniture placement or metre elevation. Meeting plans add actual room subdivisions and selected dimensions, and the individual suite plans establish room relationships and published areas, but none is a complete as-built hotel plan. No authoritative whole guest-floor corridor/core blueprint was found during this pass. Interior photographs, measured anchors and portal validation are still required. Exterior photorealism remains unachieved; these plans improve layout certainty rather than proving visual fidelity.
