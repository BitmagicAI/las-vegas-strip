import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '@dimforge/rapier3d-compat';
await R.init();
const cells=JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json'));
const w=new R.World({x:0,y:-9.81,z:0});let checked=0;
for(const c of cells){
 assert.ok(c.indices.length>0,`Empty collision cell ${c.id}`);
 const [x,z]=c.id.split(',').map(Number);
 if(Math.abs(x-4)>2||Math.abs(z+5)>2)continue;
 const body=w.createRigidBody(R.RigidBodyDesc.fixed());
 w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)),body);checked++;
}
w.step();assert.ok(checked>0);console.log({cells:cells.length,expoNeighborhoodColliders:checked,passed:true});w.free();
