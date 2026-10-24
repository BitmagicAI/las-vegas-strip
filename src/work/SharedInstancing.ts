import * as THREE from 'three';
import type {NodeBuilder,NodeMaterial} from 'three/webgpu';
import {Fn,attribute,mat4,normalLocal,positionLocal,transformNormal,vec4} from 'three/tsl';

/** Instanced drawing that shares one shader build between meshes (2026-10-24, the owner: "If the only difference is
 * vertex buffer and textures, we should not have any recompiling").
 *
 * three r185 adds every InstancedMesh's uuid to its node cache key (its matrices are bound through the node graph), so
 * each InstancedMesh pays a whole node build, ~7 ms of main thread with this game's lights, even when its material and
 * geometry match another's: the Bellagio garden's 1,478 cell meshes cost 10 s of the start-up. Here the matrices are
 * ordinary per-instance geometry attributes (`instanceColumn0..3`, one interleaved buffer) read by name, which three
 * resolves per object at draw time, so every mesh with the same material and geometry layout shares one build, one
 * shader and one pipeline. Same transform as three's own instancing (nodes/accessors/Instance.js). */
const COLUMNS=['instanceColumn0','instanceColumn1','instanceColumn2','instanceColumn3'] as const;
const instanceMatrix=()=>mat4(attribute(COLUMNS[0],'vec4'),attribute(COLUMNS[1],'vec4'),attribute(COLUMNS[2],'vec4'),attribute(COLUMNS[3],'vec4'));
const applyInstance=Fn(([],builder:NodeBuilder)=>{
    const m=instanceMatrix().toVar();
    positionLocal.assign(m.mul(vec4(positionLocal,1)).xyz);
    if((builder as unknown as {hasGeometryAttribute:(name:string)=>boolean}).hasGeometryAttribute('normal'))normalLocal.assign(transformNormal(normalLocal,m));
},'void');
const shadowPosition=Fn(()=>instanceMatrix().mul(vec4(positionLocal,1)).xyz)();
const prepared=new WeakSet<THREE.Material>();

/** Make a node material draw shared instances: position and normal in its own passes, position in the shadow pass
 * (which renders with three's shadow material and takes only `castShadowPositionNode` from this one). */
function shareInstancing(material:NodeMaterial):void{
    if(prepared.has(material))return;prepared.add(material);
    const setupPosition=Object.getPrototypeOf(material).setupPosition as NodeMaterial['setupPosition'];
    material.setupPosition=function(this:NodeMaterial,builder:NodeBuilder){applyInstance();return setupPosition.call(this,builder);};
    material.castShadowPositionNode=shadowPosition;
}

/** A mesh drawing `count` copies of `source` (its attributes shared, not copied) at the column-major matrices in
 * `matrices`, 16 floats each. Every material must be a node material. */
export function sharedInstancedMesh(source:THREE.BufferGeometry,material:THREE.Material|THREE.Material[],matrices:Float32Array,count:number):THREE.Mesh{
    const geometry=new THREE.InstancedBufferGeometry();
    geometry.index=source.index;
    for(const name of Object.keys(source.attributes))geometry.setAttribute(name,source.attributes[name]!);
    for(const group of source.groups)geometry.addGroup(group.start,group.count,group.materialIndex);
    geometry.instanceCount=count;
    const buffer=new THREE.InstancedInterleavedBuffer(matrices,16,1);
    for(let i=0;i<4;i++)geometry.setAttribute(COLUMNS[i]!,new THREE.InterleavedBufferAttribute(buffer,4,i*4));
    // bounds of every copy, for culling (three would measure the source alone)
    if(!source.boundingBox)source.computeBoundingBox();
    const box=new THREE.Box3(),one=new THREE.Box3(),m=new THREE.Matrix4();
    for(let i=0;i<count;i++){m.fromArray(matrices,i*16);box.union(one.copy(source.boundingBox!).applyMatrix4(m));}
    geometry.boundingBox=box;geometry.boundingSphere=box.getBoundingSphere(new THREE.Sphere());
    for(const each of Array.isArray(material)?material:[material]){
        if(!(each as {isNodeMaterial?:boolean}).isNodeMaterial)throw new Error(`sharedInstancedMesh needs node materials (${each.type} ${each.name})`);
        shareInstancing(each as NodeMaterial);
    }
    const mesh=new THREE.Mesh(geometry,material);
    // three would ray-test the untransformed source; nothing picks planting
    mesh.raycast=()=>{};
    return mesh;
}
