# Sphere review checkpoint

PR522, issue210, branch task/site-sphere; base81c5a7df0d8815b75c757e1d2ff4f1b4fd547478. Scoped audit complete, merge pending. Geometry/runtime/city cells unchanged. This creates the missing lightweight record and records discrepancies; it is not a mesh upgrade or whole-block completion.

Official architect images, current official access guidance, satellite and Jan2025 Sands Street View inspected and linked in sphere.json. Six matched before/after captures inspected. Collision checks5879+doors6 passed;28 actual local walk legs passed;9-stop dev smoke clean. Final checks.json, performance-comparison.json and runtime-audit.json retain evidence. Plaza remains slow (p95 59.7→61.3ms); other views17.7–20.5ms. No >10% measured regression and no 60fps claim. Full bridge/perimeter, exact interiors/seat capacity, canopy/facade fidelity and unowned neighbors remain deferred.

Next: commit final evidence, calculate all-own-commit unique LFS bytes, update PR522 with exact scope/checks/Decisions/For release step, fetch and verify only own commits, push, ready, merge --merge --match-head-commit. Explicitly close210, picker and new branch from current origin/next. Never merge main or upload CDN/publish.
