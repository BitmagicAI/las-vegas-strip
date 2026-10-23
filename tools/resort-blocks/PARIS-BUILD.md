# Paris mapped exterior — local build and review

Paris is the active sequential block. Cosmopolitan and Bellagio retain their
unfinished refinement inventories. See `paris.json` for sources, confidence and
acceptance status. This pass changes real geometry, with no asset uploads.

The existing OSM footprint anchors the X-shaped Bordeaux tower, podium, Arc,
balloon and entrance canopy. Google Earth was inspected from overhead, west and
south; its displayed imagery date was 2022-11-09. The official property map and
operator imagery establish the public space uses. Architectural detail and level
heights (0.24 / 6.64 / 10.74 metres in game coordinates) remain fitted estimates.
Do not call this a surveyed or fully finished reproduction.

## Build

Reuse the running dev server. Use the project Python environment with NumPy and
Shapely (`PYTHONPATH=build/south-strip/python`), Blender, and the local Node loader.

1. `python tools/resort-blocks/build_paris.py`
2. `blender -b --python-exit-code 1 --python tools/resort-blocks/export_paris.py`
3. `python tools/geographic-strip/rebuild-buildings.py`
4. `python tools/geographic-strip/compact_collision.py`
5. `blender -b --python-exit-code 1 --python tools/geographic-strip/export_city.py`
6. `python tools/resort-blocks/install_paris.py`
7. `node --experimental-loader ./tools/resort-blocks/test-loader.mjs tools/resort-blocks/test-paris.mjs --city`
8. `blender -b --python-exit-code 1 --python tools/resort-blocks/render_paris.py`
9. Run `bitmagic check`, `bitmagic verify`, `bitmagic reload`, each with the creator's
   actual request passed to `--original-prompt`. Do not publish or run cloud judge.
10. Visit `http://localhost:3090/?resortReview=1&landmark=parisBlock`, inspect/walk
    the exterior levels, update the record, run `tools/resort-blocks/review.py` and
    `tools/archive-project-records.py`.

## Ownership and clustering

Thirteen explicit OSM IDs are replaced. The selective installer removes old
Paris outside render batches/collision, preserving custom casino and guest
systems. It also removes the isolated obsolete Arc that an old numeric-name
classifier incorrectly assigned to the Eiffel Tower. The 2026-10-06 tower/pool correction replaces the Eiffel render/collision owner in world metres; its existing lift interaction and landing coordinates remain. The old hardcoded shadow proxy is removed. The city installer
reapplies this replacement after a rebuild.

Static geometry is grouped by source/material and authored 64-metre spatial cell;
the hotel tower is one separate scale-aware LOD group. The runtime uses existing
material batching and city LOD. Dynamic doors stay independent. Restaurant furnishings remain proximity streamed. Pool furnishings are permanent exterior geometry in spatial LOD cells; collider residency is proximity
managed. No per-table or per-window runtime script is added. Performance profiling
is deferred at the creator's request; no 60-fps claim is made.

All material textures are original. Earth/photographic captures are visual research,
not textures baked onto the game. Screenshots, source manifests and audits are
archived into `docs/project-records/` for GitHub with remaining work clearly marked.

## Historical validation for the initial pass (superseded by entrance correction)

- Local typecheck passed.
- Rapier route audit: 1,585 clearance/floor-support samples, zero failures,
  including retained geometry and the city collision data.
- Interactive Chrome: normal walking crossed the new street door and climbed
  both flights to the restaurant and pool landings. Screenshots and observed
  player coordinates are preserved in the review evidence.
- Automated WebGPU verification failed before starting gameplay: the Play button
  appeared but could not be clicked and the render loop stalled. The interactive
  walkthrough does not turn this automated failure into a pass. See
  `build/resort-blocks/paris/verify-webgpu.json` and its project-record archive.
- Performance was not profiled or accepted in this pass, at the creator's request.

Refinement work is explicit in `paris.json`: more exact crown setbacks and
sculpture, real access alignment/elevations, east/service elevations, every guest
floor's registration, and full internal restaurant circulation. The present
reference imagery is dated; do not describe the result as a current surveyed replica.

## Entrance correction, 2026-10-05

The creator rejected the first arrival composition. The close Earth screenshot in
`references/paris-entrance-earth-2026-10-05.png` is the primary visual brief for
this correction; the corresponding previous game image is retained beside it.
The new `paris_arrival.py` constructs a three-storey curved Louvre-inspired
facade, enclosed Opera-inspired pavilion and apse, fine glazed canopy, main
entrance vestibule, motor court, approximately 30m Arc with a real vaulted
opening, and an ornamental balloon/display pedestal. The design interview
linked in `paris.json` supports the historical architectural references.

`install_paris.py` now calls `clip_paris_arrival.py`: Paris-owned legacy
triangles/colliders are clipped out of the court and main vestibule, preserving
attributes and other resorts. The driveway circle also excludes the old
rectangular interior visibility zone. Its initial duplicate collider-name
loading error was fixed, and uniqueness is covered by the route audit.

For this correction alone, run steps 1, 2, 6–10 above. The full geographic
rebuild in steps 3–5 is only necessary after changes to its sources. The clip
version marker prevents repeated GLB buffer append; original inputs are backed
up in `build/resort-blocks/paris/arrival-before/`. After any full city export,
reapply the installer. The Blender exporter uses macOS Apple Chancery for
the raised Paris lettering; a port to another OS needs a licensed script font
substitute. No reference photograph is used as a game material.

The new street-to-rooftop stair flight is at x=68m, clearing the Opera pavilion.
The final route audit covers seven routes with 1,795 clearance/support checks,
zero failures, and verifies the outdoor-court/interior visibility boundary.
Final authored geometry has 874,627 triangles across 339 source/material/cell
batches; these are authoring totals, not runtime draw-call measurements.
The arcade reliefs, sculpture, decorative balloon motifs and dimensions remain
interpretations, not exact replicas. The main vault is open; transverse Arc
passages, full sculptural fidelity and dense mature landscaping remain refinements.

The current correction passes typecheck and local WebGPU startup verification.
See `arrival-verify.json` and `entrance-walkthrough.json` in the review archive.
The new glazed vestibule has a narrow windowed visibility zone so the city
remains visible through closed doors. No frame-rate guarantee is asserted.


## Parisian facade correction — 2026-10-05

The creator corrected the house-like character around the Arc. `paris_facades.py`
now articulates the retained curved arrival shell into adjoining Parisian facades,
with paired French windows, scroll ironwork, shallow balconies, selected shutters,
red awnings, alternate pediments and dormers, stepped mansard roof sections and
chimney pots. The east pavilion now also has its courtyard-facing return.

The creator's close Earth aerial remains the plan/composition reference. Robert A.
Walker's June 2001 ground photograph corroborates the streetscape details; it is
historical, not a current signage survey. Dave Toussaint's 2010 entrance interior
photograph establishes a coffered barrel vault for a future lobby correction.
Dimensions, motifs and individual awning placements remain interpretations.

The geometry retains the 64m/material static batching and existing route collision.
Decorative windows, iron scrolls and chimneys add no per-object physics or lights.
Close facade and aerial views are available in the local review controls. Proof and
validation: `build/resort-blocks/paris/facade-proof.html` and
`build/resort-blocks/paris/facade-validation.json`. Full-block sign-off stays open.


## Eiffel / pool correction — 2026-10-06

`paris_eiffel.py` and `paris_pool.py` are called by `build_paris.py`. Rebuild/export
Paris and run the selective installer; do not regenerate roads/city for this edit.
`review_paris_tower_pool.py` audits old-owner removal, height, exterior furniture
residency and route checks, then creates the local comparison. Tower total height
is confirmed; intermediate steel dimensions and pool arrangement are photo fitted.
The pool visibility zone stays in metadata to keep outdoor lighting and skyline
when walking the terrace; its streamed interior is only an inert anchor.
Review buttons include Tower and pool, Pool aerial, Tower base, Observation deck,
Lift cabin and Ride lift (L). F6 enables flight for aerial camera reviews.

## Eiffel shape retry — 2026-10-06

Creator rejected the first Eiffel/pool correction's tower silhouette. The retry
widens the piers toward the restaurant platform, reduces foot splay, adds the
upper-stage arch/apron, and uses flange/web girders and substantial primary
braces. It retains 164.9m total height and the lift location. The pool stair
moves to x66m to clear the enlarged pier; the street entrance route goes around
the footing. The 2,014-sample collision audit passes with surrounding city.
The supplied close Earth image is the proportion reference; intermediate
measurements remain fitted estimates. Use Tower base for the close review.
Previous successful functionality tests never constituted visual acceptance.
