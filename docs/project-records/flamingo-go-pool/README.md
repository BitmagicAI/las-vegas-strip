# Flamingo GO Pool exterior pass

Issue #60 / PR #458 against `next`. Original geometry based on official 2025 opening photographs and published dimensions, with secondary current seating-map and design-rendering references. All source links, inferred dimensions and discrepancies are in research.json.

The new asset adds the main pool and swim-up bar, three VIP pools, grotto/DJ canopy, stepped pool edges, cabanas, umbrellas, loungers and palms. It preserves the existing Flamingo garden, exterior and HGV private pool. This is an exterior pass; no existing interiors are changed.

Source geometry: 13,018 triangles; 6,431 collision triangles. Level and WebP optimization installed. Source mesh audit passed, and all six adjacent model/collision files match their runtime originals. 3,228 packed-collision samples pass across the entrance ramp, eastern promenade and western garden edge. Initial route failures were corrected in this branch: the entrance starts north of the retained arrival structure and cuts through its own deck; the promenade avoids the raised VIP ramp.

Four unchanged baseline cameras and four installed preview images personally inspected. The overview shows the new pool arrangement alongside the retained garden and HGV pool. The western view shows the grotto rear wall under the retained elevated walkway. Furnishing and planting are sparse relative to photographs; exact site elevations and pool outlines are inferred. Static waterfall ribbons and reduced seat/cabana/palm counts remain explicit limitations. The separate family pool and full resort circulation are outside this pass. No photorealistic or whole-resort completion claim.

Final bake/package, movement walkthrough and step 7 results will be recorded before readiness. Published CDN cold-load validation belongs to the owner's release step and does not hold this PR.
