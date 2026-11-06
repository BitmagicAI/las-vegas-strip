# Venetian Expo covered approach

The former full-height glass wall now has an open ground arcade with pale columns, recessed glazing, continuous paving and a soffit below the upper window band. This is a scoped exterior improvement. Hall interiors, onward accessible routes, surveyed exterior roof heights/equipment and the opaque Sphere connection remain unresolved.

## Matched daylight views

960×540, DPR1, ultra, neutral daylight, identical cameras; front first. The wide front is partly obscured by an unchanged neighboring building. Entry resolves the arcade. North/east confirm retained roof and service geometry.

### Front

![Before front](../../../public/project-records/venetian-expo-refinement/before/expo-front.png)

![After front](../../../public/project-records/venetian-expo-refinement/after/expo-front.png)

### Entry

![Before entry](../../../public/project-records/venetian-expo-refinement/before/expo-entry.png)

![After entry](../../../public/project-records/venetian-expo-refinement/after/expo-entry.png)

### North

![Before north](../../../public/project-records/venetian-expo-refinement/before/expo-north.png)

![After north](../../../public/project-records/venetian-expo-refinement/after/expo-north.png)

### East

![Before east](../../../public/project-records/venetian-expo-refinement/before/expo-east.png)

![After east](../../../public/project-records/venetian-expo-refinement/after/expo-east.png)

## Movement and performance

241 support and241 capsule samples pass. The installed keyboard walk passes24legs across the approximately262m covered frontage and back. Both endpoint views face adjoining walls; they do not prove onward access. No doors were opened.

Initial p95ms: front56.3→72.6, entry60→63.2, north65.3→62.7, east43.8→44.7. Front's initial29% regression prompted a controlled serial repeat: browser-only interception loaded the old ExpoGLB/collision and old changed cell/manifest for the baseline, confirmed in baseline-hits.json; both runs blocked service workers. Same camera/quality/warmup. Repeat p50 52.5→52.9ms, p95 63.8→64.8ms(+1.57%). The initial spike did not reproduce; all original results remain in performance.json. This is a slow scene, with no60fps or speedup claim. Full perimeter driving, cold-stall and memory benchmarks remain outside this scoped evidence.

See [references](references.md), [decisions](decisions.md), [checks](local-checks.json), [walk](walk/results.json), [preservation](source-preservation.json), and [performance](performance.json).

## Supplemental covered-arcade views

Both installed close views inspected: continuous paving, pale columns, covered soffit and closed recessed glazing. These are additional after-only inspection views, not a before/after performance comparison. p95east17.9ms,west22.9ms; no whole-site60fps claim.

![Covered approach east](../../../public/project-records/venetian-expo-refinement/close/expo-arcade-east.png)

![Covered approach west](../../../public/project-records/venetian-expo-refinement/close/expo-arcade-west.png)
