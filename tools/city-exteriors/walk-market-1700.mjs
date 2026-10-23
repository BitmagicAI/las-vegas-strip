// Controller settings match engine/engine/physics/PhysicsWorld.ts.
// Match PhysicsBodyFactory: FIX_INTERNAL_EDGES (144) for trimeshes.
import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const world=new R.World({x:0,y:-9.81,z:0});
const owners=new Map();for(const [ci,c] of [...read('build/geographic-strip/city-colliders.json'),...read('src/work/geographic/level.json').colliders,read('build/strip-landmarks/market1700-exterior-collision.json')].entries())if(c.vertices?.length&&c.indices?.length){const hit=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices),144));owners.set(hit.handle,c.name??`collision ${ci}`);}
world.step();const route=[[1814.5667106097262, -3882.8124070236695], [1809.003476293988, -3872.1798897324447], [1803.4402419782498, -3861.54737244122], [1797.5293055177779, -3850.2503228192936]];
const results=[];for(const direction of [1,-1]){
 const pts=direction===1?route:[...route].reverse();const first=pts[0];const ground=world.castRay(new R.Ray({x:first[0],y:1.5,z:first[1]},{x:0,y:-1,z:0}),3,true);if(!ground)throw Error('No initial ground '+JSON.stringify({direction,first}));
 const body=world.createRigidBody(R.RigidBodyDesc.kinematicPositionBased().setTranslation(first[0],1.5-ground.timeOfImpact+.85,first[1]));const collider=world.createCollider(R.ColliderDesc.capsule(.55,.28),body);const control=world.createCharacterController(.08);control.setNormalNudgeFactor(.01);control.setSlideEnabled(true);control.enableSnapToGround(.5);control.enableAutostep(.65,.3,false);control.setMaxSlopeClimbAngle(50*Math.PI/180);control.setMinSlopeSlideAngle(45*Math.PI/180);world.step();
 const legs=[];for(const goal of pts.slice(1)){
  let frames=0;for(;frames<1600;frames++){const p=body.translation();const dx=goal[0]-p.x,dz=goal[1]-p.z,len=Math.hypot(dx,dz);if(len<.09)break;const step=Math.min(.065,len);control.computeColliderMovement(collider,{x:dx/len*step,y:-.06,z:dz/len*step});const delta=control.computedMovement();body.setNextKinematicTranslation({x:p.x+delta.x,y:p.y+delta.y,z:p.z+delta.z});world.step();}
  const p=body.translation();const collisions=[];for(let i=0;i<control.numComputedCollisions();i++){const c=control.computedCollision(i);collisions.push({owner:owners.get(c.collider.handle),normal:c.normal1,point:c.witness1});}legs.push({goal,frames,position:p,collisions:frames===1600?collisions:undefined,reached:Math.hypot(goal[0]-p.x,goal[1]-p.z)<.1});if(!legs.at(-1).reached)break;
 }results.push({direction,legs,passed:legs.length===pts.length-1&&legs.every(x=>x.reached)});world.removeCharacterController(control);world.removeRigidBody(body);
}
world.free();fs.writeFileSync('build/city-exteriors/market-1700-walk.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));if(results.some(r=>!r.passed))process.exitCode=1;
