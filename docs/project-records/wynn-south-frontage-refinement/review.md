# Wynn South Gate canopy detail review

Four matching neutral daylight cameras, front first. January2025 imagery supports seams, trim joints and stone courses; geometry is original and dimensions inferred. Preserve larger podium, roof elevations, arches, interiors and collision. Full block, exact relief and ceiling details remain incomplete.

## front

![Before front](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/before/wynn-south-front.png)

![After front](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/after/wynn-south-front.png)

## roof

![Before roof](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/before/wynn-south-roof.png)

![After roof](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/after/wynn-south-roof.png)

## under

![Before under](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/before/wynn-south-under.png)

![After under](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/after/wynn-south-under.png)

## pier

![Before pier](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/before/wynn-south-pier.png)

![After pier](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/after/wynn-south-pier.png)

## Existing route discrepancy

The original straight route hits an existing pier. A westward detour passes all10baseline keyboard legs with return. No collider was changed. The old source-only audit also loses ground and is retained as a failed diagnostic.

![Original route blocked](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/baseline-walk/direct-route-blocked.png)

Final installed detour passed all10keyboard legs and returned. Endpoint and return captures inspected; they face the retained podium, so the matched canopy views show the architectural detail. No new doorway or interior access claim. Nine-stop dev smoke passed with zero failed requests, page errors, console errors or misplaced stops.

All four installed views inspected. Roof seams and arch/pier joints are visible; larger podium, flat ceiling and terracotta relief remain simplified. No new obstruction or facade break observed.

Static p95 milliseconds before→after: front19.4→17.8,roof19.6→17.5,under21.4→17.8,pier19.3→17.5. No static p95 regression; samples are not a speedup or sustained60fps claim.

![Walk endpoint](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/walk/walk-frontage-0.png)

![Walk return](https://github.com/BitmagicAI/las-vegas-strip/raw/b80d20e945221e01d9c7dca84775eace8da115cf/public/project-records/wynn-south-frontage-refinement/walk/walk-return-0.png)
