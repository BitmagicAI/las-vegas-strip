import fs from 'node:fs';
import R from '@dimforge/rapier3d-compat';
await R.init();
const meta=JSON.parse(fs.readFileSync('build/sphere/sphere.json'));
const world=new R.World({x:0,y:-9.81,z:0});
for(const section of ['exterior','interior']){
 const {collision:c}=JSON.parse(fs.readFileSync(`build/sphere/${section}.json`));
 world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
}
// Test the final composition too: nearby mapped buildings and elevated paths
// must not leave hidden colliders inside the replacement venue or its doors.
let cityCells=0;
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json'))){
 if(Math.hypot(c.center[0]-meta.center[0],c.center[1]-meta.center[2])>300)continue;
 const vertices=new Float32Array(c.vertices.map((v,i)=>v-meta.center[i%3]));
 world.createCollider(R.ColliderDesc.trimesh(vertices,new Uint32Array(c.indices)));cityCells++;
}
world.step();const errors=[];let checks=0;
for(const {name,points} of meta.routes)for(let j=1;j<points.length;j++){
 const a=points[j-1],b=points[j];const count=Math.ceil(Math.hypot(...b.map((v,k)=>v-a[k]))/.25);
 for(let i=0;i<=count;i++){
  const [x,y,z]=a.map((v,k)=>v+(b[k]-v)*i/count);checks++;
  const ray=world.castRay(new R.Ray({x,y:y+.26,z},{x:0,y:-1,z:0}),.58,true);
  const body=world.intersectionWithShape({x,y:y+1.06,z},{x:0,y:0,z:0,w:1},new R.Capsule(.53,.28));
  if(!ray||body)errors.push({name,p:[x,y,z],floor:ray?.timeOfImpact,blocked:!!body});
 }
}
// All entrances must close physically and clear their passage when slid aside.
let doors=0;
for(const p of meta.portals){
 const yaw=Math.atan2(...p.direction),q={x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)};
 const [x,y,z]=p.p;const c=world.createCollider(R.ColliderDesc.cuboid(p.width/2,p.height/2,.06).setTranslation(x,y+p.height/2,z).setRotation(q));
 world.step();let hit=world.intersectionWithShape({x,y:y+1.06,z},{x:0,y:0,z:0,w:1},new R.Capsule(.53,.28));
 if(!hit)errors.push({name:p.name,error:'closed portal fails to block'});
 world.removeCollider(c,true);world.step();hit=world.intersectionWithShape({x,y:y+1.06,z},{x:0,y:0,z:0,w:1},new R.Capsule(.53,.28));
 if(hit)errors.push({name:p.name,error:'open portal blocked'});doors+=2;
}
const summary={checks,doors,cityCells,seats:meta.seats.length,errors:errors.length};
fs.writeFileSync('build/sphere/audit.json',JSON.stringify({...summary,failures:errors},null,2));console.log(JSON.stringify({...summary,first:errors.slice(0,16)},null,2));world.free();if(errors.length)process.exitCode=1;
