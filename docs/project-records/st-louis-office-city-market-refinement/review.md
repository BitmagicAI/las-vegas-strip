# St Louis office and City Market refinement

Two mapped structures. Six matched daylight views inspected; final12leg walk passed; smoke still running. Not full-block completion.

Building C515: pale tower infills and dark arched surrounds replace green glazing/white surrounds; two shallow layered cornice bands refine the arcade fascia. City Market: narrow central door transom and two non-emitting roof flood housings. No added scene lights, roads or interiors. Existing collision remains unchanged.

See research.md for dated Maps panoramas, official text corroboration, inferred sizes and decisions. Current appearance beyond 2022 imagery remains uncertain. Unsupported interiors, detailed signs/advertisements, landscaping, office forecourt and perimeter driving remain deferred.

Before/after source checks:164 support/headroom samples and12 CPU legs passed. Baseline actual12legs passed; the initial erroneous office height expectation is retained separately. All six matched daylight views inspected. Tower arch surrounds and pale infills are visible; the cornice no longer occludes 515/Building C labels after moving their planes forward. Market transom and two housings are visible. Initial office occlusion evidence is preserved under public/review/st-louis-office-city-market-refinement/first-review/. Level+WebP optimization2/2 passed, one grouped bake plus a second corrective bake for label occlusion,91/92cell bins unchanged with unrelated LODs restored. Bake/pack checks,typecheck,3tests and records passed; public-content check0failures11existingwarnings. Final actual12legs passed and four endpoint images inspected. All six static p95 comparisons improved; smoke and final LFS audit pending.

## For the release step

CDN/published-game checks and owner review of inferred dimensions. No publishing or CDN upload performed.

## Matching performance

960×540,DPR1,ultra;900warmframes,streaming quiet+60settle,180samples/view. Short static samples do not establish sustained60fps or driving performance.

|Building/view|Before p95 ms|After p95 ms|
|---|---:|---:|
|st-louis-office-515 front|20.5|17.7|
|st-louis-office-515 office-rear|19.2|17.8|
|st-louis-office-515 office-aerial|18.9|18.3|
|city-market-liquor front|18.7|18.0|
|city-market-liquor market-rear|19.0|18.8|
|city-market-liquor market-aerial|18.8|18.5|

## Matched views

### st-louis-office-515 front

![Before](../../../public/review/st-louis-office-city-market-refinement/before/st-louis-office-515-front.png)

![After](../../../public/review/st-louis-office-city-market-refinement/after/st-louis-office-515-front.png)

### st-louis-office-515 office-rear

![Before](../../../public/review/st-louis-office-city-market-refinement/before/st-louis-office-515-office-rear.png)

![After](../../../public/review/st-louis-office-city-market-refinement/after/st-louis-office-515-office-rear.png)

### st-louis-office-515 office-aerial

![Before](../../../public/review/st-louis-office-city-market-refinement/before/st-louis-office-515-office-aerial.png)

![After](../../../public/review/st-louis-office-city-market-refinement/after/st-louis-office-515-office-aerial.png)

### city-market-liquor front

![Before](../../../public/review/st-louis-office-city-market-refinement/before/city-market-liquor-front.png)

![After](../../../public/review/st-louis-office-city-market-refinement/after/city-market-liquor-front.png)

### city-market-liquor market-rear

![Before](../../../public/review/st-louis-office-city-market-refinement/before/city-market-liquor-market-rear.png)

![After](../../../public/review/st-louis-office-city-market-refinement/after/city-market-liquor-market-rear.png)

### city-market-liquor market-aerial

![Before](../../../public/review/st-louis-office-city-market-refinement/before/city-market-liquor-market-aerial.png)

![After](../../../public/review/st-louis-office-city-market-refinement/after/city-market-liquor-market-aerial.png)
