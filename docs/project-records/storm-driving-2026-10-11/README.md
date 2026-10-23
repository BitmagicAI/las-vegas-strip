# Playable storm driving, October 11, 2026

The owner's target is a real-time 60 fps game with free driving, many zombies,
impact-triggered ragdolls and the rain/night/neon look. A controllable local mode
is installed. **A locked 60 fps has not been achieved.** The current full-route
stress test averages 58.5 fps after the initial three seconds; occasional hitches
remain. This is live rendering, not an encoded movie frame rate.

## Launch and controls

Open `http://localhost:3090/?storm=1&quality=ultra`, wait for the level to finish
warming, then choose **Drive freely**. Click the game view if it asks for pointer
lock. WASD drive, Space brakes, E enters/exits and R rights a stopped car.
Shift+C opens the scene settings. B opens the existing performance panel.

Fresh gameplay defaults are 60 nearby zombies and a 1600×900 render budget on a
16:9 screen. The crowd setting allows up to 72; inactive actors recycle around
roads as the car travels, so the scene is not restricted to the film's route.
The car has a 1350 kg dynamic chassis, raycast suspension, body sway, up to 144km/h,
and no narrow-road speed assist. Keyboard/player controls own manual driving;
the movie's route driver does not command the car in this mode.

Daylight, weather, rain, wetness, neon, crowd size and rendering resolution are
saved locally. Gameplay settings use `afterlight:storm:settings:v1`, independent
of the movie preset; render height uses `afterlight:storm:render-height`.
**Restore level** removes the interceptor, crowd, ragdolls, temporary frontage,
audio and atmosphere, and restores exposure, environment and render scale.
The 20 cinematic lights remain allocated and are set to zero intensity, avoiding
runtime light-set shader rebuilds. Reload without `storm=1` to return the normal
boot-time renderer profile as well.

## Measurements

Hardware: Apple M5 Max, 128GiB RAM. Local headless Chrome, WebGPU/Metal,
Ultra setting, no recorder, natural timestep. The 900p internal buffer preserves
the screen aspect ratio and keeps UI at display resolution. These results do
not predict other computers or a browser competing with another live game tab.

| Test | Measured result |
| --- | --- |
| Original film settings,1920×1080,72 actors |10.6 /10.0fps over two live passes |
| Keyboard chase-camera test,1600×900,60 actors |Idle60.0; acceleration58.6; steering58.0fps |
| Final full-route stress test,1600×900,60 actors |58.4fps overall;58.5fps after 3 s |
| Final route sections |Harmon58.2; Strip57.8; Bellagio turn57.6; arrival58.6; stopped60.0fps |
| Final after 3 s frame times |Median16.6ms;95th percentile20.7ms;99th33.6ms; max97.7ms |
| Final impact load |31 strikes;14 simultaneous articulated ragdolls peak |

The route stress test uses the same dynamic vehicle with an automatic driver and
the movie camera for reproducibility. It is not a manual-control benchmark.
The separate keyboard test uses the real player controls and chase camera.
Earlier two route passes averaged57.4/57.7fps after 3 s, including a263.7ms spike;
that variability must not be hidden by quoting only the best sample.

## Changes and fidelity tradeoffs

- Normal city/foliage LOD and 4K gameplay shadows instead of the capture's16K map.
- Wet-road SSR runs at half resolution; the Bellagio lake uses animated PBR
  environment reflections in this profile instead of a second city render.
- Shared crowd materials. Optical eye/mouth detail stays within 8 m of the camera;
  distant red/blue eye glow follows the head in one instanced draw.
- Walking animation updates at 20 Hz beyond 24 m; close walking and airborne
  ragdolls update each frame. Planted-foot translation reuses the calculated
  skeleton. Bodies retain their original mesh and physical 11-body/10-joint rigs.
- Pose updates are reused across render passes. Hidden top-level scene roots
  wait until visible; hidden bones inside a visible actor are still updated.
- Up to 24 physical ragdolls; sleeping poses stop redundant bone work without
  disabling physics. Distant old actors recycle. Live thumps use actual vehicle
  and world contact events, with a bounded 24-voice sound pool.
- Resolution cap is persistent and explicit, including Retina/ultrawide screens.

## Validation and remaining work

TypeScript check, scene-pose/foot-plant translation, distant eye anchors,
resolution restoration, impact audio and film camera-hold regressions pass.
The actual GLB skeleton's Rapier test confirms an impact within 25 ms, joint
articulation in the first 100 ms and while airborne, debounced ground contacts,
and zero remaining joints/bodies after disposal.

Browser controls validation covers E entry/exit, W acceleration, R recovery,
collision sounds, settings persistence and reset. It is recorded separately
from the frame-rate benchmark. Screenshots were inspected; the speed/hit HUD,
night rain, illuminated actors and articulated airborne bodies are visible.
No world geometry, world/game JSON or geographic data changed; hashes included.
No engine edits, cloud verification, publishing or uploads.

Remaining discrepancies:

- Performance still misses a sustained60fps budget, with occasional shader or
  streaming hitches. Further profiling must separate those spikes from steady
  rendering; no broad completion claim.
- The rain collision height field still covers the original Elara–Bellagio film
  corridor; rain follows the camera elsewhere, but outside that field its ground
  splash coupling is not validated. Crowd placement spans 81,682 sampled road
  sites, including the rebuilt Bellagio arrival roads, but the whole map has not
  been driven manually.
- This is a driving sandbox with hit count, not a completed survival/combat game.
  Full movie engine/tyre/thunder mix is not yet live; collision thumps are.
- Existing stylized facades and dark road appearance remain; no photorealism claim.
  A hard curb/wall collision can roll the physical car; R is the explicit recovery.


A diagnostic switch to environment-only road reflections was not installed: it
rebuilt shader variants during the drive and produced many compilation stalls
(47.0fps after 3 s in that experiment, versus58.5fps for the retained SSR profile).
This is evidence against that mid-run switch, not a clean isolated GPU cost
comparison. The final pose regression also explicitly verifies that an attached
skin's inverse bind frame follows a cached root translation; the optimized
foot-plant update initially omitted that refresh and has been corrected.


Final keyboard review after the skin-binding correction:60.02fps idle,
60.02fps accelerating with three car strikes,55.56fps over the braking segment.
The braking sample includes121.8ms and216.5ms hitches; these are retained in the
report, not discarded. All stages have16.5–16.6ms median frames and18.9–19.3ms
95th-percentile frame times. The car stops upright with four wheel contacts;
E exits and re-enters both at spawn and after stopping. Zero browser errors.
The full-route58.5fps figure precedes this small binding correction; only the
keyboard test was repeated afterward. The final screenshot was visually reviewed.


## Rollover correction

The interceptor's low barrier-contact friction also applied to its roof, allowing
very long inverted slides. SceneChassisGrip now switches solid body contacts to
0.6 friction when overturned, restoring each collider's original material when
upright. No velocity clamps, added airborne drag or tire changes.

Rapier regression: 90km/h roof slide stops in4.02s versus66km/h still remaining
after8s previously; throttle held gives the same stop. 144km/h and sloped-road
cases stop too. Upright acceleration, glancing wall contact and airborne momentum
match baseline. TypeScript passes. Local browser test confirms roof stopping with
W held, R recovery, friction restoration and subsequent upright acceleration.
Screenshots were inspected; no browser errors. Evidence in `rollover/`.

## On-foot machine gun

In **Drive freely**, E exits the car and equips the Tempest automatic. Hold left
mouse to fire; right mouse aims down sights in first person, R reloads, and V
switches player views. The native touch attack/aim controls and the shared
Reload / Right car button provide mobile bindings. Mobile layout has not had a
separate device review. A 100-round belt fires at 900 rounds/minute, reloads in
2.4 seconds, and has unlimited reserve ammunition for this sandbox.

Native engine projectiles, recoil, ammo UI and arm IK are used. The custom
VegasCast character needs a thin PlayerLoader adapter for third-person grips;
its existing movement, grounding and animation remain in charge. Gunshots use a
local eight-voice synthesized audio pool. The weapon mesh is the native rifle
with an olive belt box, carry handle and brass rounds; this is not a new
photorealistic weapon asset.

A bullet immediately enables the struck zombie's complete eleven-body,
ten-joint ragdoll and applies a localized impulse. Wall and car collisions block
bullets. Ground-contact thumps work for bullet casualties as well as car strikes.
Ammo persists across view changes and vehicle entry/exit. Firing is blocked in
vehicles and menus. The existing car recovery action stays R while driving.
Crowd placement now follows the player on foot. At the 24-ragdoll limit, a new
kill retires the oldest corpse, preserving the simulation budget; reserve bodies
recycle for continued play. This adds shooting to the driving sandbox, not enemy
attack AI or a player-health loop.

Combat validation: local Chrome/WebGPU checks cover solid cover, real bullet
hits, instant articulated ragdolls, both views, reloads, input blocking, ammo
persistence and reset. Twenty-eight additional synthetic queued hits exercise
the 24-ragdoll cap; reset removes all target and limb bodies after the engine's
deferred physics cleanup. The warm stationary 11-second fire/reload sample ran
at60.05fps (20.3ms p95) at900p with60 zombies and rain, with at most11 live
projectiles. This is not a map-wide or maximum-ragdoll benchmark. Screenshots
were inspected in both views. No page errors. Evidence and exact results are in
`combat/`; the existing bullet-ragdoll and car-contact physics tests pass.
