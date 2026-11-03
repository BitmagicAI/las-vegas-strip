Refine two neighboring Circus Circus frontage buildings with original decorative geometry. The wider nine-building block remains refinement-deferred.

### Slots-A-Fun
Add two pearl lamp rows and thin gold rails to the front fascia, based on an inspected ground photo. Corrected the upper row from 5.3m to 5.65m after close-up review found it crossed existing lettering. These are static meshes, with no new scene lights or collision. Graphic art is not copied.

### McDonalds
Add thin standing seams to the existing yellow dining roof, supported by inspected Google aerial imagery. Existing roof planes, flat service roof and building footprint remain intact. Spacing and section sizes are inferred.

### Verification
- Source preservation: 61→62 groups; only two existing material groups changed and one added. All other geometry groups, labels and collision identical.
- Level optimization plus WebP: PASS, 10.88→3.43MiB.
- Eight corrected installed daylight views personally inspected, front first, same cameras as reference captures. Lettering overlap fixed; roof seams visible.
- Actual frontage walking: PASS, 16 segments, all four endpoint captures inspected. This does not establish full-site or public-interior traversal.
- Existing motel stair/gallery support/headroom: 432 samples PASS.
- bitmagic check: PASS. review.py: PASS, 289 valid block records. check-public.py: PASS, zero failures and three existing email warnings.
- Initial timing regressions are preserved in the record. Longer 900-frame motel trials show original P95 19.6/33.5/21.2ms and installed19.2/18.8/18.7ms, demonstrating variance also on the original. Corrected broad views P95 19/19.4/18.9/19.1/18.2/19.9ms. Roof-detail longer three900-frame trials: original18.8/19/18.7ms, installed18.8/18.7/18.6ms. The29ms outlier was not reproduced; all original outliers remain recorded. No speedup or 60fps claim.
- Exactly one shared bake completed. check-runtime-glbs.py --changed origin/next: PASS, one GLB. bake-city.mjs check: PASS. asset-pack.py check: PASS, 1,930 present, zero missing or unoptimized.
- Local smoke-clone.mjs against bitmagic dev: PASS, nine stops; zero failed requests, page errors, console errors or unplaced stops.
- git diff --check: PASS.

### Runtime asset changes
**3,870,109 new Git LFS bytes**: Circus exterior GLB, LOD cell cell-0_-3.bin, and LOD manifest. **184/186** geographic/LOD cell files byte-identical; all collision unchanged. Gold Coast and Wyndham LOD blocks drifted during the bake and were restored byte-for-byte without rebaking. Out-of-scope metadata touches: shared asset-pack date/hash entries, active queue, survey/verification records; no unrelated runtime geometry changes.

### Scope and decisions
Other seven mapped buildings, roads, foliage, runtime code and existing interiors remain unchanged. Six prior whole-block gaps remain documented. Lamp size/spacing, roof-seam spacing and material finish are reversible photographic estimates. No claim of photorealism or complete block reconstruction.

### For the release step
CDN upload and published cold-load validation happen before next merges to main. No upload, publishing or release performed.

Closes #35 (explicit closure after merging to next).
