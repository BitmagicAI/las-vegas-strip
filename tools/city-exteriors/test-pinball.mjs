import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
await R.init();const w=new R.World({x:0,y:-9.81,z:0});const read=p=>JSON.parse(fs.readFileSync(p));
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/pinballHall-exterior-collision.json')])if(c.vertices?.length&&c.indices?.length)w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
w.step();let samples=0;const failures=[];
for(let x=75;x<155;x+=3)for(let z=3440;z<3502;z+=3){samples++;const hit=w.castRay(new R.Ray({x,y:1,z},{x:0,y:-1,z:0}),1.2,true);if(!hit)failures.push({x,z});}
const result={samples,failures,scope:'Forecourt floor support only. No claim of an accessible museum interior.'};fs.writeFileSync('build/city-exteriors/pinball-collision.json',JSON.stringify(result,null,2));console.log(result);w.free();if(failures.length)process.exitCode=1;
