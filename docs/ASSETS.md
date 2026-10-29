# Assets: what is in git, and what stays local

The runtime set (every model, texture and data file the game loads) is in the repository, stored with Git LFS
(decided 2026-10-23, so that anyone can update models through an ordinary pull request).

| Tier | Size | Where | What |
|---|---|---|---|
| **Code and records** | ~80 MB | git | Code, tools, block records, `src/work/` (world, levels, hotel templates), `public/` (foliage) |
| **Runtime set** | 1,345 files, 1.1 GiB | Git LFS, `runtime-assets/` → copied into `build/` | Every file the game loads from `build/`: optimized GLBs, collision, routes, venue lists, PBR strips, Sphere media |
| **Release snapshot** | ~515 MiB download | GitHub release asset (optional) | The same runtime set as one `.tar.gz`, for a download without git |
| **Source files** | ~10 GiB | maintainers' machines (pack planned: `tool-source-pack`) | Original (unoptimized) GLBs, Blender scenes, OSM extracts, intermediates the builders read |
| **Never published** | – | local only | Third-party reference photos, plans and screenshots; review renders; film recordings; probe output |

## Getting the runtime set

```bash
git lfs install                                  # once per machine, before cloning
pnpm install                                     # copies runtime-assets/ into build/ and adds the git hooks
node tools/release/fetch-assets.mjs --verify     # is build/ complete and current?
node tools/release/fetch-assets.mjs --pack       # or: download the release snapshot instead of using LFS
```

The game reads `build/`, which git ignores, so builders can write intermediates there freely. `pnpm install` runs
`fetch-assets.mjs --auto`, which copies only the files that differ from `tools/release/asset-pack.json` (SHA-256
digests); on APFS and btrfs the copies are clones and take no extra space. It also appends itself to the clone's
`post-merge` and `post-checkout` git hooks (next to Git LFS's own lines), so `build/` follows every `git pull` and
branch switch. A file you rebuilt in `build/` and have not staged yet is kept, never overwritten
(`build/.runtime-sync.json` remembers what was copied). If `runtime-assets/` holds LFS pointer files instead of data, it says so: run
`git lfs pull`. It refuses to copy into a full working checkout (one with `build/optimized/manifest.json`), because the
runtime set stores optimized GLBs at the original paths and would overwrite the originals the Blender pipelines patch.

## Updating the runtime set

1. Change the geometry through its builder (never hand-edit an exported GLB); the result lands in `build/`.
2. Re-optimize (`AGENTS.md`, "Runtime GLBs") and bump the folder's `version.json` revision.
3. The optimizer's install step (`tools/optimize/install-optimized.mjs`) then runs
   `python3 tools/release/asset-pack.py stage` for you; after any other runtime change (collision, routes, venue lists)
   run `pnpm assets`. It lists the set again and mirrors it into `runtime-assets/`: new and changed files are copied,
   files that left the set are deleted (it refuses to delete more than a tenth of the set without `--force`). It also
   refuses while anything is missing (a stale bake included) or a model is not optimized
   (`python3 tools/optimize/check-runtime-glbs.py --help`).
4. `git add -A runtime-assets tools/release/asset-pack.json`, commit, and open the pull request from your fork.
   A maintainer uploads the change to the CDN (`node tools/release/cdn-upload.mjs`) before the next publish.

Every LFS version is kept, so stage after real changes only; re-optimizing an unchanged GLB writes identical bytes and
adds nothing.

## The published game: the CDN copy

A published Bitmagic game is one file in object storage, with nothing beside it to fetch. So the runtime set also
lives on the Bitmagic CDN, where forged assets live (uploaded 2026-10-24 under this game's id, `worlds/v3/<gameId>/`).
`src/work/RuntimeAssets.ts` picks the source: `/build/...` and `/foliage/...` on the dev server, the CDN copy in a
published game. `src/work/runtime-cdn.json` maps each request path to its CDN URL.

```bash
node tools/release/cdn-upload.mjs --dry-run   # what is new or changed since the last upload
node tools/release/cdn-upload.mjs             # upload it and update src/work/runtime-cdn.json (maintainers)
SMOKE_CDN=1 node tools/release/smoke-clone.mjs   # the game loading everything from the CDN (?assets=cdn)
```

Uploads cannot be deleted. Each file is named by its content hash, so a changed file is uploaded once more under a new
name and an unchanged one is never sent twice. The CDN stores data files and models brotli-compressed: the 1.1 GiB set takes
much less space and bandwidth than its size on disk.

## How the runtime set is chosen

```bash
python3 tools/release/asset-pack.py list    # refresh tools/release/asset-pack.json from build/
python3 tools/release/asset-pack.py check   # anything a loader asks for that build/ lacks
python3 tools/release/asset-pack.py stage   # list, then mirror into runtime-assets/
python3 tools/release/asset-pack.py build   # list, then .bitmagic/release/las-vegas-strip-assets-<date>.tar.gz
```

`asset-pack.py` lists the runtime set by the same rules the loaders use, and names the loader beside each rule:

- **GLBs:** every runtime GLB the optimizer knows (`build/optimized/manifest.json`), stored as its meshopt-optimized
  copy at the original path. In a clone there is no optimized manifest, so `glbUrl()` (`src/work/OptimizedGlb.ts`)
  returns the original URL and the compressed bytes load from there. A GLB whose source changed after it was optimized
  ships as the current original.
Data files ship as the packed `.bin` that `tools/optimize/pack-data.mjs` writes beside each JSON; the game never parses
JSON at runtime.

- **Landmark and resort venues:** `venues.bin` in `build/strip-landmarks/` and `build/resort-blocks/{cosmo,bellagio,paris}/`.
  Each venue contributes its exterior GLB and exterior collision, plus, unless it is `exteriorOnly`, its interior GLB
  and interior collision.
- **City:** `city.glb`, `detailed.glb`, `city-colliders.bin`, `speed-map.bin` (the road network and the Bellagio
  arrival roads, baked) and the bridge concourses listed in `access/manifest.bin`.
- **City bake:** `build/baked/city-lod.bin`, the distant LODs (`tools/bake/bake-city.mjs`).
- **High-rises:** `exteriors.glb` and every `*-collision.bin`.
- **Hotel modules:** every hotel module GLB the optimizer lists (HotelLayout's set and part names) with its `<module>.mesh-level.bin`.
- **Coaster:** `route.bin`, `coaster-collision.bin`, `coaster.glb` and `train.glb`.
- **Sphere:** `sphere.bin`, `media.bin`, the GLBs and collision, and the media `media.bin` names.
- **Other:** the PBR strips (`sets.bin` and three WebP layers), the jeep, and the `world.json` assets served from `build/`.

The garden foliage is not in the set: `public/foliage/` holds the trees' and grass's optimized copies (5.8 MiB, committed;
`node tools/optimize/foliage-trees.mjs` makes them from the sources in `tools/foliage/models/`, which the Blender
exporters import). `check-runtime-glbs.py` fails when a source changed after its copy was made.

After a new loader or a new runtime folder, add a rule there. Then confirm that a fresh clone plays with nothing
missing:

1. Clone into a clean folder, run `pnpm install`, and start `bitmagic dev` there.
2. Run `node tools/release/smoke-clone.mjs --shots`. It visits:
   - hotel rooms in four towers;
   - three venues;
   - the Sphere and the coaster.

   It fails on any 404, and on any data file the dev server answers with its HTML fallback.

It passed on 2026-10-22 (from the pack) with no failed requests and no page errors.

Publishing a release snapshot (optional):

1. Run `build`.
2. Upload the `.tar.gz` as a GitHub release asset (limit 2 GiB per file).
3. Put its URL in `tools/release/asset-pack.json` `pack.url`, and commit that file.

## How optimized the shipped assets are

`python3 tools/optimize/audit-pack.py` reads every shipped GLB's header. On 2026-10-22, the 628 runtime GLBs in the pack
(845 MiB) were all encoded with the optimizing-assets skill's `level` preset (`tools/optimize/optimize-runtime-glbs.mjs`):

- **Buffers:** meshopt-compressed (`EXT_meshopt_compression`) and quantized (`KHR_mesh_quantization`).
- **Normals:** int8. **UVs:** 16-bit.
- **Positions:** float, as the preset keeps them for level meshes (batching, coplanar seams).
- **Indices:** 98% uint16. 216 primitives still use uint32 although they have fewer than 65,536 vertices (about
  1.7 MiB).
- **Colour maps:** lossy WebP (the `webp-textures` variant, approved 2026-10-07; 42 MiB). Other maps are JPEG
  (56 MiB) or PNG (7 MiB).

Not optimized yet:

- **No KTX2.** Textures upload uncompressed to the GPU. Adding KTX2 needs the `ktx` tool, plus a game-side KTX2 wait,
  because the vendored engine has neither the meshopt decoder nor `expectGltfLoaderSupport`.

## Why Git LFS

- Models change often, and contributors need to send those changes in pull requests. A release asset could only be
  replaced by a maintainer.
- GitHub refuses plain git files over 100 MB. LFS allows 2 GiB per file.
- The cost is the owner's: LFS storage keeps every version of every changed file, and each clone downloads the
  1.1 GiB set from the organisation's LFS bandwidth. The repository's GitHub plan is sized for that.

## What the game does and does not need

The game streams. Every hotel room, corridor and venue is reachable, but nothing is loaded or drawn until the player or
the film camera is close (`HotelStreaming`, `StripLandmarks`, `GeographicPassages`, `SphereVenue`). The runtime set therefore
contains everything, and the browser fetches only what is near. A cold start loads the city, the high-rises, the
landmark exteriors and the PBR strips. Interiors arrive as you approach them.
