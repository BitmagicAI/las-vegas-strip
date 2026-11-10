# Santa Paula courtyard and St Louis Square refinement

Six mapped structures; scoped exterior corrections, not whole-block completion.

Santa Paula courtyard: the southern apron extends241.25m² to the retained county sidewalk curve, with zero road/sidewalk overlap. Streaming bounds enclose the addition. Neighbor boundary numerical residual is below1e-6m². Northern courtyard and other two buildings remain intact. Planting pockets, conifers, carport, fine fencing, roof/weathering and inferred rear openings remain unresolved; no residential interiors reconstructed.

St Louis Square: the southern west parapet now has a broad flat raised center and stepped shoulders, while the northern triangular pediment stays intact. The other two mapped structures, circulation and collision remain unchanged. Profile dimensions are estimated from January2026 Street View. Repeated bays, roof subdivisions, planting and current tenant lettering remain unresolved; no new interior access claim.

Original authored geometry only. Dated Maps/satellite links and official address evidence are in research.json. Official site-specific architectural photographs remain unavailable; address evidence is not treated as layout proof.

## Installed visual review

Eight matched daylight views inspected front first at960×540 DPR1 ultra. Curved apron meets the retained sidewalk without covering roads; stepped southern parapet reads separately from northern gable. Existing coarse roof textures, stylized palms, repeated glazing and brick patterns remain visible limitations.

## Performance

900 warm frames, streaming quiet plus60frames,180 samples per view; identical before/after cameras. Largest p95 increase1.68%, no observed >10% regression. Short local measurements do not establish sustained60fps or a speedup. See performance-comparison.json for every result.

## Decisions for the owner

Use the existing county pavement boundary as the reversible apron edge; exact joints/planting pockets remain deferred. Keep stepped profile dimensions inferred, preserving dated source links. No road/interior/runtime code changes. One grouped bake; known unrelated GoldCoast/Wyndham regenerated LOD bytes restored,91of92cells byte-identical.

## For the release step

CDN and published-game checks, owner review of inferred dimensions and inaccessible official photographs. No uploads or publishing performed.

## Matching views

### santa-paula-courtyard front

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/santa-paula-courtyard-front.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/santa-paula-courtyard-front.png)

### santa-paula-courtyard north

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/santa-paula-courtyard-north.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/santa-paula-courtyard-north.png)

### santa-paula-courtyard south

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/santa-paula-courtyard-south.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/santa-paula-courtyard-south.png)

### santa-paula-courtyard aerial

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/santa-paula-courtyard-aerial.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/santa-paula-courtyard-aerial.png)

### st-louis-square-frontage front

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/st-louis-square-frontage-front.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/st-louis-square-frontage-front.png)

### st-louis-square-frontage south

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/st-louis-square-frontage-south.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/st-louis-square-frontage-south.png)

### st-louis-square-frontage plaza

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/st-louis-square-frontage-plaza.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/st-louis-square-frontage-plaza.png)

### st-louis-square-frontage aerial

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/before/st-louis-square-frontage-aerial.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/santa-paula-st-louis-refinement/after/st-louis-square-frontage-aerial.png)

## Local checks

Typecheck passed; three runtime lighting/LOD tests passed. Both models passed level and WebP optimization and the changed-model audit. Grouped bake freshness and asset pack passed.918 courtyard/apron and187 Square support/headroom samples passed. Both CPU route sets passed12legs before/after. Actual installed keyboard walks passed12matched legs before/after plus4new apron legs after; all six after endpoint images inspected. Record review passed; public-content check passed with11pre-existing warnings. Smoke against bitmagic dev passed all9stops with0failed requests,0page errors and0console errors. New unique Git LFS bytes across all own commits:12,062,566bytes in29objects (including proof captures); see lfs-audit.json.
