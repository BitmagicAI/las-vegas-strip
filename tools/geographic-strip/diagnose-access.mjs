import fs from 'node:fs';
import R from '@dimforge/rapier3d-compat';
await R.init();let errors=JSON.parse(fs.readFileSync('build/geographic-strip/access/audit.json')).errors;
for(const id of [...new Set(errors.map(e=>e.id))]){
const data=JSON.parse(fs.readFileSync(`build/geographic-strip/access/${id}.json`)),c=data.collision;
const w=new R.World({x:0,y:-9.81,z:0}),names=new Map();
for(const [mat,start,count] of c.spans){const col=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices.slice(start*3,(start+count)*3))));names.set(col.handle,mat)}w.step();
for(const e of [errors.find(e=>e.id===id&&e.body),errors.find(e=>e.id===id&&e.floor==null)].filter(Boolean)){
 const[x,y,z]=e.p;let hits=[];w.intersectionsWithShape({x,y:y+1,z},{x:0,y:0,z:0,w:1},new R.Capsule(.5,.28),col=>{hits.push(names.get(col.handle));return true});
 const ground=w.castRay(new R.Ray({x,y:y+.28,z},{x:0,y:-1,z:0}),30,true);
 console.log(id,'route',e.route,'p',e.p,'hits',hits,'ground',ground?.timeOfImpact,ground?names.get(ground.collider.handle):'none');
}w.free();}
