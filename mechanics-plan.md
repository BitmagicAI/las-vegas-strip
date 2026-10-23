# Mechanics plan: the city

The city has no game loop of its own; a game adds one as a layer (`src/work/GameLayers.ts`). This plan covers what the
city itself provides, and in what order it grows. Open work, item by item, is on the task board
(`tasks/BOARD.md`, generated from the block records). The status in numbers is in `STATUS.md`.

## In place

1. Map: OpenStreetMap footprints, heights and roads, and Clark County pavement, with a box building for every mapped
   footprint.
2. Detailed exteriors for 188 blocks and 631 reviewed mapped buildings, each with a record of its sources and its gaps.
3. Streaming: landmark and resort venues, 64 hotel towers with enterable rooms, bridge concourses, the Sphere. All load
   near the player or the film camera and are released behind them.
4. Movement: walking, the jeep with road speed assist, doors, the Paris lift, the coaster.
5. Looks: day, dusk, night, neon and rain presets on the same models (film takes; a game can call FilmLook too).
6. Tools: probes for frame time, streaming, interiors and memory; the film director; the release smoke test.

## Next, in order

1. The current engine. The repository follows the published engine (task `rel-engine-current`).
2. Release blockers: texture provenance, Clark County terms (`release` tasks).
3. Public interiors built to the resort maps, starting with the casino resorts that have none (`int-*` tasks).
4. Exterior refinement, block by block, in queue order (`ext-*` tasks).
5. Performance: GPU-compressed textures, binary collision data, draw calls at the lakefront (`perf-*` tasks).
6. A source pack, so contributors can rebuild every existing building (`tool-source-pack`).

## Not in the city

Characters, NPC crowds, missions, combat, inventories, scores and game HUD. A game built on the city owns these. The
zombie-survival game's cast, sanctuary, supply caches and storm-chase film scenes moved to its own project on
2026-10-22. Their history is in `docs/history/`.
