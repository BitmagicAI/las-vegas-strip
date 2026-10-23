# Why point lights got so expensive, and the engine's new lighting (2026-10-07/08)

Owner request (summary): analyze why performance was so poor, whether the engine can fix it, and whether the new light pooling helps.

Analysis and measurement only. The game's fixes (InteriorLighting, NearbyLights, sun-only foliage) stay as
shipped, and the engine repo is unchanged.

Setup: headless Chrome 153 on the owner's Mac, WebGPU on Metal. Canvas 3010×1544 (1505×772 CSS px at DPR 2),
4× MSAA, `?quality=ultra`. Five views: the Caesars corridor, the spawn jeep (`jeep-west`), the garden,
the trees and the Strip looking north.

Each view was measured two ways:
- **As shipped**: the game-side light lists are on.
- **Full list**: every lit material uses the scene's light list (43 point lights, sun, sky, ambient), the
  way the game was before the fixes.

The lighting system is installed at boot by a local switch, `?lighting=engine<cap>|clustered` in `Game.ts`.
The new engine files are copied unchanged into `src/work/experiments/engine-lighting/`.

Tools: `tools/probe-lighting-modes.sh`, which runs `tools/probe-interiors.mjs --query` for each mode, and
`tools/probe-eval.mjs build/probe/shader-size/jeep-churn.js` for shader size and pipeline builds.
Data: `data/`.

## Why it got so bad

1. **three r185 builds per-light shader code.** Its default WebGPU lighting compiles every visible light into
   every lit material's fragment shader as a separate block of straight-line code, with no loop and no culling.
   The jeep body's fragment shader:
   - with its 8-light nearby list: 59,775 characters, 1,402 lines;
   - with the scene's 43 point lights: 187,974 characters, 3,712 lines, 0 loops.

   Run on every pixel of a screen-filling surface, the big shader is far slower than its arithmetic
   suggests. The same 43 lights in a loop (below) cost 8-12× less GPU time.
2. **The light count grew because of how the shader-rebuild stalls were solved.** three also hashes every
   visible light into each material's shader key, so adding or hiding one light froze the game for
   0.3-3 s. The fix was a rule: never change the light set; keep pool lights visible and park them at
   intensity 0. A parked light costs the same per pixel as a lit one. The pools were added one at a time,
   each sensible on its own:

   | Pool | Lights |
   |---|---:|
   | Engine fixture pool (`pointLightPoolSize: 25` in `Game.ts`) | 25 |
   | Hotel pool | 8 |
   | Shared venue lights | 4 |
   | Others | 6 |

   Together that is 43 point lights in every lit pixel. The 8 nearest lights give an identical picture in
   every view measured. The other 35 were pure cost.
3. **Pixels.** Retina at 2× with 4× MSAA, plus surfaces that fill the screen or overlap many times: grass
   blades, leaf cards, the jeep up close, corridor walls.
4. **The places people usually test hid it.** The Strip and the car camera run 60 fps even with the full
   list (Strip looking north: 9.5 ms GPU). The overlay shows fps but not GPU time, so the drops beside the
   jeep, in the garden and inside looked random. The 20-40 fps while standing still had a second, separate
   cause: V8's memory limit (`idle-performance-2026-10-07`).

## Measurements

GPU ms per frame (p50) and fps. On this GPU the per-pass timestamps overlap, so treat GPU figures as
relative (±2 ms).

**Full list (every material on the scene's 43 point lights)**

| View | three (default) | engine, cap 64 | cap 32 | cap 16 | cap 8 | three Clustered |
|---|---:|---:|---:|---:|---:|---:|
| Caesars corridor | 55.6 ms, 41 fps | 20.9, 60 | 11.0, 60 | 7.3, 60 | 9.7, 60 | 5.9, 60 |
| Jeep at spawn | 192.3 ms, 11.6 fps | 15.0, 60 | 12.6, 60* | 9.5, 60* | 8.8, 60* | 7.1, 60* |
| Garden | 245.7 ms, 8.2 fps | 20.6, 60 | 17.8, 60 | 11.7, 60 | 10.1, 60 | 8.8, 60 |
| Trees | 175.0 ms, 11.6 fps | 23.4, 60 | 17.8, 60 | 11.6, 60 | 9.6, 60 | 8.6, 60 |
| Strip north | 9.5 ms, 60 fps | 13.7, 60 | 9.0, 60 | 9.4, 60 | 10.6, 60 | 9.4, 60 |

\* About 22 fps (clustered: 8.6) in the multi-view probe. Those frames had low GPU and CPU time and
were measured seconds after the light lists were switched, while new pipelines were still building.

An independent run settled 15 s before measuring, counted pipeline builds and used no timestamp
queries (`data/jeep-churn-*.json`):
- engine at cap 64, engine at cap 32 and Clustered: 60 fps with 0 pipeline builds a second;
- three's default: 8.8 fps, also with 0 builds, so its cost is pure shading.

**As shipped (game-side lists on)**

| View | three | engine 64 | engine 32 | engine 16 | engine 8 | Clustered |
|---|---:|---:|---:|---:|---:|---:|
| Caesars corridor | 8.9 | 8.9 | 8.4 | 9.8 | 10.4 | 9.9 |
| Jeep at spawn | 9.0 | 7.6 | 10.3 | 8.8 | 9.1 | 8.9 |
| Garden | 14.8 | 9.4 | 10.2 | 7.9 | 9.6 | 9.3 |
| Trees | 26.7 | 9.2 | 11.4 | 8.7 | 11.1 | 10.4 |
| Strip north | 10.0 | 9.8 | 8.8 | 8.4 | 10.3 | 8.2 |

All of these run at 60 fps. The trees view still has materials on the scene list (the grove), and the
engine lighting helps them too: 26.7 → 9.2 ms.

**Shader size** (jeep body, fragment shader, full list):

| Lighting | Characters | Lines | Loops |
|---|---:|---:|---:|
| three default | 187,974 | 3,712 | 0 |
| engine (`BatchedLightsNode`) | 40,494 | 1,031 | 4 |
| three Clustered | 35,108 | 957 | 1 |

**Pictures.**
- The engine's batched lighting matches three's default, comparing screenshots taken with each lighting
  installed at boot. At cap 64 every view and both states show 0-0.01% of pixels differing by more than
  16 levels. Caps 32, 16 and 8 are also identical, apart from 1-2% at cap 32 in two views, which
  caps 16 and 8 do not show; that comes from NPCs moving, not lighting.
- `garden-full-list-three-vs-engine.png`: three at 8 fps on the left, the engine at 60 fps on the right.
- Clustered matches in the corridor, trees and Strip views. Its jeep and garden captures were framed
  differently (the camera position differed), so they say nothing about its lighting.

## Does the new light pooling help?

Yes, a lot, but for a different reason than its name suggests. The new engine lighting in the Aitopia5
working tree has two parts:

1. **`EngineLighting` + `BatchedLightsNode` (batching).** All point, spot, directional and hemisphere
   lights go into one uniform array, and the shader loops over a count uniform. The shader stays small
   whatever the light count, and light changes never alter the shader key. This is the part that fixes
   it: the full list goes from 8-12 fps to 60 fps with an identical picture, and no game-side workaround
   is needed. Hidden lights are free, so the never-change-the-set rule can relax: pool lights can be
   hidden instead of parked.
2. **`LightManager` (pooling and budget).** Lights are virtual, the best `dynamicLights` of them get real
   slots (32 on desktop, 12 on low) and swaps fade. On top of batching it saves a few ms here. Going
   from 43 to 32 lights saves 3-6 ms in the garden and trees, and 16 lights saves 9-12 ms. Without
   batching, a 32-light budget would still compile 32 per-light blocks into every shader: about three
   quarters of the 43-light code (estimated, not measured).

Caveats:

- **Not in this game yet.** Vegas runs the vendored engine 3.1223. The new lighting files are
  uncommitted in Aitopia5, next to about 185 other modified files from other work. Getting it here needs
  three steps: the engine work committed, a CLI release, then `bitmagic upgrade` in this project.
- **The budget only covers lights registered with the `LightManager`.** The engine's fixture pool will
  go through it. This game's own lights are plain `THREE` lights: the hotel 8, the venue 4, and the
  NearbyLights stand-ins (which live outside the scene). Those would be batched but not budgeted; the
  only limit is the cap, where the nearest 64 to the camera win.
- **Material-level lists (`lights([...])`) still compile per light.** That covers InteriorLighting,
  NearbyLights and the foliage list. They hold at most about 11 lights, so the cost is small. They still
  halve GPU time compared with the engine's full list: corridor 8.9 against 20.9 ms, jeep 7.6 against
  15.0, garden 9.4 against 20.6. Keep them after the upgrade, since weaker GPUs need the margin.

## Engine fixes proposed (not done; engine repo untouched)

1. **Ship `EngineLighting` and upgrade this game to it.** This is the fix that matters.
2. **A batched node for material-level lists.** For example, an engine call that returns a fixed
   `BatchedLightsNode` list for a set of lights, or `LightManager` zones whose materials get the zone's
   list. Interiors, close-up movers and foliage would then loop too.
3. **GPU time in the performance overlay** (timestamp queries), and a dev-build warning when a lit
   shader carries more than a few per-light blocks. The existing `LightingKeyTripwire` names key
   changes but not cost.
4. **Ranking and garbage in the new code.** Two things go against the owner's no-JS-arrays rule:
   - Over the cap, `EngineLightsNode.showNearest` refills an array, sorts it with a closure and fills a
     `Map` on every render, shadow passes included (where it ranks by the shadow camera).
   - `BatchedLightsNode.listOf` slices a new array every frame when over the cap.

   Use typed scratch arrays, and rank once per frame from the view camera.
5. **The three r185 traps hit on the way**, worth absorbing in the engine:
   - `MeshStandardNodeMaterial.copy()` drops `alphaTest`.
   - The shadow pass toggles one shared material's `alphaTest`, which rebuilds every caster's pipeline
     key each frame.
   - `Lighting.getNode` caches per scene in a module-level map shared by every `Lighting`, so a
     `renderer.lighting` swapped in after the first frame renders wrong pictures. Install it before the
     first render; the engine already does.

## Corrections to earlier records

Earlier statements that three's `ClusteredLighting` is "as slow as the full loop" or "slower" came from
runtime A/Bs that swapped `renderer.lighting` after boot. On r185 that swap does not take effect cleanly,
because of the shared `Lighting.getNode` cache above, and it also produced the dark cap-32 corridor seen
on 2026-10-07. Installed at boot, Clustered runs every full-list view at 60 fps (5.9-9.4 ms GPU).

It is still not the recommendation:
- it batches only point lights;
- it adds a compute pass;
- it is three's addon, not the engine path that removes the shader-key stalls.

Corrected in AGENTS.md, `interior-performance-2026-10-07/README.md` and
`idle-performance-2026-10-07/README.md`.

## Experiment code left in the game

- The local boot switch `?lighting=engine<cap>|clustered` in `Game.ts`. It runs on localhost only and
  does nothing without the parameter.
- `src/work/experiments/engine-lighting/`, which the switch uses.

Keep both until the engine upgrade, to repeat this A/B against the real engine lighting. Then remove
both; the engine's own `?lighting=three` gives the reverse A/B. The runtime-swap probe hooks
(`clusteredLighting`, `engineLighting`) were removed because they rendered wrong pictures.
