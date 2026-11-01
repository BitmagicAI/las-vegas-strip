import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';import {CollisionPack} from '../../src/work/CollisionPack.ts';await R.init();
const world=new R.World({x:0,y:-9.81,z:0});
const load=async path=>{const b=fs.readFileSync(path),p=await CollisionPack.decode(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));for(let i=0;i<p.count;i++)world.createCollider(R.ColliderDesc.trimesh(p.vertices(i),p.indices(i),144));};
for(const key of ['flamingoGoPool','flamingoExterior','flamingoGarden','hgvFlamingoExterior'])await load(`build/strip-landmarks/${key}-exterior-collision.bin`);
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/collision-cells/manifest.json')).cells)await load('build/geographic-strip/collision-cells/'+c.file);
world.step();const routes=JSON.parse(fs.readFileSync('build/city-exteriors/flamingo-go-pool-routes.json'));let samples=0,terrain=0;const failures=[];
for(const route of routes)for(let k=1;k<route.points.length;k++){
 const a=route.points[k-1],b=route.points[k],L=Math.hypot(b[0]-a[0],b[2]-a[2]),dx=(b[0]-a[0])/L,dz=(b[2]-a[2])/L;
 for(let t=0;t<=L;t+=.25)for(const off of [-.4,0,.4]){
  const x=a[0]+dx*t-dz*off,z=a[2]+dz*t+dx*off,y=a[1]+(b[1]-a[1])*t/L;
  const floor=world.castRay(new R.Ray({x,y:y+.4,z},{x:0,y:-1,z:0}),.7,true);samples++;
  if(!floor){if(y<.2)terrain++;else failures.push({route:route.name,kind:'floor-missing',x,y,z});continue;}
  const fy=y+.4-floor.timeOfImpact;if(Math.abs(fy-y)>.18)failures.push({route:route.name,kind:'floor-height',x,y,z,fy});
  const head=world.castRay(new R.Ray({x,y:fy+.08,z},{x:0,y:1,z:0}),1.75,true);samples++;if(head)failures.push({route:route.name,kind:'headroom',x,y,z});
  if(t+.3<L)for(const h of [.45,1,1.7]){samples++;if(world.castRay(new R.Ray({x,y:fy+h,z},{x:dx,y:0,z:dz}),.3,true))failures.push({route:route.name,kind:'obstruction',x,y,z,h});}
 }
}
const report={samples,terrainFloorSamples:terrain,failures};fs.writeFileSync('docs/project-records/flamingo-go-pool/collision.json',JSON.stringify(report,null,2)+'\n');console.log(report);world.free();assert.equal(failures.length,0);
