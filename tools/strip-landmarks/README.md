# Local Strip architecture

`plan_next.py` fits Park MGM, Palazzo, Treasure Island and Harrah's arrival halls
and routes them to the existing guest cores inside the mapped podium envelopes.
`next_arrivals.py`, called by `build.py`, authors these halls and Polo Towers.
Photo sources are recorded in `build/strip-landmarks/references-next/sources.json`.
Interior circulation and art are interpretations, not surveyed replicas.

Regenerate from the project root, using the bundled Python 3.12 and local Blender:

1. Run `plan_next.py`, then `build.py`. Copy the resulting `guest-towers.json` to
   `src/work/hotels/landmark-towers.json`.
2. Run `export.py` in Blender. Arguments after `--` select asset names, such as
   `park-exterior park-interior`. No arguments exports every landmark.
3. If connections changed, regenerate `tools/highrises/exteriors.py`, then run
   `tools/highrises/export.py` in Blender. That exporter also restores the authored
   New York–New York and Excalibur surfaces. Run `export_guest_lobbies.py` in Blender
   to cut the corresponding guest-lobby doorways.
4. Run `guest_sets.py -- polo` in Blender for Polo's shared modules and lobby.
   Increment `HotelTemplates.ts`'s revision when changing hotel GLBs.
5. After changing replacement IDs, run `tools/geographic-strip/rebuild-buildings.py`,
   then `compact_collision.py`, then `export_city.py` in Blender. This preserves the
   expensive road/sidewalk/landscape geometry. Do not use a full road regeneration
   merely to remove a replaced building.
6. Run `node --experimental-loader ./tools/geographic-strip/test-loader.mjs
   tools/strip-landmarks/test-routes.mjs --city`, `bitmagic check`, and local WebGPU
   verification. Route checks include neighboring city geometry, public halls,
   connecting guest lobbies, stair flights and representative rooms.
7. Render `review.py -- park palazzo ti harrahs polo` and
   `review_guests.py -- polo` in Blender, then run `make_review_next.py`.

The exported models use material batches. Upper facade ornament is tagged for
distance culling. Public halls and hotel modules stream independently; decorative
flowers, lighting fixtures and artwork do not each create physics bodies.
Internal gallery access points also keep the public hall loaded when approaching
from guest stairs. Original map objects owned by each replacement are excluded.

Everything is served locally. These steps do not publish or upload the level.

## Targeted north-Strip corrections (2026-10-09)

- `build_venetian_exterior.py` runs the shared exterior section and
  `venetian_surface_ownership.reconcile`: subtracts duplicate tower/podium faces,
  retaining collisions and every interior. `test-venetian-overlaps.py` now tests
  ten known independent surface pairs; `audit_lower_venetian.py` inventories the
  wider set for diagnosis (internal caps are not automatically visible defects).
- `build_linq_exterior.py` replaces the blue tower skin without regenerating the
  High Roller or interiors; `linq_facades.py` owns the projecting glass bays.
- `build_ti_exterior.py` moves only tower render ownership from HighriseCity to
  StripLandmarks. Keep HighriseCity's collision and guest modules.
- `build_forum_shops.py` restores OSM way/34068416, already excluded by the legacy
  Caesars replacement. `forum_shops.py` creates a separate `exteriorOnly` venue;
  it intentionally has no invented interior or lights. Run
  `node tools/strip-landmarks/test-forum-shops.mjs` for roof/sidewalk collision.

Run these with the existing Python 3.12/numpy/shapely environment. Export only the
changed `*-exterior` names with Blender `export.py`, then optimize and install
those assets. For a new venue run `node tools/optimize/optimize-runtime-glbs.mjs
--list` before installing, since the installer uses that generated inventory.
No road, city or interior regeneration is needed. Neutral reviews use
`review_facades.py -- <venue key>` in Blender; the installed-game probe's `--hold`
option is for airborne visual inspection only, not a driving/performance test.

Evidence, known approximations and protected-file hashes:
`docs/project-records/north-strip-corrections-2026-10-09.md`.

## City exterior passes (2026-10-12)

Use the targeted builders `build_planet_hollywood.py`, `build_mgm_grand.py`,
`build_park_mgm.py`, `build_luxor.py`, `build_mandalay_bay.py`, and
`build_new_york_frontage.py`. They preserve the other venue metadata and interiors.
Do not run the older full `build.py` over these passes: its older Park exterior and
venue list do not represent these installed replacements. Follow each block record.
For building-only geographic exports pass `-- --preserve-surfaces`; no road, lawn,
or sidewalk rebuild is necessary. The optimizer now refreshes its installer list
on every invocation so newly added venues are not silently omitted from installation.

### 2026-10-14 Flamingo podium and Vanderpump exterior

`build_flamingo.py` includes `flamingo_podium_detail.py`; follow the surgical
`tools/city-exteriors/install-flamingo-podium.py` removal and block record before
exporting city buildings. Four mapped podium/canopy IDs now have explicit ownership.
`build_vanderpump_exterior.py` is exterior-only: it retains the occupied footprint,
public entry and venue metadata. Its compressed source snapshots in `retained-source/`
make the targeted rebuild reproducible; they are original project geometry, not
external assets. It replaces old guest-source facade/roof geometry and keeps the
lower shell and entrance. Export/optimize only `vanderpump-exterior` afterwards.
Do not run the whole legacy `build.py`. Interior JSON and collision remain untouched.

## Wynn remaining structures, 2026-10-14

`build_wynn.py` owns all fourteen mapped Wynn/Encore IDs and appends them to
`replacement-ids.json`. The older city boxes must be removed with the building-only
rebuild, preserving surfaces. The Beach Club court is cut out of the broad Encore
podium before rendering and collision generation. `cut-encore-pool-paths.py` removes
only obsolete bridge-kit faces inside that court; rerun it after any intentional
future full street regeneration. Do not remove the public street bridges.

Way886592894 and way886592897 are open entrance canopies, not retail blocks; the
latter's earlier enclosed-pavilion interpretation was corrected using its exact
Earth view. Way142899198 is the raised round pavilion with a roof oculus.
See the Wynn block record for source URLs, estimated elevations and remaining
landscape/furniture/circulation work. This is a reviewed exterior pass, not a claim
of photo-perfect completion.

## Mandalay pool court, 2026-10-14

`mandalay_pool_detail.py` uses preserved OSM pool contours in
`mandalay-pool-plans.json`, including lazy-river island holes. Tree positions are
mapped in `mandalay-palm-positions.json`; heights and furniture layout are estimates.
The Four Seasons pool courtyard is subtracted from its coarse building outline.
`build_mandalay_bay.py` owns its four main podiums and fifteen small pavilions.
A building-only city rebuild removes those old generic shells.
`tools/city-exteriors/cut-mandalay-pool-paths.py` clips only obsolete bridge-kit
geometry inside the private pool-court envelope; rerun after a future intentional
full surface regeneration. Public road geometry is not regenerated.
Current review and incomplete gates are in the Mandalay block record.
