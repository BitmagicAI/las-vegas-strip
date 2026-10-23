# Notices and credits

## Licences at a glance

This repository's licences apply to the Vegas project only. They do not cover the Bitmagic engine, the Bitmagic CLI or
its skills, or third-party material.

| What | Where | Licence |
|---|---|---|
| Program code | `src/`, `tools/`, `tests/`, configuration | MIT ([LICENSE](LICENSE)) |
| Original content: models, textures, level/collision/route data, records, documentation | repository and asset packs | CC BY 4.0 ([LICENSE-CONTENT.md](LICENSE-CONTENT.md)) |
| OpenStreetMap-derived data | inventory, city/road/footprint data | ODbL 1.0 ([LICENSE-DATA.md](LICENSE-DATA.md)) |
| The Bitmagic engine (a dependency, not in this repository) | `engine/` after `bitmagic upgrade` | Bitmagic Engine License: PolyForm Shield 1.0.0 with the games permission (`engine/LICENSE.md`) |
| Third-party assets | listed below | their own licences |

**Credit line** for games, videos and renders that use the city:

> Las Vegas Strip (https://github.com/BitmagicAI/las-vegas-strip), CC BY 4.0 · Map data © OpenStreetMap contributors, ODbL · Pavement data: Clark County GISMO

The game itself shows the map credits in the corner of the screen (`src/work/GeographicCity.ts`).

## The Bitmagic engine

Required Notice: Copyright Bitmagic Oy (https://bitmagic.ai)

The game runs on the Bitmagic engine. The engine is **not part of this repository** and not covered by its licences.
`bitmagic upgrade` installs it into `engine/` (ignored by git) for anyone with a Bitmagic Pro subscription, under its
own licence (`engine/LICENSE.md`). That licence allows you to build, modify, publish and sell games with the engine,
anywhere. It does not allow you to distribute the engine itself as an engine, framework or starter kit. The same applies
to the agent skills the CLI installs into `.agents/skills/` and `.claude/skills/`. The publish configs
(`vite.publish*.config.js`) stamp the engine's required notice into every built bundle; leave their `banner` in place.

## Third-party data and assets

- **OpenStreetMap:** © OpenStreetMap contributors, ODbL 1.0. https://www.openstreetmap.org/copyright. Covers building
  footprints, heights, names, roads, paths and land cover, fetched through the Overpass API.
- **Clark County GISMO:** Pavement MapServer, Clark County, Nevada.
  https://maps.clarkcountynv.gov/arcgis/rest/services/GISMO/Pavement/MapServer. Covers road, sidewalk and median
  surfaces. Terms being confirmed (task `rel-county-terms`).
- **Poly Haven:** CC0. The 15 scanned surface sets packed into `build/pbr/strips/` by `tools/pbr/pack-strips.py`:
  clean_asphalt, concrete_pavement, concrete_floor_02, white_stucco, concrete_wall_008, sandstone_blocks_08, marble_01,
  brick_wall_02, metal_plate, aerial_grass_rock, gravel_floor_02, clay_roof_tiles_02, bitumen, dry_ground_01 and
  granite_tile_03. https://polyhaven.com.
- **Statue of Liberty scan:** gomeasure3d, CC BY 4.0, https://zenodo.org/records/10307962. Adapted: decimated,
  centred and placed as New York-New York's statue (`tools/south-strip/prepare_liberty.py`, then the south-Strip
  export). The adapted mesh ships in the runtime pack under CC BY 4.0, and the game credits it on screen.
- **Bitmagic-generated assets** (the cover image, the sky and the legacy level at `bitmagic.ai/worlds/...` URLs in `src/work/world.json`)
  were generated with Bitmagic's tools for this project and are served from Bitmagic's CDN.
- **The Sphere's screen content** (`build/sphere/*.mp4`) is original procedural artwork, not official Sphere
  programming.
- **npm dependencies:** three (MIT), @dimforge/rapier (Apache-2.0), @msgpack/msgpack (ISC), fflate (MIT), i18next (MIT)
  and jszip (MIT). They are installed by pnpm, not vendored.

Every other texture is drawn by the project's own scripts, for example `tools/make-public-resort-textures.py`,
`tools/make-arrival-materials.py` and `tools/strip-landmarks/luxor_obelisk_texture.py`. The task
`rel-texture-provenance` tracks the remaining unrecorded images.

## Research sources

Block records (`tools/resort-blocks/*.json`) and project records (`docs/project-records/`) link the public sources
consulted for each building. These include resort maps, floor plans, photographs, Google Earth and Street View
observations, and architects' pages. They were **viewed for reference only**. None of those images, plans or
screenshots is part of this repository or its asset packs, and no geometry was extracted from Google Earth or Google 3D
Tiles.

## Real places and brands

This project depicts real buildings in Las Vegas, Nevada. The names of resorts, casinos, shops and restaurants,
and the lettering of their signs, appear only to describe and depict those places. All trademarks belong to their
owners. The project is not affiliated with, sponsored by or endorsed by any of the property owners or brands depicted.
The licences above cover this project's own copyright only. They grant no rights in third-party trademarks, and if you
build something commercial on the city you are responsible for clearing those yourself.
