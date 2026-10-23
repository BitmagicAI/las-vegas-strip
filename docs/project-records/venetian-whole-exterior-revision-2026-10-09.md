# Venetian whole-exterior correction — 2026-10-09

This is an installed correction pass, not a photorealistic completion claim. The creator’s rejected game/Google Earth pair is retained in `venetian-exterior-2026-10-09/`.

## Changed geometry and surfaces
- Replaced the long constant-width canal with two mapped OSM basins, including the larger irregular main basin and its narrow branches. Added stone coping, shoreline mooring posts and repositioned gondolas.
- Added the missing upper volume of the north canal frontage on its mapped podium footprint, with recessed four-storey facade bays, heavy cornices and a roof parapet. Height34m remains an estimate.
- Revised Venetian tower body glazing, arched crown proportions, recessed stone reveals, solid end walls/vertical lettering, and the secondary tower’s horizontal parking-level bands. Mapped footprints and existing hotel collision/rooms retained.
- Completed the covered upper Rialto connection to its existing gallery landing.
- Replaced the podium’s dark generic roof with a pale surface.
- Added3,515m² of canal-side paving clipped against mapped water, buildings and roads, with stone courses and two palms in clearance-checked planters. Landscaping remains too sparse.
- Applied the existing scanned stone/brick PBR sets to the new material names; no new runtime lighting or per-object update systems.

## Verification and views
Existing city route checks:9,889, zero failures. Type check passed. Local WebGPU verification is recorded separately; startup performance does not establish resort performance. Optimized asset and source hashes are in `tools/resort-blocks/venetian.json`.

Installed game views: `revision-installed-game.png` (whole complex), `revision-frontage-game.png` (closer frontage, before final pale-roof material correction), and `revision-final-game.png` (final).
Camera whole-site eye[-40,225,-1050], target[260,50,-650]; closer eye[110,145,-900], target[265,55,-655]. Game’s normal sunset lighting and camera FOV; no pixel-exact camera match to Google Earth. Offline image was useful for geometry but is not final installed evidence.

## Sources and uncertainty
OSM ways115776193/180831029 (raw `canal-osm-reference.json`) provide horizontal water outlines. Projection usesR6378137 and origin(-115.173,36.116), consistent with the project survey. Water0.31m, quay0.245m, width10m and north-frontage34m are provisional. Planting positions preserve roads and mapped footpaths; this does not constitute an as-built planting survey. Earlier official pool maps and photographs remain in the source register.

## Outstanding whole-exterior work
The quality gate remains failed: this still lacks photo-real fidelity. Largest discrepancies are incomplete/dilute gardens and podium frontage, overly plain large roof areas, unverified tower/wing proportions and physical elevations, simplified campanile/palace sculpture, approximate bridge span/understructure, and generic storefront details. Public pool/deck access remains unresolved; existing route tests do not certify unbuilt connections. Full perimeter walk/drive and matched-camera performance comparison are pending. No other resort should be started before this block’s next architectural correction.

The overnight automation remains paused. Local generator files, references, tests and comparisons are preserved for GitHub; nothing was uploaded or published.
