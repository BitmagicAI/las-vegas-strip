# Assets: what is in git, what comes in the pack, what stays local

The city's runtime data is too big for git. Three tiers keep a clone small and runnable:

| Tier | Size | Where | What |
|---|---|---|---|
| **Repository** | ~180 MB | git | Code, tools, block records, `src/work/` (world, characters, animations), `public/` (foliage), the vendored engine |
| **Runtime pack** | 492 MiB download, 1.07 GiB unpacked, 1,337 files | release asset → `build/` | Every file the game loads from `build/`: optimized GLBs, collision, routes, venue lists, PBR strips, Sphere media |
| **Source files** | ~10 GiB | maintainers' machines (pack planned: `tool-source-pack`) | Original (unoptimized) GLBs, Blender scenes, OSM extracts, intermediates the builders read |
| **Never published** | – | local only | Third-party reference photos, plans and screenshots; review renders; film recordings; probe output |

## Getting the runtime pack

```bash
node tools/release/fetch-assets.mjs            # download, check sha256, unpack into build/, verify every file
node tools/release/fetch-assets.mjs --verify   # is build/ complete and current?
node tools/release/fetch-assets.mjs --from las-vegas-strip-assets-2026-10-22.tar.gz   # a pack you already have
```

The list of files, with sizes and SHA-256 digests, is committed in `tools/release/asset-pack.json`. Its `pack.url` names
the download. The fetcher leaves files that already match alone, so after a new pack only changed files are rewritten.
It refuses to unpack into a full working checkout (one with `build/optimized/manifest.json`), because the pack stores
optimized GLBs at the original paths and would overwrite the originals the Blender pipelines patch.

## How the pack is made (maintainers)

```bash
python3 tools/release/asset-pack.py list    # refresh tools/release/asset-pack.json from build/
python3 tools/release/asset-pack.py check   # anything a loader asks for that build/ lacks
python3 tools/release/asset-pack.py build   # .bitmagic/release/las-vegas-strip-assets-<date>.tar.gz
```

`asset-pack.py` lists the runtime set by the same rules the loaders use, and names the loader beside each rule:

- **GLBs:** every runtime GLB the optimizer knows (`build/optimized/manifest.json`), stored as its meshopt-optimized
  copy at the original path. In a clone there is no optimized manifest, so `glbUrl()` (`src/work/OptimizedGlb.ts`)
  returns the original URL and the compressed bytes load from there. A GLB whose source changed after it was optimized
  ships as the current original.
- **Landmark and resort venues:** `venues.json` and `version.json` in `build/strip-landmarks/` and
  `build/resort-blocks/{cosmo,bellagio,paris}/`. Each venue contributes its exterior GLB and exterior collision, plus,
  unless it is `exteriorOnly`, its interior GLB and interior collision.
- **City:** `city-version.json`, `city-colliders.json`, `road-network.json` and the bridge concourses listed in
  `access/manifest.json`.
- **High-rises:** `version.json`, `exteriors.glb` and every `*-collision.json`.
- **Hotel modules:** every hotel module GLB the optimizer lists (HotelLayout's set and part names) with its `<module>.mesh-level.json`.
- **Coaster:** `version.json`, `route.json`, `coaster-collision.json`, `coaster.glb` and `train.glb`.
- **Sphere:** `sphere.json`, `version.json`, `media.json`, the GLBs and collision, and the media `media.json` names.
- **Other:** the PBR strips, the jeep, the Bellagio south-arrival roads, and the `world.json` assets served from `build/`.

After a new loader or a new runtime folder, add a rule there. Then confirm that a fresh clone plays with nothing
missing:

1. Fetch the pack into a clean checkout and start `bitmagic dev` there.
2. Run `node tools/release/smoke-clone.mjs --shots`. It visits:
   - hotel rooms in four towers;
   - three venues;
   - the Sphere and the coaster.

   It fails on any 404, and on any data file the dev server answers with its HTML fallback.

It passed on 2026-10-22 with no failed requests and no page errors.

Publishing a new pack:

1. Run `build`.
2. Upload the `.tar.gz` as a GitHub release asset (limit 2 GiB per file).
3. Put its URL in `tools/release/asset-pack.json` `pack.url`.
4. Commit that file.

The pack's file name carries the revision date, and its sha256 is checked before unpacking.

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
- **`public/foliage/tree-*.glb` (34 MiB).** Optimized copies exist only in a full working checkout, so a clone loads
  the originals.
- **The nine characters (about 54 MiB).** They load from Bitmagic's CDN as originals; the encoder cannot read their
  required `BITMAGIC_sparse_correctives` extension.
- **Collision and route data:** 203 MiB of plain-text JSON (`city-colliders.json` is 118 MiB). It is gzipped in the
  pack, but the game downloads and parses the text.

## Why GLBs are not in git

- Git keeps every version forever, and the city's GLBs change almost every day. A year of history would be hundreds of
  gigabytes.
- GitHub refuses files over 100 MB. `city-colliders.json` alone is 118 MiB.
- Git LFS would work, but every contributor pays its bandwidth quota, and forks inherit nothing.

## What the game does and does not need

The game streams. Every hotel room, corridor and venue is reachable, but nothing is loaded or drawn until the player or
the film camera is close (`HotelStreaming`, `StripLandmarks`, `GeographicPassages`, `SphereVenue`). The pack therefore
contains everything, and the browser fetches only what is near. A cold start loads the city, the high-rises, the
landmark exteriors and the PBR strips. Interiors arrive as you approach them.
