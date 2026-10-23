import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const w=new R.World({x:0,y:-9.81,z:0}),c=JSON.parse(fs.readFileSync('build/strip-landmarks/fashion-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();const failures=[];let samples=0;
for(const q of JSON.parse(fs.readFileSync('build/city-exteriors/fashion-roof-samples.json'))){samples++;if(!w.castRay(new R.Ray({x:q[0],y:q[1]+.06,z:q[2]},{x:0,y:-1,z:0}),.12,true))failures.push(q);}
const venue=JSON.parse(fs.readFileSync('build/strip-landmarks/venues.json')).find(v=>v.key==='fashion'),z=venue.zones[0],co=Math.cos(z.yaw),si=Math.sin(z.yaw);let routeSamples=0;
const check=(x,y,zz)=>{const p={x:z.origin[0]+co*x+si*zz,y:y+z.origin[1],z:z.origin[2]-si*x+co*zz};routeSamples++;if(!w.castRay(new R.Ray({...p,y:p.y+.05},{x:0,y:-1,z:0}),.11,true))failures.push({support:p});if(w.castRay(new R.Ray({...p,y:p.y+.2},{x:0,y:1,z:0}),1.8,true))failures.push({headroom:p});};
for(const x of [-25,25])for(let zz=-17.95;zz< -5.8;zz+=.2)check(x,6.63*(zz+18)/12.2,zz);
for(let x=-30;x<=30;x+=1)check(x,6.63,-5);
const report={samples,routeSamples,failures,scope:'Roof support coverage on all authored mall/anchor partitions; not public circulation validation.'};fs.writeFileSync('build/city-exteriors/fashion-roof-test.json',JSON.stringify(report,null,2));console.log(report);w.free();assert.equal(failures.length,0);
