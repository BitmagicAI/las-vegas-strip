# Runtime GLB optimization

<!-- generated:start -->
Generated 2026-10-08T01:34:01.696Z by `node tools/optimize/optimize-runtime-glbs.mjs --analyze && ... --summary`. MiB = 1,048,576 bytes.

### Totals by group

| Group | Files | With candidate | Before MiB | After MiB | Change |
|---|---:|---:|---:|---:|---:|
| build/geographic-strip | 2 | 2 | 676.12 | 209.39 | -69% |
| build/strip-landmarks | 20 | 20 | 308.28 | 108.02 | -65% |
| build/resort-blocks/cosmo | 12 | 6 | 30.43 | 13.41 | -56% |
| build/resort-blocks/bellagio | 10 | 5 | 167.37 | 62.79 | -62% |
| build/resort-blocks/paris | 6 | 2 | 102.51 | 35.86 | -65% |
| build/highrises | 1 | 1 | 48.62 | 11.61 | -76% |
| build/south-strip | 2 | 2 | 15.04 | 4.37 | -71% |
| build/sphere | 2 | 2 | 14.63 | 6.02 | -59% |
| build/vehicles | 1 | 1 | 3.63 | 1.14 | -69% |
| build/hotels | 393 | 393 | 461.77 | 297.53 | -36% |
| public/foliage | 3 | 3 | 35.00 | 15.91 | -55% |
| characters | 9 | 9 | 51.40 | 31.48 | -39% |
| build/arrival-reconstruction | 4 | 4 | 0.26 | 0.13 | -51% |
| **all runtime GLBs** | **465** | **450** | **1915.06** | **797.67** | **-58%** |

GPU estimate (encoder, 441 files with an encoder candidate): geometry 1563.48 -> 1056.22 MiB, textures 1767.66 -> 1738.32 MiB. Drawn triangles unchanged in every candidate (checked: all equal).

### Variant: level + WebP colour maps (experiment, needs the A/B)

`--variant=webp-textures` re-encodes base/emissive maps as lossy WebP q90 at their own size and ORM maps as lossless WebP; normal maps and everything else as the level preset. Files: 381 (every level file that has textures). Those files: 623.96 MiB (level) -> 380.01 MiB (variant). All runtime GLBs with the variant where it exists: **1915.06 -> 553.71 MiB**. GPU memory does not change (WebP and PNG both upload as RGBA8).

Lowest colour-map PSNR (original vs WebP, whole map): `hotels/bellagio-corridor.glb` 32.6 dB, `hotels/caesars-corridor.glb` 33.2 dB, `hotels/cosmopolitan-corridor.glb` 33.5 dB, `hotels/fontainebleau-corridor.glb` 33.8 dB, `hotels/resorts-world-corridor.glb` 34.1 dB, `hotels/flamingo-corridor.glb` 34.2 dB, `hotels/aria-corridor.glb` 34.3 dB, `hotels/circus-circus-corridor.glb` 34.4 dB. Median file minimum: 41.3 dB.

Loaded at boot (local dev view): 47 files, 1298.45 -> 434.70 MiB. Streamed later: 418 files, 616.60 -> 362.97 MiB.

### Vertex layouts (attribute: componentType [norm] x itemSize; counts are primitives)

**build/geographic-strip**

- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`

**build/strip-landmarks**

- 20 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`

**build/resort-blocks/cosmo**

- 6 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`
- 6 file(s): before `NORMAL: float32 x3, POSITION: float32 x3`
  after `(original kept)`

**build/resort-blocks/bellagio**

- 5 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `(original kept)`
- 3 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
- 2 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`

**build/resort-blocks/paris**

- 4 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `(original kept)`
- 2 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`

**build/highrises**

- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: uint16 norm x2`

**build/south-strip**

- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: uint16 norm x2`
- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3`
  after `NORMAL: int8 norm x3, POSITION: float32 x3`

**build/sphere**

- 2 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`

**build/vehicles**

- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`

**build/hotels**

- 244 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
- 98 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_1: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_1: float32 x2`
- 45 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2`
- 3 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_1: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2, TEXCOORD_1: float32 x2`
- 2 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_1: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_1: uint16 norm x2`
- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_1: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_0: uint16 norm x2, TEXCOORD_1: float32 x2, TEXCOORD_1: uint16 norm x2`

**public/foliage**

- 2 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, TEXCOORD_1: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: uint16 norm x2, TEXCOORD_1: float32 x2, TEXCOORD_1: uint16 norm x2`
- 1 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: uint16 norm x2`

**characters**

- 9 file(s): before `COLOR_0: float32 x3, COLOR_0: float32 x4, JOINTS_0: uint16 x4, NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, WEIGHTS_0: float32 x4, _LID_WALL_ROOT: float32 x3, _LID_WALL_WEIGHT: float32 x1`
  after `COLOR_0: float32 x3, COLOR_0: float32 x4, JOINTS_0: uint16 x4, NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2, WEIGHTS_0: float32 x4, _LID_WALL_ROOT: float32 x3, _LID_WALL_WEIGHT: float32 x1`

**build/arrival-reconstruction**

- 4 file(s): before `NORMAL: float32 x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`
  after `NORMAL: int8 norm x3, POSITION: float32 x3, TEXCOORD_0: float32 x2`

Primitive counts per format, largest files:

- `build/geographic-strip/city.glb`
  - before: POSITION: float32 x3 (945); NORMAL: float32 x3 (945); TEXCOORD_0: float32 x2 (346)
  - after: POSITION: float32 x3 (945); NORMAL: int8 norm x3 (945); TEXCOORD_0: float32 x2 (346)
- `build/geographic-strip/detailed.glb`
  - before: POSITION: float32 x3 (1516); NORMAL: float32 x3 (1516); TEXCOORD_0: float32 x2 (1516)
  - after: POSITION: float32 x3 (1180); TEXCOORD_0: float32 x2 (949); NORMAL: int8 norm x3 (1180); TEXCOORD_0: uint16 norm x2 (231)
- `build/strip-landmarks/linq-exterior.glb`
  - before: POSITION: float32 x3 (231); NORMAL: float32 x3 (231); TEXCOORD_0: float32 x2 (55)
  - after: POSITION: float32 x3 (231); NORMAL: int8 norm x3 (231); TEXCOORD_0: uint16 norm x2 (47); TEXCOORD_0: float32 x2 (8)
- `build/strip-landmarks/venetian-exterior.glb`
  - before: POSITION: float32 x3 (35); NORMAL: float32 x3 (35); TEXCOORD_0: float32 x2 (10)
  - after: POSITION: float32 x3 (35); NORMAL: int8 norm x3 (35); TEXCOORD_0: uint16 norm x2 (1); TEXCOORD_0: float32 x2 (9)
- `build/strip-landmarks/palazzo-interior.glb`
  - before: POSITION: float32 x3 (31); NORMAL: float32 x3 (31); TEXCOORD_0: float32 x2 (14)
  - after: POSITION: float32 x3 (31); NORMAL: int8 norm x3 (31); TEXCOORD_0: uint16 norm x2 (6); TEXCOORD_0: float32 x2 (8)
- `build/strip-landmarks/polo-exterior.glb`
  - before: POSITION: float32 x3 (32); NORMAL: float32 x3 (32); TEXCOORD_0: float32 x2 (10)
  - after: POSITION: float32 x3 (32); NORMAL: int8 norm x3 (32); TEXCOORD_0: uint16 norm x2 (4); TEXCOORD_0: float32 x2 (6)
- `build/resort-blocks/bellagio/bellagioBlock-exterior.glb`
  - before: POSITION: float32 x3 (305); NORMAL: float32 x3 (305); TEXCOORD_0: float32 x2 (87)
  - after: POSITION: float32 x3 (305); NORMAL: int8 norm x3 (305); TEXCOORD_0: uint16 norm x2 (34); TEXCOORD_0: float32 x2 (53)
- `build/resort-blocks/paris/parisBlock-exterior.glb`
  - before: POSITION: float32 x3 (422); NORMAL: float32 x3 (422); TEXCOORD_0: float32 x2 (170)
  - after: POSITION: float32 x3 (422); NORMAL: int8 norm x3 (422); TEXCOORD_0: uint16 norm x2 (34); TEXCOORD_0: float32 x2 (136)
- `build/highrises/exteriors.glb`
  - before: POSITION: float32 x3 (472); NORMAL: float32 x3 (472); TEXCOORD_0: float32 x2 (62)
  - after: POSITION: float32 x3 (472); NORMAL: int8 norm x3 (472); TEXCOORD_0: uint16 norm x2 (62)

### Encoder notes (distinct, numbers folded; count = files)

- 548 x TEXCOORD_# leaves #-# (tiling UVs) on some meshes, so those stay float. Harmless: it is what glTF-Transform's "Skipping" line meant
- 3 x a texture with transparency was written as WebP: JPEG has no alpha

### Per file

Glossy = meshes with a material of metalness factor > 0.5 or roughness factor < 0.2 (glTF defaults count: metalness 1). Merge = the game-side batch merge check (see Risks); "-" = no merge consumer. GPU = the encoder's estimate (textures RGBA8 + mips; geometry = accessor bytes, so int8 normals count 3 bytes where the GPU stores 4).

| File | When | Preset (+overrides) | Before MiB | After MiB | Change | WebP-tex variant MiB (min PSNR) | Drawn triangles | GPU tex MiB | GPU geom MiB | Validator (after) | Glossy | Merge | Result |
|---|---|---|---:|---:|---:|---|---:|---|---|---|---|---|---|
| `geographic-strip/city.glb` | boot (localhost) | level | 343.47 | 107.88 | -69% |  | 6,179,452 | 0.00 -> 0.00 | 342.75 -> 247.17 | 0 errors (0 new), 0 warnings | 48/945 | ok | ok |
| `geographic-strip/detailed.glb` | boot (localhost) | level | 332.65 | 101.51 | -69% | 75.84 (35.1 dB) | 4,646,533 | 177.33 -> 172.00 | 293.05 -> 144.49 | 0 errors (0 new), 14 warnings; MESH_PRIMITIVE_GENERATED_TANGENT_SPACE /meshes/77/primitive | 428/1516 | CityBatches MIX (front: uv, double: uv) | ok; 336 meshes no node references (1,761,239 triangles three never loads) pruned; drawn triangles unchanged |
| `strip-landmarks/linq-exterior.glb` | boot (localhost) | level | 37.46 | 13.11 | -65% | 12.31 (41 dB) | 747,202 | 5.33 -> 5.33 | 36.40 -> 25.28 | 0 errors (0 new), 0 warnings | 99/231 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/linq-interior.glb` | streamed on approach | level | 4.60 | 2.56 | -44% | 1.46 (40.7 dB) | 101,164 | 8.00 -> 8.00 | 3.32 -> 2.38 | 0 errors (0 new), 0 warnings | 4/38 | - | ok |
| `strip-landmarks/vanderpump-exterior.glb` | boot (localhost) | level | 15.64 | 5.59 | -64% | 4.18 (41 dB) | 237,790 | 9.33 -> 9.33 | 14.04 -> 9.61 | 0 errors (0 new), 0 warnings | 13/40 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/vanderpump-interior.glb` | streamed on approach | level | 8.38 | 3.38 | -60% | 2.28 (40.7 dB) | 105,784 | 8.00 -> 8.00 | 7.11 -> 4.79 | 0 errors (0 new), 0 warnings | 5/20 | - | ok |
| `strip-landmarks/fashion-exterior.glb` | boot (localhost) | level | 1.67 | 1.05 | -37% | 0.44 (41 dB) | 26,427 | 4.00 -> 4.00 | 0.98 -> 0.68 | 0 errors (0 new), 0 warnings | 6/23 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/fashion-interior.glb` | streamed on approach | level | 7.81 | 4.04 | -48% | 2.83 (40.7 dB) | 226,700 | 8.00 -> 8.00 | 6.40 -> 4.88 | 0 errors (0 new), 0 warnings | 8/61 | - | ok |
| `strip-landmarks/venetian-exterior.glb` | boot (localhost) | level | 36.97 | 11.69 | -68% | 10.07 (40.7 dB) | 455,489 | 10.67 -> 10.67 | 35.13 -> 23.85 | 0 errors (0 new), 0 warnings | 15/35 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/venetian-interior.glb` | streamed on approach | level | 10.47 | 5.55 | -47% | 2.48 (40.1 dB) | 129,514 | 14.66 -> 14.66 | 7.01 -> 4.79 | 0 errors (0 new), 0 warnings | 7/24 | - | ok |
| `strip-landmarks/arena-exterior.glb` | boot (localhost) | level | 3.78 | 2.20 | -42% | 0.99 (40.9 dB) | 41,174 | 8.00 -> 8.00 | 2.44 -> 1.70 | 0 errors (0 new), 0 warnings | 10/20 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/arena-interior.glb` | streamed on approach | level | 12.98 | 5.25 | -60% | 4.44 (41 dB) | 322,032 | 5.33 -> 5.33 | 12.03 -> 9.02 | 0 errors (0 new), 0 warnings | 3/74 | - | ok |
| `strip-landmarks/park-exterior.glb` | boot (localhost) | level | 2.77 | 1.29 | -54% | 0.68 (41 dB) | 38,301 | 4.00 -> 4.00 | 2.09 -> 1.38 | 0 errors (0 new), 0 warnings | 8/23 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/park-interior.glb` | streamed on approach | level | 14.13 | 5.49 | -61% | 4.19 (40.7 dB) | 237,681 | 9.33 -> 9.33 | 12.67 -> 8.79 | 0 errors (0 new), 0 warnings | 9/37 | - | ok |
| `strip-landmarks/palazzo-exterior.glb` | boot (localhost) | level | 18.03 | 5.90 | -67% | 4.89 (41 dB) | 221,768 | 6.67 -> 6.67 | 16.90 -> 11.41 | 0 errors (0 new), 0 warnings | 10/25 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/palazzo-interior.glb` | streamed on approach | level | 35.37 | 10.57 | -70% | 9.28 (40.7 dB) | 468,986 | 9.33 -> 9.33 | 33.87 -> 23.00 | 0 errors (0 new), 0 warnings | 8/31 | - | ok |
| `strip-landmarks/ti-exterior.glb` | boot (localhost) | level | 13.32 | 4.68 | -65% | 3.68 (41 dB) | 167,253 | 6.67 -> 6.67 | 12.19 -> 8.25 | 0 errors (0 new), 0 warnings | 11/31 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/ti-interior.glb` | streamed on approach | level | 8.09 | 3.04 | -62% | 2.25 (40.7 dB) | 127,041 | 6.67 -> 6.67 | 7.20 -> 4.98 | 0 errors (0 new), 0 warnings | 7/23 | - | ok |
| `strip-landmarks/harrahs-exterior.glb` | boot (localhost) | level | 3.05 | 1.63 | -47% | 0.82 (41 dB) | 46,587 | 5.33 -> 5.33 | 2.14 -> 1.44 | 0 errors (0 new), 0 warnings | 9/23 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/harrahs-interior.glb` | streamed on approach | level | 8.34 | 3.38 | -59% | 2.82 (40.7 dB) | 196,104 | 5.33 -> 5.33 | 7.65 -> 5.60 | 0 errors (0 new), 0 warnings | 13/32 | - | ok |
| `strip-landmarks/polo-exterior.glb` | boot (localhost) | level | 63.20 | 16.08 | -75% | 15.08 (41 dB) | 874,686 | 6.67 -> 6.67 | 62.07 -> 42.41 | 0 errors (0 new), 0 warnings | 10/32 | CityBatches MIX (double: uv) | ok |
| `strip-landmarks/polo-interior.glb` | streamed on approach | level | 2.23 | 1.55 | -31% | 0.46 (40.7 dB) | 28,840 | 8.00 -> 8.00 | 1.00 -> 0.69 | 0 errors (0 new), 0 warnings | 3/17 | - | ok |
| `resort-blocks/cosmo/cosmo-exterior.glb` | boot (localhost) | level | 13.53 | 4.11 | -70% | 3.31 (41 dB) | 232,380 | 5.33 -> 5.33 | 12.60 -> 8.66 | 0 errors (0 new), 0 warnings | 28/57 | CityBatches MIX (double: uv) | ok |
| `resort-blocks/cosmo/cosmo-interior.glb` | streamed on approach | level | 0.00 | 0.00 | -0% |  | 12 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/cosmo/cosmoL1-exterior.glb` | boot (localhost) | level | 0.00 | 0.00 | -0% |  | 12 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/cosmo/cosmoL1-interior.glb` | streamed on approach | level | 3.80 | 1.96 | -48% | 1.07 (40.7 dB) | 93,924 | 6.67 -> 6.67 | 2.76 -> 1.98 | 0 errors (0 new), 0 warnings | 5/16 | - | ok |
| `resort-blocks/cosmo/cosmoL2-exterior.glb` | boot (localhost) | level | 0.00 | 0.00 | -0% |  | 12 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/cosmo/cosmoL2-interior.glb` | streamed on approach | level | 3.42 | 1.93 | -44% | 1.11 (40.7 dB) | 93,020 | 5.33 -> 5.33 | 2.49 -> 1.83 | 0 errors (0 new), 0 warnings | 2/19 | - | ok |
| `resort-blocks/cosmo/cosmoL3-exterior.glb` | boot (localhost) | level | 0.00 | 0.00 | -0% |  | 12 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/cosmo/cosmoL3-interior.glb` | streamed on approach | level | 2.76 | 1.47 | -47% | 0.87 (40.7 dB) | 72,544 | 4.00 -> 4.00 | 2.07 -> 1.50 | 0 errors (0 new), 0 warnings | 3/18 | - | ok |
| `resort-blocks/cosmo/cosmoL4-exterior.glb` | boot (localhost) | level | 0.00 | 0.00 | -0% |  | 12 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/cosmo/cosmoL4-interior.glb` | streamed on approach | level | 3.04 | 1.85 | -39% | 0.84 (40.7 dB) | 58,806 | 6.67 -> 6.67 | 1.89 -> 1.36 | 0 errors (0 new), 0 warnings | 6/31 | - | ok |
| `resort-blocks/cosmo/cosmoL14-exterior.glb` | boot (localhost) | level | 0.00 | 0.00 | -0% |  | 12 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/cosmo/cosmoL14-interior.glb` | streamed on approach | level | 3.86 | 2.07 | -46% | 1.06 (40.7 dB) | 74,593 | 6.67 -> 6.67 | 2.70 -> 1.89 | 0 errors (0 new), 0 warnings | 7/27 | - | ok |
| `resort-blocks/bellagio/bellagioBlock-exterior.glb` | boot (localhost) | level | 156.29 | 57.36 | -63% | 54.65 (40.7 dB) | 2,380,526 | 20.00 -> 20.00 | 152.94 -> 113.50 | 0 errors (0 new), 1 warnings; MESH_PRIMITIVE_GENERATED_TANGENT_SPACE /meshes/138/primitive | 67/305 | CityBatches MIX (double: uv) | ok |
| `resort-blocks/bellagio/bellagioBlock-interior.glb` | streamed on approach | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/bellagio/bellagioLobby-exterior.glb` | boot (localhost) | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/bellagio/bellagioLobby-interior.glb` | streamed on approach | level | 3.43 | 1.81 | -47% | 0.80 (40.7 dB) | 35,614 | 6.67 -> 6.67 | 2.29 -> 1.51 | 0 errors (0 new), 0 warnings | 4/17 | - | ok |
| `resort-blocks/bellagio/bellagioGarden-exterior.glb` | boot (localhost) | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/bellagio/bellagioGarden-interior.glb` | streamed on approach | level | 1.68 | 0.66 | -61% | 0.45 (40.7 dB) | 24,471 | 1.33 -> 1.33 | 1.44 -> 0.96 | 0 errors (0 new), 0 warnings | 2/8 | - | ok |
| `resort-blocks/bellagio/bellagioConservatory-exterior.glb` | boot (localhost) | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/bellagio/bellagioConservatory-interior.glb` | streamed on approach | level | 0.77 | 0.41 | -47% | 0.21 (41.2 dB) | 7,570 | 1.33 -> 1.33 | 0.54 -> 0.36 | 0 errors (0 new), 0 warnings | 2/10 | - | ok |
| `resort-blocks/bellagio/bellagioPromenade-exterior.glb` | boot (localhost) | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/bellagio/bellagioPromenade-interior.glb` | streamed on approach | level | 4.10 | 1.46 | -64% | 1.05 (40.7 dB) | 49,816 | 2.67 -> 2.67 | 3.62 -> 2.46 | 0 errors (0 new), 0 warnings | 2/8 | - | ok |
| `resort-blocks/paris/parisBlock-exterior.glb` | boot (localhost) | level | 99.58 | 33.67 | -66% | 31.69 (40.7 dB) | 1,465,030 | 13.33 -> 13.33 | 97.05 -> 67.49 | 0 errors (0 new), 0 warnings | 14/422 | CityBatches MIX (double: uv) | ok |
| `resort-blocks/paris/parisBlock-interior.glb` | streamed on approach | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/paris/parisDining-exterior.glb` | boot (localhost) | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/paris/parisDining-interior.glb` | streamed on approach | level | 2.05 | 1.31 | -36% | 0.51 (40.7 dB) | 25,632 | 5.33 -> 5.33 | 1.13 -> 0.80 | 0 errors (0 new), 0 warnings | 10/43 | - | ok |
| `resort-blocks/paris/parisPool-exterior.glb` | boot (localhost) | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `resort-blocks/paris/parisPool-interior.glb` | streamed on approach | level | 0.22 | 0.22 | -0% | 0.02 (41.5 dB) | 12 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | no candidate: smaller: the output is not smaller than the input: keep the original -> the original ships |
| `highrises/exteriors.glb` | boot (localhost) | level | 48.62 | 11.61 | -76% |  | 747,518 | 0.00 -> 0.00 | 48.25 -> 27.32 | 0 errors (0 new), 0 warnings | 85/470 | CityBatches MIX (double: uv) | ok |
| `south-strip/coaster.glb` | boot (localhost) | level | 14.98 | 4.35 | -71% |  | 199,244 | 0.00 -> 0.00 | 14.97 -> 10.08 | 0 errors (0 new), 0 warnings | 1/13 | - | ok |
| `south-strip/train.glb` | boot (localhost) | code-driven | 0.06 | 0.02 | -58% |  | 1,124 | 0.00 -> 0.00 | 0.05 -> 0.04 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `sphere/exterior.glb` | boot (localhost) | level | 1.76 | 0.97 | -45% | 0.48 (40.2 dB) | 39,040 | 12.00 -> 12.00 | 1.13 -> 0.82 | 0 errors (0 new), 0 warnings | 2/8 | - | ok |
| `sphere/interior.glb` | streamed on approach | level | 12.87 | 5.05 | -61% | 4.71 (40.2 dB) | 197,506 | 12.00 -> 12.00 | 12.42 -> 9.01 | 0 errors (0 new), 0 warnings | 2/14 | - | ok |
| `vehicles/afterlight-jeep.glb` | boot | code-driven | 3.63 | 1.14 | -69% |  | 58,552 | 0.00 -> 0.00 | 3.31 -> 1.26 | 0 errors (0 new), 0 warnings | 67/403 | JEEP MERGE: 2 material group(s) mix types | ok |
| `hotels/allure-1-lobby.glb` | streamed (hotel visit) | level | 3.24 | 1.51 | -53% | 1.04 (40.9 dB) | 69,799 | 4.00 -> 4.00 | 2.74 -> 2.16 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/allure-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (40.9 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/allure-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (40.9 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/allure-corridor.glb` | streamed (hotel visit) | level | 1.42 | 1.36 | -4% | 0.25 (36.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/allure-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/allure-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (40.9 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/allure-room.glb` | streamed (hotel visit) | level | 1.61 | 1.17 | -27% | 0.37 (40.9 dB) | 20,752 | 5.67 -> 5.67 | 0.71 -> 0.55 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/allure-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (40.9 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/aria-cap.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.8 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/aria-closure.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.8 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/aria-corridor.glb` | streamed (hotel visit) | level | 1.58 | 1.53 | -3% | 0.22 (34.3 dB) | 1,848 | 7.00 -> 7.00 | 0.09 -> 0.07 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/aria-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/aria-entry.glb` | streamed (hotel shell) | level | 0.60 | 0.58 | -4% | 0.03 (40.8 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/aria-room.glb` | streamed (hotel visit) | level | 1.65 | 1.23 | -26% | 0.32 (40.8 dB) | 20,344 | 5.67 -> 5.67 | 0.70 -> 0.54 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/aria-stair.glb` | streamed (hotel shell) | level | 0.31 | 0.29 | -8% | 0.02 (41.8 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/bellagio-cap.glb` | streamed (hotel shell) | level | 0.11 | 0.03 | -73% |  | 2,308 | 0.00 -> 0.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/bellagio-closure.glb` | streamed (hotel shell) | level | 0.00 | 0.00 | -26% |  | 60 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/bellagio-corridor-end.glb` | streamed (hotel visit) | level | 0.16 | 0.10 | -38% | 0.10 | 3,612 | 1.33 -> 1.33 | 0.13 -> 0.10 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/bellagio-corridor.glb` | streamed (hotel visit) | level | 5.36 | 5.05 | -6% | 1.42 (32.6 dB) | 14,576 | 16.00 -> 16.00 | 0.53 -> 0.42 | 0 errors (0 new), 0 warnings | 1/8 | - | ok |
| `hotels/bellagio-door.glb` | streamed (hotel visit) | level | 0.13 | 0.05 | -60% |  | 2,284 | 0.00 -> 0.00 | 0.13 -> 0.10 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/bellagio-entry.glb` | streamed (hotel shell) | level | 17.67 | 17.54 | -1% | 2.98 (40.8 dB) | 3,804 | 64.00 -> 64.00 | 0.21 -> 0.16 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/bellagio-room.glb` | streamed (hotel visit) | level | 7.17 | 5.47 | -24% | 1.36 (40.5 dB) | 76,230 | 25.33 -> 25.33 | 2.65 -> 1.99 | 0 errors (0 new), 0 warnings | 4/19 | - | ok |
| `hotels/bellagio-spa-1-lobby.glb` | streamed (hotel visit) | level | 3.49 | 1.57 | -55% | 1.10 (41.4 dB) | 74,151 | 4.00 -> 4.00 | 2.99 -> 2.35 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/bellagio-spa-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.2 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/bellagio-spa-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.2 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/bellagio-spa-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.25 (38.6 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/bellagio-spa-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/bellagio-spa-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/bellagio-spa-room.glb` | streamed (hotel visit) | level | 1.54 | 1.15 | -25% | 0.35 (41.4 dB) | 19,520 | 5.67 -> 5.67 | 0.65 -> 0.50 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/bellagio-spa-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.2 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/bellagio-stair.glb` | streamed (hotel shell) | level | 0.05 | 0.02 | -56% |  | 768 | 0.00 -> 0.00 | 0.05 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/caesars-cap.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/caesars-closure.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/caesars-corridor.glb` | streamed (hotel visit) | level | 1.69 | 1.62 | -4% | 0.28 (33.2 dB) | 2,472 | 7.00 -> 7.00 | 0.12 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/caesars-door.glb` | streamed (hotel visit) | level | 0.09 | 0.04 | -56% |  | 1,500 | 0.00 -> 0.00 | 0.08 -> 0.06 | 0 errors (0 new), 0 warnings | 2/4 | - | ok |
| `hotels/caesars-entry.glb` | streamed (hotel shell) | level | 0.64 | 0.61 | -3% | 0.03 (40.8 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/caesars-room.glb` | streamed (hotel visit) | level | 1.76 | 1.35 | -23% | 0.37 (40.8 dB) | 20,924 | 5.67 -> 5.67 | 0.69 -> 0.53 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/caesars-stair.glb` | streamed (hotel shell) | level | 0.31 | 0.29 | -8% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/circus-circus-1-lobby.glb` | streamed (hotel visit) | level | 5.14 | 2.12 | -59% | 1.65 (41.4 dB) | 115,552 | 4.00 -> 4.00 | 4.63 -> 3.64 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/circus-circus-2-lobby.glb` | streamed (hotel visit) | level | 6.36 | 2.55 | -60% | 2.08 (41.4 dB) | 150,533 | 4.00 -> 4.00 | 5.86 -> 4.60 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/circus-circus-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.8 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/circus-circus-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.8 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/circus-circus-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.26 (34.4 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/circus-circus-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/circus-circus-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/circus-circus-room.glb` | streamed (hotel visit) | level | 1.65 | 1.24 | -25% | 0.39 (34.4 dB) | 20,000 | 7.00 -> 7.00 | 0.67 -> 0.52 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/circus-circus-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.8 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/cosmopolitan-cap.glb` | streamed (hotel shell) | level | 0.25 | 0.25 | -0% | 0.01 (43 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/cosmopolitan-closure.glb` | streamed (hotel shell) | level | 0.25 | 0.24 | -0% | 0.01 (43 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/cosmopolitan-corridor.glb` | streamed (hotel visit) | level | 1.62 | 1.55 | -4% | 0.27 (33.5 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/cosmopolitan-door.glb` | streamed (hotel visit) | level | 0.09 | 0.04 | -56% |  | 1,500 | 0.00 -> 0.00 | 0.08 -> 0.06 | 0 errors (0 new), 0 warnings | 2/4 | - | ok |
| `hotels/cosmopolitan-entry.glb` | streamed (hotel shell) | level | 0.60 | 0.58 | -3% | 0.03 (40.8 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/cosmopolitan-room.glb` | streamed (hotel visit) | level | 1.74 | 1.31 | -24% | 0.34 (40.8 dB) | 21,716 | 5.67 -> 5.67 | 0.71 -> 0.55 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/cosmopolitan-stair.glb` | streamed (hotel shell) | level | 0.29 | 0.26 | -9% | 0.03 (43 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/elara-1-lobby.glb` | streamed (hotel visit) | level | 6.09 | 2.50 | -59% | 2.02 (41.4 dB) | 145,553 | 4.00 -> 4.00 | 5.59 -> 4.39 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/elara-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.2 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/elara-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.2 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/elara-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.26 (35.9 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/elara-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/elara-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/elara-room.glb` | streamed (hotel visit) | level | 1.70 | 1.21 | -29% | 0.41 (41.4 dB) | 25,144 | 5.67 -> 5.67 | 0.81 -> 0.62 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/elara-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.2 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/encore-1-lobby.glb` | streamed (hotel visit) | level | 6.36 | 2.63 | -59% | 2.16 (41 dB) | 153,457 | 4.00 -> 4.00 | 5.86 -> 4.59 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/encore-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/encore-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/encore-corridor.glb` | streamed (hotel visit) | level | 1.30 | 1.24 | -5% | 0.25 (37.3 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/encore-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/encore-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/encore-room.glb` | streamed (hotel visit) | level | 1.57 | 1.16 | -26% | 0.36 (41 dB) | 20,660 | 5.67 -> 5.67 | 0.68 -> 0.53 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/encore-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/flamingo-cap.glb` | streamed (hotel shell) | level | 0.21 | 0.21 | -0% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/flamingo-closure.glb` | streamed (hotel shell) | level | 0.21 | 0.21 | -1% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/flamingo-corridor.glb` | streamed (hotel visit) | level | 1.59 | 1.53 | -4% | 0.26 (34.2 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/flamingo-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/flamingo-entry.glb` | streamed (hotel shell) | level | 0.55 | 0.53 | -4% | 0.03 (41.3 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/flamingo-room.glb` | streamed (hotel visit) | level | 1.61 | 1.25 | -22% | 0.41 (35.1 dB) | 16,988 | 7.00 -> 7.00 | 0.59 -> 0.46 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/flamingo-stair.glb` | streamed (hotel shell) | level | 0.25 | 0.23 | -10% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/fontainebleau-1-lobby.glb` | streamed (hotel visit) | level | 6.63 | 2.56 | -61% | 2.09 (41.4 dB) | 149,085 | 4.00 -> 4.00 | 6.13 -> 4.88 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/fontainebleau-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.8 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/fontainebleau-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.8 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/fontainebleau-corridor.glb` | streamed (hotel visit) | level | 1.42 | 1.36 | -4% | 0.27 (33.8 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/fontainebleau-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/fontainebleau-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/fontainebleau-room.glb` | streamed (hotel visit) | level | 1.61 | 1.17 | -27% | 0.37 (41.4 dB) | 20,640 | 5.67 -> 5.67 | 0.72 -> 0.56 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/fontainebleau-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.8 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/grand-chateau-1-lobby.glb` | streamed (hotel visit) | level | 6.32 | 2.55 | -60% | 2.07 (41.3 dB) | 150,045 | 4.00 -> 4.00 | 5.82 -> 4.56 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/grand-chateau-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/grand-chateau-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/grand-chateau-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.26 (38.6 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/grand-chateau-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/grand-chateau-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.3 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/grand-chateau-room.glb` | streamed (hotel visit) | level | 1.76 | 1.23 | -30% | 0.43 (41.3 dB) | 27,244 | 5.67 -> 5.67 | 0.86 -> 0.67 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/grand-chateau-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/harrahs-1-lobby.glb` | streamed (hotel visit) | level | 3.31 | 1.53 | -54% | 1.06 (41.4 dB) | 71,215 | 4.00 -> 4.00 | 2.81 -> 2.21 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/harrahs-2-lobby.glb` | streamed (hotel visit) | level | 4.66 | 2.00 | -57% | 1.53 (41.4 dB) | 108,116 | 4.00 -> 4.00 | 4.16 -> 3.26 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/harrahs-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.5 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/harrahs-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.5 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/harrahs-corridor.glb` | streamed (hotel visit) | level | 1.29 | 1.24 | -5% | 0.24 (36 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/harrahs-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/harrahs-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/harrahs-room.glb` | streamed (hotel visit) | level | 1.54 | 1.15 | -25% | 0.35 (41.4 dB) | 19,520 | 5.67 -> 5.67 | 0.65 -> 0.50 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/harrahs-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.5 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/hgv-boulevard-1-lobby.glb` | streamed (hotel visit) | level | 5.10 | 2.10 | -59% | 1.63 (41.4 dB) | 114,852 | 4.00 -> 4.00 | 4.60 -> 3.62 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/hgv-boulevard-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.5 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/hgv-boulevard-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.5 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/hgv-boulevard-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.25 (38.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/hgv-boulevard-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/hgv-boulevard-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/hgv-boulevard-room.glb` | streamed (hotel visit) | level | 1.58 | 1.16 | -26% | 0.36 (41.4 dB) | 20,284 | 5.67 -> 5.67 | 0.68 -> 0.53 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/hgv-boulevard-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.5 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/horseshoe-cap.glb` | streamed (hotel shell) | level | 0.25 | 0.25 | -0% | 0.01 (41.8 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/horseshoe-closure.glb` | streamed (hotel shell) | level | 0.25 | 0.25 | -0% | 0.01 (41.8 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/horseshoe-corridor.glb` | streamed (hotel visit) | level | 1.64 | 1.58 | -4% | 0.25 (35.2 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/horseshoe-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/horseshoe-east-1-lobby.glb` | streamed (hotel visit) | level | 6.35 | 2.55 | -60% | 2.07 (41.4 dB) | 149,993 | 4.00 -> 4.00 | 5.85 -> 4.59 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/horseshoe-east-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.7 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/horseshoe-east-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.7 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/horseshoe-east-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.26 (37.2 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/horseshoe-east-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/horseshoe-east-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/horseshoe-east-room.glb` | streamed (hotel visit) | level | 1.54 | 1.15 | -25% | 0.35 (41.4 dB) | 19,520 | 5.67 -> 5.67 | 0.65 -> 0.50 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/horseshoe-east-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.7 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/horseshoe-entry.glb` | streamed (hotel shell) | level | 0.60 | 0.57 | -4% | 0.03 (40.8 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/horseshoe-room.glb` | streamed (hotel visit) | level | 3.15 | 1.86 | -41% | 0.92 (40.8 dB) | 58,652 | 5.67 -> 5.67 | 2.12 -> 1.69 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/horseshoe-stair.glb` | streamed (hotel shell) | level | 0.29 | 0.26 | -9% | 0.03 (41.8 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/linq-1-lobby.glb` | streamed (hotel visit) | level | 1.92 | 1.10 | -43% | 0.54 (40.7 dB) | 35,133 | 4.00 -> 4.00 | 1.33 -> 1.05 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/linq-cap.glb` | streamed (hotel shell) | level | 0.21 | 0.21 | -0% | 0.01 (41.6 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/linq-closure.glb` | streamed (hotel shell) | level | 0.21 | 0.21 | -1% | 0.01 (41.6 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/linq-corridor.glb` | streamed (hotel visit) | level | 1.59 | 1.52 | -5% | 0.25 (35 dB) | 2,712 | 7.00 -> 7.00 | 0.13 -> 0.10 | 0 errors (0 new), 0 warnings | 1/8 | - | ok |
| `hotels/linq-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/linq-entry.glb` | streamed (hotel shell) | level | 0.55 | 0.53 | -4% | 0.03 (40.7 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/linq-room.glb` | streamed (hotel visit) | level | 1.89 | 1.49 | -21% | 0.40 (40.7 dB) | 19,364 | 7.00 -> 7.00 | 0.66 -> 0.51 | 0 errors (0 new), 0 warnings | 3/15 | - | ok |
| `hotels/linq-stair.glb` | streamed (hotel shell) | level | 0.25 | 0.23 | -10% | 0.03 (41.6 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/luxor-1-lobby.glb` | streamed (hotel visit) | level | 4.67 | 2.00 | -57% | 1.53 (41.3 dB) | 107,888 | 4.00 -> 4.00 | 4.17 -> 3.27 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/luxor-2-lobby.glb` | streamed (hotel visit) | level | 4.67 | 2.00 | -57% | 1.53 (41.3 dB) | 107,888 | 4.00 -> 4.00 | 4.17 -> 3.27 | 0 errors (0 new), 0 warnings | 2/13 | - | ok (identical source to build/hotels/luxor-1-lobby.glb, output copied) |
| `hotels/luxor-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/luxor-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/luxor-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.25 (38.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/luxor-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/luxor-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.3 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/luxor-room.glb` | streamed (hotel visit) | level | 1.63 | 1.23 | -24% | 0.37 (38.6 dB) | 19,700 | 7.00 -> 7.00 | 0.66 -> 0.51 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/luxor-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/mandalay-bay-1-lobby.glb` | streamed (hotel visit) | level | 6.04 | 2.48 | -59% | 2.00 (41.4 dB) | 144,869 | 4.00 -> 4.00 | 5.54 -> 4.35 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/mandalay-bay-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.6 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/mandalay-bay-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.6 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/mandalay-bay-corridor.glb` | streamed (hotel visit) | level | 1.30 | 1.24 | -5% | 0.25 (36.4 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/mandalay-bay-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/mandalay-bay-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/mandalay-bay-room.glb` | streamed (hotel visit) | level | 1.57 | 1.18 | -25% | 0.38 (41.4 dB) | 19,580 | 7.67 -> 7.67 | 0.65 -> 0.50 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/mandalay-bay-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.6 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/martin-1-lobby.glb` | streamed (hotel visit) | level | 3.37 | 1.56 | -54% | 1.09 (41.4 dB) | 72,151 | 4.00 -> 4.00 | 2.87 -> 2.26 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/martin-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.6 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/martin-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.6 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/martin-corridor.glb` | streamed (hotel visit) | level | 1.34 | 1.27 | -5% | 0.27 (35.8 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/martin-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/martin-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/martin-room.glb` | streamed (hotel visit) | level | 1.61 | 1.17 | -27% | 0.37 (41.4 dB) | 20,752 | 5.67 -> 5.67 | 0.71 -> 0.55 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/martin-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.6 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/mgm-grand-1-lobby.glb` | streamed (hotel visit) | level | 6.14 | 2.50 | -59% | 2.03 (41.4 dB) | 146,541 | 4.00 -> 4.00 | 5.64 -> 4.42 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/mgm-grand-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.6 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/mgm-grand-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.6 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/mgm-grand-corridor.glb` | streamed (hotel visit) | level | 1.29 | 1.23 | -5% | 0.25 (37.6 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/mgm-grand-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/mgm-grand-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/mgm-grand-room.glb` | streamed (hotel visit) | level | 1.70 | 1.21 | -29% | 0.41 (41.4 dB) | 23,000 | 5.67 -> 5.67 | 0.81 -> 0.62 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/mgm-grand-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.6 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/mirage-1-lobby.glb` | streamed (hotel visit) | level | 6.19 | 2.52 | -59% | 2.05 (41.2 dB) | 147,725 | 4.00 -> 4.00 | 5.69 -> 4.45 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/mirage-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.2 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/mirage-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.2 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/mirage-corridor.glb` | streamed (hotel visit) | level | 1.30 | 1.24 | -5% | 0.24 (38.7 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/mirage-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/mirage-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.2 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/mirage-room.glb` | streamed (hotel visit) | level | 1.54 | 1.15 | -25% | 0.35 (41.2 dB) | 19,520 | 5.67 -> 5.67 | 0.65 -> 0.50 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/mirage-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.2 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/new-york-1-lobby.glb` | streamed (hotel visit) | level | 4.25 | 1.84 | -57% | 1.37 (41.4 dB) | 95,893 | 4.00 -> 4.00 | 3.75 -> 2.95 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/new-york-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43.2 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/new-york-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43.2 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/new-york-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.25 (35.2 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/new-york-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/new-york-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/new-york-room.glb` | streamed (hotel visit) | level | 1.98 | 1.32 | -34% | 0.51 (41.4 dB) | 27,620 | 5.67 -> 5.67 | 1.09 -> 0.83 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/new-york-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (43.2 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/palazzo-1-lobby.glb` | streamed (hotel visit) | level | 5.93 | 2.46 | -59% | 1.98 (41.4 dB) | 143,669 | 4.00 -> 4.00 | 5.43 -> 4.25 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/palazzo-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.7 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/palazzo-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.7 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/palazzo-corridor.glb` | streamed (hotel visit) | level | 1.31 | 1.24 | -5% | 0.25 (36.8 dB) | 2,472 | 7.00 -> 7.00 | 0.12 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/palazzo-door.glb` | streamed (hotel visit) | level | 0.08 | 0.04 | -48% |  | 2,076 | 0.00 -> 0.00 | 0.07 -> 0.06 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/palazzo-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/palazzo-room.glb` | streamed (hotel visit) | level | 1.52 | 1.14 | -25% | 0.34 (41.4 dB) | 18,184 | 5.67 -> 5.67 | 0.63 -> 0.48 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/palazzo-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.7 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/palms-1-lobby.glb` | streamed (hotel visit) | level | 6.12 | 2.50 | -59% | 2.03 (41.3 dB) | 145,973 | 4.00 -> 4.00 | 5.62 -> 4.41 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/palms-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/palms-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/palms-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.25 (38.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/palms-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/palms-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.3 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/palms-room.glb` | streamed (hotel visit) | level | 1.71 | 1.22 | -29% | 0.41 (41.3 dB) | 26,240 | 5.67 -> 5.67 | 0.82 -> 0.63 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/palms-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/panorama-1-lobby.glb` | streamed (hotel visit) | level | 4.29 | 1.85 | -57% | 1.38 (41.4 dB) | 96,781 | 4.00 -> 4.00 | 3.79 -> 2.98 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/panorama-2-lobby.glb` | streamed (hotel visit) | level | 4.28 | 1.85 | -57% | 1.38 (41.4 dB) | 96,721 | 4.00 -> 4.00 | 3.78 -> 2.98 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/panorama-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.9 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/panorama-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.9 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/panorama-corridor.glb` | streamed (hotel visit) | level | 1.42 | 1.36 | -4% | 0.27 (35.3 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/panorama-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/panorama-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/panorama-room.glb` | streamed (hotel visit) | level | 1.61 | 1.17 | -27% | 0.37 (41.4 dB) | 20,752 | 5.67 -> 5.67 | 0.71 -> 0.55 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/panorama-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.9 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/paris-cap.glb` | streamed (hotel shell) | level | 0.25 | 0.25 | -0% | 0.01 (41.1 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/paris-closure.glb` | streamed (hotel shell) | level | 0.25 | 0.25 | -0% | 0.01 (41.1 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/paris-corridor.glb` | streamed (hotel visit) | level | 1.70 | 1.61 | -5% | 0.27 (37.3 dB) | 2,792 | 7.00 -> 7.00 | 0.15 -> 0.11 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/paris-door.glb` | streamed (hotel visit) | level | 0.09 | 0.04 | -56% |  | 1,500 | 0.00 -> 0.00 | 0.08 -> 0.06 | 0 errors (0 new), 0 warnings | 2/4 | - | ok |
| `hotels/paris-entry.glb` | streamed (hotel shell) | level | 0.60 | 0.58 | -3% | 0.03 (40.7 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/paris-room.glb` | streamed (hotel visit) | level | 1.66 | 1.27 | -23% | 0.34 (37.3 dB) | 18,512 | 7.00 -> 7.00 | 0.64 -> 0.49 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/paris-stair.glb` | streamed (hotel shell) | level | 0.29 | 0.27 | -8% | 0.02 (41.1 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/park-mgm-1-lobby.glb` | streamed (hotel visit) | level | 6.04 | 2.48 | -59% | 2.01 (41.4 dB) | 145,049 | 4.00 -> 4.00 | 5.54 -> 4.35 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/park-mgm-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/park-mgm-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/park-mgm-corridor.glb` | streamed (hotel visit) | level | 1.34 | 1.28 | -4% | 0.26 (37.6 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/park-mgm-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/park-mgm-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/park-mgm-room.glb` | streamed (hotel visit) | level | 1.65 | 1.24 | -25% | 0.39 (39.1 dB) | 20,180 | 7.00 -> 7.00 | 0.68 -> 0.53 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/park-mgm-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (43 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/planet-hollywood-cap.glb` | streamed (hotel shell) | level | 0.22 | 0.22 | -0% | 0.01 (41.7 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/planet-hollywood-closure.glb` | streamed (hotel shell) | level | 0.22 | 0.22 | -1% | 0.01 (41.7 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/planet-hollywood-corridor.glb` | streamed (hotel visit) | level | 1.60 | 1.53 | -4% | 0.27 (35.4 dB) | 2,472 | 7.00 -> 7.00 | 0.12 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/planet-hollywood-door.glb` | streamed (hotel visit) | level | 0.09 | 0.04 | -56% |  | 1,500 | 0.00 -> 0.00 | 0.08 -> 0.06 | 0 errors (0 new), 0 warnings | 2/4 | - | ok |
| `hotels/planet-hollywood-entry.glb` | streamed (hotel shell) | level | 0.55 | 0.53 | -4% | 0.03 (40.6 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/planet-hollywood-room.glb` | streamed (hotel visit) | level | 1.87 | 1.38 | -26% | 0.44 (35.4 dB) | 26,300 | 7.00 -> 7.00 | 0.81 -> 0.63 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/planet-hollywood-stair.glb` | streamed (hotel shell) | level | 0.26 | 0.24 | -10% | 0.02 (41.7 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/polo-1-lobby.glb` | streamed (hotel visit) | level | 3.99 | 1.86 | -54% | 1.22 (40.8 dB) | 84,470 | 4.00 -> 4.00 | 3.33 -> 2.62 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/polo-cap.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.9 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/polo-closure.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.9 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/polo-corridor.glb` | streamed (hotel visit) | level | 1.66 | 1.59 | -4% | 0.25 (36.3 dB) | 2,472 | 7.00 -> 7.00 | 0.12 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/polo-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/polo-entry.glb` | streamed (hotel shell) | level | 0.62 | 0.60 | -3% | 0.03 (40.8 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/polo-room.glb` | streamed (hotel visit) | level | 1.90 | 1.44 | -24% | 0.42 (40.2 dB) | 23,164 | 7.00 -> 7.00 | 0.77 -> 0.59 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/polo-stair.glb` | streamed (hotel shell) | level | 0.31 | 0.29 | -8% | 0.03 (41.9 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/resorts-world-1-lobby.glb` | streamed (hotel visit) | level | 5.05 | 2.10 | -58% | 1.62 (41.4 dB) | 113,796 | 4.00 -> 4.00 | 4.55 -> 3.57 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/resorts-world-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.7 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/resorts-world-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.7 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/resorts-world-corridor.glb` | streamed (hotel visit) | level | 1.37 | 1.30 | -5% | 0.22 (34.1 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/resorts-world-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/resorts-world-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/resorts-world-room.glb` | streamed (hotel visit) | level | 1.71 | 1.22 | -29% | 0.41 (41.4 dB) | 26,240 | 5.67 -> 5.67 | 0.82 -> 0.63 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/resorts-world-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.7 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/rio-1-lobby.glb` | streamed (hotel visit) | level | 2.72 | 1.33 | -51% | 0.85 (41.4 dB) | 56,396 | 4.00 -> 4.00 | 2.22 -> 1.75 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/rio-2-lobby.glb` | streamed (hotel visit) | level | 5.98 | 2.46 | -59% | 1.99 (41.4 dB) | 144,001 | 4.00 -> 4.00 | 5.48 -> 4.30 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/rio-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.2 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/rio-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.2 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/rio-corridor.glb` | streamed (hotel visit) | level | 1.42 | 1.36 | -4% | 0.26 (36.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/rio-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/rio-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/rio-room.glb` | streamed (hotel visit) | level | 1.48 | 1.13 | -24% | 0.33 (41.4 dB) | 17,360 | 5.67 -> 5.67 | 0.59 -> 0.45 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/rio-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.2 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/sahara-1-lobby.glb` | streamed (hotel visit) | level | 3.28 | 1.52 | -54% | 1.05 (41.4 dB) | 70,403 | 4.00 -> 4.00 | 2.78 -> 2.19 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/sahara-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.5 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/sahara-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.5 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/sahara-corridor.glb` | streamed (hotel visit) | level | 1.34 | 1.28 | -4% | 0.24 (38.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/sahara-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/sahara-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/sahara-room.glb` | streamed (hotel visit) | level | 1.72 | 1.22 | -29% | 0.42 (41.4 dB) | 26,360 | 5.67 -> 5.67 | 0.82 -> 0.64 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/sahara-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.5 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/signature-1-lobby.glb` | streamed (hotel visit) | level | 3.72 | 1.64 | -56% | 1.17 (41.2 dB) | 78,351 | 4.00 -> 4.00 | 3.22 -> 2.54 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/signature-2-lobby.glb` | streamed (hotel visit) | level | 3.67 | 1.63 | -56% | 1.15 (41.2 dB) | 77,631 | 4.00 -> 4.00 | 3.17 -> 2.50 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/signature-3-lobby.glb` | streamed (hotel visit) | level | 3.66 | 1.62 | -56% | 1.15 (41.2 dB) | 77,571 | 4.00 -> 4.00 | 3.16 -> 2.49 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/signature-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.2 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/signature-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.2 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/signature-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.25 (38.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/signature-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/signature-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.2 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/signature-room.glb` | streamed (hotel visit) | level | 1.53 | 1.14 | -25% | 0.34 (41.2 dB) | 18,364 | 5.67 -> 5.67 | 0.63 -> 0.49 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/signature-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.2 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/sky-1-lobby.glb` | streamed (hotel visit) | level | 3.40 | 1.55 | -55% | 1.07 (41.4 dB) | 72,443 | 4.00 -> 4.00 | 2.90 -> 2.29 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/sky-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43.2 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/sky-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43.2 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/sky-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.26 (35.6 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/sky-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/sky-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/sky-room.glb` | streamed (hotel visit) | level | 1.61 | 1.17 | -27% | 0.37 (41.4 dB) | 20,752 | 5.67 -> 5.67 | 0.71 -> 0.55 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/sky-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (43.2 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/springhill-1-lobby.glb` | streamed (hotel visit) | level | 2.41 | 1.18 | -51% | 0.71 (41.1 dB) | 45,821 | 4.00 -> 4.00 | 1.91 -> 1.51 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/springhill-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.1 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/springhill-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.1 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/springhill-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.26 (37.9 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/springhill-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/springhill-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.1 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/springhill-room.glb` | streamed (hotel visit) | level | 1.48 | 1.13 | -24% | 0.33 (41.1 dB) | 17,360 | 5.67 -> 5.67 | 0.59 -> 0.45 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/springhill-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.1 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/strat-1-lobby.glb` | streamed (hotel visit) | level | 4.65 | 2.00 | -57% | 1.52 (41.4 dB) | 107,468 | 4.00 -> 4.00 | 4.15 -> 3.26 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/strat-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.6 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/strat-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.6 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/strat-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -5% | 0.26 (35.3 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/strat-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/strat-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/strat-room.glb` | streamed (hotel visit) | level | 1.71 | 1.22 | -29% | 0.41 (41.4 dB) | 26,240 | 5.67 -> 5.67 | 0.82 -> 0.63 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/strat-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.6 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/treasure-island-1-lobby.glb` | streamed (hotel visit) | level | 6.12 | 2.50 | -59% | 2.03 (41.4 dB) | 146,745 | 4.00 -> 4.00 | 5.62 -> 4.40 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/treasure-island-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.4 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/treasure-island-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.4 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/treasure-island-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.24 (40.4 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/treasure-island-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/treasure-island-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/treasure-island-room.glb` | streamed (hotel visit) | level | 1.56 | 1.16 | -26% | 0.36 (41.4 dB) | 19,760 | 5.67 -> 5.67 | 0.66 -> 0.51 | 0 errors (0 new), 0 warnings | 3/14 | - | ok |
| `hotels/treasure-island-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.4 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/trump-1-lobby.glb` | streamed (hotel visit) | level | 4.74 | 2.02 | -57% | 1.55 (41.3 dB) | 109,260 | 4.00 -> 4.00 | 4.24 -> 3.32 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/trump-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/trump-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/trump-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.25 (38.1 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/trump-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/trump-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.3 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/trump-room.glb` | streamed (hotel visit) | level | 1.59 | 1.17 | -26% | 0.37 (41.3 dB) | 20,524 | 5.67 -> 5.67 | 0.69 -> 0.54 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/trump-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/turnberry-place-1-lobby.glb` | streamed (hotel visit) | level | 4.29 | 1.85 | -57% | 1.38 (41.4 dB) | 96,661 | 4.00 -> 4.00 | 3.79 -> 2.98 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/turnberry-place-2-lobby.glb` | streamed (hotel visit) | level | 4.29 | 1.85 | -57% | 1.38 (41.4 dB) | 96,661 | 4.00 -> 4.00 | 3.79 -> 2.98 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/turnberry-place-3-lobby.glb` | streamed (hotel visit) | level | 4.29 | 1.85 | -57% | 1.38 (41.4 dB) | 96,661 | 4.00 -> 4.00 | 3.79 -> 2.98 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/turnberry-place-4-lobby.glb` | streamed (hotel visit) | level | 4.30 | 1.85 | -57% | 1.38 (41.4 dB) | 96,661 | 4.00 -> 4.00 | 3.79 -> 2.98 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/turnberry-place-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.4 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/turnberry-place-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.4 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/turnberry-place-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.25 (38.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/turnberry-place-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/turnberry-place-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/turnberry-place-room.glb` | streamed (hotel visit) | level | 1.61 | 1.17 | -27% | 0.37 (41.4 dB) | 20,752 | 5.67 -> 5.67 | 0.71 -> 0.55 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/turnberry-place-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.4 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/turnberry-towers-1-lobby.glb` | streamed (hotel visit) | level | 2.49 | 1.21 | -52% | 0.73 (41.4 dB) | 47,053 | 4.00 -> 4.00 | 1.99 -> 1.57 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/turnberry-towers-2-lobby.glb` | streamed (hotel visit) | level | 2.49 | 1.21 | -52% | 0.73 (41.4 dB) | 46,993 | 4.00 -> 4.00 | 1.99 -> 1.57 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/turnberry-towers-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/turnberry-towers-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (43 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/turnberry-towers-corridor.glb` | streamed (hotel visit) | level | 1.33 | 1.27 | -4% | 0.25 (38.5 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/turnberry-towers-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/turnberry-towers-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/turnberry-towers-room.glb` | streamed (hotel visit) | level | 1.61 | 1.17 | -27% | 0.37 (41.4 dB) | 20,752 | 5.67 -> 5.67 | 0.71 -> 0.55 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/turnberry-towers-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (43 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/vanderpump-1-lobby.glb` | streamed (hotel visit) | level | 2.48 | 1.32 | -47% | 0.69 (40.7 dB) | 44,105 | 4.00 -> 4.00 | 1.82 -> 1.44 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/vanderpump-cap.glb` | streamed (hotel shell) | level | 0.25 | 0.25 | -0% | 0.01 (41.5 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/vanderpump-closure.glb` | streamed (hotel shell) | level | 0.25 | 0.25 | -0% | 0.01 (41.5 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/vanderpump-corridor.glb` | streamed (hotel visit) | level | 1.60 | 1.53 | -5% | 0.24 (38.9 dB) | 2,712 | 7.00 -> 7.00 | 0.13 -> 0.10 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/vanderpump-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/vanderpump-entry.glb` | streamed (hotel shell) | level | 0.61 | 0.59 | -3% | 0.03 (40.7 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/vanderpump-room.glb` | streamed (hotel visit) | level | 2.24 | 1.58 | -29% | 0.57 (39.2 dB) | 33,908 | 9.67 -> 9.67 | 1.06 -> 0.83 | 0 errors (0 new), 0 warnings | 3/15 | - | ok |
| `hotels/vanderpump-stair.glb` | streamed (hotel shell) | level | 0.29 | 0.27 | -8% | 0.03 (41.5 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/vdara-cap.glb` | streamed (hotel shell) | level | 0.27 | 0.26 | -0% | 0.01 (42.9 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/vdara-closure.glb` | streamed (hotel shell) | level | 0.26 | 0.26 | -0% | 0.01 (42.9 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/vdara-corridor.glb` | streamed (hotel visit) | level | 1.55 | 1.48 | -4% | 0.27 (36.7 dB) | 2,480 | 7.00 -> 7.00 | 0.12 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/vdara-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/vdara-entry.glb` | streamed (hotel shell) | level | 0.57 | 0.55 | -4% | 0.03 (40.7 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/vdara-room.glb` | streamed (hotel visit) | level | 1.70 | 1.28 | -25% | 0.33 (40.7 dB) | 20,312 | 5.67 -> 5.67 | 0.69 -> 0.54 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/vdara-stair.glb` | streamed (hotel shell) | level | 0.31 | 0.28 | -8% | 0.02 (42.9 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/veer-cap.glb` | streamed (hotel shell) | level | 0.11 | 0.03 | -73% |  | 2,308 | 0.00 -> 0.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/veer-closure.glb` | streamed (hotel shell) | level | 0.00 | 0.00 | -26% |  | 60 | 0.00 -> 0.00 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/veer-corridor.glb` | streamed (hotel visit) | level | 0.11 | 0.05 | -57% |  | 1,956 | 0.00 -> 0.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/6 | - | ok |
| `hotels/veer-entry.glb` | streamed (hotel shell) | level | 0.02 | 0.01 | -47% |  | 252 | 0.00 -> 0.00 | 0.01 -> 0.01 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/veer-room.glb` | streamed (hotel visit) | level | 0.15 | 0.06 | -57% |  | 2,448 | 0.00 -> 0.00 | 0.14 -> 0.10 | 0 errors (0 new), 0 warnings | 1/9 | - | ok |
| `hotels/veer-stair.glb` | streamed (hotel shell) | level | 0.05 | 0.02 | -56% |  | 768 | 0.00 -> 0.00 | 0.05 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/venetian-1-lobby.glb` | streamed (hotel visit) | level | 5.92 | 2.46 | -58% | 1.98 (41.4 dB) | 143,345 | 4.00 -> 4.00 | 5.42 -> 4.24 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/venetian-2-lobby.glb` | streamed (hotel visit) | level | 5.92 | 2.45 | -58% | 1.98 (41.4 dB) | 143,285 | 4.00 -> 4.00 | 5.41 -> 4.24 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/venetian-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.6 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/venetian-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.6 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/venetian-corridor.glb` | streamed (hotel visit) | level | 1.30 | 1.23 | -5% | 0.23 (35.7 dB) | 2,472 | 7.00 -> 7.00 | 0.12 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/venetian-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/venetian-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/venetian-room.glb` | streamed (hotel visit) | level | 1.52 | 1.14 | -25% | 0.34 (41.4 dB) | 18,184 | 5.67 -> 5.67 | 0.63 -> 0.48 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/venetian-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.6 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/w-las-vegas-1-lobby.glb` | streamed (hotel visit) | level | 4.70 | 2.01 | -57% | 1.53 (41.3 dB) | 108,268 | 4.00 -> 4.00 | 4.20 -> 3.29 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/w-las-vegas-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/w-las-vegas-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/w-las-vegas-corridor.glb` | streamed (hotel visit) | level | 1.34 | 1.28 | -4% | 0.24 (37.7 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/w-las-vegas-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/w-las-vegas-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.3 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/w-las-vegas-room.glb` | streamed (hotel visit) | level | 1.76 | 1.22 | -30% | 0.42 (41.3 dB) | 28,160 | 5.67 -> 5.67 | 0.86 -> 0.67 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/w-las-vegas-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/waldorf-cap.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/waldorf-closure.glb` | streamed (hotel shell) | level | 0.27 | 0.27 | -0% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/waldorf-corridor.glb` | streamed (hotel visit) | level | 1.65 | 1.57 | -5% | 0.25 (38.6 dB) | 2,552 | 7.00 -> 7.00 | 0.14 -> 0.11 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/waldorf-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/waldorf-entry.glb` | streamed (hotel shell) | level | 0.64 | 0.62 | -3% | 0.03 (40.7 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/waldorf-room.glb` | streamed (hotel visit) | level | 1.82 | 1.37 | -25% | 0.39 (40.7 dB) | 21,740 | 5.67 -> 5.67 | 0.74 -> 0.57 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/waldorf-stair.glb` | streamed (hotel shell) | level | 0.31 | 0.29 | -8% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/westgate-1-lobby.glb` | streamed (hotel visit) | level | 6.09 | 2.49 | -59% | 2.02 (41.4 dB) | 145,665 | 4.00 -> 4.00 | 5.59 -> 4.39 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/westgate-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.9 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/westgate-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (42.9 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/westgate-corridor.glb` | streamed (hotel visit) | level | 1.32 | 1.26 | -4% | 0.26 (36.8 dB) | 2,232 | 7.00 -> 7.00 | 0.11 -> 0.08 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/westgate-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/westgate-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.4 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/westgate-room.glb` | streamed (hotel visit) | level | 1.65 | 1.19 | -28% | 0.39 (41.4 dB) | 24,080 | 5.67 -> 5.67 | 0.76 -> 0.59 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/westgate-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (42.9 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `hotels/wynn-1-lobby.glb` | streamed (hotel visit) | level | 6.34 | 2.63 | -59% | 2.16 (41.3 dB) | 152,837 | 4.00 -> 4.00 | 5.84 -> 4.57 | 0 errors (0 new), 0 warnings | 2/13 | - | ok |
| `hotels/wynn-cap.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 72 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 1/2 | - | ok |
| `hotels/wynn-closure.glb` | streamed (hotel shell) | level | 0.14 | 0.14 | -1% | 0.01 (41.3 dB) | 60 | 1.33 -> 1.33 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/1 | - | ok |
| `hotels/wynn-corridor.glb` | streamed (hotel visit) | level | 1.30 | 1.24 | -5% | 0.24 (37.9 dB) | 2,352 | 7.00 -> 7.00 | 0.11 -> 0.09 | 0 errors (0 new), 0 warnings | 1/7 | - | ok |
| `hotels/wynn-door.glb` | streamed (hotel visit) | level | 0.03 | 0.02 | -50% |  | 540 | 0.00 -> 0.00 | 0.03 -> 0.02 | 0 errors (0 new), 0 warnings | 1/3 | - | ok |
| `hotels/wynn-entry.glb` | streamed (hotel shell) | level | 0.46 | 0.44 | -4% | 0.03 (41.3 dB) | 732 | 2.67 -> 2.67 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/5 | - | ok |
| `hotels/wynn-room.glb` | streamed (hotel visit) | level | 1.62 | 1.18 | -27% | 0.38 (41.3 dB) | 21,440 | 5.67 -> 5.67 | 0.72 -> 0.56 | 0 errors (0 new), 0 warnings | 3/13 | - | ok |
| `hotels/wynn-stair.glb` | streamed (hotel shell) | level | 0.18 | 0.16 | -13% | 0.03 (41.3 dB) | 648 | 1.33 -> 1.33 | 0.04 -> 0.03 | 0 errors (0 new), 0 warnings | 1/4 | - | ok |
| `public/foliage/tree-0.glb` | boot (localhost, Bellagio block) | hero-prop --orm=webp-lossless:512 | 26.97 | 11.27 | -58% |  | 250,000 | 48.00 -> 36.00 | 20.70 -> 13.12 | 0 errors (0 new), 3 warnings; MESH_PRIMITIVE_GENERATED_TANGENT_SPACE /meshes/0/primitives/ | 0/1 | - | ok |
| `public/foliage/tree-1.glb` | boot (localhost, Bellagio block) | hero-prop --orm=webp-lossless:512 | 7.40 | 4.49 | -39% |  | 13,139 | 48.00 -> 36.00 | 1.13 -> 0.69 | 0 errors (0 new), 3 warnings; MESH_PRIMITIVE_GENERATED_TANGENT_SPACE /meshes/0/primitives/ | 0/1 | - | ok |
| `public/foliage/tree-2.glb` | boot (localhost, Bellagio block) | hero-prop --orm=webp-lossless:512 | 0.63 | 0.14 | -77% |  | 6 | 3.66 -> 3.66 | 0.00 -> 0.00 | 0 errors (0 new), 0 warnings | 0/3 | - | ok |
| `src/work/characters/b6101/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.29 | 3.09 | -42% |  | 27,445 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6102/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.58 | 3.32 | -41% |  | 29,347 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6103/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 6.03 | 3.71 | -38% |  | 34,862 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6104/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.51 | 3.38 | -39% |  | 31,225 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6105/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.68 | 3.44 | -39% |  | 31,607 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6106/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.81 | 3.67 | -37% |  | 34,951 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6107/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.86 | 3.72 | -36% |  | 33,731 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6108/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.67 | 3.40 | -40% |  | 30,720 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `src/work/characters/b6109/character.glb` | boot | character --base=webp:1024:90 --emissive=webp:1024:90 --orm=webp-lossless:512 | 5.97 | 3.75 | -37% |  | 35,446 | unchanged | unchanged | 260 errors (0 new; the original has 260: ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS) | 4/24 | - | encoder cannot read it (required BITMAGIC_sparse_correctives); texture-only candidate |
| `arrival-reconstruction/door-bronze.glb` | boot | level | 0.07 | 0.03 | -51% |  | 1,104 | 0.00 -> 0.00 | 0.06 -> 0.04 | 0 errors (0 new), 0 warnings | 3/4 | - | ok |
| `arrival-reconstruction/door-silver.glb` | boot | level | 0.07 | 0.03 | -53% |  | 1,104 | 0.00 -> 0.00 | 0.06 -> 0.04 | 0 errors (0 new), 0 warnings | 2/3 | - | ok |
| `arrival-reconstruction/door-black.glb` | boot | level | 0.07 | 0.03 | -51% |  | 1,104 | 0.00 -> 0.00 | 0.06 -> 0.04 | 0 errors (0 new), 0 warnings | 2/4 | - | ok |
| `arrival-reconstruction/door-sage.glb` | boot | level | 0.07 | 0.03 | -51% |  | 1,104 | 0.00 -> 0.00 | 0.06 -> 0.04 | 0 errors (0 new), 0 warnings | 3/4 | - | ok |
<!-- generated:end -->
