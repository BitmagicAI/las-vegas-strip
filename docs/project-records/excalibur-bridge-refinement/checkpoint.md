# Excalibur pedestrian corridor ownership review

2026-11-06: Sphere review PR522 merged to next at ab7ecb6335b7d7dee6b92c571fc6bc6898b6ca47; issue210 explicitly closed. Picker selected site-geographic-pedestrian-bridge-visual-replacement-suppressed (#207). Claim confirmed janiverse. Branch created from current origin/next.

Task concerns way/567108272, mapped building=corridor, layer1, unknown5m height,2800.6m², bounds[-125.565,1721.177,-25.917,1815.465], center[-66.7913,1769.8298]. Inventory owner is a descriptive suppression string rather than a normal record key, so picker reports no covering block.

Existing work must be preserved: tools/strip-landmarks/build_excalibur_frontage.py deliberately adds this ID to replacement-ids.json; historical README says duplicate ground-level corridor extrusion removed while raised pedestrian bridge and114 support samples remained. tools/resort-blocks/excalibur.json already mentions this ID in remainingIds and its October14 hall correction. Do not regenerate the removed solid or replay the hall rebuild. Determine whether the fix is ownership bookkeeping plus present-day validation before considering any geometry edits. Preserve all remaining whole-site and full-movement discrepancies.

Next: read full Excalibur record and existing bridge collision/test/probe tools; inspect installed bridge/suppression ownership; current official/Maps references; matched daylight captures and actual walk forward/return with surrounding collision; add or reconcile lightweight record+queue without claiming whole Excalibur. No geometry/runtime edits or GPU jobs started for this task. All prior Sphere GPU jobs finished. Browser tab69 closed.
