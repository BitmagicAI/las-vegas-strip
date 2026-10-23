import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const w=new R.World({x:0,y:-9.81,z:0});const c=JSON.parse(fs.readFileSync('build/strip-landmarks/mandalayParking-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();const failures=[];let deckSamples=0,rampSamples=0;
const model=JSON.parse(fs.readFileSync('build/strip-landmarks/mandalayParking-exterior.json'));
for(const g of model.meshes){if(g.material!=='skg-deck')continue;for(const f of g.faces){const a=g.vertices[f[0]],b=g.vertices[f[1]],d=g.vertices[f[2]];if(Math.abs((b[0]-a[0])*(d[2]-a[2])-(b[2]-a[2])*(d[0]-a[0]))<1e-8)continue;const x=(a[0]+b[0]+d[0])/3,y=(a[1]+b[1]+d[1])/3,z=(a[2]+b[2]+d[2])/3;deckSamples++;const hit=w.castRay(new R.Ray({x,y:y+.03,z},{x:0,y:-1,z:0}),.06,true);if(!hit||Math.abs(hit.timeOfImpact-.03)>.015)failures.push({type:'support',x,y,z});}}
for(const [x0,z0,x1,z1] of [[-562,2620,-534,2639],[-451,2693,-385,2712]])for(let level=0;level<5;level++)for(let step=1;step<20;step++){
 const t=step/20,x=x0+(x1-x0)*t,z=(z0+z1)/2,y=.24+level*3+t*3;rampSamples++;
 const floor=w.castRay(new R.Ray({x,y:y+.1,z},{x:0,y:-1,z:0}),.2,true);assert.ok(floor&&Math.abs(floor.timeOfImpact-.1)<.02,'Ramp floor continuity');
 const head=w.castRay(new R.Ray({x,y:y+.15,z},{x:0,y:1,z:0}),2.4,true);if(head)failures.push({type:'headroom',x,y,z,toi:head.timeOfImpact});
}
const report={deckSamples,rampSamples,failures,scope:'Deck support and both ramps at all five rises;2.4m clear headroom. Driving/traffic route not asserted.'};fs.writeFileSync('build/city-exteriors/mandalayParking-collision-test.json',JSON.stringify(report,null,2));console.log(report);w.free();assert.equal(failures.length,0);
