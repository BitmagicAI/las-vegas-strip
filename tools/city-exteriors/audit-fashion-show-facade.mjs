import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const w=new R.World({x:0,y:-9.81,z:0}),c=JSON.parse(fs.readFileSync('build/strip-landmarks/fashion-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();
const samples=JSON.parse(fs.readFileSync('docs/project-records/fashion-show-refinement/facade-clearance-samples.json')),failures=[];
for(const [i,s] of samples.entries()){
 const point=a=>({x:a[0],y:a[1],z:a[2]});
 if(!w.intersectionWithShape(point(s.skin),{x:0,y:0,z:0,w:1},new R.Ball(.06)))failures.push({i,kind:'skin-not-solid'});
 if(w.intersectionWithShape(point(s.outside),{x:0,y:0,z:0,w:1},new R.Capsule(.53,.28)))failures.push({i,kind:'outside-blocked'});
}
const result={samples:samples.length,failures};fs.writeFileSync('docs/project-records/fashion-show-refinement/facade-clearance.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));w.free();assert.equal(failures.length,0);
