// Canopy drive aisle must have real horizontal and vertical clearance.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
await RAPIER.init();const w=new RAPIER.World({x:0,y:-9.81,z:0});
const read=p=>JSON.parse(fs.readFileSync(p));
const cs=[...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/lawrys-hughes-exterior-collision.json')];
for(const c of cs)w.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
w.step();const yaw=Math.PI/2+.058,co=Math.cos(yaw),si=Math.sin(yaw);let checks=0;const failures=[];
for(let u=-8;u<=8;u+=.4)for(const v of [7,9,11]){
 const x=1202.55+co*u+si*v,z=97.8-si*u+co*v;
 const hit=w.intersectionWithShape({x,y:1.95,z},{x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)},new RAPIER.Cuboid(.19,1.45,1));
 checks++;if(hit)failures.push({u,v});
}
assert(!read('build/geographic-strip/building-index.json').some(b=>b.id==='way/896655229'));
w.free();const result={checks,failures,scope:'3m tall clear aisle under the canopy, current city collision'};
fs.writeFileSync('build/strip-landmarks/lawrys-hughes-route-audit.json',JSON.stringify(result,null,2));console.log(result);assert.equal(failures.length,0);
