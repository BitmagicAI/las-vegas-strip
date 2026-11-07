Refine two existing New York-New York exterior details while preserving circulation, landscape, roads and interiors. This is a limited detail pass, not whole-resort completion.

## Per building
- Irish kiosk (#200): original curved dark sign-light fixtures on exposed faces, with inferred spacing/dimensions and no runtime lights. Current official patio gallery corroborates retention of the freestanding kiosk after the October2025 patio renovation; April2025 Street View alone predates that work. Installed GLB621,536bytes;51,744 exported indexed triangles including lettering.
- Arrival (#201): replace17 cylindrical gold crown rays with shallow tapered blades at unchanged endpoints, supported by January2025 Street View. Width .46m and depth .10m inferred. Retain existing canopy, pavilion, CC0 imported trees, island, letters and coaster. Installed GLB12,698,116bytes;275,513 indexed triangles including retained foliage meshes.

## Validation
- Direct Google aerial/Street View and official photos inspected; links, dates and limits in research.json.
- Both scoped-build collision JSON files byte-identical. Roofsupport133kiosk/864arrival samples pass. Kiosk8CPU directions pass. Arrival6CPU directions pass using installed packed coaster collision; original legacy test failed only because raw coaster JSON is absent, retained and resolved by scoped equivalent.
- Both models: level and WebP passes completed before installation (untextured kiosk has no image conversion). Shared bake once;90/92cell binaries byte-identical, only-1_1/-1_2changed. Asserted unrelated GoldCoast/Wyndham LOD differences restored before staging.
- Six matched neutral daylight views inspected, fronts first. Seven actual keyboard routes/14legs pass before and after;14after endpoint/return captures inspected. Initial arrival endpoints at1610.5 faced dark facade; original evidence retained, matched tests end at1613.5 before facade. No rear-entrance access claim.
- Matching p95 ms: kiosk19.2→18.5,22.7→23.3,28.7→18.6; arrival34.1→23.5,21.3→21.2,22.7→23.2. Baseline variance retained; no general speedup claim.
- bitmagic check; city-lazy-lod, city-lighting-resize, site-lights tests; resort record review; optimization gate2/2; bake currency; asset pack check: all pass.
- Nine-stop dev smoke: zero failed requests, page errors, console errors or unplaced stops.
- Publiccheck0failures/15existingwarnings; archive3846files/1108.3MB; diffcheck passed. Board generator run with unrelated historical completion state preserved.

## Decisions for the owner
Fixtures and crown dimensions are reversible approximations. Retain unresolved kiosk terrace grade/broad stairs, parent streetwall ornament and cracked paving; arrival typography, heights, exact ornament and rear frontage; legacy dense coaster supports and full-resort requirements. No unsupported public interior added.

## Out-of-scope touches
Shared cell manifest and release asset manifest; scoped board/record updates; new verification helpers/evidence. No runtime engine changes, road/interior changes, foliage-source edits, CDN uploads or releases.

## For the release step
CDN and published-game checks, owner judgment of exact dimensions/materials and wider resort fidelity. These do not hold this local merge.

Closes #200
Closes #201

## New Git LFS storage
35,983,008 bytes across 46 unique new objects absent from origin/next, including captured evidence and runtime assets. Full audit: docs/project-records/nyny-kiosk-arrival-refinement/lfs-audit.json.
