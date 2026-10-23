import * as THREE from 'three';
import {releaseAfterUpload} from './CpuGeometryRelease.js';
/** Shadows use no facade materials. Merge their existing triangles per 160 m
 * cell, preserving exact casting geometry and independent skyline visibility.
 * Positions and indices are written straight into typed arrays; the CPU copy is
 * released once the shadow pass has uploaded it. */
export function batchCityShadows(root:THREE.Group):void {
    root.updateWorldMatrix(true,true);const buckets=new Map<string,THREE.Mesh[]>(),sources:THREE.Mesh[]=[];
    root.traverse(o=>{if(o instanceof THREE.Mesh&&o.layers.mask===(1<<30))sources.push(o);});
    const materials=new Set<THREE.Material>(),box=new THREE.Box3(),c=new THREE.Vector3(),p=new THREE.Vector3();
    for(const mesh of sources){
        box.setFromObject(mesh).getCenter(c);const key=`${Math.floor(c.x/160)},${Math.floor(c.z/160)}`;
        const list=buckets.get(key);if(list)list.push(mesh);else buckets.set(key,[mesh]);
        for(const m of Array.isArray(mesh.material)?mesh.material:[mesh.material])materials.add(m);mesh.removeFromParent();
    }
    materials.forEach(m=>m.dispose());const mat=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
    for(const [key,meshes] of buckets){
        let vertices=0,indices=0;for(const m of meshes){const n=m.geometry.getAttribute('position').count;vertices+=n;indices+=m.geometry.index?.count??n;}
        const positions=new Float32Array(vertices*3),index=vertices>65535?new Uint32Array(indices):new Uint16Array(indices);let v=0,ix=0;
        for(const m of meshes){
            const position=m.geometry.getAttribute('position') as THREE.BufferAttribute,source=m.geometry.index,base=v;
            for(let i=0;i<position.count;i++,v++){p.fromBufferAttribute(position,i).applyMatrix4(m.matrixWorld);positions[v*3]=p.x;positions[v*3+1]=p.y;positions[v*3+2]=p.z;}
            if(source)for(let j=0;j<source.count;j++)index[ix++]=source.getX(j)+base;else for(let j=0;j<position.count;j++)index[ix++]=base+j;
        }
        const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(positions,3));geo.setIndex(new THREE.BufferAttribute(index,1));geo.computeBoundingSphere();
        const m=new THREE.Mesh(geo,mat);m.name='Batched city shadow / '+key;m.layers.set(30);m.castShadow=true;m.matrix.copy(root.matrixWorld).invert();m.matrixAutoUpdate=false;root.add(m);
        releaseAfterUpload(geo);
    }
}
