/** Local keyboard driving comfort targets, not surveyed/legal speed limits. */
export interface DriveRoad { id: number; highway?: string; width: number; points: [number, number, number][] }
type Segment = { a: [number, number, number]; b: [number, number, number]; width: number; limit: number };
export function roadSpeedTarget(road: DriveRoad): number {
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
export class DrivingSpeedAssist {
    private cells = new Map<string, Segment[]>();
    constructor(roads: DriveRoad[]) {
        for (const road of roads) for (let i = 1; i < road.points.length; i++) {
            const a = road.points[i-1]!, b = road.points[i]!, width = road.width;
            const segment = { a, b, width, limit: roadSpeedTarget(road) };
            const pad = width / 2 + 2;
            for (let x=Math.floor((Math.min(a[0],b[0])-pad)/40);x<=Math.floor((Math.max(a[0],b[0])+pad)/40);x++)
                for(let z=Math.floor((Math.min(a[2],b[2])-pad)/40);z<=Math.floor((Math.max(a[2],b[2])+pad)/40);z++) {
                    const key=`${x},${z}`; const bucket=this.cells.get(key) ?? []; bucket.push(segment);this.cells.set(key,bucket);
                }
        }
    }
    targetAt(x: number, y: number, z: number): number {
        // Authored multi-floor garage and its graded side access, above the ground road.
        if(x>=-375 && x<=-192 && z>=488 && z<=564 && y>=0 && y<=13) return 10;
        if(x>=-366 && x<=-203 && z>564 && z<=578 && y>=0 && y<=13) return 12;
        let nearest=Infinity, target=10; // Off-network courtyards/parking remain manageable.
        for(const s of this.cells.get(`${Math.floor(x/40)},${Math.floor(z/40)}`) ?? []) {
            const dx=s.b[0]-s.a[0],dz=s.b[2]-s.a[2],l=dx*dx+dz*dz;
            const t=l ? Math.max(0,Math.min(1,((x-s.a[0])*dx+(z-s.a[2])*dz)/l)) : 0;
            const height=s.a[1]+t*(s.b[1]-s.a[1]);
            if(Math.abs(y-height) > 2.2) continue;
            const distance=Math.hypot(x-s.a[0]-t*dx,z-s.a[2]-t*dz);
            if(distance>s.width/2+1.5)continue;
            // Prefer the closest centerline, not every road crossing the same cell.
            if(distance<nearest){nearest=distance;target=s.limit;}
        }
        return target;
    }
}
