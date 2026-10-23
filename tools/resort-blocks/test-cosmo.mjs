import fs from 'node:fs';import assert from 'node:assert/strict';import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p)),B='build/resort-blocks/cosmo/';await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});const names=new Map();
function add(c,name){if(!c.indices.length)return;const rb=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)),rb);names.set(rb.handle,name);}
for(const v of read(B+'venues.json'))for(const layer of ['exterior','interior'])add(read(B+v.key+'-'+layer+'-collision.json'),v.key+'/'+layer);
if(process.argv.includes('--city'))for(const c of read('build/geographic-strip/city-colliders.json'))add(c,'city '+c.id);
world.step();const capsule=new RAPIER.Capsule(.60,.28),q={x:0,y:0,z:0,w:1},report={checks:0,failures:[],city:process.argv.includes('--city')};
for(const route of read(B+'routes.json'))for(let s=1;s<route.points.length;s++){
 const a=route.points[s-1],b=route.points[s],n=Math.max(1,Math.ceil(Math.hypot(...a.map((v,i)=>v-b[i]))/.3));
 for(let i=0;i<=n;i++){let p=a.map((v,j)=>v+(b[j]-v)*i/n);const body=world.intersectionWithShape({x:p[0],y:p[1]+1.25,z:p[2]},q,capsule),floor=world.castRay(new RAPIER.Ray({x:p[0],y:p[1]+.35,z:p[2]},{x:0,y:-1,z:0}),.75,true);report.checks++;if(body||!floor)report.failures.push({route:route.name,p,blocker:body?names.get(body.parent().handle):null,floor:!!floor});}
}
// A clear standing capsule is insufficient: exercise Rapier's movement solver
// against the ramp face in both directions, including the bottom/top seams.
report.stairWalks=[];
for(const route of read(B+'routes.json').filter(r=>r.name.startsWith('public stair'))){
 for(const reverse of [false,true]){
  const [a,,b]=route.points;const x=a[0],z=reverse?b[2]+.7:a[2]-.7,y=reverse?b[1]:a[1];
  const rb=world.createRigidBody(RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(x,y+.92,z));
  const collider=world.createCollider(RAPIER.ColliderDesc.capsule(.60,.28),rb),motor=world.createCharacterController(.02);
  motor.setMaxSlopeClimbAngle(50*Math.PI/180);motor.enableSnapToGround(.5);motor.disableAutostep();
  for(let i=0;i<260;i++){
   world.step();motor.computeColliderMovement(collider,{x:0,y:-.01,z:reverse?-.075:.075});
   const p=rb.translation(),m=motor.computedMovement();rb.setNextKinematicTranslation({x:p.x+m.x,y:p.y+m.y,z:p.z+m.z});
  }
  world.step();const p=rb.translation(),passed=reverse?p.z<a[2]-.3&&p.y<y-4.5:p.z>b[2]+.3&&p.y>y+4.5;
  report.stairWalks.push({route:route.name,reverse,passed,end:[p.x,p.y,p.z]});
  if(!passed)report.failures.push({route:route.name,reverse,reason:'kinematic stair traversal failed'});
  world.removeCharacterController(motor);world.removeRigidBody(rb);
 }
}
fs.writeFileSync(B+'route-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({...report,failures:report.failures.slice(0,12)},null,2));assert.equal(report.failures.length,0);
