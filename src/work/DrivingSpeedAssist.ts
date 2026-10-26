/** Local keyboard driving comfort targets, not surveyed/legal speed limits. */
export interface DriveRoad { id: number; highway?: string; width: number; points: ArrayLike<number>[] }
export function roadSpeedTarget(road: { highway?: string; width: number }): number {
    if (['footway','pedestrian','path','steps','cycleway'].includes(road.highway ?? '')) return 9;
    if (road.width < 4.5) return 10;
    if (road.highway === 'service') return 12;
    if (road.width < 7) return 12;
    if (['residential','living_street'].includes(road.highway ?? '')) return 10;
    return 24;
}
export function assistedAcceleration(speed: number, target: number, empty: boolean): number {
    if (empty) return 0;
    const base = target < 24 ? .85 : 1;
    // Keep reverse/braking input responsive; the engine independently gates signed speed.
    return base * Math.max(.12, Math.min(1, (target - Math.abs(speed)) / (target * .1)));
}

/** The road map as the assist reads it (2026-10-25): baked offline from the road network (tools/optimize/pack-data.mjs,
 * speed-map.bin; SpeedMapFile.ts reads it), so the game neither parses the 8 MB network nor builds objects from it.
 * Roads are polylines in centimetres; a 40 m grid lists, per cell, the segments within reach (a segment is named by the
 * index of its first point). */
export interface SpeedMap {
    /** x, y, z per point, centimetres */
    points: Int32Array;
    /** first point of each road, and the end (roads + 1 entries) */
    roadStart: Uint32Array;
    /** comfort target per road (roadSpeedTarget) */
    limit: Uint8Array;
    /** half the width plus 1.5 m per road, centimetres (widths are whole decimetres, up to 34 m) */
    reach: Uint16Array;
    /** occupied cells, ascending: (cell x + 32768) * 65536 + cell z + 32768 */
    cellKeys: Uint32Array;
    /** each cell's first segment in `segments`, and the end (cells + 1 entries) */
    cellStart: Uint32Array;
    segments: Uint32Array;
}
const CELL = 40;

/** The baked map from roads in metres (the packer, and tests). */
export function buildSpeedMap(roads: DriveRoad[]): SpeedMap {
    let total = 0;
    for (const road of roads) total += road.points.length;
    const points = new Int32Array(total * 3), roadStart = new Uint32Array(roads.length + 1), limit = new Uint8Array(roads.length), reach = new Uint16Array(roads.length);
    const cells = new Map<number, number[]>();
    let p = 0;
    roads.forEach((road, r) => {
        roadStart[r] = p; limit[r] = roadSpeedTarget(road); reach[r] = Math.round((road.width / 2 + 1.5) * 100);
        for (const q of road.points) { points[p * 3] = Math.round(q[0]! * 100); points[p * 3 + 1] = Math.round(q[1]! * 100); points[p * 3 + 2] = Math.round(q[2]! * 100); p++; }
        const pad = road.width / 2 + 2;
        for (let i = roadStart[r]! + 1; i < p; i++) {
            const ax = points[(i - 1) * 3]! / 100, az = points[(i - 1) * 3 + 2]! / 100, bx = points[i * 3]! / 100, bz = points[i * 3 + 2]! / 100;
            for (let x = Math.floor((Math.min(ax, bx) - pad) / CELL); x <= Math.floor((Math.max(ax, bx) + pad) / CELL); x++)
                for (let z = Math.floor((Math.min(az, bz) - pad) / CELL); z <= Math.floor((Math.max(az, bz) + pad) / CELL); z++) {
                    const key = (x + 32768) * 65536 + z + 32768, list = cells.get(key);
                    if (list) list.push(i - 1); else cells.set(key, [i - 1]);
                }
        }
    });
    roadStart[roads.length] = p;
    const keys = [...cells.keys()].sort((a, b) => a - b), cellKeys = Uint32Array.from(keys), cellStart = new Uint32Array(keys.length + 1);
    let count = 0;
    keys.forEach((k, c) => { cellStart[c] = count; count += cells.get(k)!.length; });
    cellStart[keys.length] = count;
    const segments = new Uint32Array(count);
    keys.forEach((k, c) => segments.set(cells.get(k)!, cellStart[c]!));
    return { points, roadStart, limit, reach, cellKeys, cellStart, segments };
}

export class DrivingSpeedAssist {
    /** road of each point (derived once) */
    private readonly pointRoad: Uint32Array;
    private readonly map: SpeedMap;
    constructor(map: SpeedMap) {
        this.map = map;
        const roads = map.limit.length;
        this.pointRoad = new Uint32Array(map.points.length / 3);
        for (let r = 0; r < roads; r++) this.pointRoad.fill(r, map.roadStart[r]!, map.roadStart[r + 1]!);
    }
    targetAt(x: number, y: number, z: number): number {
        // Authored multi-floor garage and its graded side access, above the ground road.
        if(x>=-375 && x<=-192 && z>=488 && z<=564 && y>=0 && y<=13) return 10;
        if(x>=-366 && x<=-203 && z>564 && z<=578 && y>=0 && y<=13) return 12;
        let nearest=Infinity, target=10; // Off-network courtyards/parking remain manageable.
        const m=this.map,key=(Math.floor(x/CELL)+32768)*65536+Math.floor(z/CELL)+32768;
        let lo=0,hi=m.cellKeys.length-1,cell=-1;
        while(lo<=hi){const mid=(lo+hi)>>>1,k=m.cellKeys[mid]!;if(k<key)lo=mid+1;else if(k>key)hi=mid-1;else{cell=mid;break;}}
        if(cell<0)return target;
        const P=m.points;
        for(let s=m.cellStart[cell]!;s<m.cellStart[cell+1]!;s++){
            const a=m.segments[s]!*3,b=a+3,road=this.pointRoad[a/3]!;
            const ax=P[a]!/100,ay=P[a+1]!/100,az=P[a+2]!/100,dx=P[b]!/100-ax,dz=P[b+2]!/100-az,l=dx*dx+dz*dz;
            const t=l ? Math.max(0,Math.min(1,((x-ax)*dx+(z-az)*dz)/l)) : 0;
            const height=ay+t*(P[b+1]!/100-ay);
            if(Math.abs(y-height) > 2.2) continue;
            const distance=Math.hypot(x-ax-t*dx,z-az-t*dz);
            if(distance>m.reach[road]!/100)continue;
            // Prefer the closest centerline, not every road crossing the same cell.
            if(distance<nearest){nearest=distance;target=m.limit[road]!;}
        }
        return target;
    }
}
