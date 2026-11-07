# CityCenter63 terrace shade refinement

This bounded pass replaces twelve bright conical terrace shades with original shallow dark eight-panel canopies and underside ribs. The two mapped buildings remain a single CityCenter63 asset: only the main building's Ocean Prime terrace changes; the west ARTE wing remains unchanged. The 32 other authored groups, labels, furniture, poles, collision and original glass/paving materials are retained.

Official gallery photographs support the canopy palette and support structure. The 2.4 m span, 0.25 m pitch and retained twelve placements are modeling estimates, not a measured seating plan. References and limits are in references.md. Existing metal furniture, simplified billboard, paving, tenant doors and public vertical access remain unfinished. This is not a whole-block or photorealistic completion claim.

The first isolated candidate exposed legacy material drift in the shared exporter. Its candidate/ images are rejected evidence. preserve-citycenter63-materials.py restores original texture-free material definitions by name before optimization; candidate-material-preserved/ is the corrected preview. The source-level patch changes only the old canopy group and adds new canopy/rib groups. Its preservation test also rejects non-finite or degenerate triangles.

Three neutral daylight fixed views use the same camera names and positions, with east front first. The actual terrace walk starts by teleporting onto the terrace, then uses player movement over four segments and returns. It verifies terrace movement only, not access from the street or neighboring bridges. Historical four clearance failures and old Crystals wall conflicts remain recorded in the block record and are outside this mesh-only change.

Decisions for the owner: retain existing placements and all surrounding geometry; use dark fabric and inferred shallow pitch; preserve legacy materials rather than allowing a shared exporter update to recolor the building. These choices are reversible in the source helper and scoped patch.

For the release step: CDN and published-game checks remain with the owner. No publication, CDN upload, release or main merge is part of this work.

Validation: all 11 local checks passed (local-checks.json); three matching before/after views inspected; 8 before and 8 after player-movement legs passed. Saved endpoint positions can drift after the arrival threshold while the screenshot settles. Nine dev smoke stops passed with zero failed requests, page errors, console errors or unplaced stops. One shared bake changed only cell--1_1.bin; 91/92 cells and collision JSON remain byte-identical. All shared material definitions are unchanged. Level optimization reduced 6,143,900 raw bytes to 2,026,092 bytes; zero textures, standard WebP pass skipped appropriately, validator zero errors/warnings. See performance.json for matching measurements; no speedup claim.
