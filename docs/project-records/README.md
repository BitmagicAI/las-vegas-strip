# Project record

This directory keeps the research and work history with the game. It is outside
the ignored `build/` directory so Git can include it.

- [Journal](journal-2026-10-06.md) (and [2026-10-05](journal-2026-10-05.md)): exact current-session comments and decisions;
  earlier work is explicitly labeled as a reconstructed summary.
- [City batching and LOD](city-lod-performance.md): implemented architecture, draw-count reductions, validation and the remaining 60 FPS acceptance gap.
- [Scene performance](scene-performance.md): panel controls, counter definitions, measured draw breakdown and optimization candidates.
- [Interiors](interior-performance-2026-10-07/README.md): hotel stairs, corridors, rooms, lobbies and casino interiors 15-51 → 60 fps (local light lists).
- [Lighting analysis](lighting-analysis-2026-10-08/README.md): why point lights got so expensive (three r185 compiles one shader block per light; pools kept 43 visible), and the engine's new batched lighting (8-12 → 60 fps with every light, identical picture; not in engine 3.1223 yet).
- [Showcase video](showcase-video-2026-10-08/README.md): 2:28 1080p60 tour (drive, casinos, door kicks, window views, Eiffel deck, Big Apple Coaster); new shadow-distance setting, F/KICK door kicks, local film director and tools/film/. v2: realistic water, drone drives, logo. v3: scanned CC0 surface detail (PbrDetail), lake anti-aliasing, motion-blur sub-frames, spline flights checked by clearance.py, routed drives.
- [Idle frame rate](idle-performance-2026-10-07/README.md): foliage at 5 fps and 20-40 fps standing still (full GCs on a ~9.6 GB process): causes, the fixes (60 fps, no full GCs, 1.4 GB), rejected approaches, optimized GLBs, probe tools.
- [Streaming stalls](streaming-stalls-2026-10-06/README.md): the long pauses when driving near buildings: cause, measurements, fix, probe tools, what remains.
- [Open work](open-work.md): remaining implementation and refinement work.
- [Reference index](reference-index.json): original paths, durable archive paths,
  sizes and SHA-256 hashes, plus links to source registers.
- [User reference images](user-references/index.json): all 29 supplied attachments preserved.
- `archive/`: preserved research manifests, reference media and review evidence.
- [Resort queue](../../tools/resort-blocks/queue.json) and per-resort JSON files:
  authoritative component, level, route, source and verification inventories.
- [Production workflow](../../tools/resort-blocks/README.md).

Refresh the archive from the project root with:

```sh
python3 tools/archive-project-records.py
```

Source URLs, access dates, attribution and limitations belong in the adjacent source
register or resort JSON. Photographs and Google Earth screenshots are visual
research references; copying them locally does not establish redistribution rights.
Retain the source links if preparing a public repository without those images.
Original game captures and authored geometry have separate provenance.

This record does not pretend to reproduce assistant messages no longer available
verbatim. It preserves existing plans and manifests and records future user-facing
comments as they are made. No chat is uploaded, and no GitHub repository is created
or pushed by this archive command.

`build/` also contains runtime assets the local game currently loads. This archive
preserves research and evidence, not a self-contained clean-clone game distribution.
Asset packaging/rebuild inputs must be included separately before claiming that a
fresh clone can run the game. Keep engine license notices with any such package.
