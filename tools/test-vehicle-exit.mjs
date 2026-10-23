import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
import { vehicleExitCandidates } from '../src/work/VehicleExit.ts';
await RAPIER.init();
let checks=0;
for (const yaw of [0,Math.PI/2,Math.PI,-Math.PI/2,.37,-2.1]) {
 const world=new RAPIER.World({x:0,y:-9.81,z:0});
 const position={x:-40,y:.8,z:9}, forward={x:Math.sin(yaw),z:Math.cos(yaw)};
 const q={x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)};
 const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(position.x,0,position.z).setRotation(q));
 world.createCollider(RAPIER.ColliderDesc.cuboid(1.25,1.3,2.35).setTranslation(0,1.3,0),body);
 world.step();
 const radius=.3,height=1.7,shape=new RAPIER.Capsule(height/2-radius,radius);
 const clear=p=>!world.intersectionWithShape({x:p.x,y:height/2+.025,z:p.z},{x:0,y:0,z:0,w:1},shape);
 const candidates=vehicleExitCandidates(position,forward,radius);
 assert(clear(candidates[0]),`Door exit overlaps vehicle at yaw ${yaw}`);checks++;
 // Wall blocks the preferred door; the opposite door remains usable.
 const p=candidates[0];const wall=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(p.x,.9,p.z));
 world.createCollider(RAPIER.ColliderDesc.cuboid(.5,.9,.5),wall);world.step();
 assert(!clear(candidates[0]));assert(clear(candidates[1]));checks+=2;
 world.free();
}
console.log(`${checks} rotated jeep / blocked-door collision checks passed`);
