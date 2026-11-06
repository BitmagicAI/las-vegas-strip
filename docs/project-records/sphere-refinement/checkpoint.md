# Sphere refinement checkpoint

PR522, issue210 claimed by janiverse, branch task/site-sphere from origin/next 81c5a7df0d8815b75c757e1d2ff4f1b4fd547478. Initial checkpoint commit f61d8e99 is pushed.

2026-11-06: Read prior inventory, existing-large audit, AGENTS owner long-run rules, queue and block workflow. Existing Sphere dimensions already match 366 ft × 516 ft; no model/runtime edits are justified by this audit alone. Added lightweight sphere.json and queue entry, retaining all fidelity/circulation/neighbor discrepancies. Separate sphere-garage owns the already reconstructed adjacent garage and service block.

Recovered ignored sphere.json, exterior.json and interior.json from main checkout only after sphere.bin was verified byte-identical. Existing test passes 5879 support/body samples and 6 closed/open door checks against 11 city cells; 10394 authored seats. Six baseline installed daylight cameras captured and visually inspected (front first). Baseline plaza p95 59.7 ms is a real outstanding performance concern, not a 60 fps result. Other views p95 17.7–19.3 ms. Bridge camera is brace-obstructed; bowl camera favors the screen. Original video frame differences are expected.

Official Populous photographs inspected locally without committing them; source links and observations in block record. Accessibility page confirms East/West and Venetian bridge entries. Maps/Street View inspection is still pending. Do not claim that this pass verified it.

Actual keyboard walks running via tools/city-exteriors/walk-sphere-refinement.js, output build/city-exteriors/sphere-refinement-walk-before, log /tmp/sphere-walk-before.log, exec session63848. Five local routes with forward/return legs; wait for report and inspect failures, not just process exit. No second GPU job while it runs.

Passed typecheck, public check (0 failures, 13 pre-existing warnings), city bake check, asset pack (1930 present,0 missing,0 unoptimized), three relevant runtime tests, and changed-GLB check (0 changed). Evidence checks-in-progress.json plus /tmp/sphere-tests.log and /tmp/sphere-optimization.log. No changed GLB means no optimization or revision bump is required. All installed assets remain unchanged.

Next: finish actual walk review; investigate any failed segments; inspect Maps once GPU free; run identical after camera pass and compare performance; run dev smoke; archive evidence; update record/task/PR with every result, scope and LFS byte audit; commit/push only own commits; mark ready and self-merge only after acceptance evidence. Close issue210 explicitly, then picker. Do not mark whole Sphere complete.
