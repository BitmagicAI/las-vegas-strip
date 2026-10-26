import * as THREE from 'three';
import {releaseAfterUpload} from './CpuGeometryRelease.js';
import {runSync} from './FrameBudget.js';
import {floats,Scratch} from './AttributeReader.js';
import {bakeCapture} from './CityBake.js';
/** Shadows use no facade materials. Merge their existing triangles per 160 m
 * cell, preserving exact casting geometry and independent skyline visibility.
 * Positions and indices are written straight into typed arrays; the CPU copy is
 * released once the shadow pass has uploaded it. */
export function batchCityShadows(root:THREE.Group):void {runSync(batchCityShadowsSteps(root));}

const CASTER=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});CASTER.name='City shadow caster';
/** A city batch's sun-shadow casters (2026-10-26): its own GPU positions (the attribute is shared, so nothing is copied)
 * and an index list of the triangles of its casting parts, on the shadow-only layer. Replaces the per-cell copies of
 * every caster's positions (200 MB of GPU memory for the city). Null when nothing in the batch casts. */
export function casterShadowMesh(batch:THREE.BufferGeometry,index:Uint16Array|Uint32Array,name:string):THREE.Mesh|null {
    if(!index.length)return null;
    const g=new THREE.BufferGeometry();g.setAttribute('position',batch.getAttribute('position'));g.setIndex(new THREE.BufferAttribute(index,1));
    // the batch's bounds (conservative for culling; computing the casters' own would read every position)
    if(!batch.boundingBox)batch.computeBoundingBox();if(!batch.boundingSphere)batch.computeBoundingSphere();
    g.boundingBox=batch.boundingBox!.clone();g.boundingSphere=batch.boundingSphere!.clone();
    const m=new THREE.Mesh(g,CASTER);m.name=name;m.layers.set(30);m.castShadow=true;m.receiveShadow=false;m.matrixAutoUpdate=false;
    return m;
}
/** Sun-shadow casters for the meshes a loader marked (`userData.cityCaster`) that no city batch took: water edges,
 * glass, details outside CityLod's blocks. Proxies on the shadow layer, merged per 160 m cell (batchCityShadowsSteps).
 * The batched ones cast from their batches (casterShadowMesh). Call after the owner's CityLod is built. */
export function* unmergedCasterShadowsSteps(root:THREE.Group):Generator<void,void> {
    root.updateWorldMatrix(true,true);
    const inverse=root.matrixWorld.clone().invert(),casters:THREE.Mesh[]=[];
    root.traverse(o=>{if(o instanceof THREE.Mesh&&o.userData.cityCaster&&o.layers.mask!==(1<<30))casters.push(o);});
    for(const o of casters){const p=new THREE.Mesh(o.geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));p.matrix.multiplyMatrices(inverse,o.matrixWorld);p.matrixAutoUpdate=false;p.layers.set(30);p.castShadow=true;p.userData.cityProxy=true;root.add(p);}
    yield* batchCityShadowsSteps(root);
}
export function unmergedCasterShadows(root:THREE.Group):void {runSync(unmergedCasterShadowsSteps(root));}
/** batchCityShadows as steps (FrameBudget.ts): yields per cell and every 8192 vertices. */
export function* batchCityShadowsSteps(root:THREE.Group):Generator<void,void> {
    root.updateWorldMatrix(true,true);const buckets=new Map<string,THREE.Mesh[]>(),sources:THREE.Mesh[]=[],scratch=new Scratch();
    // only the proxies made for unbatched casters (unmergedCasterShadowsSteps), never the batches' own caster meshes
    root.traverse(o=>{if(o instanceof THREE.Mesh&&o.layers.mask===(1<<30)&&o.userData.cityProxy)sources.push(o);});
    const materials=new Set<THREE.Material>(),box=new THREE.Box3(),c=new THREE.Vector3();
    for(const mesh of sources){
        box.setFromObject(mesh).getCenter(c);const key=`${Math.floor(c.x/160)},${Math.floor(c.z/160)}`;
        const list=buckets.get(key);if(list)list.push(mesh);else buckets.set(key,[mesh]);
        for(const m of Array.isArray(mesh.material)?mesh.material:[mesh.material])materials.add(m);mesh.removeFromParent();
    }
    materials.forEach(m=>m.dispose());const mat=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
    for(const [key,meshes] of buckets){
        yield;let vertices=0,indices=0;for(const m of meshes){const n=m.geometry.getAttribute('position').count;vertices+=n;indices+=m.geometry.index?.count??n;}
        const positions=new Float32Array(vertices*3),index=vertices>65535?new Uint32Array(indices):new Uint16Array(indices);let v=0,ix=0;
        for(const m of meshes){
            const position=m.geometry.getAttribute('position') as THREE.BufferAttribute,source=m.geometry.index,base=v,P=floats(position,scratch,0),e=m.matrixWorld.elements;
            // Vector3.applyMatrix4 on the source's components as doubles (AttributeReader.ts): the same values, without calls
            for(let i=0;i<position.count;i++,v++){if((v&8191)===8191)yield;const x=P[i*3]!,y=P[i*3+1]!,z=P[i*3+2]!,w=1/(e[3]!*x+e[7]!*y+e[11]!*z+e[15]!);
                positions[v*3]=(e[0]!*x+e[4]!*y+e[8]!*z+e[12]!)*w;positions[v*3+1]=(e[1]!*x+e[5]!*y+e[9]!*z+e[13]!)*w;positions[v*3+2]=(e[2]!*x+e[6]!*y+e[10]!*z+e[14]!)*w;}
            if(source){const s=source.array;for(let j=0;j<source.count;j++)index[ix++]=s[j]!+base;}else for(let j=0;j<position.count;j++)index[ix++]=base+j;
        }
        const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(positions,3));geo.setIndex(new THREE.BufferAttribute(index,1));geo.computeBoundingSphere();
        const m=new THREE.Mesh(geo,mat);m.name='Batched city shadow / '+key;m.layers.set(30);m.castShadow=true;m.matrix.copy(root.matrixWorld).invert();m.matrixAutoUpdate=false;root.add(m);
        bakeCapture?.shadows(root,[m]);releaseAfterUpload(geo);
    }
}
