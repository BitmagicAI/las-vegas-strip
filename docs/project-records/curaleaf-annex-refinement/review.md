# Curaleaf 1736 and White Cross annex scoped refinement

This pass refines two existing exterior models. Both remain refinement-deferred.

## Changes
Curaleaf: shallow gray rectangular tower panels replace coarse blue strips; an original C/leaf outline replaces the generic loop and unsupported tower wordmarks. Overall tower dimensions and collision remain unchanged.

White Cross annex: the north sign now has clipped corners and a red inset name ribbon with white lettering, based on August 2024 Street View. The west FOR SALE sign remains. Sign dimensions and letterforms are estimates; current north branding is uncertain.

## Decisions for the owner
Retain the existing building envelopes and public approach routes. Keep the dated north sign with an explicit uncertainty; the newest image at that viewpoint remains August 2024. Do not infer public interiors or additions from the architect’s explicitly unbuilt proposal. No third-party imagery is embedded.

## Remaining discrepancies
Curaleaf still needs surveyed tower/side/rear dimensions, more exact emblem/stone/board finishes, a fuller planting layout and reference-supported interiors. Annex tile/board weathering, exact lettering, roof equipment and current north branding remain unresolved. All source collision JSON is byte-identical to the prior version.

## Validation
Source support: 836 Curaleaf and 923 annex samples passed. CPU walks: 12 legs before and after passed. All six baseline views and four baseline walk endpoints inspected. All six corrected after views and four corrected walk endpoints inspected. Twelve actual after legs passed; nine smoke stops placed with zero request, page or console errors. Typecheck, three relevant runtime tests, record review, public scan (seven existing warnings), optimized GLB check, fresh bake and 1930 assets passed. 91/92 cells remain byte-identical. The emblem correction required a second grouped bake; the first attempt and discrepancy are retained. Performance repeat for the aerial outlier is recorded separately.

## Matching views

### curaleaf-1736: front

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/before/curaleaf-1736-front.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/after/curaleaf-1736-front.png)

### curaleaf-1736: north

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/before/curaleaf-1736-north.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/after/curaleaf-1736-north.png)

### curaleaf-1736: aerial

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/before/curaleaf-1736-aerial.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/after/curaleaf-1736-aerial.png)

### white-cross-annex: front

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/before/white-cross-annex-front.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/after/white-cross-annex-front.png)

### white-cross-annex: north

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/before/white-cross-annex-north.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/after/white-cross-annex-north.png)

### white-cross-annex: aerial

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/before/white-cross-annex-aerial.png)

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/curaleaf-annex-refinement/after/white-cross-annex-aerial.png)

Curaleaf aerial corrected first run p95 23.4ms versus 21ms baseline (+11.43%); identical-camera repeat p95 18.5ms. Both retained. Other corrected p95 values 17.9–19.3ms. Baseline north views were unusually slow; no speedup or sustained60fps claim. Cold stalls, memory, draw calls and separate CPU/GPU spans were not measured.
