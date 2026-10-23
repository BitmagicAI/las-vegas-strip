import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';await R.init();
const read=p=>JSON.parse(fs.readFileSync('build/geographic-strip/'+p));const w=new R.World({x:0,y:0,z:0});const names=new Map();
for(const c of read('bridge-only-colliders.json')){const q=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));names.set(q.handle,c.id)}
for(const e of read('access/manifest.json')){const c=read('access/'+e.id+'.json').collision;const q=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));names.set(q.handle,e.id)}w.step();
for(const e of read((process.argv[2]??'street-physics-bellagio-corner.json')).obstructions){const[x,y,z]=e.point;const hits=[];w.intersectionsWithShape({x,y:y+1.1,z},{x:0,y:0,z:0,w:1},new R.Cuboid(.25,.7,.25),c=>{hits.push(names.get(c.handle));return true});console.log(e.way,e.point,hits)}
