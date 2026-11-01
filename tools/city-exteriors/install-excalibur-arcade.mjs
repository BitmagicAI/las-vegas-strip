// Remove only the ten obsolete low arcade piers rendered as conical turrets.
import fs from 'node:fs';import crypto from 'node:crypto';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const file='build/highrises/exteriors.glb',doc=await io.read(file),masks=JSON.parse(fs.readFileSync('docs/project-records/excalibur-arcade/replacements.json'));
let removed=0,kept=0;const report=[];
for(const node of doc.getRoot().listNodes()){
 if(node.getExtras().property!=='excalibur'||node.getExtras().source!=='castle-turrets'||node.getExtras().detail!==0||!node.getMesh())continue;
 for(const prim of node.getMesh().listPrimitives()){
  const pos=prim.getAttribute('POSITION'),idx=prim.getIndices(),arr=idx.getArray(),out=[];let cut=0;
  for(let i=0;i<arr.length;i+=3){const pts=[...arr.slice(i,i+3)].map(j=>pos.getElement(j,[]));
   const replace=masks.some(m=>pts.every(p=>p[1]>=.19&&p[1]<=11.6&&Math.hypot(p[0]-m.x,p[2]-m.z)<=m.r));
   if(replace){cut++;removed++;}else{out.push(arr[i],arr[i+1],arr[i+2]);kept++;}
  }
  if(cut)prim.setIndices(doc.createAccessor().setType('SCALAR').setArray(new Uint32Array(out)).setBuffer(idx.getBuffer()));
  report.push({node:node.getName(),removed:cut,retained:out.length/3});
 }
}
if(!removed)throw Error('No obsolete turret faces found; do not overwrite the model.');
for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
await io.write(file,doc);fs.writeFileSync('build/highrises/version.json',JSON.stringify({revision:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex').slice(0,16)}));
fs.writeFileSync('docs/project-records/excalibur-arcade/replacement-report.json',JSON.stringify({removed,retainedTargetFaces:kept,scope:'Only indices inside ten mapped pier radii below 11.6m; other node meshes and all collision unchanged.',nodes:report},null,2)+'\n');console.log({removed,kept});
