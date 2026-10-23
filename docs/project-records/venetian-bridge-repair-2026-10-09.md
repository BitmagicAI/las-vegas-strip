# Venetian bridge and overlapping surfaces — 9 October 2026

The creator's latest game screenshot exposed a failed integration review: the
standalone resort render excluded an older city walkway, and the constructed
Rialto followed an inherited diagonal stair plus an unrelated gallery extension.
The previous visual signoff was insufficient. This pass repairs those specific
defects; it does not establish a photorealistic or complete Venetian resort.

## Installed changes

- Removed the old city bridge meshes and colliders belonging to mapped ways
  1352089771 and 543728952. The latter made the floating metal gallery across the
  palace. Exact collider footprints and tightly bounded bridge-material corridors
  identify the replacement geometry. The raw city GLB was patched in place:
  5,248 visual triangles and 3,040 collision triangles removed, no unrelated roads
  regenerated. The geographic generator now excludes both superseded ways.
- Gave each plaza/entrance floor and adjoining podium wall a single owner.
  Four independently authored coplanar overlaps previously measured approximately
  566.68, 226.67, 107.08 and 55.94 square metres. All four now measure zero.
- Rebuilt the Rialto on one mapped axis, with continuous arch sides and soffit,
  visible treads over smooth collision ramps, open arched galleries, shallow
  barrel roofs, a transverse central gable, and a connected plaza stair.
  Balustrades have collision infill with a real opening at the stair connection.
- Cut an actual entrance through the small palazzo at the lower bridge end.
  Retained the existing upper public portal and all interior geometry.

Final exterior: 168 groups / 1,229,034 triangles; 93.71 MiB raw → 25.88 MiB installed
WebP/meshopt GLB. The city was separately optimized and installed. The 450-entry
runtime manifest retains other assets. Source/installed hashes are in
[installed-assets.json](venetian-bridge-repair-2026-10-09/installed-assets.json).
No runtime TypeScript or lighting changes, uploads or publishing.

## Reference and visual inspection

Compared the model to the creator's Google Earth canal/plaza/campanile aerials
and [Tony Hisgett's September 2014 bridge photograph](https://commons.wikimedia.org/wiki/File:The_Venetian_12_(15550338560).jpg)
(CC BY 2.0; archived in the preceding exterior evidence folder). The photograph
exposed the roof and central gable errors during this pass; both were corrected
before the final export. Its age does not establish current decorative details.

Combined renders include **the city, Venetian exterior and existing interior**.
This caught remaining legacy rail fixtures and an under-deck gap which were
repaired before final capture. Final overview, underside and plaza renders were
all opened and inspected:

![Combined geometry review](venetian-bridge-repair-2026-10-09/rialto-overview-combined.png)

The final optimized asset was then loaded at localhost:3090 in the actual game.
Three ground views were inspected: underpass, palace/plaza and plaza-to-bridge
stair. They show the continuous bridge and clean plaza surface; no browser errors
were logged in the last view. These are approximate comparison views, not matched
photogrammetric cameras. The game screenshots include the game's own lighting.

![Installed game underpass](venetian-bridge-repair-2026-10-09/installed-underpass.png)
![Installed game plaza landing](venetian-bridge-repair-2026-10-09/installed-plaza-landing.png)

Reproduce the combined renders with:
`blender -b --python tools/strip-landmarks/review_venetian_bridge.py`.
Game review queries: `?landmark=venetian&view=rialto-underpass`,
`?landmark=venetian&view=palace-ground`, and
`?landmark=venetian&view=rialto-plaza-ground`.

## Verification

- `bitmagic check`: passed.
- Full city route audit: 9,904 samples, zero failures, 284 virtual rooms.
- New Rialto audit: 666 floor/capsule/underpass samples, zero failures. Tests both
  collision output and visible bridge/adjacent-building geometry for obstructions.
- Plaza audit: 502 samples and five rail rays, zero failures.
- New coplanar ownership audit: all four conflict areas zero; no legacy bridge
  triangles remain in the two replacement corridors of the actual city GLB.
- Final `bitmagic verify`: WebGPU backend, playing, startup 4.1 seconds / 42 fps
  on this host with concurrent review work. This is **not** a route benchmark.

Reports and screenshots are in `venetian-bridge-repair-2026-10-09/`.
Both optimized assets were checked against their recorded source SHA-256 hashes.
Automated route sampling does not constitute a complete keyboard walkthrough.

## Remaining limits

Bridge horizontal alignment is mapped; the height profile (street 0.24 m,
crest 7.84 m, existing upper portal 6.24 m), width and ornament proportions are
reference estimates. Sculpture, lanterns, facade recesses and end pavilions remain
simplified. The wider resort still has sparse grounds, approximate podium/roof
massing, incomplete pool access and inaccurate interior topology. The official
floor-map registration work remains pending. The full-resort visual gate stays
failed; no photorealism or whole-resort completion claim is justified.

Continue Venetian before other resorts. The overnight automation remains paused.
