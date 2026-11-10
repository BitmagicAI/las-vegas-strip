# Installed baseline — PR541

Six neutral daylight captures from `tools/city-exteriors/probe-grand-chateau-refinement.js`, exterior front first. All six personally inspected. Renderer: WebGPU ultra, 960×540, DPR1. Warm-up 900 frames, await streaming idle, settle 60 frames, 180 timing samples. Preserve these exact cameras for the installed comparison.

- Front west: modeled parking bands fill the inward court; entrance monument, ramps and south arrival canopy are absent. Ground routes must be tested independently; the reference monument is not a canopy.
- North: the existing flat canopy sits directly in front of the parking facade, contrary to the Jan2025 Street View.
- Pool: inset pool and broad empty terrace, no furnishings, handrails or perimeter safety enclosure. No continuous public route from ground is established.
- Crown west: flat vertical green band with rectangular dormer decals and a large flat roof. A modest inward roof slope and proper dormer cheeks are warranted by official photography; the raised wing-end crown and rooftop pool need separate height/access reconciliation.
- Tower south: broad silhouette and window rhythm are recognizable but end-crown heights are uniform and fine facade detail remains approximate.
- Aerial: branched footprint and separate podium visible. Do not change footprint ownership or rebuild nearby roads.

Measured p50/p95 ms: west 16.8/18.0; north 16.7/18.1; pool 28.6/29.9; crown 16.6/18.8; tower south 30.2/35.0; aerial 23.3/37.8. These are short-window baseline observations, not a framerate guarantee. Before/after comparisons must keep these lighting settings, cameras and warm-up unchanged.

Actual keyboard route baseline is separate in `before-walk`; no route result is implied by a still capture. No new model has yet been installed.

Keyboard baseline completed: all three routes and all 12 legs pass, six endpoint/return captures saved. Each route starts by teleporting to its first point; the pool route proves local deck traversal only, not connected public access. No doors were exercised.
