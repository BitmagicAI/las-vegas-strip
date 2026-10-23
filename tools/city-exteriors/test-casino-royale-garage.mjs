// Floor and ramp clearance against the installed city and garage collision.
import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
await R.init();const read=p=>JSON.parse(fs.readFileSync(p));const w=new R.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),...read('src/work/geographic/level.json').colliders,read('build/strip-landmarks/casinoRoyaleGarage-exterior-collision.json')])if(c.vertices?.length&&c.indices?.length)w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices),144));
w.step();const yaw=Math.atan2(1.394,51.853),point=(u,y,v)=>({x:201.764+Math.cos(yaw)*u+Math.sin(yaw)*v,y,z:-491.77-Math.sin(yaw)*u+Math.cos(yaw)*v});const failures=[];let count=0;
function check(u,y,v,headroom){count++;const p=point(u,y+.3,v),h=w.castRay(new R.Ray(p,{x:0,y:-1,z:0}),.5,true);if(!h||Math.abs(h.timeOfImpact-.3)>.04)failures.push({type:'floor',u,y,v,hit:h?.timeOfImpact});if(headroom){const q=point(u,y+.08,v),up=w.castRay(new R.Ray(q,{x:0,y:1,z:0}),2.5,true);if(up)failures.push({type:'clearance',u,y,v,height:up.timeOfImpact});}}
for(let level=0;level<6;level++)for(const u of [-15,-8,2,5,15])for(let v=-22;v<=22;v+=4)check(u,.24+3.2*level,v,true);
for(let level=0;level<5;level++)for(const u of [8,10,12])for(let v=-18;v<=18;v+=2)check(u,.24+3.2*level+(v+19)/38*3.2,v,true);
w.free();const r={samples:count,minimumHeadroom:2.58,failures,passed:!failures.length};fs.writeFileSync('build/city-exteriors/casino-royale-garage-support.json',JSON.stringify(r,null,2));console.log(JSON.stringify(r));if(failures.length)process.exitCode=1;
