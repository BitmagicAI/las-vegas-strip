# Fashion Show northern restaurant frontage

Original outward-raked glazing, joined corner mullions and a broad projecting soffit improve the northern east frontage. Official landlord photography and Oct2026StreetView support the form;2.2m upper offset and approximately.8m eave remain inferred. The groundportal,galleria,stairs,plaza,Cloud and anchorroofvolumes are retained. Fine corner framing, central flat entryassembly, restaurantinteriors, landscaping and exact branding remain incomplete.

All six installed matched neutral daylight views inspected,960×540,DPR1,ultra. Front first; restaurant closeview resolves the actual change. East aerial has an unchanged signpost occlusion. North-entry view shows Nordstrom, not MacysMen.

## front

![Before front](../../../public/project-records/fashion-show-refinement/before/fashion-front.png)

![After front](../../../public/project-records/fashion-show-refinement/after/fashion-front.png)

## upper-plaza

![Before upper-plaza](../../../public/project-records/fashion-show-refinement/before/fashion-upper-plaza.png)

![After upper-plaza](../../../public/project-records/fashion-show-refinement/after/fashion-upper-plaza.png)

## east

![Before east](../../../public/project-records/fashion-show-refinement/before/fashion-east.png)

![After east](../../../public/project-records/fashion-show-refinement/after/fashion-east.png)

## north-entry

![Before north-entry](../../../public/project-records/fashion-show-refinement/before/fashion-north-entry.png)

![After north-entry](../../../public/project-records/fashion-show-refinement/after/fashion-north-entry.png)

## roof

![Before roof](../../../public/project-records/fashion-show-refinement/before/fashion-roof.png)

![After roof](../../../public/project-records/fashion-show-refinement/after/fashion-roof.png)

## restaurant

![Before restaurant](../../../public/project-records/fashion-show-refinement/before/fashion-restaurant.png)

![After restaurant](../../../public/project-records/fashion-show-refinement/after/fashion-restaurant.png)

## Performance and scope

p95ms front18.2→18.2,upper18.8→17.2,east17.9→17.3,north24.3→23.6,roof18.1→19.2,restaurant19.1→18.8. No regression above10%; north remains above16.7ms. No speedup or sustained60fps claim. Full driving/streaming,cold stalls and memory benchmarks remain unverified.

Source checks:2956roof+183stairs/plaza support/headroom and97rakedskin/outwardcapsule samples pass. Source proof retains all existingcollision,labels and unrelated sourcegroups. Final installed keyboard walk passed all 82 legs: both plaza stairs and terrace (20), preserved ground portal/galleria (6), and two local northern facade approaches (28 each), each with return. No door interaction events were required. All eight endpoint/return captures inspected; plaza endpoints face across the road, so the height trace and upper-plaza comparison supply terrace evidence. The temporary mid-route screenshot was overwritten by later routes and is excluded; the script now limits that capture to the plaza route. The northern walks are local segments, not the complete perimeter. Nine-stop dev smoke passed with zero failed requests, page errors, console errors or misplaced stops.

See [references](references.md),[decisions](decisions.md),[geometry](geometry.json),[performance](performance.json),[cell preservation](cell-preservation.json).

![Walk endpoint 0](../../../public/project-records/fashion-show-refinement/walk/walk-frontage-0.png)

![Walk return 0](../../../public/project-records/fashion-show-refinement/walk/walk-return-0.png)

![Walk endpoint 1](../../../public/project-records/fashion-show-refinement/walk/walk-frontage-1.png)

![Walk return 1](../../../public/project-records/fashion-show-refinement/walk/walk-return-1.png)

![Walk endpoint 2](../../../public/project-records/fashion-show-refinement/walk/walk-frontage-2.png)

![Walk return 2](../../../public/project-records/fashion-show-refinement/walk/walk-return-2.png)

![Walk endpoint 3](../../../public/project-records/fashion-show-refinement/walk/walk-frontage-3.png)

![Walk return 3](../../../public/project-records/fashion-show-refinement/walk/walk-return-3.png)
