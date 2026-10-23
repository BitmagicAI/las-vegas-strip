## Current v4 preview — lighting, impacts and camera hold fixed

`<repo>-movies/vegas-afterlight-storm-v4-preview.mp4`

44.983333 seconds, 2,699 frames, 1920×1080 at 60 fps, H.264 with stereo 48 kHz AAC, 159,750,070 bytes. Uses the continuous `storm-v4c-rt` capture; every available frame is used without padding or retiming. Capture throughput was 7.8 frames per wall-clock second, not an interactive 60 fps claim. The previous v3 preview remains intact.

The final footage was inspected as an exported contact sheet and dense source sequences covering launch, airborne impacts, the earlier loading-jump location, roadside lighting and the Bellagio turn. Paris retains its blue/gold colours under the floods. Street light pools visibly reach pavement and passing actors; headlights illuminate ahead without the earlier nearby whiteout. The small eye glow was checked separately in a close-up. The wider PS5/UE5 photorealism target remains unachieved: existing character/building assets remain stylized, some walls are plain, road reflections still look too broad in some views, portico lighting is concentrated, and the cyan sanctuary graphic remains visible. Light positions are estimates, not surveyed fixture locations.

Actual final physics: 124.35 km/h peak; 20.75° Bellagio sideslip at 83.32 km/h; 7.65° peak chassis roll, 7.14° sprung roll and 4.62° sprung pitch; at least two wheel contacts in 99.74% of samples; stops within 1.17 m of the arrival guide. 88 car impacts, 492 debounced ground-contact audio cues, peak 22 ragdolls. All physical-route assertions pass. The v3 stunt-contact accommodation described below remains explicit. Audio cue timestamps exactly match the recorded strikes and landings; later bounces can generate additional thumps.

A rejected v4b capture revealed that repeated rendering during streaming holds advanced the camera spring without advancing the car/film clock. `Film.applyCamera` now reapplies the cached pose for a repeated tick and logs/integrates only on advancing ticks. The new regression checks 100 held redraws, exact position/quaternion/FOV, one sample, and resumed movement on the next tick. Final v4c source scan finds no black frames, freezes or flashes. Camera checker still flags the intentional fast launch sweep at 1.1–1.6 s (83°/s maximum); dense frames were reviewed and the car remains framed. No jerk, hunting or steep-view flags. This is not represented as a completely clean automated camera report.

Final export decodes without errors. Its frame scan detects only the opening/closing fades; no freezes or flashes. Audio peak −2.7 dBFS, mean −16.0 dBFS. TypeScript and driver, scene, real-skeleton ragdoll and camera-hold regressions pass. Controls/restoration browser check passes with zero browser errors: temporary actors, ragdoll/vehicle handles and frontage removed; environment/exposure restored; all 20 persistent cinematic lights remain allocated with intensity zero. World/game/geographic hashes were rechecked unchanged after capture. No main level/interior/road regeneration, supersampled final, cloud judging, upload or publication. The local CLI verification limitation documented below remains applicable.

### V4 implementation

- Cinematic actor lighting explicitly includes both persistent headlight spotlights. A 25 m actor comparison shows clear beam illumination. Headlight range is 90 m (not a 90 m verified recognition-distance claim), intensity 80 and cinematic decay 1. This deliberately gentler falloff replaced an inverse-square 3,000 setting after full-capture review exposed bleached nearby actors. Six-metre and 25-metre images were then compared. Separate optimized point-light proxies remain in use for the crowd/car.
- Seven persistent street light slots illuminate fixed estimated kerb/arrival positions; warm/cool sources are distance-faded, with 48 m falloff. No new poles, geometry or runtime light creation. Paris balloon uses two boot-allocated floods at intensity 2,500. Initial overbright settings were reduced after rendered review.
- Existing iris/pupil layers emit red or blue. The cinematic cornea uses a thin transparent highlight coat so the existing iris remains visible; blanket ashen roughness no longer covers optical layers. A front close-up confirms visible small red/pink eyes. This does not replace the existing human meshes with bespoke zombies.
- Wet-road masks now produce localized pooled areas and animated rain normals, retaining scanned aggregate between pools. They were inspected in the moving-sequence frames; broad sheen remains a visual limitation.
- Ragdoll ground contacts record their actual clock and pre-solver downward speed. A horizontal-contact test and 140 ms debounce suppress simultaneous limb noise and resting contacts; subsequent bounces may make another sound. These events and every car strike generate distinct offline audio cues, without a guessed landing delay. The real-skeleton physics regression records twelve ground events and passes immediate airborne articulation and cleanup checks.
- Film-only Planet Hollywood storefront lettering faced backwards; corrected exporter text orientation and rebuilt that temporary asset. Main resort, road and interior assets were not regenerated. Source world/game/geographic hashes remain unchanged.

## Completed v3 physics preview (superseded by the current lighting/audio work)

`<repo>-movies/vegas-afterlight-storm-v3-preview.mp4` — 45.000 seconds, 2,700 frames, 1920×1080, 60 fps, H.264/AAC; 145,681,707 bytes. The owner supplied additional requirements before final delivery. Prior previews are preserved.

Eleven dynamic anatomical bodies and ten joints start at the animated skeleton pose. A real vehicle contact triggers a localized chest stunt impulse with equal/opposite recoil; limbs articulate immediately and continue through flight and landing. Following the first collision, vehicle contacts are suppressed only until every limb clears the car; world contacts/joints remain live. This explicit stunt-contact accommodation prevents repeated wheel-guard wedging. Unfiltered contact trials tipped the car, and a boost alone did not solve the repeated contact problem. This is not a claim that unmodified contact solving alone produces the launch.

The driver now uses rate-limited steering and measured sideslip feedback with constant tyre settings. No chassis position/velocity track or geographic tyre-property switch. The actual recording measured 20.07° Bellagio sideslip at 89.10 km/h, peak 124.75 km/h, 88 impacts, peak 22 simultaneous ragdolls, and arrival within 1.16 m. At least two wheels in contact for 99.74% of samples; peak actual chassis roll 7.89°. All route assertions pass. A real-skeleton/Rapier test verifies joint movement within 100 ms and while airborne; disposal/restore checks leave no ragdoll bodies behind.

Consecutive impact and turn frames, launch camera flag, lightning and arrival were visually inspected. Export decodes cleanly; no frozen sequences; only explicit opening/end fades and the lightning brightness flag. Audio peak −3.5 dBFS. TypeScript and driver/scene/ragdoll tests pass. Protected world/game/geographic hashes are unchanged. Art limitations remain: flat wall areas, approximate window emission and concentrated arrival lighting; no photorealism or owner-approval claim. The local CLI verification limitation below remains applicable.

# Elara to Bellagio storm cinematic

## Historical v2 preview — rejected physics

The owner rejected the two-minute cut and requested a shorter, much faster run, a sideways Bellagio turn, stronger articulated impacts, better asphalt/night lighting, foot planting and actual vehicle physics with body sway. The original preview below is historical and is not acceptance evidence for this revision.

The current car is a 1,350 kg dynamic Rapier chassis with four suspension raycasts, tyre forces, CCD, wheel guards and a cabin collision shape. SceneDriver only supplies steering/throttle/brake and temporary rear lateral grip reduction at the Bellagio drift. It does not overwrite body transforms or velocities. A damped sprung-shell model uses measured acceleration and yaw rate on the simulation clock for pitch and roll; independently suspended wheels follow the physics contacts. This is a real-time raycast vehicle model, not a multibody suspension-linkage or soft-body simulation.

The guide is approximately 1,001 m. The accepted physical preflight reaches the entrance in approximately 38 s; the cut lasts 45 s including the short final hold. Sampled peak speed 124.97 km/h; Bellagio slide 88.5 km/h and 21.2 degrees slip. Sampled sprung-body roll reaches 7.05 degrees, pitch 4.53 degrees; actual chassis roll reaches 1.49 degrees. Minimum sampled wheel contact count is 2 over surface transitions. 77 impact events; peak 20 articulated ragdolls. See physics-preflight-v2.json.

Impacts transfer momentum to the chassis and launch all ten jointed bodies coherently. The newly created limb shapes exclude vehicle collision for 0.22 s to clear their initial overlap, then restore normal body contact. This avoids the previous solver explosion flipping a 1.35 tonne car on the first person. The limbs continue colliding with the world throughout. Walking roots follow their planted support foot rather than sliding over an in-place clip. Crowd placement is distributed by road distance; the old time distribution piled actors onto the stationary starting point.

Visual changes: rough scanned aggregate is retained between localized wet patches; lower mirror strength; actual spot floodlights for Eiffel and Bellagio; boot-allocated car lights and fill; reduced ambient daylight; window-aperture emission with dark spandrels; modest bloom; a reversible film-only Planet Hollywood/Miracle Mile storefront layer. The latter follows surveyed footprints and official access/lease maps, but sign placement and elevations remain estimates. It does not complete the full resort reconstruction queue. See frontage-references.json.

Validation: TypeScript and driver/scene regressions pass; source world/game/geographic files match the original protected hashes. The film shadow map is allocated at its final size before first rendering, because resizing after reflection/bloom compilation left stale WebGPU bindings. The first revised recording exposed launch framing and extra recording ticks during holds/end polling. Camera framing was rebuilt for the fast drive; capture now writes only advancing film ticks, and streaming holds freeze cinematic physics as well as the game clock. The UI controls/restoration test passed with the dynamic 1,350 kg car: saved settings applied, restore removed car, vehicle handle, crowd and frontage and restored the environment/exposure (zero browser errors).

### Delivered revision and actual capture evidence

`<repo>-movies/vegas-afterlight-storm-v2-preview.mp4`

44.983333 seconds, 2,699 frames, 1920×1080 H.264 at 60 fps, stereo 48 kHz AAC, 142,933,729 bytes. Capture took 303.1 wall-clock seconds (8.9 fps offline throughput). This is not an interactive 60 fps claim. The source starts after the initial recorder tick; the edit uses all 2,699 available frames without padding or playback speed changes. The earlier 120-second movie remains intact.

The actual final trace (2,701 physics samples) reaches 125.00 km/h, records a 30.73° sideways Bellagio slide at 77.79 km/h, stops within 2.15 m of the entrance guide endpoint, and registers 77 impacts with at most 20 simultaneous articulated ragdolls. Peak sprung roll/pitch: 7.05°/5.04°; peak physical chassis roll: 1.49°. At least two wheel contacts in 99.56% of samples; brief crest hops remain. `check-stunt-track.py` passes all physical-route assertions. The tire mesh radius (0.401 m casing plus tread) matches the 0.405 m physics radius; each rendered wheel uses the engine's actual suspension contact transform.

Camera rates: median 8°, p95 42°, max 84°/s. The automated camera checker flags short fast turns at launch (1.1–1.6 s) and the final orbit (37.1–37.4 s). Those ranges were reviewed in dense motion sheets: the car remains framed; the flags are retained, not reported as a clean camera-check pass. No hunting, jerk or steep-view flags. Source and export pixel scans detect no freezes. The two brightness flags were inspected: lightning at 28.57 s and the bright portico lamp emerging into view at 36.25 s. Opening/closing black frames are the explicit fades. Full exported MP4 decode reports zero errors. Audio peaks at −3.3 dBFS; engine, tyre slip and impact cue timing follows the recorded physical trace/events. Final capture reported no director warnings or WebGPU validation errors (one unrelated initial HTTP 404 was logged).

Visually inspected the exported contact sheet plus actual launch, drift, arrival and flagged brightness sequences. Asphalt grain, airborne bodies and the vehicle are visible; the wider art target remains unachieved. The road still needs better contact shading/reflection integration and richer tyre spray; some large walls/frontages are plain, window emission is an approximate aperture grid, and portico lighting is too concentrated. The Planet Hollywood layer adds limited storefront detail, not a complete resort facade reconstruction. The actors are existing human meshes adapted as infected, not bespoke zombie sculpts. The current result must not be called PS5/UE5 photorealistic or owner-approved.

Film mode remains reversible; base world/game/geographic JSON hashes were rechecked unchanged after export. No supersampled final, cloud judging, upload or publication. The local CLI verification limitation described under the historical section still applies. Evidence files with `v2` names belong to this revision; unversioned files below refer to the rejected first preview.

## Historical first version (rejected by owner)

User selected Elara on Harmon. This is a new, approximately two-minute cinematic with a separate military coupe, rain, wet asphalt, neon/window illumination, lightning and a bounded crowd of articulated ragdolls. It is local work; no assets were uploaded and no level geometry was regenerated.

## Implementation

- `tools/film/build-interceptor.py` builds the separate Blender car (`build/film/storm/interceptor.glb`). Its body and four independently turning wheels are loaded only for the cinematic. The original player jeep is not replaced.
- `tools/film/make-storm.py` generates the 120-second route and independent drone camera in `tools/film/takes/storm.json`. It follows Harmon west, turns right onto the Strip, left into Bellagio, and follows the existing arrival road. Peak sampled speed is 84.7 km/h. The movement is directed by the film, not by the gameplay driving controller.
- `SceneSession` owns temporary car physics and crowd resources. `SceneAtmosphere` saves/restores lighting, sky, environment, fog, exposure and weather. Eight cinematic lights are allocated once at boot, then controlled through intensity/position.
- `SceneSurface` applies the engine wet-road BRDF to asphalt material rows while retaining their scanned surface detail. Window emission and existing neon are controlled separately. Normal gameplay is not assigned this shader variant.
- The rain uses the engine GPU rain component with a cached mesh-level height field and the deterministic film clock. The engine's ordinary weather terrain adapter only supports VXL, so the cinematic owns the rain component while the public weather API supplies reflections.
- `SceneCrowd` uses three existing detailed, skinned human character assets with an ashen tint and altered gait. They are repurposed infected people, not newly sculpted zombie assets. The resident pool is capped at 72; impact physics at 16 simultaneous ragdolls, each with ten bodies and nine joints. Bodies are retired outside the shot.
- `tools/film/storm-audio.py` synthesizes stereo rain, engine, wet tyres, two skids, thunder and impact cues from the recorded event times. This is procedural sound design, not a licensed recorded engine library.

## Local controls

Open `http://localhost:3090/?film=1`, start the game, and press **Shift+C**. Daylight, weather, rain, wetness, neon and crowd settings are saved under `afterlight:cinematic:v1` on that browser. **Play preview** runs the route using those settings. **Restore level** removes cinematic actors/physics and restores the captured scene look. Ordinary game boot without film mode retains its existing defaults.

## Validation and remaining review

- TypeScript compilation passes.
- `tests/film-scene.test.mjs` passes: finite route samples, 120-second duration, bounded speed/frame travel, stationary endpoint, default weather and unchanged world file.
- Installed car inspected in Blender and engine. The crowd mesh-material shape bug was corrected after an actual motion review found invisible actors despite impact counters. Visible people and airborne ragdolls were confirmed in the subsequent motion frames.
- Original world/game/geographic JSON hashes are retained in `protected-hashes.json`; the working world file has remained byte-identical to its backup.
- The 1080p preview, exported-file inspection, camera report, scene restore and controls checks are complete and recorded below. No photorealism claim is made. This is a cinematic scene layer over the existing level, including its existing architectural limitations.

The project instruction requires showing the real-time preview before a supersampled final. No supersampled final is implied by this pass.

## Recorded preview and checks

The preview uses a clear six-second introduction (trimmed to 5.8 seconds), the recorded chase through 98 seconds, and a 22-second pickup on the corrected mapped driveway. Full route motion is deterministic; the pickup uses 12 residents to avoid crowding the arrival into an unreadable mass. The full chase recorded 62 impact events and at most 16 simultaneous articulated ragdolls. Its 1080p capture took about 10 minutes, averaging 11.8 captured frames per wall-clock second; the resulting video plays at fixed 60 fps. This is an offline cinematic capture, not a claim of interactive 60 fps with this population and film shadow reach.

Camera inspection: the used 98-second chase has median/p95/max turn rates 4/19/28 degrees per second and no turn, jerk, hunting or steep-view flags. The initial pickup inspection caught one late frame beyond its camera segment; scenario camera selection now clamps to the duration even while the wait step finishes. The opening review also caught Hermite overshoot reversing the slow car's heading; the first five seconds now hold position with an explicit initial heading. A regression test covers the stationary intro and endpoint. Obsolete pickup tail frames are excluded or under the final fade.

Actual controls test through `http://localhost:3090/?film=1`: Shift+C opened the dialog; day/clear/zero rain/zero crowd settings were saved and applied; Restore level removed the interceptor and all crowd actors and restored the original environment UUID and exposure. Zero browser errors. Evidence: `controls-check.json`. The first attempt through the editor shell was blocked by the shell boot overlay; it is not counted as a successful test.

Bitmagic CLI verification was not run: automatic approval review rejected it because passing the full prompt to a CLI with unestablished network/logging behavior could violate the local-only restriction. No bypass, publishing or uploading occurred. Local browser execution, controls/restoration, TypeScript, route regressions, captured-frame analysis and MP4 decoding were used instead. Supersampled final remains subject to the owner's preview review.

## Delivered preview

`<repo>-movies/vegas-afterlight-storm-preview.mp4`

Final export: 120.000 seconds, 7,200 frames, 1920×1080 H.264 at 60 fps, stereo 48 kHz AAC, 419,621,664 bytes. Full FFmpeg decode returned zero errors. Frame analysis found only the intentional opening/closing fades and cuts at 5.8 and 98 seconds; no freezes. The final exported contact sheet and corrected opening were visually inspected. Evidence: `export-metadata.json`, `export-decode.txt` (empty = no errors), `export-frame-check.txt`, `export-contact-sheet.jpg`, `hero-reviewed.png`. The recorder's reload hold was removed. The movie is in a visible folder beside the project, not inside `.bitmagic`.
