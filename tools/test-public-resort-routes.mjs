import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const level=JSON.parse(fs.readFileSync('build/hotels/staged-vegas.mesh-level.json'));
const added=level.colliders.filter(c=>c.name.startsWith('Public design /'));
await RAPIER.init();const world=new RAPIER.World({x:0,y:0,z:0}),names=new Map();
for(const c of added){
 const b=world.createRigidBody(RAPIER.RigidBodyDesc.fixed().setTranslation(...c.position).setRotation({x:0,y:Math.sin(c.yaw/2),z:0,w:Math.cos(c.yaw/2)}));
 const shape=world.createCollider(RAPIER.ColliderDesc.cuboid(...c.size.map(v=>v/2)),b);names.set(shape.handle,c.name);
}
world.step();const failures=[];let checks=0;const q={x:0,y:0,z:0,w:1},capsule=new RAPIER.Capsule(.64,.31);
function route(name,points){
 for(let j=1;j<points.length;j++){
  const a=points[j-1],b=points[j],n=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.25);
  for(let i=0;i<=n;i++){
   const p={x:a[0]+(b[0]-a[0])*i/n,y:1.1,z:a[1]+(b[1]-a[1])*i/n};checks++;
   const hit=world.intersectionWithShape(p,q,capsule);if(hit)failures.push({name,p,blocker:names.get(hit.handle)});
  }
 }
}
// Both sides of every existing exterior opening, with a full standing capsule.
const doors=JSON.parse(fs.readFileSync('build/level/vegas.doors.json'));
for(const d of doors){const {x,z}=d.position,a=d.rotationY??0;route(d.id,[[x-7*Math.sin(a),z-7*Math.cos(a)],[x+7*Math.sin(a),z+7*Math.cos(a)]]);}
for(const t of JSON.parse(fs.readFileSync('src/work/hotels/towers.json'))){
 const [x,,z]=t.origin,c=Math.cos(t.yaw),s=Math.sin(t.yaw);route(t.id+' guest approach',[[-12*s+x,-12*c+z],[-5*s+x,-5*c+z]]);
}
for(const [name,p] of Object.entries({
 paris:[[68,-39],[81,-39],[120,-39],[120,5]],
 caesars:[[-88,-242],[-158,-242]],'caesars-garden':[[-109,-242],[-109,-216]],
 cosmopolitan:[[-25,242],[-171,242]],'cosmo-reception':[[-41,242],[-41,264]],
 flamingo:[[87,-237],[160,-237],[160,-219],[145,-219],[145,-212]],
 horseshoe:[[110,-151],[110,-89]],
 'planet-hollywood':[[61,218],[119,218]],'ph-retail':[[174,190],[174,270]],
 aria:[[-239,448],[-267,448],[-295,448],[-309,440],[-443,440]],
 vdara:[[-299,291],[-299,242],[-257,242]],
 waldorf:[[-91,528],[-91,552],[-77,568],[-35,576]],
 'veer-east':[[-93,456],[-123,456],[-123,453.425],[-129.8,453.425]],
 'veer-west':[[-163,397],[-163,422.575],[-193.8,422.575]]
}))route(name,p);
world.free();
const report={checks,newColliders:added.length,failures};fs.writeFileSync('build/public-resorts/routes-test.json',JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,failures:failures.slice(0,12)},null,2));assert.equal(failures.length,0,'New architecture obstructs an existing public route');
