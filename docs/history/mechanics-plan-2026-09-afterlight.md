# Mechanics plan
1. Build and visually inspect the Blender Strip district; audit sanctuary-to-cache routes and hide exits.
2. Load GLB and matching colliders in Bitmagic; use first-person movement and desktop controls while Hero characters are pending.
3. Add sanctuary state, proximity supply collection, return-to-base mission progress, and dormant horde metadata.
4. Integrate supplied Hero (WebHuman) player and infected rigs; implement enemy perception/physical exclusion at the shield, then ambush activation, health, combat, inventory and mission failure.
5. Add higher-frequency material assets, authored character animation and audio; judge visual fidelity before performance tuning.
The user explicitly prioritizes level generation and defers FPS checks. Combat win/lose and character population are later-stage dependencies, not fabricated in the environment delivery.

## Bellagio reconstruction completed
- Reference-led curved exterior, crown arches, central cupola, lakefront pavilions and supporting arcades.
- Walkable lobby/casino/gallery loop and service corridor with four rooms; eight automatic doors.
- Food mission and hidden horde staging moved into the hotel.
- Final route and envelope audits passed; desktop WebGPU loads the 478-collider export.
- Upper hotel floors remain exterior-only. Destruction detail and the other hotels are later passes.

## Paris Las Vegas milestone
Build a recognizable Bordeaux-style hotel with blue mansard roofs, dormers and French street frontage, the balloon landmark, and a 165 m Eiffel replica with curved splayed legs, truss work, lower platforms and a 140 m observation deck. Keep the current district footprint and sunset.

| Space | Footprint / floor | Connections |
|---|---|---|
| Paris public casino | x72–138, z-80–10, floor0 | West entry at (72,-39), north exit at (120,10) |
| Elevator ground cabin | 4 × 3.3 m, rotated 45° about (93,-39) | Diagonal entrance into casino; L / touch LIFT to observation deck |
| Observation deck | Chamfered 12.4 m deck, rotated 45°, floor140 | Enclosed perimeter, central return lift, panoramic walk around cabin |
| Casino service recess | x125–137, z-76–-62 | Reserved enemy hide and supply staging |
| Hotel tower | Two ±18° wings and three pavilions around (164,-75) | Exterior only this pass |

Routes: east sidewalk to west casino entrance to lift; casino to north exit; full observation-deck perimeter; lift return to casino. Lift transitions require proximity and a fresh interaction press. Validate both endpoints, return travel, perimeter collision, facade winding, route/envelope audits, Blender renders and real WebGPU views. No FPS-driven reductions.

## Paris reference geometry correction
Use the creator's supplied real-world photograph as the visual target. Rotate the Eiffel structure 45 degrees relative to the casino, including its supports, platforms, observation deck, cabin, colliders, lights and route nodes. Split the hotel into angled wings (approximately ±18 degrees around its central pavilion), with aligned mansards and end pavilions. Replace the square observation crown with a smaller chamfered deck and open domed lantern; add platform trusses and hipped restaurant roof. Strengthen the distinct opera-style north frontage and tall south pavilion. Preserve the casino west entrance and two-way lift. Validate an elevated overview plus street and deck views, then rerun collision and orientation checks and verify the rotated lift endpoints in the game.

Reference correction delivered: rendered overview, overhead footprint, casino and deck reviewed; 548 colliders, 76 volumes, 67 links. Both collision audit modes pass, all facade probes pass, and 37,646 closed solids have no inverted shells. Lift tests and in-game descent/ascent pass at the rotated landings.
Runtime handoff verified with the new CDN GLB: 548 colliders, 36 lights and 76 volumes loaded; sanctuary spawn restored. External Bitmagic visual judge was blocked by automatic approval review (screenshot/project-context transmission); local renders and browser checks completed instead.

## Eiffel structural weight pass
Widen the four tapered truss legs, increase the primary chord and web-brace sections, add visible junction gussets, and strengthen the upper-shaft cross-bracing against the supplied close-up. Preserve the 45-degree orientation, platforms and lift route; regenerate lower-leg collision hulls and audit clearances.

Structural-weight pass completed: widened tapered legs and reinforced bracing/gussets reviewed at street, close-up and overview scales. Both collision audits pass; 38,526 closed solids have zero inverted shells. Updated mesh/colliders loaded and desktop WebGPU verification passed. External vision judge remains unavailable under the prior approval-review restriction; local visual review completed.

## Paris frontage and X-plan correction
Rebuild Bordeaux as four ±30° arms with four end pavilions and one central core within the district boundary. Replace repeated street-roof huts with continuous Louvre frontage and a recessed connecting gallery; articulate opera pediment/cupolas/terrace. Move balloon to (48,45) on the right of the frontage. Add a 28 m-wide freestanding Arc de Triomphe at (88,39) with a real 11 m-wide rounded passage and audited sidewalk→arch→casino-exit route. Preserve Eiffel geometry, casino entrances and lift.

Frontage/X-plan pass delivered: corrected street view and X roof plan reviewed; both collision audits pass (585 colliders, 79 volumes, 71 links), and 46,347 closed solids have no inverted shells. Desktop WebGPU verification loads the new CDN mesh with 612 physics bodies and the normal sanctuary spawn. Lift regression tests pass. External visual judge remains unavailable under the previously reported approval restriction; local visual review completed.

## Caesars Palace reconstruction
Replace the northern placeholder beside Bellagio with ivory/red-roof high-rise groups, a curved central hotel, temple portico, fountain gardens and cylindrical Colosseum. Existing district bounds and ammunition arcade remain unchanged.

| Space | Footprint | Route |
|---|---|---|
| Casino | x-182..-100, z178..216; 8 m high | East temple entrance to north garden exit |
| Service corridor | x-170..-161, z178..216 | Casino hall connects two service rooms |
| Supply/hide rooms | x-182..-170, centers z185 and205 | Separate sliding doors, staging landmarks |
| Forecourt | x-100..-48, z178..250 | Existing north-west route → entrance → garden walk |
| Colosseum | center(-83,273), radius21, height25 | Exterior landmark beside north garden walk |
| Towers | rear x-214..-115, z171..291 | Exterior only; casino is the playable slice |

Review street/overhead/interior renders, audit both door modes and normals, register/sync/check/verify. Preserve prior sunset, sprint, Paris lift and all existing caches.

Caesars pass completed: exterior, casino and service-room renders reviewed; curved-bay seams closed. Both audit modes pass, with 630 colliders, 14 doors, 95 volumes, 41 lights and no inverted closed solids. Verified the player on the new casino floor in WebGPU, then restored and verified the sanctuary spawn. Paris lift regression tests still pass. Supply/horde rooms are staging locations; upper towers and Colosseum remain exterior-only. External vision judge remains unavailable under the prior approval-review restriction; local visual review completed.

## Cosmopolitan addition
Replace the south-of-Bellagio skyline placeholder with reference-led Boulevard/Chelsea towers and a walkable casino/service route. Detailed spatial plan: tools/level/COSMOPOLITAN.md. Supply and hide landmarks are reserved for later missions; existing four-cache loop stays active.

## Sanctuary electric jeep
Add one detailed locally authored military utility jeep and a charger in the
sanctuary. Use Bitmagic's existing four-wheel physics, E enter/exit and chase
camera. Park at (-40,9), facing east toward the boulevard, clear of the survivor.
Provide speed/battery state and recharge while parked in the marked charging bay.
Use Blender for the vehicle and charger meshes; all assets remain local.
Validate vehicle scale, ground contact, entry/exit, steering/braking, driving
out of the sanctuary, and charging on return. Preserve the walking controller,
character assets, level visibility, and the Aria/Crystals surface repairs.

Jeep pass complete: local Blender GLB, native AWD vehicle, charging bay and battery HUD.
Typecheck and WebGPU verify passed. Live driving out of sanctuary, braking, entry/exit,
and parked charging verified; see tools/level/SANCTUARY-JEEP.md.

## Streamed hotel rooms and apartments
Implement shared Blender stair/corridor/room modules with compact tower recipes,
lazy room creation before door opening, short unload grace and bounded residency.
Persist sparse room state by stable IDs, maintain physical stair continuity, and
integrate room windows/corridors with BuildingVisibility. See
`tools/level/HOTEL-STREAMING.md` for layout and validation contract.

First pass: custom Bellagio guest wings and both Veer residential towers. Compact
recipes cover 1,184 units, physical stairs, native room doors, bounded residency,
and sparse visited-room persistence. Staged shell keeps original level assets
intact. Other properties remain on their existing ground-floor interiors until
their own custom guest-floor sets are authored.


## Public resort architecture — 2026-10-02
Replace generic public finishes and entry canopies with photo-led architecture
for every existing property. Apply as an incremental stage change, preserving
shell cuts, native doors, guest cores and current circulation. Keep all detail
in existing visibility zones, batch decorative pieces and use simple obstacles
only for substantial reachable furnishings. Validate doorway routes, stairs,
loading/camera transitions, and inspect the exported level in WebGPU. Work
remains local. Design/reference record: `build/public-resorts/DESIGN.md`.

Public architecture pass completed locally. Thirty public-area WebGPU views and
the final Paris mural view reviewed. Existing door and guest stair routes pass
regression; local typecheck and WebGPU verification pass. No publishing.

## South Strip landmarks and Big Apple Coaster (October 4)
- Replace New York–New York tower surfaces with individual photo-referenced facades and stepped Empire State / Chrysler crowns. Replace Excalibur's mapped volumes with white castle wings, crenellations, turrets, colored roofs and a connected entry. Remove the corresponding OSM boxes; preserve geographic footprints and existing guest access.
- Add Liberty on the surveyed pedestal site and red coaster track on OSM relation 19531865. Horizontal alignment is mapped; vertical profile/inversions are reconstructed from photographs and RCDB's 203 ft height / 144 ft drop / 4,777 ft length, not an engineering survey.
- Local Blender assets, material batches, simple streamed architectural collision; no physics per track tie. Coaster station has a walkable access route. R / mobile RIDE boards an 18-seat train, dispatches, follows the complete circuit and restores walking/camera at the platform; R also ends the ride safely.
- Validate geometry/collision, track closure and ride lifecycle, then typecheck and local runtime verification. Capture reference-angle renders and a ride view. No publishing or uploads.

Completed locally: both landmark replacements and credited Liberty scan are in the
runtime. The coaster follows the OSM plan with reconstructed elevations/banking;
its generated circuit is 1,476.0 m versus the published 1,456.0 m, reaches 67 mph,
and completes in about 180 seconds including dispatch/lift. Layer separation at
crossings is checked (minimum 3.65 m between nonadjacent centerlines). Boarding,
full circuit, automatic return and manual return are exercised in the browser.
262 station approach checks, 739 ride/building clearance samples and 37,913 hotel
route regression checks pass. Typecheck and desktop WebGPU verify pass without
warnings. Final daylight asset reviews and an actual in-game ride screenshot are
in build/south-strip/. Reference and adaptation credits are in ATTRIBUTION.txt.

## LINQ, Vanderpump, Fashion Show, Venetian frontage and arena (October 4)

Implemented locally in `tools/strip-landmarks` and `src/work/StripLandmarks.ts`:
photo-informed exterior shells fitted to the mapped footprints, working glazed
entrances and furnished public interiors. The LINQ includes the Vortex frontage,
promenade and a rotating High Roller with 28 upright cabins. Fashion Show has the
Cloud and a two-storey gallery. Venetian has the campanile, palace arcade, canal,
painted Grand Colonnade and a connected Rialto stair/upper entrance route.
T-Mobile Arena has its copper shell, enclosed concourse, concessions, passageways,
stepped bowl, radial stairs, instanced seats, rink and scoreboard.

LINQ and Vanderpump have distinct reusable room/corridor sets with 102 streamed
room instances. Interiors unload when distant; exterior detail uses distance
culling and nearby collision. Twenty-five replaced map features are excluded,
along with the obsolete Rialto ramp and duplicate campanile. The High Roller is
an animated landmark, without passenger boarding. Interior plans are authored
adaptations, not surveyed replicas. Photo sources and comparison renders are in
`build/strip-landmarks/review.html`. All 4,572 combined-city route/capsule checks
and the TypeScript check pass. Final desktop WebGPU verification passes at
60 fps in the local startup sample; this is not a full-map performance benchmark.
No level uploads or publication.

## Park MGM, Palazzo, Treasure Island, Harrah's and Polo Towers (October 5)

Replaced the four plain podiums with individually authored entrances and public
halls, connected through map-fitted galleries to the existing guest stairs.
Added Park MGM's Eataly pavilion and green garden reception; Palazzo's glazed
arrival dome and fountain rotunda; Treasure Island's galleon, covered arrival,
curved reception and bell furnishings; Harrah's purple marquee and layered
reception artwork. Polo Towers replaces its plain mapped footprint with recessed
balconies, stucco/window bays, purple sign blade, covered motor court, furnished
lobby and a custom shared room/corridor set representing 182 rooms.

Interiors remain lazy. Gallery endpoints keep arrival halls visible when returning
from guest stairs; low facade courses stop at entrances and passages. Removed two
overlapping map structures inside Harrah's route and closed the guest-lobby stair
threshold gaps. The existing tower/room assets are retained for the four resorts.
Photo-era features and fitted circulation are interpretations, not exact plans.
Sources, exported-asset views and play links: `build/strip-landmarks/review-next.html`.
The combined-city audit passes all 9,889 capsule/ground probes, including the
previous five landmarks. Work remains local, with no publication or level uploads.

Final validation for this batch: typecheck and desktop WebGPU startup verification
pass (4.1 s settle, 54 fps startup sample; not a map-wide benchmark). One
automated run stopped at the visible Play menu while offline renders were active;
the retry passed after renders finished. Park MGM, Polo Towers and Palazzo were
also inspected in the live browser. Final exported-asset renders were reviewed.

## Complete exterior blocks — process established October 5

The next architectural standard covers the entire resort site, including smaller
buildings, podium sections, restaurant patios, pool decks, bridge landings and public
routes between levels. Follow `tools/resort-blocks/README.md`. Work sequentially:
Cosmopolitan → Bellagio → Paris → Planet Hollywood. Earlier completed passes above
describe their implementation milestones; they do not certify whole-block accuracy.

The initial process milestone placed Cosmopolitan at the survey stage (superseded by the geometry implementation below). Its record inventories 20 components,
seven level groups and twelve route checks, with official map/photo sources, known
discrepancies and seven completion gates. Source inspection confirms two rectangular
tower recipes distorted by the legacy whole-site transform; this must be replaced
with independently fitted components. Physical elevations remain unverified, even
where the official map establishes a numbered floor.

`python3 tools/resort-blocks/review.py` validates the records and creates
`build/resort-blocks/index.html`, including a diagnostic footprint overlay.
`--ready` rejects incomplete or stale completion evidence. This process milestone
changes no game geometry. The first construction task is the complete Cosmopolitan
block; the other three remain queued. No uploads or publishing.

## Cosmopolitan block geometry proof — October 5

Replaced the legacy stretched Cosmopolitan with separately fitted geographic
footprints for Boulevard, folded Chelsea, the multi-level podium and both Jockey
Club low-rise wings. The exterior now includes projecting balcony bands, recessed
glass, glazing bays, roof parapets, street portals and the Chelsea porte-cochere.
Levels 1, 2, 3, 4 and 14 have actual slabs/soffits, continuous stair stacks and
independently streamed furnishings. Boulevard and Chelsea pools, Marquee terrace,
Overlook dining and recreation courts are modeled and reachable. The physical
podium elevations are estimated; hotel floor labels do not imply metric heights.

Removed 149 legacy mesh owners, 127 old colliders, 18 lights and 27 visibility
volumes; relocated the two custom guest cores without whole-site stretching.
Corrected the two inferred raised service drives across Chelsea arrival while
preserving their map centerlines and city endpoints. The Harmon bridge joins the
new Level 2 landing. City roads elsewhere are retained.

The final combined-city audit passes 7,609 floor/clearance probes and all 16
Rapier ascent/descent simulations. The actual game player also reached Level 2
from Level 1 using normal movement. Typecheck and local WebGPU verification pass.
The local proof board is `build/resort-blocks/cosmo/proof.html`. See its performance
report for warm samples; no pre-change route benchmark or cold-stall profile was
captured. Startup verification is not a block performance benchmark.

Cosmopolitan stays active for full architectural matching. The western external
connection, east bridge continuity, private bungalow terraces, room/balcony fit,
exact crown/frontage/pool tiers and lift/escalator machinery remain open in the
block record. Public level geometry is implemented; full photo-realistic completion
is not claimed. All assets and verification remain local.

## 2026-10-11 — playable storm driving
The existing physical interceptor, night/rain look and immediate collision ragdolls become a local free-roam mode. Keep the authored city intact. Separate the 60 fps gameplay rendering budget from the film capture profile. Reuse engine vehicle entry/exit and chase camera, regenerate crowds near drivable roads beyond the original take, and expose speed/impact count. Free-roam has no win/lose state. Validate actual live frame times at 1080p with rain, car and zombies; an encoded 60 fps movie is not performance evidence. First deliverable: a controllable local mode and measured rendering bottlenecks; don't label it 60 fps until measured.
