import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '@dimforge/rapier3d-compat';
await R.init();
const read=p=>JSON.parse(fs.readFileSync(p)),level=read('build/geographic-strip/detailed.mesh-level.json'),cells=read('build/geographic-strip/city-colliders.json'),network=read('build/geographic-strip/road-network.json');
const world=new R.World({x:0,y:0,z:0}),names=new Map();
function add(c){let d;if(c.shape==='box')d=R.ColliderDesc.cuboid(...c.size.map(v=>v/2)).setTranslation(...c.position).setRotation({x:0,y:Math.sin((c.yaw??0)/2),z:0,w:Math.cos((c.yaw??0)/2)});else if(c.shape==='trimesh')d=R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices));else d=R.ColliderDesc.convexHull(new Float32Array(c.vertices));assert(d,c.name);let col=world.createCollider(d);names.set(col.handle,c.name);}
for(const c of level.colliders)add(c);for(const c of cells)add({...c,shape:'trimesh',name:'OSM '+c.id});world.step();
const failures=[],floorFailures=[],route=network.stripRoute;let checks=0;
for(let j=1;j<route.length;j++){
 const a=route[j-1],b=route[j],dx=b[0]-a[0],dz=b[2]-a[2],n=Math.max(1,Math.ceil(Math.hypot(dx,dz)/2)),yaw=Math.atan2(dx,dz),q={x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)};
 for(let i=0;i<=n;i++){
  const t=i/n,x=a[0]+dx*t,z=a[2]+dz*t,y=a[1]+(b[1]-a[1])*t;
  const floor=world.castRay(new R.Ray({x,y:y+.5,z},{x:0,y:-1,z:0}),1.0,true);checks++;
  if(!floor)floorFailures.push({j,i,x,y,z});
  const p={x,y:y+1.05,z};world.intersectionsWithShape(p,q,new R.Cuboid(.94,.65,1.95),col=>{failures.push({j,i,x,y,z,blocker:names.get(col.handle)});return true;});
 }
}
const report={routeMeters:read('build/geographic-strip/report.json').stripRouteMeters,checks,physicsCells:cells.length,failures,floorFailures};fs.writeFileSync('build/geographic-strip/road-physics-test.json',JSON.stringify(report,null,2));console.log(JSON.stringify({...report,failures:failures.slice(0,15),floorFailures:floorFailures.slice(0,5),totalFailures:failures.length,totalFloorFailures:floorFailures.length},null,2));world.free();assert.equal(failures.length,0,'Vehicle envelope intersects mapped Strip route');assert.equal(floorFailures.length,0,'Route has missing drivable floor');
