import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
await R.init();const w=new R.World({x:0,y:-9.81,z:0});const read=p=>JSON.parse(fs.readFileSync(p));
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/harleyDealership-exterior-collision.json')])if(c.vertices?.length&&c.indices?.length)w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
w.step();let samples=0;const failures=[];
for(let x=40;x<90;x+=3)for(let z=3602;z<3695;z+=3){samples++;const hit=w.castRay(new R.Ray({x,y:1,z},{x:0,y:-1,z:0}),1.2,true);if(!hit)failures.push({x,z});}
const result={samples,failures,scope:'Forecourt floor support only. No claim of an accessible dealership interior.'};fs.writeFileSync('build/city-exteriors/harley-collision.json',JSON.stringify(result,null,2));console.log(result);w.free();if(failures.length)process.exitCode=1;
