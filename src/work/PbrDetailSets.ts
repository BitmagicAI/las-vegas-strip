/** Which scanned material (build/pbr/, see PbrDetail.ts) a surface gets, decided by its material name. Kept free of three.js
 * so `node --import ./tools/ts-register.mjs tools/pbr/check-sets.mjs` can list the mapping for every runtime material. */
export const PBR_SETS=['clean_asphalt','concrete_pavement','concrete_floor_02','white_stucco','concrete_wall_008','sandstone_blocks_08','marble_01',
    'brick_wall_02','metal_plate','aerial_grass_rock','gravel_floor_02','clay_roof_tiles_02','bitumen','dry_ground_01','granite_tile_03'] as const;
export type PbrSet=typeof PBR_SETS[number];

/** Per set: metres per tile, scan colour share (0 keeps the surface's own colour; faded out with distance), colour variation
 * (how much of the scan's light/dark and hue variation is laid over the surface), relief (normal strength), roughness share
 * and AO strength. */
export const PBR_PARAMS:Record<PbrSet,readonly [tile:number,scanColor:number,variation:number,relief:number,roughness:number,ao:number]>={
    clean_asphalt:[3.0,.25,.8,.8,.75,.7],
    concrete_pavement:[3.2,.1,.8,.9,.6,.8],
    concrete_floor_02:[3.0,.1,.7,.8,.6,.7],
    white_stucco:[2.6,0,.5,.7,.5,.5],
    concrete_wall_008:[3.5,0,.5,.7,.5,.5],
    sandstone_blocks_08:[3.0,0,.4,.8,.5,.6],
    marble_01:[2.5,0,.5,.25,.35,.3],
    brick_wall_02:[2.2,.2,.7,1.0,.6,.8],
    metal_plate:[2.0,0,.35,.4,.45,.4],
    aerial_grass_rock:[7.0,.3,.8,.8,.6,.6],
    gravel_floor_02:[3.0,.25,.8,1.0,.6,.8],
    clay_roof_tiles_02:[2.4,.2,.8,1.0,.6,.8],
    bitumen:[4.0,.1,.7,.7,.6,.6],
    dry_ground_01:[5.0,.25,.8,.9,.6,.7],
    granite_tile_03:[2.8,.1,.6,.6,.5,.6],
};

/** First match wins. Surfaces that must stay as authored come first (glass, water, light, signage, foliage, fabric, paint,
 * polished decorative metal); then the ground (OSM kinds), then architecture. */
const RULES:readonly (readonly [RegExp,PbrSet|null])[]=[
    [/rw-garden|mi-garden|osm \/ (grass|planting|woodland|shrub)/,'aerial_grass_rock'],
    [/forum-flat-roof|cp-flat-roof|cp-chair-frame|cp-colosseum-joint|cp-patina|cp-pool-tile|cp-basin|cp-fabric|cp-cushion|rw-flat-roof|rw-blue-panel|fb-flat-roof|fb-canopy-white|fb-soffit|fb-rib-metal|bellagio-flat-roof|st-flat-roof|st-joint|st-panel-dark|sa-flat-roof|sa-soffit|sa-trim|sa-champagne|sa-joint|sa-blue-reveal|sa-basin/,null],
    [/fs-(glass|metal|joint|service|sign|solar|screen|flat-roof)/,null],
    [/fs-(white|stone|sand|taupe)/,'white_stucco'],
    [/cc-(flat-roof|metal|door|blue|gold|yellow|pink|sill|shadow|dome|window)/,null],
    [/cc-asphalt/,'clean_asphalt'],
    [/cf-(glass|frame|blue|red$|flat-roof|screen|joint|roof-seam)/,null],
    [/cf-white/,'white_stucco'],
    [/cf-red-tile/,'brick_wall_02'],
    [/aria-trim/,null],
    [/ga-(mosaic|flat-roof|roof|seam|glass|frame|door)/,null],
    [/aria-mulch/,'aerial_grass_rock'],
    [/aria-paving/,'granite_tile_03'],
    [/lake-tile-light/,'granite_tile_03'],
    [/bricklight|campanile-brick/,'brick_wall_02'],
    [/venetian-taupe|venetian-salmon|palazzo-stone|ph-stone|mgm-stone|mandalay-stone|park-stone|nyny-stone/,'sandstone_blocks_08'],
    [/wf-stone|wf-plinth/,'granite_tile_03'],
    [/wf-roof-metal/,'metal_plate'],
    [/skg-deck|wd-roof|pt-roof|we-roof|es-roof|ub-roof|ps-roof|ps-deck|hs-roof|fl-roof|cp-roof|gco-roof|gco-paving|vh-roof|vh-paving|hf-roof|hf-paving|wa-roof|wa-paving/,'concrete_floor_02'],
    [/lvw-white|lvw-panel|oy-white|oy-sill|gd-cream|gd-gray|gd-trim|rh-cream|rh-trim|pk-white|pk-sill|skg-sand|skg-rail|wd-white|wd-pink|pt-white|pt-blue|we-white|we-stone|es-stone|es-gray|ub-stone|ps-white|ps-stone|hs-white|hs-stone|fl-white|cp-colosseum-sand|cp-colosseum-recess|cp-white|cp-stone|gco-white|gco-stone|vh-white|vh-stone|hf-white|hf-burgundy|hf-stone|wa-stone|pm-white|pm-stone|ri-white|ri-sand|ri-cream|ma-white|pa-white|sg-stone|sg-white|gc-cream|gc-white|gc-taupe|mi-white|mi-cream|wy-white|wy-stone|wy-trim|tr-white|sh-white|sh-sill|park-white|mandalay-white|luxor-stone|nyny-white|wg-white|wg-stone|tp-white|tp-stone|tt-white|st-white|st-stone|hgv-sand|hgv-cream|sky-white|allure-white|sa-white|sa-stone|cc-white|cc-cream|rw-white|fb-white/,'white_stucco'],
    [/allure-rail|glass|glazing|window|mirror|water|_pool$|underwater|lake-deep|screen|display|\bled|led$|neon|emissive|light|lamp|glint|letter|script|sign|leaf|foliage|flower|tree|hedge|shrub|bark|trunk|velvet|felt|carpet|fabric|linen|rattan|cushion|rope|seat|rubber|vortex|cloudskin|shell|crystal|paint|shadow|soot|torch|statue|gold|gilt|brass|bronze|copper|chrome|silver|verdigris|walnut|wood|timber|rose$/,null],
    [/osm \/ road|asphalt|mi-drive|bridge-deck/,'clean_asphalt'],
    [/sidewalk|plaza|paving|paver|pavement|walkway/,'concrete_pavement'],
    [/pa-parking|gutter|curb|kerb|median|bridge-concrete|utility|pedestal|support/,'concrete_floor_02'],
    [/verge|gravel/,'gravel_floor_02'],
    [/osm \/ ground|soil|earth|dirt/,'dry_ground_01'],
    [/cp-tile|gco-tile|terracotta|redroof|clay/,'clay_roof_tiles_02'],
    [/stationroof/,'metal_plate'],
    [/roof|bitumen|slate|chimney/,'bitumen'],
    [/marble/,'marble_01'],
    [/granite|terrazzo|tile/,'granite_tile_03'],
    [/brick/,'brick_wall_02'],
    [/mi-rock|limestone|sandstone|travertine|ashlar|pinkstone|paris-stone|lake-stone|lake-rock|c_stone|p_stone|cc_stone|ba_limestone/,'sandstone_blocks_08'],
    [/steel|iron|zinc|metal|frame|rail|alumin|eiffel/,'metal_plate'],
    [/skg-slab|concrete|cement|^[a-z0-9-]+\/stone$|\/ stone$/,'concrete_wall_008'],
    [/stucco|plaster|ivory|cream|champagne|pearl|chalk|beige|coffer|wall|facade|building|osm \/ tag\/|\/ warm$|\/ white$|_white$|_warm$/,'white_stucco'],
];

/** The scan for a material name (an index into PBR_SETS), or -1 to leave the surface as authored. */
export function detailSetFor(name:string):number{
    const n=name.toLowerCase();
    for(const [re,set] of RULES)if(re.test(n))return set?PBR_SETS.indexOf(set):-1;
    return -1;
}
