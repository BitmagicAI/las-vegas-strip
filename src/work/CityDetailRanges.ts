import * as THREE from 'three';
import {isGeometryReleaseSuspended} from 'engine/GeometryCpuRelease.js';
import {filmDetail} from './FilmDetail.js';

interface DetailCell {bounds:THREE.Box3;wrappers:THREE.Group[];visible:boolean}
/** Small entrance/core details are culled as spatial cells, independently of
 * the skyline. Wrappers preserve animation, gameplay visibility and physics.
 * This inventory is built once; no scene traversal occurs while moving.
 */
export class CityDetailRanges {
    private cells=new Map<string,DetailCell>();
    private sources:{node:THREE.Object3D;parent:THREE.Object3D;wrapper:THREE.Group}[]=[];
    private last=0;private point=new THREE.Vector3();private previousPoint=new THREE.Vector3(Infinity,Infinity,Infinity);
    private disposed=false;private registered=new WeakSet<THREE.Object3D>();
    private unwatch:(()=>void)[]=[];
    private previous:THREE.Scene['onBeforeRender'];private hook:THREE.Scene['onBeforeRender'];
    constructor(private scene:THREE.Scene,roots:THREE.Object3D[],private range=240){
        scene.updateMatrixWorld(true);
        this.register(roots);
        this.previous=scene.onBeforeRender;
        this.hook=(...args)=>{this.previous.apply(scene,args);if(!scene.overrideMaterial)this.select(args[2]);};
        scene.onBeforeRender=this.hook;
    }
    /** Engine-authored door assets arrive after Game.load. Subscribe to their
     * parent instead of rescanning the scene in the frame loop. Wait until the
     * creator has fitted/positioned the new pivot before measuring its bounds. */
    watchDoorParent(parent:THREE.Object3D):void {
        const added=(event:{child:THREE.Object3D})=>{const node=event.child;
            if(!isDoorPivot(node))return;
            queueMicrotask(()=>{if(!this.disposed&&node.parent===parent)this.register([node]);});
        };
        parent.addEventListener('childadded',added);
        this.unwatch.push(()=>parent.removeEventListener('childadded',added));
    }
    private register(roots:THREE.Object3D[]):void {
        for(const node of roots){
            if(this.registered.has(node))continue;
            const parent=node.parent;if(!parent)continue;
            node.updateWorldMatrix(true,true);
            const bounds=new THREE.Box3().setFromObject(node);if(bounds.isEmpty())continue;
            const center=bounds.getCenter(new THREE.Vector3()),key=`${Math.floor(center.x/160)},${Math.floor(center.z/160)}`;
            let cell=this.cells.get(key);if(!cell){cell={bounds:new THREE.Box3(),wrappers:[],visible:true};this.cells.set(key,cell);}
            const wrapper=new THREE.Group();wrapper.name='Small city details / '+key;wrapper.userData.cityDetailRange=true;
            // Keep the original local transform and parent coordinate system.
            parent.add(wrapper);wrapper.add(node);cell.wrappers.push(wrapper);cell.bounds.union(bounds);
            wrapper.visible=cell.visible;this.sources.push({node,parent,wrapper});this.registered.add(node);
        }
        this.previousPoint.set(Infinity,Infinity,Infinity);this.last=-Infinity;
    }
    select(camera:THREE.Camera,now=performance.now()):void {
        if(now-this.last<200||isGeometryReleaseSuspended())return;this.last=now;
        camera.getWorldPosition(this.point);const moved=this.point.distanceToSquared(this.previousPoint)>=1;if(moved)this.previousPoint.copy(this.point);
        for(const cell of this.cells.values()){
            if(filmDetail.full)cell.visible=true;else if(moved)cell.visible=cell.bounds.distanceToPoint(this.point)<this.range*(cell.visible?1.12:.88);
            // Re-assert even when still: the engine warm-up restores stale visibility.
            for(const wrapper of cell.wrappers)if(wrapper.visible!==cell.visible)wrapper.visible=cell.visible;
        }
    }
    dispose():void {
        this.disposed=true;this.unwatch.forEach(stop=>stop());this.unwatch=[];
        if(this.scene.onBeforeRender===this.hook)this.scene.onBeforeRender=this.previous;
        for(const {node,parent,wrapper} of this.sources){if(node.parent===wrapper)parent.add(node);wrapper.removeFromParent();}
        this.sources=[];this.cells.clear();
    }
}

function isDoorPivot(node:THREE.Object3D):boolean {return node.name.startsWith('door_')&&node.name.endsWith('_pivot');}

/** Only existing small entrance objects, never whole towers or gameplay actors. */
export function cityEntranceDetails(scene:THREE.Scene):THREE.Object3D[]{
    const roots:THREE.Object3D[]=[];
    const visit=(node:THREE.Object3D)=>{
        if(isDoorPivot(node) || node.name.startsWith('Streamed ') || node.userData.perfOwner==='Public entrance doors' || node.userData.perfOwner==='Guest · doors and signs'){
            roots.push(node);return;
        }
        for(const child of node.children)visit(child);
    };
    visit(scene);return roots;
}
