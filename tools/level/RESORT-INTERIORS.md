# Local resort interior pass

Keep all assets local. Do not upload or publish.

Public references (layout relationships, not survey reproductions):
- Caesars property plan: https://www.wyndhamhotels.com/content/dam/property-assets/en-us/ce/us/nv/las-vegas/51490/floor-plans/51490_ce_floor_plans_1.pdf
- Forum Shops directory: https://www.simon.com/mall/the-forum-shops-at-caesars-palace/map/Casino
- Curved escalators: https://mitsubishielevator.com/projects/forum-shops-at-caesars-palace
- Flamingo property plan: https://www.wyndhamhotels.com/content/dam/property-assets/en-us/ce/us/nv/las-vegas/51487/meetings/51487_Flamingo_Sales_Kit.pdf
- Horseshoe casino/mall plan: https://gravislaw.com/wp-content/uploads/2025/09/Horseshoe-Property-Map-2024.pdf
- Paris Le Boulevard/lobby plan: https://www.caesars.com/content/dam/meetings/PDFs/FloorPlans/PLV_Facilities-PropertyMap_Capacities_REV1-13.pdf
- Planet Hollywood casino/lobby/mezzanine: https://www.wyndhamhotels.com/content/dam/property-assets/en-us/ce/us/nv/las-vegas/51494/meetings/51494_Ceasers_Planet_Hollywood_Sales_Kit.pdf
- Miracle Mile: https://www.miraclemileshopslv.com/wp-content/uploads/2024/02/Miracle-Mile-Shops-Leasing-Brochure.pdf

| Resort | Ground-floor coverage and circulation | Upper route |
|---|---|---|
| Flamingo | Entire existing 110 × 44 m block: casino, registration, retail, cafe, garden exit | Stopped escalator to lounge/gallery |
| Horseshoe | Entire 36 × 62 m block: casino, poker, lobby, retail, connection to Paris | Stairs to restaurant landing |
| Planet Hollywood | Expanded 133 × 101 m podium: casino, registration, Heart Bar, Miracle Mile loop, selected shops | Paired stopped escalators to mezzanine |
| Caesars | Preserve casino/service suite; connect northern 84 × 39 m Forum Shops, statues/fountain court and shops | Paired curved escalators to upper arcade |
| Paris | Preserve casino/tower lift; add Le Boulevard shops, registration and north passage to Horseshoe | Stair and upper shopping gallery |
| Cosmopolitan | Preserve full casino/service floor; add registration and selected retail | Interior stair to mezzanine lounge |
| Bellagio | Existing full public podium, lobby, casino, galleries and service suite retained | Existing ground-floor access retained |

All footprints are compressed to the existing district. Ground floors are interconnected public spaces; shops are a curated subset. Floors/ramps/rails/furniture have collision. Doors and route links are audited. Stopped escalators are walkable stairs, not moving belts. Landmark sculptures are original simplified geometry inspired by Roman statuary, not exact scans. No character assets are modified.

## Validation and local review

- Blender normal repair and eight interior renders completed.
- Open-door audit: 237,121 floor probes, 1,428 doorway probes and 65,889 route probes; no failures.
- Closed-door audit: 283,195 enclosure probes; no failures.
- Shared-plane warnings remain (mostly floor/step/shop slab contacts); they are warnings, not navigation failures.
- Type check and local WebGPU verification passed: 1,361 level colliders, 28 total doors.
- Browser review confirms the modeled curved escalators load in the local runtime. Full manual traversal of every new route has not been performed; geometric route audits cover them.
- Review URLs: `?inspect=flamingo`, `horseshoe`, `planet-hollywood`, `miracle-mile`, `forum`, `forum-escalators`, `forum-upper`, `paris-shops` on localhost:3090.
- `resort_interiors.py` rebuilds this pass from `build/interiors/baseline.blend` and companion JSON. That baseline deliberately preserves all previous architecture. Capture a new baseline before adapting this script to later unrelated architectural changes.

## Forum storefront repair

`repair_jeep_forum.py` patches the current level without restoring the older
interiors baseline. It separates shop window/base ends from arch jambs by 4cm,
updates matching base collisions, and fits measured sign meshes between the
jambs. The three arcade shops now read FORUM GIFTS, GALLERIA and BOUTIQUE; the
upper shop reads UPPER BOUTIQUE. The source generator includes the same bounds
and label changes. Run the patch before `export_visibility.py` when rebuilding
the current CityCenter level. Blender and live WebGPU review images plus the
measured clearances are in `build/repairs/`; `?inspect=forum-storefront` is the
local in-game review position.
