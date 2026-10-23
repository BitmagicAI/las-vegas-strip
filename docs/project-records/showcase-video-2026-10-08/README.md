# Showcase video: a 60 fps tour of the Strip (2026-10-08)

Owner request (summary): make a 60 fps video driving around Las Vegas, entering casinos, kicking open hotel-room doors, looking out of a window and riding the New York coaster, recorded with far foliage, a longer shadow distance and the highest graphics setting.

## Result

**`VEGAS: AFTERLIGHT — a tour of the Strip`**, 2:28.

**Format:**
- 1920×1080 at exactly 60 fps.
- H.264 High 4:2:0 (x264 slower, CRF 12), tagged BT.709.
- AAC 320 kbps at -14 LUFS.

**Files:**
- Master: `.bitmagic/film/out/vegas-afterlight-tour.mp4`.
- Copy for the owner: `~/Movies/Vegas Afterlight/`.
- Not published or uploaded anywhere.

**What the video covers:**
- **Opening and title:** an aerial over Planet Hollywood toward the Eiffel Tower, then the title card.
- **The drive:** the jeep north past Paris, Caesars, the Flamingo and the Venetian. It then turns south past CityCenter toward New York-New York, cut with chase, front-tracking, side-tracking and crane cameras.
- **Seven casinos and lobbies:** the Caesars approach and dome, the Venetian (street → glass doors → frescoed lobby), Flamingo, the Bellagio glass-flower lobby, Planet Hollywood and the Palazzo fountain.
- **Three hotel room doors kicked open:**
  - Caesars, level 21.
  - The Cosmopolitan, level 41, with its floor-to-ceiling window over the Strip.
  - Bellagio, level 21, held at the window with the Eiffel Tower outside.
- **The Eiffel deck** at 140 m.
- **The Big Apple Coaster** at New York-New York, in POV: boarding, the lift hill, the crest, the drop, the inversion and the fast twists.
- **The ending:** a rising aerial over the Bellagio lake, then the end card.

**Sound:** a generated 150 s instrumental music bed (`bitmagic generate music`, one call). The game itself has no audio. The cut follows the bed's beat grid: 99.6 bpm, cuts on beats, the drive starting where the drums enter, and the coaster on the loudest stretch.

## Graphics settings used while recording

| Setting | Value | How it was set |
|---|---|---|
| Quality | Ultra, the highest tier (4096 shadow cap, SSR, AO, DOF, bloom, high materials) | `bm.quality` = `ultra` |
| Foliage distance | 200 %, the slider maximum: grass 72 m, trees 1.3 km | `afterlight:foliage:v1` |
| Shadow distance | 192 m, new setting (below), 8192 shadow map | `afterlight:shadows:v1` |
| Resolution | 1920×1080 frames from the engine recorder, at a pixel ratio of 1 | — |

## Built for this

- **Shadow distance setting** (new; `src/work/ShadowSettings.ts`):
  - Lives in the B panel as "Sun shadows", 32–192 m, saved in the browser.
  - The focused sun's receiver region was fixed at ±32 m. `AfterlightShadows.setDistance()` now widens it.
  - Above ±48 m it uses an 8192 map, so ±96 m still has 2.3 cm texels.
  - Measured cost at 192 m: the shadow pass goes from 0.3–0.7 to 1.2–2.3 ms, and every probe view stays at 60 fps.
  - The default (32 m) is unchanged.
- **Kicking doors** (new; `src/work/DoorKick.ts` plus `GuestDoor` in `hotels/HotelStreaming.ts`):
  - **F** on desktop, **KICK** on phones, kicks a closed hotel room door in front of you open.
  - In first person the view lunges and jolts on impact. The door leaf swings on its hinge away from you (0.34 s, with a small overshoot) while its collider slides out of the doorway as before.
  - A room that is not loaded yet loads first (the usual hold), then bursts open.
  - The swing animates the door's skin on its own hinge pivot, so the engine's slide never shows.
  - E still opens doors normally.
  - There is no kick animation for the third-person body and no sound: the game has no audio, and the player rig has no kick clip.
- **Film director** (local filming only; `src/work/film/Film.ts`):
  - Loaded when localStorage `afterlight:film` is `1` on localhost; it never loads in a published game.
  - Takes are JSON scripts played on the game clock: walk, drive, look, kick, keys, waits, plus a camera track (world-, jeep- or player-relative keyframes).
  - A virtual gamepad drives the player. It gives analog walking and analog steering, with the throttle and brake on RT and A, which is how the engine drives vehicles from a pad.
- **Tools** (`tools/film/`):

  | File | What it does |
  |---|---|
  | `make-takes.py` | Writes `takes/*.json` from the level data and the scouted spots |
  | `record.mjs <take>...` | Boots once with the settings above and records each take with the engine's frame recorder (exact 60 fps) |
  | `sheet.py <take>` | Contact sheets |
  | `plan-cut.py` | Writes the beat-snapped cut, `cuts/vegas-tour.json` |
  | `build.py <cut> [--preview]` | One encode from the PNG frames, with music, title and caption cards, and two-pass loudness |

- **Review hooks:**
  - `__afterlightProbe.inspect(name)` (the `?inspect=` placements), `kickDoors()` and `kick()`.
  - `--storage` on `probe-eval.mjs` and `probe-interiors.mjs`.
  - `__shot(name)` in probe-eval scripts.

## Footage

19 takes are kept in `.bitmagic/trailer/recordings/<take>/` (69 GB of PNG frames) for recuts. Not all were used.

| Takes | Length |
|---|---|
| `aerial-open`, `aerial-close` | 16 s each |
| `drive-north` | 117 s |
| `drive-south` | 81 s |
| `casino-*`, `lobby-*`, `bellagio-conservatory`, `crystals-atrium`, `caesars-approach` | 10–21 s each |
| `kick-bellagio`, `kick-caesars`, `kick-cosmo` | 13–15 s each |
| `eiffel-deck` | 50 s; the walk stalled at the safety cage, used as a slow look |
| `coaster-ride` | 181 s, the full ride |

## Traps found while filming

- **Gamepads after boot:** `GamepadControls` only rescans while it already holds a pad. A pad added after boot needs a `gamepadconnected` event.
- **Vehicle throttle:** in a vehicle the engine ignores the left stick's Y and takes the throttle from RT and the brake from A.
- **Pitch sign:** the first-person camera's vertical angle is positive DOWN. The film uses positive up and negates it.
- **Seating while filming:** `SanctuaryJeep.seatForReview` now also works under the film flag, not only with `?probe`.
- **Leave the jeep first:** a teleport does not move a seated player, so an on-foot take must leave the jeep first.
- **Streamed places:** the Eiffel deck and upper floors stream in after a teleport, and the player can fall first. Place again once streaming is idle.
- **Runaway takes:** a drive that never reached its last point recorded 9 minutes. Drives now end when they pass the last point, and every take has a time limit (`maxSeconds`, default 240).
- **Frame storage:** frames stream into `capture.mp4` and are extracted to PNG after the stop. Deleting a take while the dev server is still extracting needs the extractor stopped and a retry.
- **Chained edits:** an edit chained after a failing `rm` with `&&` never ran. That looked like a stale dev server; check the source file before restarting.

## Version 2: realistic water, drone drives, logo, resort numbers (2026-10-08)

Owner request (summary): add realistic water to the water features (such as the Bellagio pool), fly the drive camera as a drone on a more interesting path, and add a semi-transparent Bitmagic logo at the bottom right.

Owner question while working (summary): how many resorts and hotel rooms are there? Numbers worth showing in the video.

**Output:**
- File: `.bitmagic/film/out/vegas-afterlight-tour-v2.mp4`, copied to `~/Movies/Vegas Afterlight/`.
- Same length (2:28), same music and the same format as version 1. Cut: `tools/film/cuts/vegas-tour-v2.json`.

### Realistic water (in the game, not only the video)

`src/work/RealisticWater.ts` swaps every water surface's flat material when its asset loads. The hook is the shared GLTF parse patch (`gltfSceneHooks` in `GltfDecoders.ts`). The material names come from a scan of all 598 runtime GLBs:
- `Strip / lake-water` (the Bellagio lake);
- `Strip / water` and `Strip / paris-water`;
- `*_water` / `*_pool` (the level's pools);
- `mirage_water`.

19 surfaces convert. They include the Bellagio lake and back pools, the Paris pool deck, the Caesars and Flamingo pools, the Venetian canal, the Treasure Island lagoon, the Crystals water features and the Palazzo fountain.

**Pools and fountains:**
- A physical material with moving waves: 5–7 directional wave trains per surface, with deep-water dispersion, evaluated per pixel. Each wave fades out with distance before it can shimmer.
- Near-mirror roughness, with water's Fresnel response (ior 1.33).
- They reflect the actual sunset sky at full strength.
- Lit by the sun, sky and ambient only, a fixed list in line with the light-set rule.
- Waves run on the game clock, so the frame recorder films them at real speed.

**The Bellagio lake (ultra tier):**
- A real planar mirror of the hotels, the Eiffel Tower and the sky, broken up by the waves, plus Fresnel, the sun's glint and a deep green-blue body.
- Rendered at half resolution, only for the view camera.
- In play it refreshes every other frame; while filming or recording, every frame.
- The sun's shadow map is not re-rendered for it.
- The mirror's camera stops at 1.4 km. Meshes wholly below the water (the lake bed) sit on render layer 3, which the view camera sees and the mirror skips.
- `?water=nomirror` turns the mirror off for A/B checks.

**Traps found:**
- three's ReflectorNode bends the near clip plane with a projection trick that assumes a standard depth buffer. This game renders with a reversed one (`SkylineDepth.ts`), so the reflector clipped away everything and the lake rendered black. The mirror render is therefore replaced (`renderMirror`).
- Static level parents are not re-walked by the scene's matrix update, so the mirror plane's world matrix is refreshed each frame.

**Cost (headless, 3010×1544, M5 Max):**

| View | Without mirror | With mirror |
|---|---|---|
| By the lake | — | 60 fps |
| Spawn, CPU per frame | 8.5 ms | 12.6 ms (draw calls doubled on mirror frames) |

GPU time rises by about 2–4 ms on mirror frames.

### Drone drives

New camera anchor `drone` in `Film.ts`:
- The key path is set in a smoothed jeep frame: position follows within ~0.1 s, heading within ~0.9 s.
- The camera chases its target on a critically damped spring (lag 0.6 s).
- A raycast pulls the drone in front of any building between it and the jeep. Signs without colliders, such as the Flamingo's, can still cut in.

Takes:
- `drone-north`, 108 s: low start, fly-over, high trailing reveal, side passes past Caesars and the Flamingo, an overtake, the LINQ and the Venetian, a straight-up look down the Strip.
- `drone-south`, 84 s: CityCenter, a close pass, New York-New York with the coaster.
- `lake-glide`, 14 s: a low glide over the Bellagio lake toward the hotel and its reflection.

### Numbers on screen

From the game's tower data (`hotels/towers.json`, `highrise-towers.json`, `landmark-towers.json`; rooms = guest floors × rooms per floor, as `HotelStreaming` builds them):

| Count | Value |
|---|---|
| Hotels and resorts with walkable guest floors | **38** |
| Towers | 64 |
| Hotel rooms | **30,892** |
| Apartments | 5,806 |
| Doors you can open or kick | 36,698 |

- **Resorts:** 41 named buildings, counting Bellagio's Spa Tower, Horseshoe East and MGM Grand's Signature towers with their main resorts.
- **Apartments:** 8 residential towers: Veer, Turnberry Place, Turnberry Towers, Panorama, Sky, Allure, The Martin and Polo Towers.

The video shows "38 RESORTS" over the casino section and "30,892 HOTEL ROOMS" over the first door kick (`stat` cards in `build.py`).

### Logo

The white Bitmagic wordmark (`tools/film/brand/bitmagic-logo-white.png`, from `Aitopia5/portal/public`) sits in the bottom-right for the whole video:
- 5 % of the frame height, 2.2 % margin, 60 % opacity, soft shadow;
- under the final fade.

## Version 3: the owner's feedback on v2 (2026-10-08)

The owner's feedback, their two later comments and their answers are quoted verbatim in `../journal-2026-10-08.md`:
- the feedback: a jerky jeep, the lake, carpets, camera speed and spline flights, the overlay text, the subtitle, foliage;
- the later comments: curving in from the side roads, and UE5-style photoreal materials;
- the answers: CC0 downloads, and one video recorded after the materials and a filmic finish.

**Output:**
- File: `.bitmagic/film/out/vegas-afterlight-tour-v3.mp4`, copied to `~/Movies/Vegas Afterlight/`.
- Format: 2:28, 1080p60, x264 CRF 12, BT.709, AAC 320k at -14 LUFS, the same music bed.
- Cut: `tools/film/cuts/vegas-tour-v3.json` (`python3 tools/film/plan-cut.py v3`).
- About 2.4 GB, three times v2: the film grain costs bitrate at CRF 12.
- Not published or uploaded.

### What changed, point by point

| # | Feedback | Change |
|---|---|---|
| 1 | Jerky jeep, onto the sidewalk | Drives follow real routes on the OSM road network (`tools/film/roads.py`): one-way aware, corners smoothed, speed set by road class and curve radius. Obstacles were raycast in the game (`route-check.js`); the first routes hit a bollard, the LINQ promenade and the ARIA porte-cochère loop and were rerouted. A new pure-pursuit plus Stanley steering controller drives them. Preview track: mean 0.1–0.33 m from the line, at most 1.7 m in the tightest turns. |
| 2 | Lake aliasing, "not like water" | Each wave fades by its on-screen size (`fwidth` of its phase), so grazing views cannot alias either. The lake is calmer (slopes of 1–2 %). The mirror bends with the long swell only and is softened by a 9-tap disc, like a slightly rough mirror. It renders at full resolution while filming. Before/after: `v3-evidence/water-v4-450.jpg` (zebra) and `water-v5-450.jpg`. |
| 3 | Shiny carpets | `MaterialFixes.ts`: carpets and rugs are made fully rough at load. They were exported at roughness 0.4 and 0.74. |
| 4 | Camera 2× faster, spline flights | Five constant-speed spline flights (`flight()` in `make-takes.py`), each cleared by `tools/film/clearance.py` (below): Paris, the High Roller, the Sphere, the Strip and the lake (details below). The drone keys change every 3–5 s instead of every 8, with lag 0.42 s and velocity feed-forward so the drone no longer trails the jeep at speed. Casino walks are runs. |
| 5 | Dark text bands | Type only, with a two-step soft shadow. The end card dims the whole frame evenly instead. |
| 6 | The sunset subtitle | Removed; the title is just VEGAS: AFTERLIGHT. |
| 7 | Foliage off | It was never off (133,254 instances at spawn with these settings). Trees and grass exist only in the Bellagio garden and groves, so the north drive now starts under them. |

**The five flights:**
- **Paris** (24 m/s): over the casino podium, through the Arc de Triomphe's vault at 9 m, past the balloon sign, then up and around the Eiffel Tower.
- **The High Roller:** across the wheel's face at hub height and over its rim.
- **The Sphere:** a half-orbit at 235 m with the city around it.
- **The Strip:** a low run up the Boulevard from CityCenter.
- **The lake:** a glide at 8–14 m.

**The drives:**
- **North:** from the Bellagio drive onto the Boulevard, then Flamingo Road, then LINQ Lane past the High Roller.
- **South:** Harmon Avenue onto the Boulevard, past CityCenter to New York-New York.

### Photoreal surface detail (in the game, high and ultra tiers)

`src/work/PbrDetail.ts` and `PbrDetailSets.ts` add 15 scanned CC0 sets from Poly Haven:

| Group | Sets |
|---|---|
| Ground | clean asphalt, concrete pavement, concrete floor, gravel, dry ground, aerial grass with rock |
| Walls | white stucco, concrete wall, sandstone blocks, marble, brick, granite tile |
| Roofs and metal | clay roof tiles, bitumen, metal plate |

**How they are applied:**
- **Packing:** the 2K downloads (in `.bitmagic/pbr-sources/`, manifest included) are packed at 1024 px into three 15-layer texture arrays (`build/pbr/strips/`, 14 MB). The packer divides out each albedo's low frequencies so stains do not repeat.
- **Projection:** world-space, along each surface's dominant axis, with right-handed tangent frames.
- **Colour:** each surface keeps its authored colour. The scan's variation around its mean is laid over it, with a small share of the scan's own hue near the camera.
- **Relief, AO and roughness:** relief from the normal map, cavity AO and roughness come from the scan. All of it fades between 60 and 240 m, the city LOD's near range.
- **Which set:** chosen by material name. About 240 exterior materials get one; glass, signs, lights, foliage, fabric and polished metals stay as authored (`tools/pbr/check-sets.mjs` lists the mapping).

**How it hooks in:**
- **City batches:** the set is a column of the surface table, so thousands of facades still share one shader.
- **Other exterior GLBs:** at load (`gltfUrlHooks`), as node inputs on the plain material with a per-set program key.
- **Not covered:** interiors, hotel modules, vehicles and people.
- **Cost:** with it on, the four city probe views hold 60 fps.
- **A/B:** `?pbr=off` turns it off.

**Two scans replaced after the first look:**
- `large_sandstone_blocks` is a wall section with a cornice and a plinth, so it stacked ledges up every wall. Replaced by `sandstone_blocks_08`.
- `asphalt_02` has one crack across the whole tile, which became an endless straight crack down the Boulevard. Replaced by `clean_asphalt`.

Evidence: `v3-evidence/ab-*.jpg` (top: off, bottom: on).

### Motion blur and grain

**Sub-frames:**
- A take's `subframes: 4` runs the game clock and physics at 1/240 s while the recorder runs. The film host's `stepping` replaces the frame timer's tick and PhysicsWorld's FIXED_TIMESTEP.
- `tools/film/blend-subframes.py` averages 3 of every 4 frames back to 60 fps, a 270° shutter.
- Capture runs at about 48 fps, 4.2× slower than real time.

**Grain:** `build.py` adds a fine moving grain under the cards (`grain: 0.035`).

### Tools added

| Tool | Purpose |
|---|---|
| `tools/film/clearance.py` | Distance from a world-anchored camera path to every triangle of the exterior GLBs. It caught a 0.8 m skim over the Paris podium roof and a start inside a building. |
| `tools/film/glb-bounds.py` | Landmark bounds for laying out flights. |
| `tools/film/route-map.py`, `tools/film/route-check.js` | Routes. |
| `REC_SUBFRAMES`, `REC_SUFFIX` on `record.mjs` | Low-res previews. |

### Traps found

- **Sub-frames ran at 1/60 anyway:** `BackgroundActivity.ts` saves the engine's `forceFixedDeltaTime` before each frame and restores it after, which undid the switch every frame. While sub-frames run, the flag reads false through an accessor.
- **Physics without interpolation:** physics steps a fixed 1/60 with an accumulator and no interpolation. At 1/240 frames, the jeep would move on one frame in four, so physics must step at 1/240 as well.
- **Drives overshot their route:** `roads.py` treats `end_speed=0` as "none", so routes end at full speed, and the jeep brakes weakly. The drives use `stop: false` and end at the last point.
- **Coaster frames renamed mid-extraction:** the 43k-frame coaster spent minutes finalising `capture.mp4` and extracting into the hidden `.extract` folder. The recorder only counted PNGs, so it timed out and renamed the folder mid-extraction. It now watches the video and `.extract` as well, and `blend-subframes.py` can blend straight from `capture.mp4`.
- **Close drone keys:** keys on opposite sides of the jeep fly through it; put a side key between them.

## The continuous camera (after the 45-second preview 2)
The owner asked for one continuous camera: the Arc flight speeding up into the jeep chase, every place joined by a fast
camera run, "everything, but order them spatially". One take, no cuts (tools/film/make-tour.py → takes/tour.json; cut
tools/film/cuts/vegas-continuous-rt.json): the Arc, the jeep (the camera rides beside it and looks at it), low over the
Bellagio lake, the Cromwell run (casino, lobby, stairs, level-3 corridor, room 303, the window), out through the window,
the High Roller's face, round the Sphere, the Venetian's colonnade and fresco hall (a U-turn under the fresco), down the Strip
and round the Eiffel Tower, onto the Big Apple Coaster's front seat for the drop. 2:04.

Director additions: overlapping camera segments blend; anchor `coaster` (a film-driven train); start `venues` (pinned landmark
interiors), segment `hide` (a building kept hidden), the film camera posed before visibility, door reach scaled by camera
speed. Layout tools: plan-slice.py, plan-section.py, frame-check.py; clearance.py on a grid.

Game fixes found on the way (all hotels, not only the Cromwell): a corridor wall panel crossed every room doorway (8 sets) and a
lobby moulding crossed every stair door (47 of 49 sets); a guest floor is now shown while its stair door is open.

Preview: `.bitmagic/film/out/vegas-afterlight-continuous-rt.mp4` (real time, 1080p60). Recorded three times: the first showed the
blend bug (views snapped at the end of each blend) and the invisible coaster train, the second a half-open stair door.
