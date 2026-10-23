import * as THREE from 'three';
import type {MeshLevelCollider} from 'engine/meshlevel/MeshLevelSchema.js';
import {worldPoint,type Point,type Tower} from './HotelLayout.js';
export function colliderVertices(c:MeshLevelCollider):number[]{
    if(c.shape!=='box')return c.vertices;
    const v:number[]=[],cos=Math.cos(c.yaw),sin=Math.sin(c.yaw);
    for(const x of [-c.size[0]/2,c.size[0]/2])for(const y of [-c.size[1]/2,c.size[1]/2])for(const z of [-c.size[2]/2,c.size[2]/2])
        v.push(c.position[0]+cos*x+sin*z,c.position[1]+y,c.position[2]-sin*x+cos*z);
    return v;
}

export function moduleMatrix(t:Tower,p:Point,rotation=0,shear=false):THREE.Matrix4 {
 const c=Math.cos(t.yaw),s=Math.sin(t.yaw),m=new THREE.Matrix4().makeRotationY(t.yaw);
 if(t.linear){const [a,b,c,d]=t.linear;m.set(a,0,b,0, 0,1,0,0, c,0,d,0, 0,0,0,1);}
 const w=worldPoint(t,p);m.setPosition(w.x,w.y,w.z);
 m.multiply(new THREE.Matrix4().makeRotationY(rotation));
 if(shear && t.lean)m.multiply(new THREE.Matrix4().set(1,t.lean[0],0,0,0,1,0,0,0,t.lean[1],1,0,0,0,0,1));
 return m;
}

/** Block only the outgoing left flight at the roof; the right flight is the
 * route down from this landing and must remain open. */
export function stairStopMatrix(t:Tower,p:Point):THREE.Matrix4 {
 return moduleMatrix(t,{x:p.x-1.65,y:p.y,z:p.z}).scale(new THREE.Vector3(.46,1,1));
}
