# Proposed task: Hofbräuhaus Las Vegas exterior and public interior

Mapped building: `way/111339182`, 4510 Paradise Road. Present in the 6,162-building index; absent from the earlier 631-building review ledger and block task records searched on 2026-10-26. Mapped footprint area: 1,857.54 m². Existing 6 m height is an unknown-source commercial default, not a measured height.

## Scope
- Inspect the installed shell and audit ownership before replacing it.
- Rebuild the street facade, pitched roof/dormers, entrances, rear/service elevations and immediate yard from public references and editable OSM footprint data.
- Author streamed, walkable main beer hall and indoor beer garden, linked by real openings. Start with documented architectural features; do not invent inaccessible kitchen/back-of-house layouts.
- Keep shared runtime changes minimal and check other open PRs before touching shared files.

## Sources found (2026-10-26; linked, not copied)
- https://www.hofbrauhauslasvegas.com/the-experience/ — official exterior/interior photographs and descriptions; long wooden tables, painted ceilings, indoor garden and bar.
- https://www.hofbrauhauslasvegas.com/about/ — official hall and indoor garden descriptions; garden sky ceiling, circular fountain and six chestnut trees.
- https://www.hofbrauhauslasvegas.com/group-sales/ — official venue photographs. Seating capacity is not a measured floor plan.
- https://lasvegasmagazine.com/dining/2026/jun/15/hofbruhaus-las-vegas-fathers-day-german-beer-hall/ — June 2026 description corroborates dormers, window boxes, arched hall and indoor garden.

## Still required before modeling
Current street/aerial visual inspection, matching installed baseline cameras, footprint orientation, height estimates, entrance locations, internal layout reference and a duplicate-shell/collision removal plan. No claim of a verified floor plan yet.

## Acceptance
Matching installed before/after views under neutral daylight; doorway and return-route walk tests; bounded streamed interior residency; before/after frame timing; no new runtime light set; original or redistribution-licensed textures only; optimized/versioned runtime assets; block and public-release checks pass. Record remaining deviations honestly.

## Coordination
Proposed task ID: `ext-hofbrauhaus`. Create one issue for this scope, obtain its claim assignment before geometry edits, use branch `task/ext-hofbrauhaus`, and create an early draft PR. Owner authorized GitHub task creation and claims. Issue #232 is assigned to janiverse; branch task/ext-hofbrauhaus.
