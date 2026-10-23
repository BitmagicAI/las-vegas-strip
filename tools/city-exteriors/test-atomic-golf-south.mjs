import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
await R.init();const w=new R.World({x:0,y:-9.81,z:0});const read=p=>JSON.parse(fs.readFileSync(p));
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/atomicGolf-exterior-collision.json')])if(c.vertices?.length&&c.indices?.length)w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
w.step();const samples=read('build/city-exteriors/atomic-south-samples.json'),failures=[];
for(const [x,y,z] of samples){const h=w.castRay(new R.Ray({x,y:y+.1,z},{x:0,y:-1,z:0}),.2,true);const ceiling=w.castRay(new R.Ray({x,y:y+.15,z},{x:0,y:1,z:0}),1.9,true);if(!h||ceiling)failures.push({x,y,z,floor:!!h,blocked:!!ceiling});}
const report={samples:samples.length,failures,scope:'Open bay support and1.9m headroom; does not establish vertical access or doors.'};fs.writeFileSync('build/city-exteriors/atomic-south-collision.json',JSON.stringify(report,null,2));console.log(report);w.free();if(failures.length)process.exitCode=1;
