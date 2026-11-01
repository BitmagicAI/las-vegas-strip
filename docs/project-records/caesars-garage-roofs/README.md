# Caesars parking structures

Issue #59, based on next bf0ee10. Scope: the two mapped self-parking roof decks, original parking markings and roof details. Preserve all towers, pool architecture, interiors, roads and existing collision. Inspect installed baselines before choosing exact placement. Reference dates and uncertain dimensions are in research.json.

Garage internal ramps and public ground-to-roof access remain unverified; this exterior pass must not claim full circulation. Local step7 checks precede merge. CDN/published validation is part of the owner release step.

Installed preview: all four fixed daylight views personally inspected. Both previously blank roofs now have clipped diagonal parking rows, three service housings, eight static pole fixtures and a western mechanical bank. Front remains the existing public frontage beneath the bridge; no facade change. Original geometry adds 6,726 triangles, replacing only 13 roof triangles in two nodes. All 179 other nodes and all 12,006 existing collision triangles are preserved; rooftop fixtures add 324 collision triangles. Packed collision audit passes 1,785 samples, including 213 terrain-supported frontage samples that require the movement check.

The 23 m roof height is retained from the installed model, not newly surveyed. Stall pitch, equipment and housing dimensions are inferred. Ground-to-roof access and garage internal ramps are explicitly outside this pass; rooftop movement begins with a testing teleport and is not proof of public access. January 2025 facade grille observations require ownership and height reconciliation before a separate facade replacement. Existing road, bridge, towers and interiors remain intact.

Rebuild from the saved pre-pass caesarsExterior GLB and collision JSON in .bitmagic/city-exterior-backups/caesars-garage-roofs: run caesars_garage_roofs.py, export_caesars_garage_roofs.py in Blender, install-caesars-garage-roofs.mjs, pack collision, optimize level and WebP, then install. No geographic face-removal export is needed.
