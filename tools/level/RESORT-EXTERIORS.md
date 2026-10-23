# Remaining resort exteriors — September 2026 pass

Local Blender reconstruction of the three generic resort towers left in the saved level: Planet Hollywood, Flamingo and Horseshoe. These are reference-based game adaptations fitted to the existing compressed parcels, not surveyed digital twins. No external images are embedded in the level; all geometry and fictional faded concert posters are authored locally.

## Visual references

- [Planet Hollywood aerial and pool terrace](https://www.vegasalways.com/planet-hollywood-las-vegas-pool/), with the linked overview image credited to @phvegas: folded cream tower, narrow vertical glazing, rounded ends, two projecting lower suite wings, pool deck and curved retail fascia.
- [Flamingo aerial](https://www.livingsocial.com/articles/flamingo-las-vegas-guide): connected wings surrounding the garden, pink glazing, white horizontal ribbons and broad end piers. [Official property overview](https://newsroom.caesars.com/Property-Fact-Sheets/Flamingo-Las-Vegas/) confirms the resort's garden/pool character.
- [Caesars' Horseshoe grand-opening release and exterior photograph](https://www.businesswire.com/news~/en/Horseshoe-Las-Vegas-Celebrates-its-Grand-Opening-on-the-Las-Vegas-Strip): champagne structural piers, stepped slabs, curtain walls, blue glazed crowns and arched entrance canopy.
- [Official Paris tower expansion announcement](https://newsroom.caesars.com/press-releases/press-release-details/2023/ADDING-MULTIMEDIACaesars-Entertainment-Unveils-Plans-to-Add-Hotel-Tower-to-Paris-Las-Vegas/default.aspx): the former Jubilee tower belongs to Paris as Versailles. This pass models Horseshoe's remaining Resort Tower rather than relabeling Versailles.

## Placement and existing gameplay

North remains negative game Z. Flamingo is north of Flamingo Road; Horseshoe is between the road and Paris; Planet Hollywood is south of Paris and across the Strip from Cosmopolitan.

| Resort | Existing public floor bounds (X / Z, m) | Entrances preserved | Exterior work |
|---|---|---|---|
| Planet Hollywood | 65–198 / 173–274 | west (65,218), south (174,274) | Folded 98 m tower, 60/63 m rounded suite wings, twin pools, cabanas, curved metal retail screen, canopies, pylon |
| Flamingo | 90–200 / -259–-215 | west (90,-237), south (145,-215) | 66 m garden wings, lower Strip wing, pink/white glazing, enclosed garden, sculpted lotus entrance marquee |
| Horseshoe | 92–128 / -147–-85 | north (110,-147), Paris connector south (110,-85) | Stepped 76/71 m slabs, projecting piers and flared bases, glazed crowns, barrel canopy |

[Flamingo entrance photograph](https://commons.wikimedia.org/wiki/File:Flamingo_hotel_(Las_Vegas)_Front_Entrance.JPG) supplied the pink/gold bulb, splayed petals, silver ribs and cursive rooftop marquee details.

The existing casino floors, lobbies, shops, stairs, doors and missions are unchanged. The Flamingo garden is compressed above the public podium to retain the playable first-floor layout. New upper masses begin at 12.42 m, above the 12.4 m public roof. This is a deliberate gameplay adaptation. The existing Bellagio, Paris/Eiffel, Caesars and Cosmopolitan geometry is retained.

## Rebuild and review

- `build/exteriors/baseline.blend`, `.mesh-level.json` and `.doors.json` are immutable pre-pass backups (after interiors and visibility changes).
- Run `Blender -b --python tools/level/finish_resort_exteriors.py` from the project root. This removes only old generic exterior objects/colliders, builds the new designs and saves the canonical Blender scene and level JSON.
- `Blender -b --python tools/level/render_resort_exteriors.py` produces street, aerial and entrance views under `build/exteriors/`.
- Audit both open and closed doors with `tools/blender-level/audit.py`.
- Run `tools/level/export_visibility.py` only after review. It rebuilds the same room-based visibility batches, then copy the canonical mesh-level JSON into `src/work/`.
- Alternatively `--export` on the builder performs that export as part of a reviewed repeat build.
- Upper mass colliders are also the simplified long-range environmental shadow casters. Window frames, lettering, facade detail and landscaping are decorative. New small ground-level foundations/portico columns collide.
- Keep everything on localhost. Do not register/upload the GLB or publish the game.

## Validation

- 3,070 old generic render parts replaced by 10,891 authored exterior details.
- 26 old tower/roof-plant colliders replaced by 36 coarse masses and canopy supports: 1,371 colliders total. All 1,335 retained colliders are byte-for-byte equivalent as JSON records.
- All 265 volumes, 28 doors, interior routes/stairs, lights and mission landmarks preserved.
- Final open-door audit: 237,121 floor rays, 1,428 doorway rays, 65,889 route rays; zero failures.
- Final closed-door audit: 283,195 envelope rays; zero failures. The existing 707 coplanar warnings are unchanged.
- Geometry orientation checked; inward closed solids repaired before export.
- Local review bookmarks: `?inspect=planet-hollywood-exterior`, `?inspect=flamingo-exterior`, `?inspect=horseshoe-exterior`.
- GLB export: 260.8 MB; 4,604,710 triangles in 378 visibility/material batches. Detailed lettering and the lotus ornament account for part of the increase; interiors remain culled by the existing policy.
- `vegas-asset-version.json` records a SHA-256 revision after each completed visibility export. The local URL includes that revision to prevent stale GLB caches after Blender rebuilds.
- Type check and all 14 visibility-policy scenarios pass.
- Final WebGPU verification passed with revision `ceb900b0d2536b70`, 1,434 total physics bodies and 235/378 batches visible from the outdoor spawn. The settle sample reported 60 fps; this is a spawn sample, not a performance benchmark of every resort.
