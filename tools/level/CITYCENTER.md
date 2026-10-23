# CityCenter extension — local prototype

Built with `citycenter.py` on the immutable, post-exteriors files in
`build/citycenter/baseline.*`. Do not run the original `vegas.py` to rebuild this
district: it predates the detailed resorts and interiors.

## Placement and scale

Game X points east; negative Z points north. The Strip remains X=0. The expanded
district is X=-520..220, Z=-300..660. Existing resorts and their circulation stay
in place. CityCenter's footprint is compressed to fit the prototype, while its
principal towers retain approximately real-world heights. This is a playable
architectural interpretation, not a survey or an exact tenant-by-tenant plan.

| Landmark | Prototype position / extent | Defining geometry |
|---|---|---|
| Vdara | west of Cosmo, X=-356..-262, Z=210..297 | Three offset curved slabs, 158–169 m, black/white spandrels and curved entrance/pool canopy |
| Aria | west of Crystals, X=-453..-244, Z=341..500 | Interlocking curved glass wings, 169/183 m, white floor bands, screened crowns, rounded porte-cochere |
| Crystals | X=-210..-32, Z=323..470 | Folded stainless roofs, triangular skylights, slanted retail fronts, two-level public arcade |
| Veer East / West | (-125,455) / (-189,421) | 144 m, opposing 5-degree shears, yellow ceramic-frit glass, rooftop pool decks |
| Waldorf Astoria | X=-125..-40, Z=535..621 | 164 m folded tower, vertical bronze/glass shadow boxes, sky-lobby belt, sheltered arrival |

Harmon Avenue crosses south of Cosmopolitan and bends west toward Vdara. Aria
Place enters from the Strip at Z=516 and bends toward the Aria arrival court.
Palms, storefronts, canopies and a static Aria Express guideway frame this view.

## Public circulation

- Crystals: north/south arcade, Boulevard entrance, western branch to Aria,
  twenty simplified retail bays across two levels, two traversable static
  escalators, grand stair, upper balconies, timber Treehouse, sculpture basins.
- Aria: public lobby, large casino floor, north/south promenades and connecting
  corridor from Crystals. Vdara and Waldorf have walkable arrival lobbies.
- Veer: residential towers integrated into the mall roof; the later hotel
  streaming pass adds ground-floor stair entrances inside Crystals and apartments
  on Levels 7–40. Follow the VEER residential signs from the Boulevard or Aria
  Place mall doors; see `HOTEL-STREAMING.md` for the two approach routes.
- Transit is modeled as architecture; the tram does not operate.
- New supply reserve landmarks are layout hooks, not new active mission objectives.

The new rooms use the existing door-driven visibility system. Crystals and the
glazed lobbies are tagged windowed, so their skyline remains visible indoors.
Aria's enclosed casino hides the outside when its doors are closed. Faceted
roof and facade batches carry an explicit `visibilityRole=shell`; they must
remain visible outside even if their geometry lies within an interior volume.
Coarse building hulls feed the existing long-range shadow-caster system.

## References inspected

- User's current map and CityCenter panorama supplied 2026-09-28.
- [Studio Libeskind: Crystals, photographs and design description](https://libeskind.com/work/crystals-at-citycenter/)
- [Simon: live Crystals L1 and L2 map](https://www.simon.com/mall/the-shops-at-crystals/map)
- [Simon: store locations / level and entrance descriptions](https://www.simon.com/mall/the-shops-at-crystals/stores/print)
- [MGM: Aria property map](https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cfa3d9a63f75919/aria-property-map.pdf)
- [Rafael Viñoly Architects: Vdara's three offset arcs](https://vinoly.com/works/vdara-hotel-spa-at-citycenter/)
- [JAHN: Veer Towers, facade and height](https://jahn.studio/work/veer-towers/)
- [Thornton Tomasetti: opposing five-degree leans](https://www.thorntontomasetti.com/project/citycenter-las-vegas-veer-towers)
- [KPF: Mandarin Oriental, now Waldorf Astoria](https://www.kpf.com/project/mandarin-oriental-las-vegas)

All geometry is authored locally. No reference photograph is copied into the
game as a texture. Nothing is uploaded, registered or published to Bitmagic.

## Build / review

1. Blender background run: `tools/level/citycenter.py`.
2. `tools/level/render_citycenter.py`, inspect aerial, Aria Place and Crystals.
3. `tools/blender-level/audit.py` in both open/closed-door modes.
4. `tools/level/export_visibility.py`, copy mesh-level JSON to `src/work`, merge
   doors with `sync_world.py --keep-spawn --keep-terrain`.
5. Bitmagic check / WebGPU verify, then local browser review bookmarks:
   `?inspect=citycenter-exterior`, `crystals-exterior`, `crystals-atrium`,
   `crystals-upper`, `aria-exterior`, `aria-casino`, `vdara-exterior`,
   `waldorf-exterior`.

The GLB version is a content hash generated after successful export, preventing
the browser from silently reusing an older level mesh.

## Validation for this pass

- All 1,366 retained pre-existing colliders and 28 pre-existing doors are unchanged.
- Final full-level open and closed door audits passed: more than 503,000 floor
  probes, 2,268 doorway probes, 91,000 route checks, and 615,000 envelope probes.
- The overlap audit reports construction seam warnings (including existing
  resort geometry); no floor, route, door or envelope failures remain.
- Visibility tests cover the new glazed rooms, enclosed Aria casino and shared
  Crystals–Aria doorway, in addition to all previous resort cases.

WebGPU verify passed on asset revision `743a38c441d2bb21`. Final render
contains 4,923,251 triangles in 510 visibility/material batches. Verification
reported 1,970 physics bodies and stable gameplay. See `build/citycenter/validation.json`.

## Interior surface repair (2026-09-28)

Aria's original tower bottom caps shared Y=14 exactly with the casino soffit.
The flat podium ceilings now have 0.95m thickness, burying those caps above the
visible ceiling. This also corrects the same construction in the Waldorf lobby.
The Aria lobby and Crystals connector reuse their neighboring walls and door
records instead of drawing duplicate partitions.

`surface_geometry.py` emits the visible union of floor and gallery slabs while
retaining overlapping collider boxes for continuous traversal. Crystals' nearly
coplanar tile boxes were redundant with the marble floor and have been removed;
its roof underside now uses the white material on the structural face itself,
rather than a second plane 2cm away.

`audit_citycenter_surfaces.py` probes the actual render geometry at the original
ceiling, wall, and gallery overlaps, independently of the collider audit. All 16
probes pass, along with both full collision-audit modes and 22 visibility cases.
Review bookmarks `aria-ceiling` and `crystals-soffit` reproduce the affected views.

The three upper landing joins are trimmed against the gallery footprint; the
last stair tread no longer draws a face beneath an identical gallery surface.
The render-surface audit reproduced this failure before the trim.
