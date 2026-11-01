# 2650 Westwood

Issue439 assigned janiverse. Branch starts from origin/next 405e0d3 after PR438 merged. Scope: mapped way/464694101. Reference study precedes original exterior geometry; assess adjacent unclaimed buildings for a grouped install. No public interior evidence yet. Broker brochure is unavailable (HTTP410), so continue with dated Street View and broker listing photographs. No waiting on the owner, no release uploads.

## Group scope and reference findings
PR440 targets next; issues439 and441 assigned janiverse. Include way/464694101 (2650 Westwood), way/464694099 (low Highland Steel storefront), way/464694100 (taller adjoining Creel complex). January2026 Street View corrected the initial business-pin interpretation before modelling. All three are still coarse shells, not existing replacement assets; no overlapping open claim found.

Westwood: white scored masonry, dark cap, two roof heights, inset brick/glazing bands, dry planting. Highland: low cream storefront, barred ornamental displays, entrance and delivery bay. Creel: tall beige walls with blue-grey bands and cap, palms and evergreen. Dimensions are estimates from mapped footprints and images. Consider a small customer display/entry area based on August2019 photos; exact room layout and current condition are not established. Preserve this uncertainty and do not open the whole warehouse as public.

## Source pass
Original geometry exported for all three buildings and a separate Highland customer display interior. Source review images inspected locally. Fixed Creel front framing and added review-only ceiling lights to make the interior inspection legible; runtime lighting uses the existing interior light pool. 1,233 source floor samples pass, with no body-width route obstructions. Placement audit found no neighbouring shell overlaps and no exterior cameras inside mapped volumes. Seven matched baseline views captured before the grouped install. Remaining: optimized installation, bake, installed views and movement, package and local step-7 gates. Creel planting and detailed unseen elevations remain discrepancies, not completed features.

## Installed pass
All seven matching daylight views inspected. Public display entry and counter approach, both Westwood frontage paths and Creel frontage passed normal movement in both directions (14 segments). Matched p95 frame intervals: before18.3–19.1ms, after18.2–18.7ms at960x540 ultra, single local run per view. Only cell0,-4 changes in geometry/collision/LOD; all other cells byte-identical. One grouped export and stable-input bake; all four new models optimized including WebP. Package:1924 present,0 missing,0 unoptimized;15 new LFS objects total4,628,636bytes. Global smoke remains the last running local gate. CDN/published validation belongs to release, not this merge.

## Smoke follow-up
First global smoke reached all9stops with0failed requests and0page errors (exit0), but logged one async render-pipeline creation error naming existing Paris carpet. Saved the complete report as smoke-first-run.json and started a clean repeat before calling this gate verified. No renderer code changed.

## Merge gate
Clean smoke repeat passed all nine stops with zero failed requests, page errors or console errors. The first run remains preserved; no recurring error established. Every local step-7 gate passes. Published/CDN validation remains solely in the release step. PR440 can merge to next; close issues439 and441 explicitly.
