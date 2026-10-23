import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
export function geometryScene(path){
 const file=fs.readFileSync(path),size=file.readUInt32LE(12),json=JSON.parse(file.subarray(20,20+size)),bin=file.subarray(28+size);
 const types={5121:Uint8Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},sizes={SCALAR:1,VEC2:2,VEC3:3,VEC4:4};
 const attribute=id=>{const a=json.accessors[id],v=json.bufferViews[a.bufferView],T=types[a.componentType];assert(!v.byteStride,'interleaved accessor');return new THREE.BufferAttribute(new T(bin.buffer,bin.byteOffset+(v.byteOffset??0)+(a.byteOffset??0),a.count*sizes[a.type]),sizes[a.type]);};
 const mats=json.materials.map(m=>new THREE.MeshBasicMaterial({side:m.doubleSided?THREE.DoubleSide:THREE.FrontSide,transparent:m.alphaMode==='BLEND'}));
 const nodes=json.nodes.map(n=>{
  const root=new THREE.Group();root.name=n.name??'';root.userData=n.extras??{};
  if(n.matrix){root.matrix.fromArray(n.matrix);root.matrixAutoUpdate=false;}else{if(n.translation)root.position.fromArray(n.translation);if(n.rotation)root.quaternion.fromArray(n.rotation);if(n.scale)root.scale.fromArray(n.scale);}
  if(n.mesh!==undefined)for(const p of json.meshes[n.mesh].primitives){assert(!p.extensions);const g=new THREE.BufferGeometry();g.setAttribute('position',attribute(p.attributes.POSITION));if(p.indices!==undefined)g.setIndex(attribute(p.indices));root.add(new THREE.Mesh(g,mats[p.material]));}
  return root;
 });
 json.nodes.forEach((n,i)=>(n.children??[]).forEach(c=>nodes[i].add(nodes[c])));
 const scene=new THREE.Group();for(const i of json.scenes[json.scene??0].nodes)scene.add(nodes[i]);scene.updateMatrixWorld(true);return scene;
}
