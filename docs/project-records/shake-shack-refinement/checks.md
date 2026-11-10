# Local checks — 2026-11-06

- Typecheck: passed.
- Runtime regression tests: city lazy LOD, lighting resize and site lights, 3 passed.
- Existing support audit: 185 samples, 0 failures. Initial run lacked ignored sample input; recovered original samples into the durable record and reran successfully.
- CPU walking: 14 legs passed.
- Actual installed keyboard walking: 14 legs passed, both directions, ramp/terrace/stair.
- Four matched before/after neutral daylight views: inspected. Static p95 comparisons are in review.md; existing terrace slowdown retained.
- All 43 existing source nodes retained before optimization; 273 collision triangles retained. Repacking unchanged collision data produced byte-identical binary. Initial staging rejected its stale timestamp, fixed by this verified repack.
- Level and WebP optimization: passed; changed-model audit 1 checked, 0 unoptimized.
- One shared city bake: passed, check current. 91 of 92 cells byte-identical, only -1_1 changed. Unrelated Gold Coast/Wyndham LOD deltas restored.
- Asset pack: 1,930 present, 0 missing, 0 unoptimized; stage 3 copied, 1,927 unchanged, 0 removed.
- Reload: dev running, no interactive browser tab open; subsequent headless probes loaded installed assets.
- Nine-stop dev smoke: 0 failed requests, 0 page errors, 0 console errors, 0 unplaced stops.
- Record validation: 291 records valid. Public check: 0 failures, 13 existing warnings.
- Diff whitespace check: passed. Local archive saved; final archive rerun after evidence collection.

No CDN, published-game or person-dependent check is used as a local merge gate. No release action performed.
