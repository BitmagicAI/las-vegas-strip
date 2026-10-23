# Complete resort exterior workflow

This is the production process for the next architectural pass of Vegas: Afterlight.
Work on **one complete resort block at a time**: Cosmopolitan → Bellagio → Paris →
Planet Hollywood. The creator's 2026-10-05 instruction allows moving to Bellagio
now and making a separate refinement pass later. Implemented blocks with remaining
requirements use `refinement-deferred`, with their issues and evidence retained;
`complete` still requires every gate below. This overrides the original advancement
rule, not the definition of architectural completion.
Future blocks are added to the same queue after those four. Keep everything local.

The unit of work is the entire visible site, from pavement to roof. A tower with a
decorated ground-floor box is not a completed resort. Public terraces, restaurant
patios, pool decks, bridge landings and the routes that reach them are part of the
building. Neighboring low-rise buildings that define its frontage must be accounted
for, even when they have a different owner (for example, Jockey Club at Cosmopolitan).

## Working files and commands

- `queue.json`: sequence and active block. Only one block may be active. An explicit
  creator-approved deferral permits advancing without claiming full completion.
- `<block>.json`: source register, component inventory, level schedule, route graph,
  reference views, discrepancies and completion gates. Cosmopolitan is the first.
- `references/`: durable copies of the creator's reference screenshots, with source
  attribution in the block record. Remote photographs and official maps stay linked.
- `build/resort-blocks/`: generated review boards and measured source-model baseline.

From the project root:

```sh
python3 tools/resort-blocks/review.py
python3 tools/resort-blocks/review.py --ready
```

The first command validates the records and generates the local review board. The
second also fails until the active block meets the recorded completion requirements.
Neither command changes the game, starts a new block, uploads assets or publishes.
The check verifies evidence records, not visual quality; visual inspection remains
mandatory. Open `build/resort-blocks/index.html` through the local dev server.

Completion record conventions: set component/route/view `status` to `verified`, gate
`status` to `passed`, and attach project-relative evidence paths. Each view records
`camera` and `gameCapture`; each physical level records `elevationM` (guest floors
instead link a `schedule`). `performance.baseline` and `performance.after` point to
measurement reports. `finalBuild.files` maps installed asset/code paths to SHA-256
digests; changing those files makes the completion check fail until revalidated.

## 1. Survey the whole block

Before modeling, inventory every tower, low-rise wing, podium, entrance, public
outdoor floor, service facade and connection at the site boundary. Assign a stable
component ID and a single geometry owner. Use OSM/county data for editable plan
geometry, official resort maps for circulation, and Google Earth, Street View,
architect photographs and current ground-level photos for visual comparison.

Record the URL, author/provider, access date, known image date and what each source
actually establishes. An extract date does not date each OSM building. Architect
concept images and old promotional maps can differ from the built resort. Label
conflicts and estimated dimensions; never silently combine incompatible eras.
Use the latest corroborated permanent architecture as the default target. Temporary
event decks and branding are separate variants, not additions to the permanent shell.

Capture or link these views: north/east/south/west aerial, top-down, skyline from
both Strip directions, every public street frontage, each entrance from outside
and just inside, each public deck, and every bridge landing. Keep the photograph
and a matching game view together. Do not stretch a reference to conceal a mismatch.

**Exit evidence:** component inventory, source register, open questions, block map,
level schedule and route graph. Required but unverified features remain visible in
the checklist; uncertainty is a research task, not permission to omit a feature.

## 2. Fit individual structures and elevations

Keep the existing world datum: metres, X east, Y up, Z south; survey coordinates use
east/north, so invert the second survey coordinate when entering the game plane.
Origin: longitude −115.173, latitude 36.116. Do not rebase the rest of the city.

Fit each tower, podium section and low-rise separately. Confirm footprint, bend,
orientation, setbacks, crown and ground-to-top height in at least two independent
views. Preserve nonrectangular plans. A whole-resort bounding box is an inventory
envelope, not a valid transformation for every component. Author walls in metres;
do not nonuniformly stretch doors, furniture, balconies or stair treads to fit a lot.

Treat mapped heights/names as evidence requiring review. An OSM feature can describe
a podium or overlap another building despite carrying a tower name and height.
Do not remove a feature until its actual geometry has an identified replacement.

Create a **physical elevation schedule** distinct from hotel floor labels. Level 14
does not imply fourteen equal floor heights above the sidewalk. Record ground,
bridge deck, each podium floor, pools, terrace transitions, tower start and roof.
Unknown elevations stay null until corroborated or explicitly estimated with a
rationale. Document flat-datum compromises at sloping roads.

Target fit tolerances, subject to source accuracy: major footprint edges within
1 m or 1% of component width; confirmed tower heights within 2%; all architectural
connections continuous. These are authoring targets, not claims of survey precision.

**Exit evidence:** component plan overlays and sections; measured deviations;
before/after aerial and skyline views. Resolve silhouette/placement errors before
spending time on thousands of facade details.

## 3. Build the complete exterior section and circulation

Model the podium as occupied, stacked spaces: slab thickness, soffits, setbacks,
columns, glazed fronts, parapets, stairs, escalators, balustrades and roof edges.
Provide the actual ground-floor entrances, motor court/porte-cochere and bridge
entrances. The space seen immediately through each entrance must have its real
architectural character and a useful onward route.

Every public patio or deck gets a walkable floor, enclosure, access door, route from
the public interior, guardrails and return route. Include indoor/outdoor restaurant
thresholds, shade structures, bar/host counter, tables, seating, planters, lighting,
pool coping and pool safety boundaries where seen in references. Do not place a
restaurant patio on a generic rooftop because the correct one is not located yet.

Model pool decks and public gardens as reachable spaces. Guest-room balconies form
part of the exterior at all distances; their reachable interiors and collision load
with the corresponding room. Private/service roofs need a complete visible exterior
and credible access treatment but do not require every mechanical interior.

The route graph must cover sidewalk → entrance → arrival hall → public upper floors
→ outdoor decks → return, plus bridge → interior → street and guest-core connections.
Provide stairs/escalators where documented and a working lift route where needed.
No bridge may terminate in an opaque wall. Mark temporary construction blockers in
the work record; they cannot pass completion.

Shared connections have one owner, a world-space endpoint, elevation, clear width,
headroom and neighboring block ID. Work to that endpoint without rebuilding the next
resort early. Inspect both sides of the boundary after installation.

**Exit evidence:** sections, endpoint coordinates and walkable route probes at all
levels, including closed/open doors, moving stairs if used, and third-person camera
clearance. Test the route with surrounding city collision enabled.

## 4. Author distinctive facades and street life

Work facade by facade. Match bay spacing, solid-to-glass ratio, recessed glazing,
balcony depth, opaque service cores, material color and roughness, mullions, spandrels,
signage placement and roof silhouette. A repeating window texture cannot correct a
wrong tower plan. Build projecting features as geometry when they change silhouette,
cast a visible shadow or are reachable; use shared materials/textures for fine detail.

Street-level scope includes smaller attached buildings, storefront bays and awnings,
canopies, outdoor dining, retaining walls, stairs, planters, trees, street furniture,
curb ramps and driveway transitions. Keep original road/sidewalk geometry unless the
block work identifies a specific error. Preserve clear walking and driving routes.

Review materials in neutral daylight before reviewing the game's sunset lighting.
Use close walking views, driving views and distant skyline views. Repeated objects
should be instanced or batched. Texture references are not automatically licensed
game textures; record asset provenance separately from visual research sources.

**Exit evidence:** reference/game pairs for every frontage and public deck, plus an
entrance/outside and entrance/inside pair for every public entrance.

## 5. Integrate replacement geometry and streaming

Maintain explicit ownership across legacy detailed GLBs, OSM buildings, new block
geometry, public interiors and guest templates. Remove or carve only the replaced
surfaces and collision. Check shared building parts, podium roofs and facade strips
for duplicates. Do not fix overlapping solid models with a blanket polygon offset.

Exterior shell and skyline silhouette stay available. Near detail can stream by
component/level with hysteresis; distant models preserve shape, facade color and
major balcony bands. Never render both near and far solid shells simultaneously.
Cull decorative fixtures without removing floors, visible soffits or safety rails
around the player. Transparent glazing needs a stable opaque backing where there is
no active interior, and real openings at loaded rooms/terraces.

Stream public interiors by connected area; preload both sides of an opening before
the door opens. Keep outdoor visibility while on terraces or in windowed rooms.
Use the existing room/corridor templates and sparse room state; moving a tower must
also relocate cores, portals, visibility volumes, navigation and collision together.
Avoid synchronous geometry work when crossing a doorway; retain the loading UI when
an unavoidable load takes long enough to be noticeable.

Use simple collision for walkable slabs, substantial walls and rail boundaries.
No collider per window, mullion, chair leg, planter leaf or light fitting. Retain
inactive-tab pause, door camera collision, vehicle controls and existing room streaming.

**Exit evidence:** replacement/retained feature ledger, duplicate-surface audit,
collision counts and bounded memory/residency after leaving and returning twice.

## 6. Verify the actual installed block

Run the Blender geometry/collision audits, relevant existing route tests, typecheck
and local WebGPU verification. Follow `AGENTS.md` for exact engine commands, including
the latest creator prompt. Do not run cloud judging or upload/publish under the
current local-only instruction. Rebuild only affected assets; a building edit does
not warrant regenerating the whole Strip's roads.

Walk every public entrance, bridge, stair/escalator, deck, patio and return route in
the game. Drive the block perimeter. Check doors and camera collision, sky leaks,
missing backs/undersides, z-fighting, sign overflow, stairs and streaming transitions.

Measure the same route before/after with the same hardware, viewport and settings:
warm p50/p95 frame time, cold transition stalls, draw calls, triangles, live collision
bodies, GPU/CPU spans where available and resident asset memory. Record missing
metrics honestly. Target 60 fps on the review machine (16.7 ms frame budget), with
no unexplained >10% regression versus the recorded baseline. A fast startup sample
does not establish street, terrace or interior performance. Optimize until the block
is usable while retaining its key architecture.

Visual gate: inspect matching views of the **installed build**, list the largest
remaining differences, and fix them. Record camera position, target/FOV or lens,
lighting, reference image date and build fingerprint with each comparison. Offline
Blender renders help iteration but cannot substitute for game captures at this gate.

## 7. Close the block, then advance

All required components and routes must be verified; every gate must have local
evidence; no unresolved blocking discrepancy may remain. Exact dimensions that
cannot be sourced can be documented approximations, but missing required spaces,
wrong silhouettes, inaccessible patios and visibly generic frontages cannot be
waived as finished. Present the resulting reference/game comparison board and the
walkable result. Continue without routine permission prompts unless the creator
requests a review stop or a new action actually requires authorization.

Record the final build fingerprint, measured performance and remaining minor
approximations. Run `review.py --ready`, then set the finished block to `complete`
and the next queue item to `active`; create its full block record before building.
Do not relabel earlier broad architectural passes as complete under this new standard.

## Existing pipeline touchpoints

| Concern | Current location |
| --- | --- |
| Legacy Cosmopolitan geometry | `tools/level/cosmopolitan.py` |
| Legacy site transforms | `tools/geographic-strip/mapping.py` |
| Detailed source export | `tools/geographic-strip/export_detailed.py` |
| Existing public entrances | `tools/level/reconstruct_arrivals.py` |
| Mapped building-only regeneration | `tools/geographic-strip/rebuild-buildings.py` |
| Shared guest modules | `src/work/HotelTemplates.ts`, `src/work/hotels/` |
| Existing building visibility | `src/work/BuildingVisibility.ts` |
| Recent local architecture workflow | `tools/strip-landmarks/README.md` |

Before replacing Cosmopolitan, inspect the preserved staged Blender source used by
`export_detailed.py`. Editing the older standalone generator alone will not update
that staged file. Preserve the existing interior improvements and room connections.
Create the replacement in geographic metres with separately identified components;
do not pass it through the legacy whole-site transform a second time.

## Cosmopolitan geometry implementation

The active block is now installed; `cosmopolitan.json` distinguishes the playable
geometry proof from final architectural sign-off. Generated files are in
`build/resort-blocks/cosmo/`, served directly by the local dev server.

1. Run `build_cosmopolitan.py` with the local Python/numpy/shapely environment.
2. Run `export_cosmopolitan.py` in Blender to export the permanent shell and five
   independently streamed public furnishing sets. Each mapped level has real slabs,
   soffits, openings and stair connections, not just labels or review markers.
3. Run `install_cosmopolitan.py`. It reads current world files, removes only the
   prior Cosmopolitan owners and relocates both custom guest cores. It is also
   reapplied by the geographic installer after a geographic rebuild.
4. If rebuilding city assets, `export_city.py` applies `replace_chelsea_drive.py`:
   two previously inferred raised service drives are replaced by the authored
   arrival grade, preserving their surveyed centerlines and city endpoints.
5. Run `node tools/resort-blocks/test-cosmo.mjs --city`. This checks floor support,
   standing clearance and actual Rapier stair movement in both directions.
6. Run the required local typecheck and WebGPU verification. Inspect the running
   game via `/?resortReview=1&landmark=cosmoL4`; the optional review controls use
   normal movement input and show measured frame times, draws and residency.
7. `render_cosmopolitan.py` renders the exported game meshes under neutral daylight.
   `make_proof.py` assembles the local proof board. Neither substitutes for the
   installed-game screenshots or completes the remaining whole-block gates.

Levels 1/2/3/4/14 are floor names, with estimated physical elevations recorded in the
block JSON. Do not interpret “14” as fourteen equal storeys above the pavement.
