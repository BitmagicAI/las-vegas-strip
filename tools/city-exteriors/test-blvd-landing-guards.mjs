import fs from 'node:fs';
import R from '@dimforge/rapier3d-compat';
await R.init();const w=new R.World({x:0,y:-9.81,z:0});const c=JSON.parse(fs.readFileSync('build/strip-landmarks/blvdRetail-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();const results=[];
for(const x of [59.4,60.5,61.6])for(const side of [-1,1]){const h=w.castRay(new R.Ray({x,y:7.65,z:1093.6},{x:0,y:0,z:side}),1.9,true);results.push({x,side,protected:!!h,distance:h?.timeOfImpact});}
console.log(JSON.stringify({results,passed:results.every(x=>x.protected)},null,2));w.free();

if(!results.every(x=>x.protected))process.exitCode=1;
