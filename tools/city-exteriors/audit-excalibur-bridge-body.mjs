import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';import {CollisionPack} from '../../src/work/CollisionPack.ts';
await R.init();const w=new R.World({x:0,y:-9.81,z:0});const names=new Map();
for(const cell of JSON.parse(fs.readFileSync('build/geographic-strip/collision-cells/manifest.json')).cells){const bytes=fs.readFileSync('build/geographic-strip/collision-cells/'+cell.file),pack=await CollisionPack.decode(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength));for(let i=0;i<pack.count;i++){const q=w.createCollider(R.ColliderDesc.trimesh(pack.vertices(i),pack.indices(i),144));names.set(q.handle,cell.file);}}
{const c=JSON.parse(fs.readFileSync('build/highrises/excalibur-collision.json'));const q=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));names.set(q.handle,'excalibur-highrise');}
const path='build/strip-landmarks/excaliburFrontage-exterior-collision.json';if(fs.existsSync(path)){const c=JSON.parse(fs.readFileSync(path));const q=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));names.set(q.handle,'excaliburFrontage');}
w.step();const samples=JSON.parse(fs.readFileSync('docs/project-records/excalibur-bridge-refinement/bridge-samples.json')).samples;const failures=[],floorFailures=[];
for(const s of samples){const[x,y,z]=s.point;const q=w.intersectionWithShape({x,y:y+1.06,z},{x:0,y:0,z:0,w:1},new R.Capsule(.53,.28));const hit=w.castRay(new R.Ray({x,y:y+.3,z},{x:0,y:-1,z:0}),.6,true);if(!hit||Math.abs(y+.3-hit.timeOfImpact-y)>.25)floorFailures.push(s);if(q)failures.push({...s,owner:names.get(q.handle)});}
const report={samples:samples.length,failures,floorFailures};fs.writeFileSync('docs/project-records/excalibur-bridge-refinement/body-baseline.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));w.free();

if(failures.length||floorFailures.length)process.exitCode=1;
