# Streamed guest floors

Local-only system. Shared Blender templates, deterministic room IDs, real stairs;
no pre-created thousands of rooms, no teleporting between stair landings.

| Module | Clear dimensions | Connection |
|---|---|---|
| Stair storey | 6.8 × 9.6 m, 3.6 m rise | two switchback flights; 1.8 m intermediate landing |
| Corridor bay | 3.6 × 6 m | two 1.3 m room doors; repeated along each floor |
| Guest room | 5.4 × 6 m | entry, bathroom, bed, desk and window |
| Apartment | 5.4 × 6 m | entry, bathroom, bed, kitchen/living and window |

One staircase spans every modeled floor. Floor numbers and room counts derive
from compact tower definitions. Current/adjacent stair modules are pinned;
only the floor approached on a landing has corridor objects and doors. Open
rooms are generated synchronously before the native door begins to move. Old
rooms close before eviction; occupied rooms and support under the player cannot
be evicted. A short grace period prevents boundary thrashing; hard resident
limits prevent exploration from accumulating geometry/physics. Clones share GPU
geometry/materials; unloading destroys colliders, doors, lights and labels.

Stable tower/floor/bay/side IDs persist sparse visited-room state
locally. No array of every possible room is built, and saved state is read only
for accessed rooms. Windowed rooms re-enable the exterior, while enclosed guest
corridors hide the city and ground-floor interiors.

## First two property sets

| Property | Modeled floors | Guest floors | Units |
|---|---|---|---|
| Bellagio north and south wings | 23 each | 4–23 | 640 rooms |
| Veer east and west towers | 40 each | 7–40 | 544 apartments |

These are compact playable layouts fitted to the existing game buildings, not
surveyed replicas of their real guest-floor plans. Podium/service levels have
stairs but no guest-room doors; their existing public interiors remain intact.
Bellagio has warm wood, brass, red runners, cornices, drapes and upholstered beds.
Veer has linear lighting, slatted panels, contemporary platform beds and kitchens.
Other hotels will receive their own sets in later passes.

Four ground stair entrances remain resident. At most five upper stair sections,
two guest corridors and 32 rooms may coexist; normally only a few opened rooms
exist. The eight shared GLBs total under 1 MB. Eight light slots are reused.
Room/floor removal disposes physics bodies, native door sensors and label textures;
shared geometry/materials live until the template library is disposed.

Enter the labeled guest stair doors in Bellagio and the Veer ground-level entries
with E. Climb the physical switchback stairs and use E on numbered room doors.
There are no floor-change teleports during normal play.

### Finding the Veer entrances

Both ground-floor stair doors are inside Crystals. Enter from Aria Place at
the south mall door (-93, 470), walk north, then follow the VEER EAST sign left
at Z=453.4 to the east stair door (-131, 453.4). For Veer West, enter Crystals
from the Boulevard door (-32, 381), follow the south arcade to Z=397, cross west
to X=-163, then follow the signs south to Z=422.6 and west to the stair door
(-195, 422.6). Press E at either door. Apartments start on Level 7; Levels 1–6
are the mall/podium stair connection. These are the prototype's adapted routes.

`veer_access.py` adds entrance canopies, illuminated frames and fixed directional
signs at the existing public doors and route turns. It updates both editable
scenes and is also called by the full CityCenter builder. No new colliders,
resident apartments or automatic floor teleports are introduced. The shared
Veer templates and the four tower recipes retain their existing positions.
`test-veer-access.mjs` checks standing-player clearance, ground support and
exported visual obstructions along the complete public approach to both towers.

## Local validation and rebuild

`node tools/test-hotel-streaming.mjs` checks 20,260 capsule-clearance and support
samples across all modeled floors, both sides of all 1,184 room entrances, stairs,
and ground entries. It also checks bounded cache eviction and persisted room IDs.
Report: `build/hotels/validation.json`.
Eight continuous Rapier capsule traversals also pass: ascending and descending
both flights in each tower, including the Veer shear near the highest floor.

Live browser review exercised native door opening, room creation, Bellagio floor
4 through 23, the Veer level-40 apartment, and exit cleanup. Bellagio's physics
count returned from 2,305 bodies to its 2,030-body outdoor baseline, with zero
guest corridors and rooms resident. Typecheck and WebGPU startup verification pass.
Screenshots and cleanup evidence: `build/hotels/review/`.

The original `build/level/vegas.*` files are retained. The game locally uses a
separate `build/hotels/staged-vegas.glb` with circulation voids. Source checksums
are recorded in `shell-report.json`. `?hotels=off` selects the original level for
comparison. No upload or publishing occurs.

Rebuild templates with Blender `--background --python tools/level/hotel_templates.py`.
Rebuild the staged shell with `prepare_hotel_shells.py`, run the collision tests,
then export with `export_hotel_stage.py`. Copy validated staged metadata/version
to `src/work/hotels/streamed-level.json` and `streamed-asset-version.json`.
The staged exporter checks the source has not changed and requires passing tests.

Optional local review URLs use `?hotel=bellagio-north&floor=3&room=0` or
`?hotel=veer-east&floor=39&room=0`; floors/bays in these developer bookmarks are
zero-based. `&hotelDebug` exposes live counts and review navigation controls.

## Bellagio Premier King room set

Bellagio's room asset is authored by `tools/level/bellagio_premier.py`, also
called by the normal `hotel_templates.py` build. Reference photographs and the
MGM floor plan are documented in `build/hotels/bellagio-premier/REFERENCES.md`.
The photo-based 8 x 6 m room adapts its foyer/bathroom to the corridor's existing
six-metre door spacing. Veer's room set and envelope remain separate.

The current room has 19 material batches, 76,230 triangles and 30 simple
structural/furniture collision boxes. Its approximately 7.5 MB GLB, textures
and materials are shared between streamed instances; rooms do not individually
load copies. Template disposal also releases the shared textures once.

The enlarged Bellagio guest volume requires
`extend_bellagio_room_voids.py` after staging colliders (the staging script
calls it automatically). The visibility export assigns all upper Bellagio
architectural faces to their owning tower, including the separate structural
bays, so those cannot protrude into rooms while viewing the city through a
window. The original source level is preserved.

`node tools/test-bellagio-room.mjs` checks standing-capsule routes in both
Bellagio wings and corridor sides at low/high floors, window-end containment,
structural-bay visibility ownership and inset bathroom geometry. Local review
bookmarks can add `&roomView=bedroom` or `&roomView=bathroom`.

Bellagio's upper exterior is a render shell, not a boolean-cut copy of the guest
collision volume. `hotel_shell_policy.py` preserves the tower geometry above the
casino podium when preparing future streamed levels. Collision voids still cut
the full guest volume; podium and stair-entry render openings remain intact.
`repair_bellagio_shell.py` can restore previously cut upper visuals from the
original Blender source without modifying the staged collision metadata.
`test-bellagio-shell.mjs` checks the exported facade with back-face culling and
asserts that it belongs to the outdoor/tower visibility groups.
