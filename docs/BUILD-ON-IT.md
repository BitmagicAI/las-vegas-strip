# Building on the city

The project is a Bitmagic game, so it works as a starting point:

1. **Fork it, or copy it.**
2. **Give the copy its own game id.** Run `bitmagic init` in an empty folder. Copy the new `gameId` into this
   project's `bitmagic.json` and `src/work/game.json`. Leave the asset URLs in `src/work/world.json` as they are: they
   point at this project's hosted assets.
3. **Add your game as a layer.** Implement `GameLayer` (`src/work/GameLayers.ts`) in your own folder and list it in
   `GAME_LAYERS`. That one line is the only city file you edit, so city updates merge in cleanly. The layer gets the
   player, the HUD, the ground and the nearby lights, and can use the city's night and rain looks (`FilmLook`).
   `AGENTS.md` and `engine/agent-docs/` explain the engine. The zombie-survival game "Vegas: Afterlight" is built this
   way, in its own repository.
4. **Publish** with `bitmagic publish`, or build it with `bitmagic build` and host it yourself.

Using another engine? The GLBs in `runtime-assets/` are standard glTF 2.0 with meshopt compression. The collision, route
and venue data are plain JSON. We support the Bitmagic path only; other engines are up to you.

**Credit the city** where your credits go:

> Las Vegas Strip (https://github.com/BitmagicAI/las-vegas-strip), CC BY 4.0 · Map data © OpenStreetMap contributors, ODbL
