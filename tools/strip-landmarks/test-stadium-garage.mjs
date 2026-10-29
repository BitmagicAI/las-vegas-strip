// Scoped public-route check, with the current surrounding city collision.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
assert(!read('build/geographic-strip/building-index.json').some(b=>['way/790044912'].includes(b.id)));
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/stadium-garage-exterior-collision.json')]){
 const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
 world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)),body);
}
// Match the game's district foundation, which is separate from city facade colliders.
for(const c of read('src/work/geographic/level.json').colliders){
 if(c.shape!=='box'||!c.name.startsWith('OSM district foundation'))continue;
 const [x,y,z]=c.position; if(Math.abs(x+777)>200||Math.abs(z-1805)>200)continue;
 world.createCollider(RAPIER.ColliderDesc.cuboid(...c.size.map(v=>v/2)).setTranslation(x,y,z));
}
world.step();
const meta=read('build/strip-landmarks/stadium-garage-metadata.json'),failures=[];let checks=0;
for(const route of meta.routes)for(let k=1;k<route.points.length;k++){
 const a=route.points[k-1],b=route.points[k],n=Math.ceil(Math.hypot(...b.map((v,i)=>v-a[i]))/.3);
 for(let i=0;i<=n;i++){
  const [x,y,z]=a.map((v,j)=>v+(b[j]-v)*i/n);checks++;
  const hit=world.intersectionWithShape({x,y:y+1.1,z},{x:0,y:0,z:0,w:1},new RAPIER.Capsule(.65,.29));
  const floor=world.castRay(new RAPIER.Ray({x,y:y+.25,z},{x:0,y:-1,z:0}),.55,true);
  if(hit||!floor)failures.push({x,y,z,blocked:!!hit,floor:!!floor});
 }
}
// Cast sideways from the middle of every flight toward both visible rails.
const yaw=-Math.atan2(30.624,25.216),co=Math.cos(yaw),si=Math.sin(yaw);
for(const [x,z] of [[23,-23],[72.8,-16]])for(let level=0;level<3;level++)for(let side=0;side<2;side++)for(const sign of [-1,1]){
 const lx=x+.68+side*1.44,lz=z+1.45,y=.12+level*3.24+(side?2.43:.81)+.6;
 const origin={x:-824.745+co*lx+si*lz,y,z:1779.52-si*lx+co*lz};
 const hit=world.castRay(new RAPIER.Ray(origin,{x:co*sign,y:0,z:-si*sign}),.8,true);checks++;
 if(!hit)failures.push({type:'stair-side-rail',x,z,level,side,sign});
}
world.free();const result={checks,failures,city:true};
fs.writeFileSync('build/strip-landmarks/stadium-garage-route-audit.json',JSON.stringify(result,null,2));
console.log(result);assert.equal(failures.length,0);
