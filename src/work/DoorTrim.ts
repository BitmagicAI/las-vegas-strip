import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
/** A moving door is the batching boundary: its five frame pieces follow one
 * mesh, while the glass leaf and physics body keep their existing animation. */
export function makeDoorTrim(parts:number[][],depth:number,material:THREE.Material):THREE.Mesh {
    const geometries=parts.map(([x,y,w,h])=>{const g=new THREE.BoxGeometry(w,h,depth);g.translate(x!,y!,0);return g;});
    const geometry=mergeGeometries(geometries,false)!;geometries.forEach(g=>g.dispose());return new THREE.Mesh(geometry,material);
}
