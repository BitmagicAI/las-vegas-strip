# blender-level

The Python and Blender scripts behind the `building-levels-in-blender` skill (see
`cli/src/scaffold/blender-level-skill-files.ts`). A level is a short Python script written against
`bmlevel` — boxes, prisms, walls, doors, stairs, signage, rooms, lights, landmarks, all in game
coordinates — that Blender runs to produce one GLB (joined per material), an editable `.blend`
(named parts), a `bitmagic-mesh-level` JSON the engine's `MeshLevel` loads, and a `doors.json` in
the shape of `worldProfileData.doors[]`. Shipped here (package.json `files`) rather than rendered
into every project: most games never build a level this way, and the scripts are large. The
skill's step 1 tells an agent how to copy them into a project's `tools/blender-level/`.

| File | Runs under | Does |
|---|---|---|
| `find_blender.py` | python3 | prints the Blender executable, or how to install one |
| `bmlevel/` | Blender, or python3 for a dry run | the authoring vocabulary (`__init__.py`), the bpy-free maths and JSON writers (`core.py`), the Blender backend (`scene_bpy.py`) and the recording backend (`scene_null.py`) |
| `bmedit/` | Blender (`colour.py`: python3) | edit GLBs and make props: `load(id)` from `build/inputs/<id>.glb`, `paint` / `recolor` / `replace_colour` by face, `box` / `cylinder` / `cone` / `sphere`, `join`, `turn`, `scatter`, `export(id)` to `build/assets/<id>.glb`; smart props (moving parts the engine animates) with `part()`, `anchor()` and `export(..., smart=)` — the vocabulary the web Creator's `blender` tool runs on the Asset Forger (`game/agent-docs/blender.md`) |
| `review_asset.py` | Blender | two three-quarter renders per GLB and a contact sheet: the review for props and edited assets |
| `example_level.py` | either | a complete hut-and-courtyard level using every helper; the tests' fixture |
| `audit.py` | Blender | ray-cast audit of the COLLIDERS: floor continuity, door and route clearance, sealed envelopes, z-fighting candidates |
| `review.py` | Blender | deterministic review renders (overview, every door, every stair, every room) and a contact sheet; `--shot 'FROM -> TO'` aims a frame anywhere, `--only` renders just those, `--lighting game` swaps the review fill for the engine's interior preset and the level's own lamps, `--engine cycles` renders without an OpenGL context |
| `sync_world.py` | python3 | carries the doors, spawn and `terrain.shape: 'none'` into `src/work/world.json` |
| `tests/` | python3 | `python3 -m unittest discover -s tests` — no Blender needed; `cli`'s `pnpm test` runs it |

`bmedit`'s `load(id)` and `review_asset.py` use Blender's glTF importer, which refuses
`EXT_meshopt_compression` and `KHR_texture_basisu`. For an asset the `optimizing-assets` skill has
compressed, put the original it recorded in `build/inputs/`, and run its preset again on the export.

`review.py` and `audit.py` are the skill's **inner loop**: with the build they answer every
geometric and (under `--lighting game`) every lighting question about a level for a few seconds
and no network, which is what lets the engine handoff — `bitmagic assets add`, `sync_world.py`,
`bitmagic verify`, `bitmagic judge` — happen once per design pass instead of once per edit.

The JSON contract is owned by the engine (`game/src/engine/meshlevel/MeshLevelSchema.ts`,
documented in `game/agent-docs/mesh-level.md`); `core.py` writes exactly that shape, and the
engine's validator is the arbiter when the two disagree. The intended end state is a
`bitmagic level build` command wrapping these once a second game has been through them.
