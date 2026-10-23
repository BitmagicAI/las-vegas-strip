# Venetian second exterior correction — installed review

2026-10-09. Responds to the creator's closer Google Earth references and request to try again, with follow-ups requesting official floor maps and their use for interiors. This is an installed local correction, not a photorealism signoff.

## Changed geometry

- Replaced the 124m stretched palace front with a 66m facade aligned to the mapped canal-front segment. Sixteen lower round arches, thirty-two upper pointed arches with open tracery, a nested diamond stone pattern, central ceremonial window and neighboring wings now form distinct elements.
- Built the missing T-shaped plaza from closed mapped footways: raised slab, geometric paving, water-edge balustrades and continuous collision infill, approach columns and kiosk silhouettes. Its 1.10m datum is an estimate; graded connections meet the existing 0.24m entrance datum.
- Cut a real passage through the south wing around the existing Rialto route; removed trim and windows that would obstruct it. The visual facade participates in the new clearance audit, so a non-colliding visible wall cannot silently pass the test.
- Replaced the previous low north building with a two-tier stepped mass, tall glazed bays and inset upper floor. Its 62m height remains a visual estimate, not a surveyed dimension.
- Muted campanile brick and changed the roof to pale patina. Moved gondolas clear of the new plaza.

Sources and uncertainty are registered in `tools/resort-blocks/venetian.json`. Official public maps, meeting plans, pool maps and suite plans are archived and explained in [the floorplan report](venetian-floorplans-2026-10-09.md). Existing interiors remain in place; their straight canal and simplified casino/lobby layout are explicitly marked as inconsistent or unverified against the plans.

## Installed comparison

![Installed game, optimized exterior](venetian-exterior-2026-10-09/plaza-revision-installed.png)

Compare with `reference-palace-plaza-close.png` and `reference-canal-plaza-aerial.png` in that directory. The new broad plaza, shorter palace frontage and stepped north structure are visible in the running game. Cameras are similar aerial views, not a calibrated matched-camera comparison. Neutral offline renders `venetian-palace-plaza-review.png` and `venetian-frontage-correction-review.png` were also visually inspected, but are not substitutes for the installed game evidence.

The reference still has substantially richer sculptural work, roof geometry, layered retail frontage and planting. Those differences remain obvious. Visual acceptance stays **failed**; whole Venetian/Palazzo completion and photorealism are not claimed.

## Build and validation

- Targeted exterior only: 173 mesh groups / 1,225,320 triangles, about 4% more than the previous 1,177,984 triangles. Raw GLB 93.33MiB → optimized WebP variant 25.78MiB. One installed asset updated; the other 449 manifest entries retained.
- Builder completed with RuntimeWarnings treated as errors. Removed a duplicate arc endpoint that initially produced a zero-length tube.
- `bitmagic check`: passed.
- City route audit: 9,889 checks, zero failures, 284 virtual rooms.
- New exported plaza and Rialto audit: 502 floor/clearance samples and five rail containment rays passed. This is geometric probing, not a complete keyboard traversal.
- Final local `bitmagic verify`: WebGPU passed, startup settled in 4.1 seconds and reported 60fps at spawn. This is startup verification, not a measured Venetian performance route.

Evidence: `plaza-check.txt`, `plaza-routes.txt`, `venetian-plaza-audit.json`, `plaza-optimize.txt`, `plaza-webp.txt`, `plaza-install.txt`, `plaza-verification.txt` in the dated evidence directory. No runtime lighting or streaming changes; no unrelated roads or interiors regenerated. No uploads or cloud judging.

## Remaining work

1. Register the official resort plans against multiple mapped exterior anchors, record registration error and reconcile physical elevations independently of floor labels. Convention Level 3 connects to shopping labeled resort Level 2.
2. Reconstruct connected public interiors from that registration, preserving optimized lighting/streaming and replacing portals, colliders and route tests together. Use the two official suite plans for distinct room templates; whole guest-floor core plans remain unavailable.
3. Continue exterior matched-view work on roof/podium shape, facade depth and rhythm, sculpture, storefronts, planting and complete yards. Verify provisional north-building and deck elevations. Pool access remains incomplete.
4. Measure a repeatable local traversal/performance route and inspect the final installed close views before any visual acceptance.

Overnight automation remains paused. This pass does not restart it or advance to another resort.
