import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';
await R.init();const base='docs/project-records/west-resort-amenities/';const gold=JSON.parse(fs.readFileSync(base+'gold-amenity-geometry.json')),wyndham=JSON.parse(fs.readFileSync(base+'wyndham-route.json'));
const reports=[];
for(const [key,points] of [['goldCoastExterior',gold.route],['wyndhamDesertBlue',wyndham.routes[0].points]]){
 const world=new R.World({x:0,y:-9.81,z:0}),c=JSON.parse(fs.readFileSync(`build/strip-landmarks/${key}-exterior-collision.json`));world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));world.step();let samples=0;const failures=[];
 for(let i=1;i<points.length;i++){
  const a=points[i-1],b=points[i],n=Math.ceil(Math.hypot(b[0]-a[0],b[2]-a[2])/.4);
  for(let k=0;k<=n;k++){
   const t=k/n,x=a[0]+t*(b[0]-a[0]),y=a[1]+t*(b[1]-a[1]),z=a[2]+t*(b[2]-a[2]);samples++;
   const support=world.castRay(new R.Ray({x,y:y+.3,z},{x:0,y:-1,z:0}),.5,true),head=world.castRay(new R.Ray({x,y:y+.1,z},{x:0,y:1,z:0}),1.8,true);
   if(!support||Math.abs(support.timeOfImpact-.3)>.06||head)failures.push({x,y,z,support:support?.timeOfImpact,head:head?.timeOfImpact});
  }
 }
 world.free();reports.push({key,samples,failures});
}
fs.writeFileSync(base+'route-support.json',JSON.stringify(reports,null,2)+'\n');console.log(reports);assert(reports.every(r=>r.samples>10&&r.failures.length===0));
