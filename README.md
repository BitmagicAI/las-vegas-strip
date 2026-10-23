# Las Vegas Strip

A walkable, drivable Las Vegas. The Strip and the blocks around it are rebuilt from public map data and public
references by AI agents working in a loop, a little more detail every pass. It runs in the browser on the
[Bitmagic](https://bitmagic.ai) engine. It is free to use as the setting for your own game.

- **6,162 buildings** from OpenStreetMap. 604 of them are replaced by detailed models, 188 sites have a block record,
  and 631 mapped buildings have been reviewed one by one.
- **8.3 km of the Strip** and the streets around it. Road, sidewalk and median surfaces come from Clark County data.
- **64 hotel and residential towers** with 2,130 floors. About **30,700 enterable hotel rooms** (49 room designs) and
  5,800 apartments are streamed in as you approach.
- **Public interiors:**
  - the Venetian's Grand Canal Shoppes;
  - Bellagio, Paris and the Cosmopolitan;
  - the LINQ, Park MGM, Treasure Island, Harrah's and Fashion Show;
  - the Sphere (with its video skin);
  - a rideable Big Apple Coaster.
- **About 97 million triangles** in 646 runtime models. Everything streams: rooms and venues are always reachable, but
  nothing loads or draws until you are near it.

[STATUS.md](STATUS.md) lists what is built and what is missing. [tasks/BOARD.md](tasks/BOARD.md) lists every open task.

## Run it

You need Node 20+, pnpm, [Git LFS](https://git-lfs.com) (the repository's models, images and archives are LFS files),
a WebGPU browser (current Chrome), and the Bitmagic CLI with a **Bitmagic Pro** subscription.
The Bitmagic engine is not part of this repository: it is a dependency that `bitmagic upgrade` installs into `engine/`,
together with the engine's documentation and the CLI's agent skills.

```bash
npm i -g @bitmagic/cli
```

```bash
bitmagic login
```

```bash
git lfs install
```

```bash
git clone https://github.com/BitmagicAI/las-vegas-strip.git
```

```bash
cd las-vegas-strip && bitmagic upgrade && pnpm install && node tools/release/fetch-assets.mjs
```

```bash
bitmagic dev
```

`bitmagic upgrade` always installs the currently published engine, and this repository follows it. If the typecheck
(`bitmagic check`) fails right after a new engine release, that is a task on the board, not your setup. The clone
downloads about 1.1 GiB of models and data through Git LFS ([docs/ASSETS.md](docs/ASSETS.md)).

Open the URL `bitmagic dev` prints and click Play:

- **Walk:** WASD to move, Shift to run, the mouse to look, Space to jump.
- **Drive:** E gets in and out of the jeep.
- **Doors and views:** F kicks a hotel-room door open, V switches the view.
- **Panel:** B shows statistics and settings.

## Use it for your own game

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

## Contribute

Pick a task, claim it on its issue, and open a pull request. [CONTRIBUTING.md](CONTRIBUTING.md) covers setup, rules
and verification, and [tasks/README.md](tasks/README.md) covers how claiming works. With an AI agent, clone the repo,
fetch the assets and say:

> Read AGENTS.md and CONTRIBUTING.md, run `node tools/tasks/pick.mjs`, claim a small open task and do it.

## How it was made

1. **The map.** OpenStreetMap footprints, heights and roads, and Clark County pavement data, became streets and box
   buildings (`tools/strip-survey/`, `tools/geographic-strip/`).
2. **The buildings.** Agents compared each building with Google Earth views, then rebuilt it in Blender from public
   photographs and published resort maps. A block record notes each source and every gap still open
   (`tools/resort-blocks/`).
3. **The interiors.** Lobbies, casinos, corridors and rooms were laid out from published floor plans and photographs
   (`tools/strip-landmarks/`, `tools/highrises/`, `tools/level/`).
4. **Checking.** Every pass was compared against its references and walked. Collision was audited, and frame time
   measured before and after.

The history is in `docs/project-records/`.

## Licence

These licences cover the Vegas project only: the city, its code, data and documentation in this repository, including its
runtime assets.

| Part | Licence |
|---|---|
| Code | MIT ([LICENSE](LICENSE)) |
| Original models, textures, data and documentation | CC BY 4.0 ([LICENSE-CONTENT.md](LICENSE-CONTENT.md)) |
| OpenStreetMap-derived data | ODbL ([LICENSE-DATA.md](LICENSE-DATA.md)) |
| The Bitmagic engine | not part of this repository; installed by `bitmagic upgrade` under its own licence |

Third-party credits are in [NOTICE.md](NOTICE.md).

This project depicts real places. It is not affiliated with, sponsored by or endorsed by any property owner or
brand shown, and all trademarks belong to their owners.
