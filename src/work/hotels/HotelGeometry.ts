import * as THREE from 'three';
import type {MeshLevelCollider} from 'engine/meshlevel/MeshLevelSchema.js';
import {worldPoint,type Point,type Tower} from './HotelLayout.js';
export function colliderVertices(c:MeshLevelCollider):ArrayLike<number>{
    if(c.shape!=='box')return 'vertices' in c?c.vertices:new Float32Array(0);   // (a heightfield has none; hotels never use one)
    // the box's eight corners, x outermost, then y, then z (as before)
    const v=new Float32Array(24),cos=Math.cos(c.yaw),sin=Math.sin(c.yaw);
    for(let k=0;k<8;k++){
        const x=(k&4?.5:-.5)*c.size[0],y=(k&2?.5:-.5)*c.size[1],z=(k&1?.5:-.5)*c.size[2];
        v[k*3]=c.position[0]+cos*x+sin*z;v[k*3+1]=c.position[1]+y;v[k*3+2]=c.position[2]-sin*x+cos*z;
    }
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
