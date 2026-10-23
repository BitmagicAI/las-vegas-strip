# The Venetian's public interiors, rebuilt (2026-10-23)

## Why

The owner, on the info video's preview 3 at 1:56 (the Grand Canal Shoppes): "What happened? This looks exactly like
before, very low detail, blocky." Offered three ways forward, they chose **"Rebuild to the floor plans"**: rebuild the
public interiors to the official resort map at full detail, before the final video.

The interiors were still the 2026-10-08 first version. The October detail passes had covered the exterior and the
outdoor canal only.

## Sources (viewed for reference, never redistributed or committed)

- The official resort map, Levels 1 and 2 (`venetianlasvegas.com/content/dam/venetian/resort/map.pdf`). The earlier
  study is in `docs/project-records/venetian-floorplans-2026-10-09.md`.
- Openly licensed photographs on Wikimedia Commons: Category:The Grand Canal Shoppes, "Venetian Hallway", "The Venetian
  Lobby", "Great Hall of The Venetian", "St. Mark's Square, The Venetian hotel" and the Venetian street lamps.
  Screenshots for local viewing are in `build/venetian-interiors/references/` (ignored).

## Layout

`tools/strip-landmarks/venetian_interior_plan.py` has every zone in world metres, plus a survey of what already stood:

- **Level 2:** the map's Venetian half is drawn close to scale. It registers as z = -811 + 0.41 (u - 1290),
  x = 436 - 0.41 (v - 400), and the canal follows it.
- **Level 1:** fitted inside the podium (relation/7770314) around what is fixed:
  - the palace door (225.0, -685.14);
  - the Rialto gallery door (225.85, -644, y 6.24);
  - the east terrace door (438.6, -734, y 7.24);
  - the hotel system's tower-1 lobby (a gallery from the door at x 250.7, then an 84 m room x 293.3..376.9,
    z -627.9..-608.9, 7 m high). Nothing may enter it.
- Exterior parts that already stand inside the podium, which the interiors route around rather than cut:
  - the podium's outdoor notch (x 224.5..242.5, z -657.8..-650.6, walls to 17 m);
  - the palace's south wing (x 226..238, z -655.7..-643.7);
  - the palace's floor bands (reaching x 230.15 at 7.31..7.87 m);
  - the Rialto's abutment wedge.
- **The Waterfall Atrium** (the map's Palazzo end) is not built. It stands inside the Palazzo's footprint, where the
  Palazzo's street facades are.

## Three streamed venues

| Venue | Built by | Contents |
|---|---|---|
| `venetian` (its interior) | `venetian_lobby.py` | the Great Hall, the Scenic Overlook, the Rialto landing, arrivals, the hotel lobby colonnade, the rotunda with the Armillary Sphere, the front desk |
| `venetianCasino` (`levelY` 3.74) | `venetian_casino.py` | the casino floor, the escalators to St Mark's Square, Restaurant Row |
| `grandCanal` (`levelY` 7.24) | `venetian_shoppes.py` | Level 2: the canal from the gondola dock to the loop round the island, quays, St Mark's Square, the Rialto street with its archway house, the passage to the terrace door |

- **Portals:**
  - the palace door is exterior-owned;
  - the Rialto gallery door and the new arrivals door (232, -630.75, onto the forecourt) belong to `venetian`. The
    arrivals opening is cut in the podium shell in build.py;
  - the east terrace door moved to `grandCanal`.
- **Anchors:** each sub-venue has a 1 cm anchor exterior (the runtime loads an exterior for every venue).

## Tools

| File | Role |
|---|---|
| `venetian_materials.py` | Every `vi-` material. Procedural albedo and normal maps for stucco, stone, brick, rustication, roof tile, tumbling blocks, the diagonal checker, St Mark's pavers, gilt and more. UV modes: world, panel and sky. |
| `venetian_textures.py` | Prepares the generated images. The day sky and the carpet are made seamless; the frames are cropped off the shop windows. |
| `venetian_kit.py` | The shared kit: profile sweeps (cornices, archivolts, surrounds), walls with real openings and reveals, windows (arched, Gothic, ogee, segmental) with shutters, balconies and flower boxes, Corinthian columns, arcades, entablatures, barrel vaults with fresco bays, oval frescoes, coffers, Murano chandeliers, house fronts and rows, balustrades, street and Murano lamps, stone bridges, mooring poles, cafe sets, planters. |
| `build_venetian_interior.py` | The harness: builds, saves, merges `venues.json` under a lock, and makes the anchors. `build.py` calls the same modules. |
| `venetian_review.py` | Offline EEVEE review renders: world ambient plus the venue's light pools. |
| `venetian_swatches.py` | The material board (`build/venetian-interiors/swatches.png`). |
| `venetian_kit_sample.py` | A kit test scene. |
| `vi_blender.sh` | One Blender run at a time. |

## Generated images (originals for this project)

Made with `bitmagic generate image`. The prompts and source URLs are in `build/venetian-interiors/generated/*.json`.
The asset rows the command adds to `world.json` were removed.

- painted skies: `vi-sky-day`, `vi-sky-dusk`;
- frescoes: `vi-fresco-a`, `vi-fresco-b`, `vi-fresco-oval`;
- the casino carpet: `vi-carpet`;
- shop-window interiors: `vi-shop-fashion`, `vi-shop-glass-art`, `vi-shop-masks`, `vi-shop-sweets`;
- ceiling panels: `vi-ornament-red`, `vi-ornament-green`.

## Checks

- **Routes:** walked with a player capsule by `tools/strip-landmarks/test-routes.mjs --only venetian,venetianCasino,grandCanal`.
  The three venues are walked together, and the Rialto approach continues into the lobby
  (`test-venetian-rialto.mjs`).
- **Review renders:** `build/venetian-interiors/review/` (ignored).
- In-game captures and the interior performance probe are to be added below as they are made.
