import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '@dimforge/rapier3d-compat';
await R.init();
const root='build/resort-blocks/bellagio/';
const c=JSON.parse(fs.readFileSync(root+'bellagioBlock-exterior-runtime-collision.json'));
const guards=JSON.parse(fs.readFileSync(root+'ramp-barriers.json'));
const world=new R.World({x:0,y:0,z:0});
world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices),144));
world.step();let checks=0;
for(const g of guards){
 for(const side of [-1,1]){
  const [x,y,z]=g.mid,[nx,nz]=g.normal;
  const ray=new R.Ray({x:x+nx*side*.65,y:y+.55,z:z+nz*side*.65},{x:-nx*side,y:0,z:-nz*side});
  const hit=world.castRay(ray,1.3,true);
  assert.ok(hit,`Missing barrier from side ${side} at ${g.mid}`);checks++;
 }
}
// Drive a tire-sized rigid body into representative guards from either side.
let impacts=0;
for(const index of [0,Math.floor(guards.length/2),guards.length-1])for(const side of [-1,1]){
 const g=guards[index],[x,y,z]=g.mid,[nx,nz]=g.normal;
 const body=world.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(x+nx*side*.8,y+.55,z+nz*side*.8).setCcdEnabled(true));
 world.createCollider(R.ColliderDesc.ball(.3).setRestitution(0),body);
 body.setLinvel({x:-nx*side*5,y:0,z:-nz*side*5},true);
 for(let i=0;i<30;i++)world.step();
 const p=body.translation();
 assert.ok(((p.x-x)*nx+(p.z-z)*nz)*side>.1,`Rigid body passed through guard ${index}`);
 world.removeRigidBody(body);impacts++;
}
const result={rigidBodyImpacts:impacts,segments:guards.length,lateralCollisionChecks:checks,failures:0};
fs.writeFileSync(root+'ramp-barrier-audit.json',JSON.stringify(result,null,2));console.log(result);
