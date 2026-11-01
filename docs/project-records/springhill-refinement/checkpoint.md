# SpringHill refinement

Claim #44 confirmed; draft PR #442 starts from origin/next c1a2d07 after the Westwood/Highland batch merged. Official entrance/pool photographs and February 2026 Street View inspected. The real arrival is east-facing, unlike the current generic west lobby entry. Preserve existing guest interiors and document this discrepancy; the exterior canopy can be improved independently. Add original roof furniture and measure local deck routes. No claim of continuous lift-to-roof access without evidence.

Next: source geometry, clearance and camera preflight; matching baseline before any installation; optimized model/WebP, one bake, installed inspection and movement, local step-7 checks, self-merge to next. No owner wait or publishing.

## Source correction and baseline
Source inspection found a second problem: the eastern canopy footprint was extruded as a 19 m garage wall, and the geographic data retains a 6 m coarse podium collider in the arrival court. Corrected the authored podium to the south garage footprint, preserving the tower shell and west access cut. A dedicated installer removes only the two owned coarse shells. The canopy, louvers, lettering, glazing, nine sling loungers, side tables and ladder rails are original geometry. Final source renders inspected; 852 roof floor samples and body-width routes pass. Four identical before/after cameras are prepared and baseline captures complete. Installation/bake not yet verified.

## Installed review
Four installed daylight views inspected: low east canopy is exposed, south garage retained, furniture and ladder rails visible on the roof. Matching p95 frame times before 18.6–18.8 ms and after 18.5–18.8 ms. One city export and bake; only cell 1,-3 changes, 272 other cell files byte-identical. Package has 1,924 files, none missing/unoptimized; both changed GLBs passed WebP optimization. 9 new LFS objects total 3,505,171 bytes.

The full packing regression initially exposed its pre-cell-split hardcoded monolithic collision filename; corrected to enumerate split files and assert complete unique source-cell coverage. Scoped city collision check passes for all 1,516 records. Full authoring-wide test remains unavailable in this worktree because unrelated Bellagio authoring JSON has no corresponding packed file; no unrelated assets regenerated. Runtime ground-index, site-light and lazy-LOD tests pass with the required TypeScript loader. Movement PASS: 4 routes / 14 segments in both directions, with arrival and return screenshots; preserved west lobby visually inspected. Smoke check running.
