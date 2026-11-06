# Excalibur pedestrian corridor ownership review

2026-11-06: Sphere review PR522 merged to next at ab7ecb6335b7d7dee6b92c571fc6bc6898b6ca47; issue210 explicitly closed. Picker selected site-geographic-pedestrian-bridge-visual-replacement-suppressed (#207). Claim confirmed janiverse. Branch created from current origin/next.

Task concerns way/567108272, mapped building=corridor, layer1, unknown5m height,2800.6m², bounds[-125.565,1721.177,-25.917,1815.465], center[-66.7913,1769.8298]. Inventory owner is a descriptive suppression string rather than a normal record key, so picker reports no covering block.

Existing work must be preserved: tools/strip-landmarks/build_excalibur_frontage.py deliberately adds this ID to replacement-ids.json; historical README says duplicate ground-level corridor extrusion removed while raised pedestrian bridge and114 support samples remained. tools/resort-blocks/excalibur.json already mentions this ID in remainingIds and its October14 hall correction. Do not regenerate the removed solid or replay the hall rebuild. Determine whether the fix is ownership bookkeeping plus present-day validation before considering any geometry edits. Preserve all remaining whole-site and full-movement discrepancies.

Next: read full Excalibur record and existing bridge collision/test/probe tools; inspect installed bridge/suppression ownership; current official/Maps references; matched daylight captures and actual walk forward/return with surrounding collision; add or reconcile lightweight record+queue without claiming whole Excalibur. No geometry/runtime edits or GPU jobs started for this task. All prior Sphere GPU jobs finished. Browser tab69 closed.


PR523 draft created. Baseline work now staged for review (not merged): added excalibur-pedestrian-bridge.json and queue entry; inventory way/567108272 reviewEvidence now points to this record with priorReviewEvidence retained. Board generation confirms ext-excalibur-pedestrian-bridge covers it and duplicate site task disappears; unrelated generated board/index changes restored, only own task row updated.

Five before cameras complete and inspected, front first. Files build/city-exteriors/excalibur-bridge-refinement-before and public/review/excalibur-bridge-refinement/before-*.png. Elevated glass-railed decks and lower arcade exist; diagonal shot shows colored roof/deck sightline overlap needing ownership/reference investigation before visual-completion claims. No geometry/runtime edits. Existing114 floor samples pass. New audit-excalibur-bridge-body.mjs reads packed city cells plus Excalibur frontage/highrise colliders, checks114 floor and114 capsule locations:0failures. Durable bridge-samples.json preserves original sample input. Typecheck, records, bake,asset pack,3runtime tests,changedGLB check pass; final checks remain pending.

GPU job session19810 running actual keyboard walks, five bridge/stair route pieces forward/return, output build/city-exteriors/excalibur-bridge-refinement-walk-before and /tmp/excalibur-bridge-walk.log. Do not start another GPU/browser job concurrently. Inspect passed AND each segment report after completion. Source lines from official current MGM property-map PDF rechecked; Maps current visual revisit still pending. Existing historical references are labeled as prior observations, not this pass's inspection.

Next: finish walk, investigate failures/roof overlap with current references, matched after cameras+smoke, final record/PR/LFS checks. Do not recreate suppressed way567108272 shell or claim full bridge-to-casino continuity from local segments.
