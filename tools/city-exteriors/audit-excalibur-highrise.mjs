import fs from 'node:fs';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const old=await io.read('.bitmagic/city-exterior-backups/excalibur-arcade/highrises-exteriors.glb'),current=await io.read('build/highrises/exteriors.glb');
const changes=JSON.parse(fs.readFileSync('docs/project-records/excalibur-arcade/replacement-report.json'));let unchanged=0,removed=0;const rows=[];
for(const a of old.getRoot().listNodes()){
 const b=current.getRoot().listNodes().find(n=>n.getName()===a.getName());assert.ok(b,a.getName());assert.deepEqual(a.getMatrix(),b.getMatrix());assert.deepEqual(a.getExtras(),b.getExtras());
 if(!a.getMesh())continue;const ap=a.getMesh().listPrimitives(),bp=b.getMesh().listPrimitives();assert.equal(ap.length,bp.length);
 for(let i=0;i<ap.length;i++){
  const delta=ap[i].getIndices().getCount()/3-bp[i].getIndices().getCount()/3,expected=changes.nodes.find(n=>n.node===a.getName())?.removed||0;assert.equal(delta,expected,a.getName());removed+=delta;
  if(!expected){for(const edge of ['getMin','getMax']){const av=ap[i].getAttribute('POSITION')[edge]([]),bv=bp[i].getAttribute('POSITION')[edge]([]);assert.ok(av.every((v,j)=>Math.abs(v-bv[j])<.02),a.getName()+' bounds');}unchanged++;}
  rows.push({name:a.getName(),removed:delta});
 }
}
assert.equal(removed,changes.removed);const report={unchangedPrimitiveTriangleCountsAndBounds:unchanged,removed,allNodeTransformsAndExtrasPreserved:true,toleranceM:.02,scope:'Optimized output count/bounds/metadata preservation; not a per-pixel guarantee',nodes:rows};fs.writeFileSync('docs/project-records/excalibur-arcade/highrise-preservation.json',JSON.stringify(report,null,2)+'\n');console.log({unchanged,removed});
