import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();const w=new R.World({x:0,y:-9.81,z:0}),c=JSON.parse(fs.readFileSync('build/strip-landmarks/caesarsExterior-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();
let legacyColliders=0,cityCells=0;const names=new Map();
for(const cc of JSON.parse(fs.readFileSync('src/work/geographic/level.json')).colliders){
 if(!cc.vertices)continue;
 const v=cc.vertices;let near=false;for(let i=0;i<v.length;i+=3)if(v[i]>-220&&v[i]<-50&&v[i+2]>-150&&v[i+2]<100){near=true;break;}if(!near)continue;
 const d=cc.shape==='trimesh'?R.ColliderDesc.trimesh(new Float32Array(v),new Uint32Array(cc.indices)):R.ColliderDesc.convexHull(new Float32Array(v));if(d){const c=w.createCollider(d);names.set(c.handle,cc.name);legacyColliders++;}
}
for(const cc of JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json'))){const v=cc.vertices;let near=false;for(let i=0;i<v.length;i+=3)if(v[i]>-220&&v[i]<-50&&v[i+2]>-150&&v[i+2]<100){near=true;break;}if(near&&cc.indices.length){const c=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(v),new Uint32Array(cc.indices)));names.set(c.handle,'city '+cc.id);cityCells++;}}
w.step();
const q={x:0,y:0,z:0,w:1},shape=new R.Capsule(.55,.3),failures=[];let samples=0;
for(const [name,ax,az,bx,bz] of [['main-arrival',-110,-17,-130,-17],['retained-entry-approach',-91,-81,-162,-81],['omnia-entrance',-68,-127,-90,-127],['south-entry',-115,72,-142,72],['arrival-link-a',-130,-17,-155,-17],['arrival-link-b',-155,-17,-155,-81],['casino-approach',-155,-81,-178,-81]])for(let i=0;i<=20;i++){const p={x:ax+(bx-ax)*i/20,y:1.2,z:az+(bz-az)*i/20};samples++;const hit=w.intersectionWithShape(p,q,shape);if(hit)failures.push({name,...p,collider:names.get(hit.handle),ground:w.castRay(new R.Ray({x:p.x,y:5,z:p.z},{x:0,y:-1,z:0}),6,true)?.timeOfImpact});}
const report={samples,legacyColliders,cityCells,failures,scope:'Capsule clearance through new shell and approach segments with legacy static geometry and surrounding city collision. Dynamic doors and full public interior layout not covered.'};fs.writeFileSync('build/city-exteriors/caesars-podium-access-test.json',JSON.stringify(report,null,2));console.log(report);w.free();assert.equal(failures.length,0);
