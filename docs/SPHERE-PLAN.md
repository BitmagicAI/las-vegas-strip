# Sphere — local reconstruction

## References inspected, 4 October 2026
- Architecture and photographs: https://populous.com/showcases/sphere (lobby and seating bowl photographs inspected).
- Official main-level and entrance maps: https://www.thesphere.com/plan-your-visit/maps (both maps inspected).
- Interior design: https://investor.sphereentertainmentco.com/press-releases/news-details/2023/SPHERE-AND-ICRAVE-REVEAL-INNOVATIVE-INTERIOR-DESIGN-DETAILS-FROM-LAS-VEGAS-NEWEST-ENTERTAINMENT-DESTINATION/default.aspx
- Structural dimensions: https://www.severud.com/left-side-main-picture/sphere-at-the-venetian/?catname=Performance+Spaces

Use the published 516 ft diameter / 366 ft height, anchored to the OSM footprint centre. The existing OSM polygon is an approximate outer footprint, not a measured sphere section. Plaza entry is east, bridge entry northwest, stage south. Atrium: black terrazzo, white flared columns with luminous collars, curved balconies and glass balustrades, blue/cyan lighting, four central escalators, suspended circular installations. Bowl: fan-shaped, four steep tiers, two suite ribbons, portal tunnels, wraparound screen rather than a flat cinema rectangle.

## Playable spaces (local metres, Y up)
| Space | Extent / elevation | Connections |
| --- | --- | --- |
| Forecourt and east vestibule | east of sphere, street +0.2 m | Street ↔ plaza doors ↔ entry escalators |
| Venetian bridge vestibule | exact existing bridge endpoint; +6.085 m | Bridge doors ↔ main atrium |
| Main atrium | north crescent, +6.085 m; ~24 m clear height | Both entries, concessions, auditorium aisles, upper balconies |
| Terrace balconies | north crescent, +15 and +24 m | Four escalators, side circulation |
| Auditorium | south-facing fan, four seating tiers | Side aisles and central stepped aisles ↔ main floor/stage |
| Upper seating and concourses | stepped +6 through +49 m | Continuous aisle stairs; cross aisles each tier |

The public-facing structure is a reference-led approximation, not a survey of backstage or every premium suite. No photos are used as game textures. No private/backstage security layouts are reproduced. Existing engine code and user world settings remain untouched.

## Runtime budget
Independent exterior and streamed interior GLBs; shared/batched materials and instanced seats; simple walkable collision without per-seat bodies. Exterior video is a local original H.264 loop, muted, without external requests. Poster fallback; stop decoding when hidden, blurred, out of range, or screen not visible. Interior video only while the bowl is nearby. Both video paths are replaceable in the runtime configuration. Interior unloaded after leaving its vicinity. Reuse the existing loading UI and native interactive doors.

## Checks
Preview exterior, bridge, atrium, escalators and bowl. Audit floors and capsule clearance on every declared route, closed and open portals, plus headroom and bounds. Verify in the real WebGPU game, not only the preview. No upload or publication.

## Implemented
- Replaces only OSM `way/976405284`; correct 157.28 m diameter and 111.56 m height.
- Three paired native sliding-door entrances, opening automatically on approach with manual E interaction retained: Venetian bridge at its mapped elevation, east Plaza Entry, and West Entry. Street arrivals connect to the main atrium by paired walkable escalators.
- Main atrium with flared columns, luminous collars, curved balconies and glass rails, four central escalator flights, concession counters, suspended rings, exhibition pods and wayfinding. The enclosed bowl has four seating tiers, two suite fascia bands, stage, continuous stepped aisles and a curved overhead screen.
- 10,394 visual seats share four instanced draw batches. This is a simplified seating layout, not the venue's full published 17,600-seat plan. Each entrance, atrium and tier is traversable; backstage and individual premium suites are not reconstructed.
- Exterior GLB: ~1.8 MiB; interior GLB: ~13 MiB. Interior has 14 material batches and ~198,000 triangles before shared seat instances. Two static collision bodies plus six door bodies when resident; no per-seat physics.
- Interior preload radius 130 m; eviction beyond 190 m after 15 seconds. The exterior remains available in the skyline; its detailed collider is resident only nearby. Closed inner areas cull the rest of the Strip.
- Two original local 2048×1024 H.264 / 24 fps / 24-second loops: `build/sphere/exosphere.mp4` (eye, planet, flowing ribbons) and `immersive.mp4` (aurora/starfield panorama). These are not recordings of actual Sphere programming. Replace paths/posters in `build/sphere/media.json` to use other suitably licensed equirectangular/wraparound footage.
- Decoding stops on pause, blur, hidden tab, page hide and eviction; the exterior also stops out of range/frustum. Poster fallback remains if playback fails. Interior image-based sky lighting is reduced only while enclosed and restored on exit/disposal.

## Rebuild and review
From the project root:
```sh
PYTHONPYCACHEPREFIX=/private/tmp/vegas-pycache tools/geographic-strip/.venv/bin/python tools/sphere/build.py
python3 tools/sphere/video.py
/Applications/Blender.app/Contents/MacOS/Blender -b --python tools/sphere/export.py
node tools/sphere/test.mjs
node tools/sphere/test-video.mjs
```
The editable authoring scene is `build/sphere/sphere.blend`. The separate local model viewer is `http://localhost:3090/build/sphere/index.html`. Actual game review starts are available with `?sphereReview=exterior`, `atrium`, `upper`, `plaza`, `bridge` or `bridge-door`. These query parameters do not change the normal spawn.

## Validation results
- 5,879 floor/headroom/capsule samples across 64 routes, including 11 neighbouring city collision cells: zero failures.
- All three closed/open portal pairs pass the collision audit. In-game bridge arrival shows the door pair opening and the prompt changing to “Close door”.
- Existing mapped Sphere bridge: 165 samples, no holes or blocked centreline; 317/328 rail probes hit a barrier.
- Playback-controller tests cover focus, visibility, page lifecycle, late play resolution after blur, poster fallback and disposal.
- Actual WebGPU game: exterior video plays, upper-bowl video plays, and both pause in the game menu. Only the exterior video element exists at the far exterior review start (interior unloaded).
- In-game screenshots: `build/sphere/proof/exterior-game.png`, `atrium-game.png`, `bowl-game.png`, `performance-game.png`. The model viewer is a separate renderer, not used as a substitute for game verification.
