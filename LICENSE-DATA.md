# Data licence: Open Database License 1.0 (ODbL) for OpenStreetMap-derived data

The city's street map, building footprints, mapped heights and names come from **OpenStreetMap**, © OpenStreetMap
contributors. They are available under the Open Database License 1.0: https://www.openstreetmap.org/copyright.

Files in this repository and its asset packs that contain OpenStreetMap data, or databases derived from it, are
licensed under the **ODbL 1.0** (https://opendatacommons.org/licenses/odbl/1-0/). They include:

- `docs/project-records/city-exteriors-2026-10-12/inventory.json`: mapped buildings, tags, heights, bounds.
- In the runtime asset pack:
  - `build/geographic-strip/` (city, roads, collision, access);
  - `build/highrises/` (mapped towers);
  - the footprint-derived parts of `build/strip-landmarks/` and `build/resort-blocks/`.
- The survey tools' outputs: `build/strip-survey/` and `build/geographic-strip/*.json`, rebuilt by
  `tools/strip-survey/` and `tools/geographic-strip/`.

What this means in practice:

- **Using the city in a game, a render or a video** makes it a "Produced Work". Credit "© OpenStreetMap contributors"
  where your credits go. You do not have to release your game.
- **Publishing a modified version of the data itself** makes it a derivative database. For example, a changed
  footprint set, height table or road network extracted from these files. That database must stay under the ODbL, and
  you must offer it (or the changes) under the same licence.

Original modelling that goes beyond the mapped data is our own work under CC BY 4.0 ([LICENSE-CONTENT.md](LICENSE-CONTENT.md)).
This covers facades, interiors, ornament and the textures we drew. Where the two are combined in one file, the ODbL
applies to the OpenStreetMap-derived part.

**Other public map data:**

- Road, sidewalk and median surfaces are also derived from the **Clark County GISMO** Pavement map service (Clark
  County, Nevada, https://maps.clarkcountynv.gov/), credited as "Pavement data: Clark County GISMO". The county's data
  itself is not in this repository: `tools/geographic-strip/fetch_county.py` downloads it at build time. Only the
  derived surfaces are in the runtime models (merged and simplified pavement, sidewalks widened from the county's
  sidewalk lines, medians closed from its curb lines, combined with OpenStreetMap), where they are part of the street
  data this file covers. NOTICE.md describes the derivation.
- Land cover (parks, water, parking) is also OpenStreetMap data, fetched through the Overpass API
  (https://overpass-api.de). The ground is a flat datum: no elevation model is used.
