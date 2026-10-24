# Contributing to Las Vegas Strip

Thank you for helping build Las Vegas. This page covers setup, how work is shared out, the rules that keep the city
fast, and what counts as done. It is written for people and for the AI agents they work with.

**With an AI agent:** set up as below, then say:

> Read AGENTS.md and CONTRIBUTING.md, run `node tools/tasks/pick.mjs`, claim a small open task and do it.

## 1. Set up

You need:

- Node 20 or newer (`.nvmrc` pins 22) and pnpm 10;
- a WebGPU browser (current Chrome);
- the Bitmagic CLI with a **Bitmagic Pro** subscription.

The engine is not in this repository: `bitmagic upgrade` installs the currently published one into `engine/`, with its
documentation (`engine/agent-docs/`) and the CLI's agent skills (`.agents/skills/`).

```bash
npm i -g @bitmagic/cli
bitmagic login
```

Then, with [Git LFS](https://git-lfs.com) installed (models, images and archives are LFS files), clone (about 1.1 GiB, most of it the runtime set in LFS), then install the engine and the packages. `pnpm install`
also copies the runtime set into `build/` and adds git hooks that keep it current after every pull:

```bash
git lfs install
git clone https://github.com/BitmagicAI/las-vegas-strip.git && cd las-vegas-strip
bitmagic upgrade
pnpm install
bitmagic dev
```

Open the URL `bitmagic dev` prints and click Play. `bitmagic upgrade` rewrites `tsconfig.json`, `vite*.config.js` and
`index.html` to the current platform versions; if that shows as a change in git, commit it on its own. For geometry
work you also need Blender 4.2+ and Python 3.12 (`uv python install 3.12`). Some builders read source files that are
not in the repository yet; see [docs/ASSETS.md](docs/ASSETS.md) and the `tool-source-pack` task.

## 2. Pick a task and claim it

The full process is in [tasks/README.md](tasks/README.md). In short:

```bash
node tools/tasks/pick.mjs                 # open, unclaimed tasks
node tools/tasks/pick.mjs show <task-id>  # the brief
node tools/tasks/pick.mjs claim <task-id> # assigns you on the task's GitHub issue
git switch -c task/<task-id>
```

Open a draft pull request early with `Closes #<issue>`. Claims with no activity for 21 days are released.

## 3. Rules that are not negotiable

These come from measured problems; [AGENTS.md](AGENTS.md) explains each one with numbers.

- **Never change the set of lights while the game runs.** Create lights at boot and drive them by intensity and
  position. Interiors go through `lightInterior()` (`src/work/InteriorLighting.ts`). `tests/site-lights.test.mjs` fails
  if a streamed venue creates a light.
- **No JS arrays and no per-frame allocation at runtime.** Runtime data lives in typed arrays or flat tables. Hot paths
  allocate nothing per frame: no closures, spread, `map`/`filter` or `new Vector3`.
- **Everything heavy streams.** Every room and venue is reachable, but nothing loads or renders until the player (or the
  film camera) is near it. New interiors stream like the existing venues (`StripLandmarks`, `HotelStreaming`).
- **Nothing crosses a doorway.** No wall panel or moulding may cross an opening; doors must open both ways.
- **`engine/` is read-only and never committed.** It is the Bitmagic engine that `bitmagic upgrade` installs.
- **Measure before and after** any change that could cost frame time: `tools/probe-views.mjs`,
  `tools/probe-idle.mjs`, `tools/probe-interiors.mjs` (they pin `?quality=ultra`).

## 4. Sources: what you may use, what you may commit

The city is rebuilt from public information. Commit what *we* made. Link everything else.

- **Allowed as sources:** OpenStreetMap, published resort maps and floor plans, public photographs, Google Earth or
  Street View for looking, and architects' published drawings. Record each in the block record with its URL, provider,
  access date and what it establishes (`tools/resort-blocks/README.md`, step 1).
- **Never commit** third-party photographs, floor-plan images, PDFs or screenshots. `.gitignore` keeps the usual
  reference folders out, and `python3 tools/release/check-public.py` fails on stray media.
- **Never trace or extract** geometry or imagery from Google Earth, Google 3D Tiles or any other source whose terms
  forbid it. Look, measure and model by hand.
- **Textures** must be drawn by our scripts, CC0 (Poly Haven), or otherwise licensed for redistribution. Name the
  script or the source in your pull request.
- **OpenStreetMap-derived data** stays under the ODbL ([LICENSE-DATA.md](LICENSE-DATA.md)). Keep the
  "© OpenStreetMap contributors" credit.
- **Brands and signage:** casino and tenant names appear because they are on the real buildings. Do not reproduce
  logos as image files. Letter the signs in our own geometry or fonts.

## 5. Verify, then open the pull request

Run what applies:

```bash
bitmagic check                                              # typecheck against the vendored engine
node --import ./tools/ts-register.mjs tests/<name>.test.mjs  # logic tests
python3 tools/resort-blocks/review.py                       # block records are valid
python3 tools/tasks/build-board.py                          # regenerate the board after editing records
python3 tools/release/check-public.py                       # nothing private or third-party slipped in
```

For geometry changes, also do the following:

- Regenerate through the builder scripts. Never hand-edit an exported GLB.
- Re-optimize (`AGENTS.md`, "Runtime GLBs") and bump the folder's `version.json` revision.
- Commit `runtime-assets/` with `tools/release/asset-pack.json`. The optimizer's install step stages them; after any
  other runtime change run `pnpm assets` ([docs/ASSETS.md](docs/ASSETS.md), "Updating the runtime set").
- Attach before and after captures from the same cameras.

Then walk it in the game: go in, come back out, and drive past it.

The pull-request template carries the checklist. A maintainer reviews it and merges it. Changed models travel in
the pull request itself, as Git LFS files.

## 6. Licence of your contribution

By opening a pull request you agree that your contribution is licensed under the same terms as the part of the
repository it changes:

- code under the MIT licence ([LICENSE](LICENSE));
- original models, textures, records and documentation under CC BY 4.0 ([LICENSE-CONTENT.md](LICENSE-CONTENT.md));
- OpenStreetMap-derived data under the ODbL ([LICENSE-DATA.md](LICENSE-DATA.md)).

Only submit work you have the right to license this way.

## 7. Talking to us

Use issues for tasks and bugs (templates provided), and the task's own issue for anything about that task. Be kind;
assume good faith.
