import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
await RAPIER.init();
const world=new RAPIER.World({x:0,y:-9.81,z:0});
const exterior=read('build/resort-blocks/bellagio/bellagioBlock-exterior-runtime-collision.json');
const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(exterior.vertices),new Uint32Array(exterior.indices)),body);
for(const c of read('build/geographic-strip/city-colliders.json')){
 if(c.center[0]<-160||c.center[0]>160||c.center[1]<320||c.center[1]>640)continue;
 world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
}
world.step();let floorChecks=0,capChecks=0;
// This is the sidewalk/arrival seam facing the Paris balloon in the owner's image.
for(let z=522;z<=537;z+=.5){
 for(let x=-24;x<=-20;x+=.1){
  const hit=world.castRay(new RAPIER.Ray({x,y:1,z},{x:0,y:-1,z:0}),1.1,true);
  assert(hit,`Missing floor at ${x},${z}`);floorChecks++;
 }
 const edgeFloor=world.castRay(new RAPIER.Ray({x:-21.999,y:1,z},{x:0,y:-1,z:0}),1.1,true);
 if(!edgeFloor||1-edgeFloor.timeOfImpact<.15)continue;
 const cap=world.castRay(new RAPIER.Ray({x:-22.5,y:.12,z},{x:1,y:0,z:0}),.6,false);
 assert(cap,`Open curb cross-section at z=${z}`);capChecks++;
}
assert(capChecks>10,'No raised curb sections checked');
const report={floorChecks,capChecks,passed:true};
fs.writeFileSync('build/resort-blocks/bellagio/water-edge-collision-audit.json',JSON.stringify(report,null,2));
console.log(report);world.free();
