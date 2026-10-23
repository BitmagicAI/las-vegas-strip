# AL-01 sanctuary electric jeep

Local Blender asset: `sanctuary_jeep.py` builds the metered `Body`, `Wheel`, and
`Charger` components into `build/vehicles/afterlight-jeep.blend` and `.glb`.
`render_sanctuary_jeep.py` renders an independent model review.
No external generation, asset upload, or publication is involved.

`src/work/SanctuaryJeep.ts` loads the local GLB and batches static parts by
material. A native Bitmagic VehicleSpawner/VehicleRenderer supplies four-wheel
suspension, rolling and steering wheel transforms, AWD physics, enter/exit,
collision body, parking brake, chase camera, and rollover recovery. The engine
is unchanged. Dimensions: 1.95m platform width, 3.95m wheel platform length,
0.48m physics tire radius, 2100kg, forward cap 24m/s, reverse cap 6m/s.

The jeep starts at X=-40, Z=9, pointing east, inside Afterlight's 16m safety
field. The cabinet stands at (-43,6.5), beside the marked induction bay. E enters
and exits within the engine's 3m interaction radius; WASD drives and Space
brakes. Native mobile driving/interaction controls remain available.

Battery starts at 82%, drains only while occupied, and charges at 2 percentage
points per second while unoccupied, nearly stationary, and within 2.3m of the
bay center. An empty battery disables drive force but leaves braking/steering
available. The cabinet displays charging status. No cable stretches after the
vehicle. Camera-view controls and the walking character are hidden while driving;
walking and its camera return on exit. Jeep/station rendering obeys the existing
interior visibility decisions.

Local review: `http://localhost:3090/?inspect=jeep` for the whole charging bay,
`?inspect=jeep-entry` for the driver-door interaction. The ordinary spawn stays
at the existing sanctuary arrival.

Validation: Blender model review, TypeScript check, WebGPU startup verify;
real in-game E entry, chase camera, throttle out to the boulevard, braking and E
exit back to walking; parked charging observed from 82% to 100%. Runtime smoke
verification reports 1963 rigid bodies (jeep + charger added to 1961).

## Exit, camera and ground-contact repair

Door-side exit candidates use the actual vehicle forward vector. A downward
floor ray and full standing-capsule overlap check choose a clear location;
blocked doors fall back to the opposite side or another clear position. If
every exit is obstructed, the player stays seated. Walking-camera restoration
also refreshes the engine vehicle helper's saved controller, including after V
changes camera mode, and restores mouse-lock/drag-orbit input.

Wheel tread blocks rotate around the wheel axle. The evaluated mesh radius is
0.47583m, leaving about 4mm clearance at the 0.48m physics radius. The sanctuary
paving and two road surfaces now have collision tops matching their rendered
surfaces; the jeep is not lifted with a visual-only offset.

After regenerating the level, run `repair_jeep_forum.py` on the current Blender
level, then `export_visibility.py`. This idempotent patch preserves newer
CityCenter geometry and adds three ground colliders. Current WebGPU verification
passes with 1966 bodies. `tools/test-vehicle-exit.mjs` passes 18 collision checks
across six headings, including obstructed preferred exits. Chrome gameplay
review confirmed a third-person E entry/exit places the player beside the jeep
and mouse orbit works immediately without V. Tire contact and Forum signs were
also reviewed in the running game. Artifacts are under `build/repairs/`.
