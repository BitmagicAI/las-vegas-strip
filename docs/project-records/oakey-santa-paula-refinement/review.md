# Oakey offices and Santa Paula office refinement

Scoped four-structure refinement, not whole-block completion. Dated reference links and inferred dimensions are in research.json and the individual block records.

Oakey west/east roofs now have distinct red-brown/dark-brown materials and darker burgundy banners. The first installed review caught Santa Paula's global material remap turning the east roof gray; explicit roof/fascia arguments now keep materials with their owner. The carport, footprints, roads, collision and interiors are preserved.

Santa Paula's fan crowns have overlapping folded leaves and visible undersides, filling the open waist. The radial foliage remains stylized; street-side palm species, willow-like planting, exact heights/rears, weathering and unsupported interiors remain documented gaps. No third-party photographs or geometry included.

## Matching installed views

960×540, DPR1, ultra, neutral daylight. Front first; camera coordinates in the dedicated probe files and performance JSON.

### oakey-offices front

Before

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/before/oakey-offices-front.png)

After

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/after/oakey-offices-front.png)

### oakey-offices east

Before

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/before/oakey-offices-east.png)

After

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/after/oakey-offices-east.png)

### oakey-offices aerial

Before

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/before/oakey-offices-aerial.png)

After

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/after/oakey-offices-aerial.png)

### santa-paula-office front

Before

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/before/santa-paula-office-front.png)

After

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/after/santa-paula-office-front.png)

### santa-paula-office east

Before

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/before/santa-paula-office-east.png)

After

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/after/santa-paula-office-east.png)

### santa-paula-office aerial

Before

![Before](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/before/santa-paula-office-aerial.png)

After

![After](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/review/oakey-santa-paula-refinement/after/santa-paula-office-aerial.png)

## Verification

900 support samples and12 CPU walking legs passed. Twelve actual forward/return movement legs passed before and after; four after endpoints visually inspected. Nine-stop dev smoke: no failed requests, page/console errors or misplaced stops. Typecheck, three runtime regression tests, record review, public check, optimization, bake freshness and asset pack passed. Two optimized WebP models; one changed cell, other91 cells unchanged. A second grouped bake was required for the caught material defect; first attempt evidence retained.

Extended exact-base browser A/B, five consecutive180-frame windows per view, reversed run order (current then baseline): median-window p95 baseline→current Oakey front37→26.3ms,east18.1→17.7,aerial17.8→17.6; Santa front17.8→17.7,east17.5→18.2(+4%),aerial18.1→18.1. No sustained >10% regression in this comparison. Large earlier front/aerial spikes also occur with baseline assets; root cause not established. All short samples/windows retained; no speedup or sustained60fps claim.

## Decisions for the owner

Keep original folded palm geometry because available foliage tree source is broadleaf. Keep inferred dimensions and existing identities pending stronger sources. No unsupported interior added.

## For the release step

CDN and published-game checks and any person-dependent review remain for release. No uploads, publication or release performed.
