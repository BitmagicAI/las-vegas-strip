// Replace only source-tagged rooftop machinery; retain the installed tower and gateway.
import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {NodeIO} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/core/dist/index.js';
import {ALL_EXTENSIONS} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/extensions/dist/index.js';
import {mergeDocuments,unpartition,prune} from '../optimize/bm-tools/gltf/node_modules/@gltf-transform/functions/dist/index.js';
import {MeshoptDecoder} from '../optimize/bm-tools/gltf/node_modules/meshoptimizer/index.js';
await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
const base='build/strip-landmarks/',backup='build/city-exteriors/strat-pool-rooftop-refinement/source-before/';
const doc=await io.read(backup+'stratExterior-exterior.glb'),extra=await io.read(base+'stratRidesRefinement-exterior.glb');
const signature=n=>JSON.stringify({name:n.getName(),extras:n.getExtras(),matrix:n.getMatrix(),primitives:n.getMesh()?.listPrimitives().map(p=>({indices:p.getIndices()?Array.from(p.getIndices().getArray()):null,attributes:p.listSemantics().map(s=>[s,Array.from(p.getAttribute(s).getArray())]),material:p.getMaterial()?.getName()}))});
const replaced=doc.getRoot().listNodes().filter(n=>n.getExtras().source==='strat-rooftop-rides');assert.equal(replaced.length,8);
const retained=doc.getRoot().listNodes().filter(n=>!replaced.includes(n)),before=retained.map(signature),gateway=retained.filter(n=>n.getExtras().source==='strat-gateway');assert.ok(gateway.length>0);
for(const n of extra.getRoot().listNodes())assert.equal(n.getExtras().source,'strat-rooftop-rides');
for(const n of replaced)n.dispose();
const map=mergeDocuments(doc,extra),scene=doc.getRoot().getDefaultScene();
for(const s of extra.getRoot().listScenes()){const copied=map.get(s);for(const n of copied.listChildren()){n.setExtras({...n.getExtras(),property:'stratExterior'});scene.addChild(n);}copied.dispose();}
assert.deepEqual(retained.map(signature),before);await doc.transform(prune(),unpartition());
for(const e of doc.getRoot().listExtensionsUsed())if(e.extensionName==='EXT_meshopt_compression')e.dispose();
await io.write(base+'stratExterior-exterior.glb',doc);
assert.deepEqual(fs.readFileSync(base+'stratExterior-exterior-collision.json'),fs.readFileSync(backup+'stratExterior-exterior-collision.json'));
const report={replacedNodes:replaced.length,retainedNodes:retained.length,gatewayNodes:gateway.length,retainedGeometryAndTransformsExact:true,collisionByteIdentical:true,source:crypto.createHash('sha256').update(fs.readFileSync(backup+'stratExterior-exterior.glb')).digest('hex')};
fs.writeFileSync('docs/project-records/strat-pool-rooftop-refinement/preservation.json',JSON.stringify(report,null,2)+'\n');console.log(report);
