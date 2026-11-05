# Albo/Dinos and Casino Center courtyard refinement

Four mapped structures; scoped exterior refinement, not full-block completion.

Dino's canopy now has a shallow projecting lower stage and steeper upper stage, with lettering moved to the upper stage. Albo's facade and canopy are preserved in the shared model. Casino Center's north-wing office now has two low planter rims with soil, leaving a2.8m central approach. The southern courtyard wing, galleries, stairs and pool remain unchanged. Planter vegetation, street trees, exact pitches, signs, weathering, parking markings and private/unsupported interiors remain unresolved.

January2026 Street View supports both changes; dimensions remain inferred. Official1520website photos show ribbon-window frontage and lush courtyard planting inconsistent with the current street reference. Their property/era attribution remains unresolved; they were not used to infer current geometry. No third-party imagery committed.

## Installed review

All eight matched daylight views inspected front first. The canopy break and office planter rims are visible. Lettering remains simplified; planters are deliberately unfinished without verified vegetation. Existing repeated windows, stark paving and coarse textures remain limitations. No road or interior changes.

## Validation and limits

Two models optimized with level and WebP passes; changed-model audit2/2passed. One grouped bake;91of92cellbins byte-identical after restoring unrelated GoldCoast/Wyndham regenerated LOD differences. Bake freshness, asset pack, typecheck, three runtime lighting/LOD tests, resort records and public-content checks passed (0failures,11existing warnings).

Existing source support tests:635Albo/Dinos and126courtyard samples passed.16CPUgroundlegs and both stair suites passed before/after. Dedicated42pointoffice source-floor test found missing floor in its JSON subset; discrepancy is retained in office-source-support-discrepancy.json. This was not reported as a floor pass. Supplemental test checks headroom only; actual installed office walks validate support. No runtime ground was added to conceal the discrepancy.

Matching p95 milliseconds: Albo front18.6→19.0, Dinos street17.9→19.0, patio18.7→19.4, aerial18.6→19.3; courtyard front18.9→18.9, inside18.8→19.8, office20.2→19.1, aerial18.4→19.0. Largest increase6.15%; no observed >10%regression.900warmframes, streaming quiet+60settle,180samples/view,960×540DPR1ultra. Static short samples do not establish sustained60fps or driving performance.

Actual after walks and smoke results pending.

## Decisions for the owner

Keep inferred canopy proportions and planter dimensions reversible. Preserve the official-gallery discrepancy instead of importing uncorroborated vegetation. Streets, existing interiors, courtyard access and stairs retained.

## For the release step

CDN/published-game checks and owner review of inferred dimensions and official-photo attribution. No uploads or publication performed.

## Matched views

### albo-dinos-frontage front

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/albo-dinos-frontage-front.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/albo-dinos-frontage-front.png)

### albo-dinos-frontage dinos-street

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/albo-dinos-frontage-dinos-street.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/albo-dinos-frontage-dinos-street.png)

### albo-dinos-frontage dinos-patio

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/albo-dinos-frontage-dinos-patio.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/albo-dinos-frontage-dinos-patio.png)

### albo-dinos-frontage frontage-aerial

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/albo-dinos-frontage-frontage-aerial.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/albo-dinos-frontage-frontage-aerial.png)

### casino-center-courtyard front

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/casino-center-courtyard-front.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/casino-center-courtyard-front.png)

### casino-center-courtyard courtyard-inside

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/casino-center-courtyard-courtyard-inside.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/casino-center-courtyard-courtyard-inside.png)

### casino-center-courtyard courtyard-office

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/casino-center-courtyard-courtyard-office.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/casino-center-courtyard-courtyard-office.png)

### casino-center-courtyard courtyard-aerial

![Before](../../../public/review/albo-dinos-casino-courtyard-refinement/before/casino-center-courtyard-courtyard-aerial.png)

![After](../../../public/review/albo-dinos-casino-courtyard-refinement/after/casino-center-courtyard-courtyard-aerial.png)
