# City exterior reconstruction — 12 October 2026

Status: in progress. No city-wide completion claimed.

Scope: every remaining large mapped building, plus all mapped footprints within 200 m of Las Vegas Boulevard. The current inventory contains 613 features, including scope expansions; 265 still need visual audit after the LINQ podium/parking review. All original large-tower rows have had an exterior review, but podiums and smaller buildings remain. Inventory rows are overlapping mapped features, not independent complete resorts. The inventory JSON and block records are authoritative for current coverage.

Current block: Luxor arrival, podium and service-building review. Existing Forum Shops detail discrepancies and interior work are retained; the creator’s new request prioritizes remaining exterior shells city-wide.

References accessed 2026-10-12:
- Google Earth: https://earth.google.com/web/search/Planet+Hollywood+Las+Vegas/ — satellite dated 2022-11-09, 3D view inspected. Bent main hotel wing, projecting end caps, pool terraces, theatre roof, mall footprint and garage.
- Caesars official photograph: https://s202.q4cdn.com/508919455/files/images/fact-sheets-images/PlanetHollywoodResortCasino/2024/Planet-Hollywood-Resort-Casino_Exterior-rgb-v2.jpg — tower crown, curved screen housings, signage and glazing, directly visually inspected.
- Miracle Mile official north entrance image: https://kyl746.media.zestyio.com/mms_north-entrance-5.f1cb27a519bdb5b6ed34049a5b86e317.jpg — directly inspected: raised Cabo Wabo terrace, stairs/escalators, Urban Outfitters curtain wall, red mall entrance, silver Sephora/M tower.
- January 15 2026 diagrammatic leasing plan: https://www.miraclemileshopslv.com/wp-content/uploads/2026/01/MMS-Lease-Plan-Jan-2026.pdf — tenancy and access relationships; landlord explicitly labels dimensions approximate.
- https://www.themorsegroup.com/miracle-mile-shops/ — electrical contractor’s exterior reference.

Images are visual references only, not game textures. Architectural bay dimensions/elevations remain estimates; OSM footprint determines horizontal registration. Existing gameplay/interior datum stays unchanged. No roads or interiors regenerated.

Baseline: build/city-exteriors/baseline, 1273×720 ultra, four fixed cameras. Median frame times 17.6 / 16.7 / 16.7 / 16.6 ms; p95 18.8 / 17.9 / 17.3 / 18.2 ms. These fixed views do not establish route performance or cold streaming.

Open: tower facade/crown, west ownership/entrance collision audit, full site roof and service treatment, installed screenshot inspection, same-route performance, remaining city inventory. No pass is complete yet.

Planet Hollywood installed review: `build/city-exteriors/planet-final` (four matching cameras). Corrected the tower window start after the first tower review exposed an over-wide blank zone. Main entrance has 132 clear half-metre samples through combined city, retained legacy and new exterior collision. New terrace/stairs pass ray-height checks. TypeScript check passed. Fixed views: p50 17.8/16.7/16.8/16.7 ms, p95 19.5/17.5/18.8/17.8 ms; no measured view exceeds the baseline by 10%. This is not a driving benchmark.

Adjacent Harmon Corner reference: https://www.harmoncorner.com/ inspected directly, image labelled “Harmon Corner Daytime June 2026.jpeg”. Three retail levels, continuous curved LED screen (owner says 60 ft tall), white bands, green glass, upper restaurant terraces, Bubba Gump/Rainforest Cafe/Sugar Factory lettering. Current owner text says renovations and some Q3/Q4 2026 openings: tenant fit-out is not assumed complete from text alone. Exterior screen design is original non-advertising artwork. Floor heights and terrace depth are estimates. Existing bridges/roads/interiors retained.

## MGM Grand and its Showcase frontage — active

Google Earth at 36.10255,-115.16918 (imagery labeled 2022–2024) established the stepped tower, nested octagonal arrival roof, Mansion tile wings and glass atrium. Official MGM gallery/map and the three existing local MGM photographs establish material identity and circulation. Installed 108,109-triangle / 115-batch architectural pass; 308 collision triangles. All 8,478 existing non-building mesh groups are byte-equivalent after normalized JSON hashing. Added `--preserve-surfaces` to city export to skip unrelated historical recut hooks during building-only exports. Canopy's 81 capsule samples pass. Fixed view median 16.6–16.8 ms; p95 17.9–18.3 ms versus baseline 17.5–18.2 ms. This is not full-site completion: lion sculpture, exact entrance artwork, pool gardens and additional entrance walks remain open.

Showcase research: https://theshowcasemall.com/site-map and https://www.wwglass.com/project/showcase-mall-world-coca-cola/ ; installer image inspected in browser (2016 page, older tenants). Google Earth at 36.1038,-115.1725 (2022 imagery) corroborates parcel and bottle placement, barrel atrium, northern separate retail parcel. Permanent structure prioritized; branding uses current tenant names and original typographic artwork, not copied advertising. Showcase first geometry pass awaits installed visual review.

MGM courtyard review exposed a missing surface in the villa ring; added bounded courtyard paving, beds and central basin (garden dimensions inferred, not surveyed). Extended ground substrate beneath the Mansion drive edges. Showcase installed views inspected: storefront/bottle/atrium are visible, typography and major sculptural signs still approximate. Local WebGPU verification passed: 55 host fps, 4.1 s settle; not a driving benchmark.

## Park MGM — installed review
Tower pale punched-window elevations and olive caps replace the generic grid. Podium generic green treatment replaced with bowed glazing and pale theatre fascia; existing public entry preserved, southern Eataly structure and CVS storefront added. Google Earth 36.1041,-115.1757, imagery 2022-11-09, plus Marriott official photo29 provide references. Tower height remains mapped110m; bay and trim dimensions estimated. Theatre roof revised again after aerial inspection exposed a wrongly circular outline. 131127 triangles/44batches. Existing collision byte-identical;80 entry-centre samples clear in combined city/podium/interior static collision. Initial installed fixed cameras remain16.6–16.7ms median,17.8–18.5ms p95, near baseline. Not complete: planting/pools, exact details and final roof revision aerial review pending.

### Luxor facade pass and filtering correction

Installed `luxorExterior` covers the surveyed stepped wings, north podium, and pyramid. Google Earth (2022-11-09 imagery) established pale stepped ends and bronze horizontal glazing. The first fine geometric grid shimmered after compression. A disjoint-face attempt remained visually noisy and cost 215,292 triangles, so it was discarded. The installed version uses mipmapped glass joints: 6,423 triangles / 13 authoring batches, about 0.09 MiB optimized. Reviewed `build/city-exteriors/luxor-textured/` from four fixed views. The main pyramid face is clean; side-face distant stippling still needs separate shadow/LOD investigation. Sphinx, arrival, service structures and landscape are NOT complete. Public model searches did not find a verified suitable Las Vegas replica; no unlicensed model was installed and no asset uploaded.

### Mandalay Bay / W exterior pass

Reference: https://earth.google.com/web/@36.0921,-115.1740,730a,800d,35y,270h,55t,0r (imagery 2022-11-09 through 2024-03-05). Observed white vertical piers on gold towers, mint entrance roofs, convention roof solar arrays, pale arched conference front. Heights use existing survey; canopy pitch, pier spacing and panel array spacing are estimates. `mandalay_bay.py` / `build_mandalay_bay.py` install 49,298 triangles in 34 material/source batches. Existing tower collision remains; both guest entrance cuts are preserved. Only the obsolete mapped arrival solid `way/364846553` was replaced, with open roof/support collision. 123 Rapier walking-clearance samples pass. All 8,478 non-building city mesh groups are unchanged. `export_city.py -- --preserve-surfaces` is required for building-only exports.

Installed views: `build/city-exteriors/mandalay-final/`; local WebGPU verify passed at 60 host fps at spawn, not a whole-city performance guarantee. The first before/after probe overlapped verification and is not suitable for strict performance comparison; use the final probe. Pool water/landscape, service details, exact crowns and final fine architectural fit remain unresolved. No full-site completion claim.

PBR mapping now explicitly recognizes the new PH/MGM/Park/Mandalay stone and pale facade material names. This mapping change follows the captures above and needs a refreshed visual check. Preserved the existing scanned-material pipeline rather than adding shaders or lights.

Current active block: New York–New York; initial Google Earth streetwall reference inspected and baseline capture started. The city-wide inventory is still unfinished. Do not treat these partial resort passes as completion of the user's all-buildings request.

## New York–New York installed pass
30855 triangles /22 batches; north podium, garage and existing miniature streetwall details installed and visually inspected. Skyline/coaster/interiors/collision retained. Exact streetwall proportions and Art Deco northeast corner remain approximate. Compressed asset installed after repairing optimizer inventory refresh. Typecheck passed; isolated frame p50 ~16.7 ms/p95 17.4–18.4 ms. Active block now Excalibur.

## Excalibur installed pass
Corrected dark castlebrick to pale limestone; 39622 triangle/15 batch low-rise/station facade pass. Removed duplicate ground-level corridor extrusion way/567108272; existing raised bridge preserved,114/114 floor support samples passed.8478 nonbuilding mesh groups unchanged. Final corridor visual inspected. Exact castle details and landscape remain approximations. Active block: Fontainebleau.

## Fontainebleau installed exterior pass
13958 triangles/27 batches, ~0.30 MiB compressed. Official Level 1 and Level 3 plans and 2025 arrival photograph guided podium, canopy, pool shapes. All four initial views and revised aerial inspected; typecheck passed;129 roof support samples passed. Upper terrace circulation, landscaping and fine facade/roof fidelity remain incomplete. Dimensions explicitly estimated in block record. Active block: Resorts World.

## Resorts World installed pass
11788 triangles/32 batches,0.42MiB optimized. Enclos built photograph and Earth2022–24 guided bronze/red tower and finned podium. Official Level5 map guided pools at estimated20m. Four initial installed views and final aerial reviewed;591 support tests passed;typecheck passed. Landscape, furnishings and public deck access incomplete. Active block: Circus Circus.

## Circus Circus installed pass
42242 triangles/43 batches,1.52MiB optimized. Earth2022–24 guided tower/window colors, casino tent and Adventuredome. Corrected circular roof ridge to mapped elongated plan after review. Final aerial and corrected street camera inspected. Fixed views16.6–16.7ms median/17.6–17.9ms p95; initial west camera invalid (inside motel). Exact frontage, signs, landscape and dome glass refinement remain. Active block: SAHARA.

## SAHARA installed pass
16275 triangles/44 batches,.50MiB optimized. OfficialMay2026map and Earth2022 guided two absent tower silhouettes, canopy, pool, garage and facade. Four installed views inspected.8478 nonbuilding groups unchanged.85 canopy samples have no new obstruction; four retained approach edge/slope contacts remain unresolved. Typecheck passed. Detailed tenant-frontage, secondary pools, planting and precise architectural fit remain open. Active block: STRAT.

## North Strip continuation
STRAT, HGV Boulevard, Sky and Allure passes are installed and inspected. Their block JSON records contain source URLs, estimated heights, screenshots and remaining discrepancies. HGV's two tower heights and low central pavilion were separated; Sky's erroneously tower-height podium was lowered. Selective collision adjustments preserve existing guest interiors. Allure glass guards are excluded from the generic scanned-metal mapping. Local WebGPU verify after Allure passed at 56 host fps at spawn; this is not city-wide performance evidence.

Turnberry Towers: 106889 triangles / 17 batches / 1.74 MiB compressed. Google Earth front/rear inspection guided curved glazing, white rear walls, projecting balcony bands and 18m estimated shared garage. Pool courts initially overlapped Karen Avenue; corrected installed court capture confirms they now sit inside the site. Planting, arrival and precise facade/roof fit remain open.

Turnberry Place: 344219 triangles / 22 batches / 6.21 MiB compressed. Four mapped towers retain their orientation and guest cores; rounded projecting terraces, white wall divisions, pale blue crowns and lower clubhouse/pavilion exteriors installed. All three revised views inspected; typecheck passed. Roof shape and club massing still approximate; pools, gardens and detailed entrances unfinished.

Current active block: Westgate. First three installed views reviewed and curved facade ribs corrected. Final pool/roof review in progress. The city-wide task is still incomplete: do not claim all buildings finished, nor treat deferred block refinements as passed gates.

SpringHill Suites: installed 17494 triangles/15 batches/0.27MiB. All three final game views inspected. Typecheck passed. Punched-window facade, garage, roof pool and enclosure present; arrival signage, canopy fit and furnishings remain unfinished. City-wide work continues.

Trump: narrow mapped195m tower separated from16m podium; 8102 triangles/15 batches/.18MiB. Three installed views inspected,45 arrival clearance samples pass, typecheck passed. Pool landscaping/enclosure and fine entry detail unfinished. WebGPU smoke check after SpringHill passed at58hostfps atspawn, not city-wide proof.

Wynn/Encore installed pass: 37049 triangles/68 batches/.66MiB. All six initial/revised game views inspected; official map rendered and inspected. 755 roof support samples pass; typecheck passed. Lower site remains sparse; Lake of Dreams, landscaping, detailed signs, furniture and route checks unfinished.

Mirage pass: 19,550 triangles / 23 batches / 0.43 MiB. Tower, low podium, dome and garage installed; obsolete future guitar footprint removed with building-only background rebuild. Lagoon and arrival reserve added and reviewed. 475 roof samples and typecheck pass. Crater, lagoon landscape and full routes remain deferred; Elara is next active.

Elara pass installed and all three final views reviewed. Tower separated from low canopy; mapped 183m retained. 10,319 triangles / 16 batches / 0.34 MiB. 36 collision clearance samples and typecheck pass. Pool and canopy estimates, sign readability, landscape and facade calibration remain open. Grand Chateau next.

Grand Chateau: 12,995tri/15batches/.21MiB; four corrected installed views inspected. Removed identical mapped17m background podium way/1421481074, which covered the new pool.31roof support samples pass. Crown, pool enclosure/furnishing and entrance route remain unfinished. Current active block: Signature.

Martin:32,173tri/25batches/.52MiB;4installed views plus corrected pool inspected.29roof and306guest-approach samples pass,typecheck passes. Gardens, sign/canopy and exact court calibration remain open. Rio now active.

Rio:63,938tri/99batches/1.08MiB; installed views inspected,228roof and807guest-approach samples passed. Red/blue facade, stepped crown, garages and four pools installed; dense gardens, arrival details and public routes remain incomplete. Palms next.

Palms:27,544tri/28batches/.4MiB; all4corrected installed views inspected.336roof support and453approach checks pass, core relocated with same rooms/templates. Pool court and arrival still sparse, exact plans estimated. Waldorf is now active; remaining city-wide inventory still incomplete.

Waldorf:21,109tri/31batches/.35MiB; all installed aerial/entry/pool views inspected and clipped pool/roof overlap corrected.366roof and24core approach checks pass.5legacy skin nodes and8tower colliders replaced; all other nodes/colliders exactly preserved. Lobby/terrace refinement remains. HGV Flamingo next active.

HGV Flamingo:21,936tri/18batches/.33MiB;3installed views inspected,69roof samples andtypecheck passed. Blank slab and5wings replaced with white/burgundy stepped facade and private pool. Landscaping, enclosure and routes remain unfinished.

Virgin:19,185tri/33batches/.31MiB. Three-tower height correction, casino/garage/pavilion facades and pool courtyard installed; all final views inspected.151roof support samples and typecheck pass. Landscape/fine geometry/circulation remain open. Gold Coast active next; city-wide task incomplete.

Gold Coast:103,894tri/31batches/2.24MiB; both corrected installed views inspected. Upper window intersection and reversed pediments fixed.43roof samples and typecheck pass. Full-site fine detail remains incomplete. Caesars tower audit now active.


### Caesars tower/service pass — 2026-10-13
Seven mapped towers replaced legacy masses; two parking structures and conference wing detailed. 98,398 triangles, 65 batches, 1.73 MiB optimized. All three final installed skyline images and guest corridor/stair images inspected in `build/city-exteriors/caesars-final/`. 154 roof, 24 entry and 9 stair roof clearance samples passed; Palace room envelope fits its mapped footprint. Public interiors preserved; five obsolete render nodes and 22 obsolete tower mass colliders removed. Guest recipe relocated without replacing rooms. Pool gardens, lower site fidelity, garage routes and full traversal remain unfinished. See `tools/resort-blocks/caesars-towers.json`.

Flamingo tower pass:72,362 triangles/9batches/2.02MiB. Four installed exterior/corridor images inspected.82roof+24entry+9stair opening tests pass; room corners fit. Initial boot schema failure repaired by replacing inherited trimesh indices with convexHull prisms. Full WebGPU verification passed,59hostfps at spawn (not city-wide performance proof). Garden/courtyard, marquee precision and public traversal remain incomplete. Horseshoe/Versailles audit active next.

## Showcase IV and Walgreens — 2026-10-14
Installed 62,024 triangles/72 batches,2.4MB optimized, three final views inspected. Duplicate corner signs corrected; terrace roof overlap removed.210floor and15guard samples pass;10,905 new triangles finite/nondegenerate/nonduplicate;8,478 road/landscape mesh groups unchanged;typecheck passes. Final fixed-view median16.6–16.8ms,p9523.6–24.9ms. Public rooftop access and exact facade/landscape fidelity remain incomplete. BLVD is next.

2026-10-14: Palazzo mapped canopy and street facade installed/inspected, 121 support/headroom and455 stair checks pass. Detailed comparison remains in venetian.json. Active block now Treasure Island frontage.

2026-10-14 TI mapped frontage reviewed in five installed views; cove/ornament refinement remains. Next active block: Planet Hollywood/Miracle Mile. Current inventory273needs-visual-audit.

2026-10-14 Miracle Mile metal skin and entrance display refresh installed and reviewed; two inventory rows reconciled. Active Paris rear podium/service audit.

Paris rear podium:1880newtri27batches,388retainedgroups unchanged except roof material.2014routechecks pass,collisionbyteidentical. Four views plus final membrane correction inspected. Detailed evidence in paris.json; full-site refinement remains.

Park MGM/Eataly2026-10-14: gray casino/white theatre roofs; diagonal mapped gable and open porch replace false solid canopy.131610tri47batches,43retainedgroups unchanged,36newcollisiontri,108checks pass.8views inspected. Four inventoryrows reconciled; rear arrival/gardens and fine facade detail remain deferred. ActiveNYNYpodium.


2026-10-14 NYNY north restaurant row: mapped roof-tagged box replaced,5installedviewschecked,22existingbatches retained. See new-york.json for explicit remaining refinements.


### 2026-10-14 Luxor site pass
47 batches, 99,788 triangles, 3,762 collision triangles; optimized installed GLB0.90MiB. North lobby/Excalibur connector, theatre/service volumes, Sphinx and Oasis pool area revised. All final views inspected;254 site and397 parking clearance samples passed;8478 road/landscape groups preserved. Sphinx remains simplified, pool planting and exact furniture arrangement approximate, complete public routes not certified. `luxor.json#sitePass20261014` retains discrepancies. Archive1760 reference/evidence files1103.5MB. Inventory expanded to630rows,256still need visual audit. Flamingo now active.


### Vanderpump hotel exterior pass, 2026-10-14

Installed and visually reviewed six views of the former Cromwell. Revised the blank western sign panel, south guest facade, glazed GIADA frontage, roof pool and two cabana tiers, raised rear club envelope, and open eastern arrival canopy. The canopy now has a 6.1 m soffit. 101 roof, entrance and canopy collision samples pass. All retained interiors, interior collision and venue metadata are unchanged. Final geometry: 118,581 triangles in 34 batches, optimized to 2.07 MiB.

Evidence: `build/city-exteriors/vanderpump-final-showcase-baseline/`; record: `tools/resort-blocks/vanderpump.json`. All six views inspected. Roof planting/furnishings and accurate ornament remain simplified, and full public roof access has not been certified. The existing bridge ramp crosses the main entrance view. This is an implemented pass with refinement deferred, not a photorealistic completion. Inventory row way/61239326 reconciled.


### Older Showcase frontage pass, 2026-10-14

Closed the curved glass atrium gable, added the Hard Rock architectural guitar panel and picture-window surround, separated lower shop signs, and replaced the flat yellow sign with a formed package profile. Reviewed three installed street/roof views and the final sign view. Exact commercial graphics, mascot sculpture and fine southern storefront details remain deferred. Showcase IV geometry and labels, all collision, and all venue metadata remain unchanged. Geometry audit passes with 70,221 triangles in 83 batches; optimized asset 3.23 MiB. Evidence and references in `tools/resort-blocks/showcase.json`. Two remaining Showcase inventory rows reconciled; 249 rows still require review.


2026-10-22: All631 inventory entries now have first-review dispositions and linked evidence; none remain needs-visual-audit. This is coverage, NOT whole-city architectural completion. Final passes include four pedestrian lifts, Flamingo garden/rotundas/gallery, CVS east apron and dated NYNY bus-stop absence. Versailles south frontage followup replaces incorrect legacy emblems with two rectangular window tiers;3installedviews inspected and370roof/24guest checksPASS. Planting, bridge/balconies, fine materials and many earlier site refinements remain open in block records. See coverage-2026-10-21.json and current-checkpoint.json.
