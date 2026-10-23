# Hotel LOD continuity — 2026-10-10

The reported Cromwell colour jump was reproducible in the installed game. The old hotel LOD clustered vertices solely by position, averaged colours across different facade surfaces, discarded the texture mapping, and recomputed the normals. The switch distance depended on height alone, so low, broad hotels switched early.

## Installed correction

- `CityLod` now offers a facade policy used by mapped high-rises, landmark resorts and legacy hotel shells. Geographic background buildings and roads retain their existing policy.
- The reduced facade keeps its original colour, material/PBR rows, texture coordinates and surface normals. Clusters cannot cross material, colour, hard-normal or separate-plane boundaries (5 mm coplanarity tolerance); texture-coordinate seams are constrained. Both levels share the same shader and atlas, with reference-counted cleanup.
- Default facade range is `max(550, min(1800, height × 6), min(650, footprint × 6))` metres from the bounds, with the existing 12% hysteresis and extra reach for zoomed perspective views. A wide resort yard alone cannot keep everything at full detail for kilometres. Hotel silhouettes remain in the distant skyline.
- Custom architectural/transparent surfaces remain continuous. Water retains its existing near-level membership; its shaders and reflection updates were not modified.
- Batching, compact buffers, GPU-upload CPU release, existing source visibility and collisions remain in use. No GLBs, roads or interiors were regenerated.

## Evidence

`before/` contains the original installed results. `verified/` and `verified.json` contain the accepted final Cromwell and other-resort results, explicitly selecting tower blocks through their venue ownership. The second set of captures includes the scene hierarchy panel on the left; the tested central tower facades remain visible. Full/reduced comparisons deliberately force the two levels at the same camera, closer than the new normal switch, to expose differences.

Cromwell's original reduced batch had 14,470 triangles; the replacement has 31,927, still about 86.4% below the full batch (~235,000). It retains the window/stone palette. The natural camera sweep originally selected reduced detail by eye position (-250,38,140); it now remains full at (-650,38,140) and selects reduced at (-850,38,140). Exact thresholds depend on the lens and hysteresis direction.

At the same 219×104-pixel crop around Cromwell, the mean per-channel full/reduced colour shift fell from about 10–13 to about 0.7–1.4 levels on a 0–255 scale. Mean absolute pixel difference fell from 21.25 to 8.13. These are a local screenshot comparison, not a universal image-error bound. Fine geometry can still change at the far handoff; no claim of pixel-identical LODs or photorealistic architecture.

| Original full | Original reduced |
| --- | --- |
| ![Original full](before/cromwell-full.png) | ![Original reduced](before/cromwell-coarse.png) |

| Corrected full | Corrected reduced |
| --- | --- |
| ![Corrected full](verified/cromwell-full.png) | ![Corrected reduced](verified/cromwell-coarse.png) |

## Performance and checks

Matched 1280×800 ultra camera, after settling, 150 animation frames:

| Policy | Median frame | p95 | Maximum | Total multipass triangles |
| --- | ---: | ---: | ---: | ---: |
| Original | 16.6 ms | 17.6 ms | 18.6 ms | 11.78M |
| Final | 16.7 ms | 18.4 ms | 29.1 ms | 14.60M |

Both final and baseline used four render passes. The higher triangle cost buys the longer detail range and more faithful distant facades; this view maintained approximately 60 fps. These timings are local warmed samples, not a whole-game/device performance guarantee.

Baseline was measured by intercepting the local browser's compiled CityLod module and disabling only the new facade path. No project files were reverted. The cache-busting service worker was blocked for that baseline so it could not bypass interception. Its expected registration warning is captured in `baseline-stderr.txt`; the guard confirms one successfully patched module. Two earlier attempts without a valid interception were rejected and are not the reported baseline.

An initial unbounded footprint-distance version was rejected: it cost 24.9 ms median / 26.2 ms p95 and activated an extra remote canal reflection pass. The final footprint cap and existing water culling restored the matched frame rate. Those superseded captures remain under `after/` and `views/` for traceability. The later `final-views/` comparison exposed same-finish white trim pulling a Harrah’s wall in front of its windows. The 5 mm plane constraint and offset-plane regression fixture correct that failure; `verified/harrahs-full.png` and `verified/harrahs-coarse.png` were inspected and retain the window grid.

Regression suite (`tools/test-city-lod.mjs`) passes: original batching/grounding/visibility/shadow/cleanup cases plus colour boundaries, separate planes with identical finishes, flat normals, UV retention, reduction, material ownership, transparent continuity, water range membership, footprint ranges and stationary zoom. Final `bitmagic check` passed (`check.txt`). Final natural-camera warm samples:

| View | Median frame | p95 |
| --- | ---: | ---: |
| Cromwell street | 16.7 ms | 18.4 ms |
| Venetian / Palazzo aerial | 18.9 ms | 19.9 ms |
| Bellagio | 16.7 ms | 18.0 ms |
| Harrah’s | 16.5 ms | 18.6 ms |

The Venetian aerial is about 53 fps in this sample; do not generalize the matched Cromwell 60 fps result to every view. The combined live-browser test successfully selected a character, started the game, entered the editor, selected natural/forced LODs and captured all these views. Browser-reported heap was approximately 2.31 GB used (this excludes GPU allocation).

Reproduce locally:

```
node --import ./tools/ts-register.mjs tools/test-city-lod.mjs
node tools/probe-eval.mjs tools/probe-hotel-lod.js --viewport 1280x800 --out build/probe/hotel-lod
node tools/probe-eval.mjs tools/probe-hotel-lod.js --lod-baseline --viewport 1280x800 --out build/probe/hotel-lod-baseline
node tools/probe-eval.mjs tools/probe-hotel-lod-views.js --viewport 1280x800 --out build/probe/hotel-lod-views
```

The visual probes use isolated local headless Chrome instances. Run them serially when comparing timings.

Final standard CLI verification passed on the stable final build (`verify-final.txt`, `verify-final.json`): WebGPU, playing, player grounded, no failures or warnings. An earlier attempt timed out in the menu (`verify.txt`); it was rerun successfully rather than counted as a pass. The existing local server reloaded two browser tabs. No cloud judging or uploads were performed, following the project’s local-only rule.
