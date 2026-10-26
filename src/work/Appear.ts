import type * as THREE from 'three';

/** City geometry that arrives after the player is in drops in from the sky instead of popping in (2026-10-25: the
 * owner suggested animating new geometry in, for example falling from the sky, instead of popping). A transform animation only: no shader changes, so nothing compiles for it. Before
 * play (under the loading screen) roots simply appear. Up to SLOTS roots fall at once; a busier moment shows the rest
 * in place. Nothing is allocated per frame. */
const SLOTS=48,DROP=70,DURATION_MS=950;
const roots:(THREE.Object3D|null)[]=new Array(SLOTS).fill(null);
const starts=new Float64Array(SLOTS),bases=new Float64Array(SLOTS);
let active=0,playing=false;

/** Set every frame from the game: drops only play once the player is in. */
export function appearPlaying(on:boolean):void{playing=on;}

/** Show `root` (already at its final place and visible): falling in when the game is playing. */
export function appear(root:THREE.Object3D):void{
    if(!playing)return;
    for(let i=0;i<SLOTS;i++)if(roots[i]===null){
        roots[i]=root;starts[i]=performance.now();bases[i]=root.position.y;active++;
        root.position.y=bases[i]!+DROP;root.updateMatrixWorld(true);
        return;
    }
}

/** Once per frame before rendering. */
export function updateAppear(now:number):void{
    if(!active)return;
    for(let i=0;i<SLOTS;i++){
        const root=roots[i];if(!root)continue;
        const t=Math.min(1,(now-starts[i]!)/DURATION_MS);
        // an accelerating fall over 85% of the time, then a small hop as it lands
        const f=t/.85,offset=t<.85?1-f*f:Math.sin((t-.85)/.15*Math.PI)*.025;
        root.position.y=bases[i]!+DROP*offset;
        root.updateMatrixWorld(true);
        if(t>=1){root.position.y=bases[i]!;root.updateMatrixWorld(true);roots[i]=null;active--;}
    }
}
