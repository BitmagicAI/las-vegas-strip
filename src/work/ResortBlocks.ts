import type * as THREE from 'three';
import type {EngineLike} from 'types/game.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import type {StreamingWork} from './StreamingWork.js';
import {StripLandmarks} from './StripLandmarks.js';
import type {SiteLights} from './SiteLights.js';
/** Installed local block passes share the existing lazy public-interior loader. */
export class ResortBlocks {
    private blocks:StripLandmarks[];
    constructor(engine:EngineLike,surfaces:GroundSurfaceIndex,loading:StreamingWork,lights:SiteLights){
        this.blocks=['cosmo','bellagio','paris'].map(id=>new StripLandmarks(engine,surfaces,loading,lights,`/build/resort-blocks/${id}/`));
    }
    setPassing(passing:boolean){for(const b of this.blocks)b.setPassing(passing);}
    async load(){for(const block of this.blocks)await block.load();}
    update(player:THREE.Vector3,outside:boolean,hideSource?:string){for(const b of this.blocks)b.update(player,outside,hideSource);}
    getView(player:THREE.Vector3,camera:THREE.Vector3){for(const b of this.blocks){const v=b.getView(player,camera);if(v)return v;}return null;}
    review(key:string,view='entrance'){for(const b of this.blocks){const v=b.review(key,view);if(v)return v;}return null;}
    get stats(){return {residentInteriors:this.blocks.flatMap(b=>b.stats.residentInteriors),physicsBodies:this.blocks.reduce((n,b)=>n+b.stats.physicsBodies,0)};}
    dispose(){for(const b of this.blocks)b.dispose();}
}
