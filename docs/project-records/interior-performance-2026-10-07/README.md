# Hotel and casino interiors: 15-51 fps → 60 fps (2026-10-07)

Owner request (summary): profile the hotel interiors: staircases, hallways and rooms.

Headless Chrome, WebGPU, 3010×1544 at DPR 2, `?quality=ultra`; `tools/probe-interiors.mjs` places the player
exactly as the `?hotel=` / `?landmark=` review URLs do (new probe hooks `hotel()` and `landmark()`), waits for
streaming and shader builds, and records frame time, render CPU, GPU time per pass and the light list.

## Cause

Interiors were GPU-bound (render CPU 3-8 ms, GPU 50-196 ms). Every lit interior material used the
renderer's full light list: about 43 point lights (the engine's 25 pooled fixture lights near the player,
the 4 shared venue lights, the hotel's 8, others) plus sun, sky and ambient, evaluated for every wall,
carpet and fixture pixel. None of the city's fixture lights reach inside the towers (pictures identical
without them), so the loop was pure cost. Ablations, one at a time:

| Interior | Before | Without city point lights | Unlit | Outside hidden | Shadows frozen | Half res |
|---|---:|---:|---:|---:|---:|---:|
| Caesars corridor | 22.7 | 60 | 60 | 22.9 | 22.8 | 60 |
| Bellagio corridor | 21.6 | 60 | 60 | 23.6 | 19.6 | 58.5 |
| Bellagio room | 19.5 | 60 | 60 | 20.2 | 20.2 | 59.5 |
| Bellagio bathroom | 14.7 | 60 | 60 | 14.5 | 14.3 | 44.5 |
| Wynn lobby | 20.2 | 60 | 60 | 21.5 | 20.4 | 60 |
| Venetian lobby | 51.1 | 60 | 60 | 51 | | 60 |
| Palazzo lobby | 36.7 | 60 | 60 | 38 | | 60 |

(fps; "Outside hidden" and "Shadows frozen" do not help: the city behind the walls and the shadow maps are
not the cost. Per-pass GPU timestamps on this GPU overlap; the scene pass is the real cost.)

## Fix

`src/work/InteriorLighting.ts`: interiors use one fixed light list, the focused sun (with its shadow), sky,
ambient and their own local pool: the hotel's eight lights (`HotelTemplates.setInteriorLights`, all modules
except the street-facing `-entry` shells) or the four shared venue lights (landmark, resort-block and Sphere
interiors). A fixed list also keeps the light-set rule (only intensity and position change).

## Result (19 interiors)

All 19 hold 60 fps (vsync cap): stairs, corridors, rooms and a bathroom in Bellagio, Caesars and
Cosmopolitan, a ground-floor stair, the Wynn lobby and entrance, and the Venetian, Palazzo, Park MGM, arena,
LINQ and Treasure Island lobbies. GPU 5-19 ms (was 48-196). Pictures: 10 hotel views bit-identical, the rest
differ only by the HUD's timed controls hint; the Palazzo dome-rim band differs between sessions with either
light list (a pre-existing coplanar edge), and within one session local and full lists render identically.

Checks: typecheck; `bitmagic verify` passed (59 fps); `tools/test-hotel-transitions.mjs` passed;
`tools/test-ground-surfaces.mjs` passed (457 checks; the typed-array index holds 1.03 M walkable triangles in
42 MB); `tools/test-hotel-streaming.mjs` fails with the same stair-route assertion on the pre-change sources
(pre-existing).

Data: before-hotels.json, ablations-hotels.json, ablations-landmarks.json, after-all.json.

## The jeep at spawn: 26 fps standing next to it, 60 fps seated (2026-10-07)

Owner report (summary): near the spawn point the game ran at 20 to 30 fps on foot, 60 fps after getting into the car with E, and about 25 fps again after getting out.

- Cause: the same light loop on the jeep's materials (and the player, NPCs and charging bay): standing
  next to it, the jeep fills the screen; seated, the camera is behind and above it. Reproduced at the
  owner's canvas size (1600×1020 CSS px at DPR 2) 2.5 m from the jeep: 28-30 fps, GPU 57-59 ms.
  Ablations: jeep hidden / unlit / without point lights → 60 fps. (A scene-wide `ClusteredLighting` A/B
  here showed no change, but that runtime swap did not take effect on r185. Installed at boot it runs this
  view at 60 fps; see `lighting-analysis-2026-10-08`.)
- Fix: `src/work/NearbyLights.ts`. These objects move through lit streets, so they keep real point lights:
  eight stand-in lights outside the scene graph copy the most influential scene point lights around the
  player each frame (slots kept while a light stays in the top eight). Their materials use sun, sky,
  ambient and the eight (`nearbyLights.apply()` on the jeep body, wheels and charging bay, the player and
  the cast). The scene's light set never changes.
- Result: facing the jeep at 2.5 m, 28-30 → 60 fps (GPU 9-10 ms); same-moment A/B against the full list:
  0-1% of pixels differ by more than 16 (no visible change).
- Sweep: 112 views along the whole Strip (56 spots, 3.4 km, looking at the buildings on both sides): all
  60 fps except one casino frontage at (18, -54) at 56-60 fps, where `WorldGroup` (the detailed level's
  unbatched meshes, here a casino interior seen through glass) still uses the full list. Those meshes are
  lit by the level's own fixture lights, so a reduced list could change their look; left as is.
