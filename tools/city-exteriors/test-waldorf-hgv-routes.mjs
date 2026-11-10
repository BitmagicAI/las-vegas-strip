import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const reports=[];
for(const key of ['waldorf','hgvFlamingo']){
 const c=JSON.parse(fs.readFileSync(`build/strip-landmarks/${key}Exterior-exterior-collision.json`)),w=new R.World({x:0,y:-9.81,z:0});w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();
 const capsule=new R.Capsule(.55,.3),q={x:0,y:0,z:0,w:1},failures=[];let samples=0;
 for(const route of JSON.parse(fs.readFileSync(`docs/project-records/waldorf-hgv-amenities/${key==='hgvFlamingo'?'hgv':key}-routes.json`))){
  for(let i=1;i<route.points.length;i++){const a=route.points[i-1],b=route.points[i],n=Math.ceil(Math.hypot(b[0]-a[0],b[2]-a[2])/.3);
   for(let j=0;j<=n;j++){const t=j/n,p={x:a[0]+(b[0]-a[0])*t,y:a[1]+(b[1]-a[1])*t+1,z:a[2]+(b[2]-a[2])*t};samples++;if(w.intersectionWithShape(p,q,capsule))failures.push({route:route.name,segment:i,position:p});}
  }
 }
 reports.push({key,samples,failures});w.free();
}
fs.writeFileSync('docs/project-records/waldorf-hgv-amenities/installed-route-clearance.json',JSON.stringify(reports,null,2)+'\n');console.log(reports.map(r=>({key:r.key,samples:r.samples,failures:r.failures.length})));assert(reports.every(r=>r.failures.length===0));
