# Rexford / Casino courtyard refinement

Three mapped buildings in two assets receive scoped changes. Rexford/Ellen adds cream piers framing its decorative street screens, following January2026 Street View. Casino Center1520 gets property-specific dark gallery rails and blue-gray gallery coating, following operator courtyard photos.

This is a partial exterior refinement. The operator photos reveal denser planting and a different courtyard arrangement than the inferred Casino model. That discrepancy remains explicitly recorded; the existing layout is not validated by this pass. Pool surround, planting, materials and precise dimensions also remain incomplete at Rexford. No private apartment interiors added.

## Local verification

Both property-specific exporters preserve the existing street-tree LODs; 27 Rexford and15 Casino tree-node metadata/transforms match the base. Both GLBs optimized with level and WebP passes before installation. One grouped city bake; unrelated Gold Coast/Wyndham LOD regenerated differences restored.90/92 cell binaries unchanged, only2_-5 and2_-6 changed. Source collision bytes identical for both assets.

Typecheck and3regressiontests pass. Optimization2/2, bakefreshness, assetpack1930present/0missing/0unoptimized pass. Stage5copied1925unchanged0removed. Resortrecords pass; publiccheck0failures11existingwarnings.

New reproducible4116roofsupport samples pass before/after,24CPUground and18CPUstair/gallery legs pass. The old ignored736/412sample sets were unavailable; the new count is not a reproduction claim.42actual keyboard walking/stair legs passed before;10endpoint images inspected. All six matched afterviews inspected: piers and scoped gallery coating/rails visible; existing trees preserved. All42 actual after walking/stair legs pass;10 endpoint images inspected. Nine-stop smoke passes with zero request/page/console errors.

## Decisions for the owner

Piers inferred .48m wide,.18m deep,5.84m high around existing screens. Gallery color estimates are scoped to Casino; shared Rexford helpers retain their original appearance. Preserve tested circulation while documenting operator-photo layout disagreement. No whole-block, photorealism or sustained60fps claim.

## Out-of-scope touches

Necessary shared cellmanifest/assetpack, queue/task records, scoped builders/probes. No roads, terrain, runtime rendering code, existing interiors or foliage layout changes.

## For the release step

CDN/published-game checks and owner review of inferred dimensions/layout. No publishing, CDN upload, release or main merge.

## Matched views

### rexford-ellen-courtyard front

![Before](../../../public/review/rexford-casino-courtyard-refinement/before/rexford-ellen-courtyard-front.png)

![After](../../../public/review/rexford-casino-courtyard-refinement/after/rexford-ellen-courtyard-front.png)

### rexford-ellen-courtyard roof

![Before](../../../public/review/rexford-casino-courtyard-refinement/before/rexford-ellen-courtyard-roof.png)

![After](../../../public/review/rexford-casino-courtyard-refinement/after/rexford-ellen-courtyard-roof.png)

### rexford-ellen-courtyard court

![Before](../../../public/review/rexford-casino-courtyard-refinement/before/rexford-ellen-courtyard-court.png)

![After](../../../public/review/rexford-casino-courtyard-refinement/after/rexford-ellen-courtyard-court.png)

### casino-center-1520 front

![Before](../../../public/review/rexford-casino-courtyard-refinement/before/casino-center-1520-front.png)

![After](../../../public/review/rexford-casino-courtyard-refinement/after/casino-center-1520-front.png)

### casino-center-1520 roof

![Before](../../../public/review/rexford-casino-courtyard-refinement/before/casino-center-1520-roof.png)

![After](../../../public/review/rexford-casino-courtyard-refinement/after/casino-center-1520-roof.png)

### casino-center-1520 court

![Before](../../../public/review/rexford-casino-courtyard-refinement/before/casino-center-1520-court.png)

![After](../../../public/review/rexford-casino-courtyard-refinement/after/casino-center-1520-court.png)

Matching 960x540DPR1ultra,900warm+streamquiet60settle,180samples/view. Maximum p95 increase3.30% (Casino roof18.2→18.8ms); other five views below baseline; see performance.json. Static samples do not establish sustained60fps, cold-streaming or full driving performance.
