import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';

// Probe exported geometry, including a visual obstruction audit of the new
// palace wing. Existing route tests see collision, not noncolliding decorations.
const read=p=>JSON.parse(fs.readFileSync(p));
await RAPIER.init();
const world=new RAPIER.World({x:0,y:-9.81,z:0});
const names=new Map();
function add(c,name){
 const body=world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
 world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)),body);
 names.set(body.handle,name);return body;
}
for(const layer of ['exterior','interior'])add(read(`build/strip-landmarks/venetian-${layer}-collision.json`),layer);
const mesh=read('build/strip-landmarks/venetian-exterior.json');
for(const g of mesh.meshes)if(g.source==='venetian-palace')add({vertices:g.vertices.flat(),indices:g.faces.flat()},'palace visible '+g.material);
world.step();
const q={x:0,y:0,z:0,w:1},capsule=new RAPIER.Capsule(.65,.29);
const report={checks:0,failures:[],railChecks:0};
function route(points,label){
 for(let k=1;k<points.length;k++){
  const a=points[k-1],b=points[k],n=Math.ceil(Math.hypot(...b.map((v,j)=>v-a[j]))/.25);
  for(let i=0;i<=n;i++){
   const p=a.map((v,j)=>v+(b[j]-v)*i/n);
   const hit=world.intersectionWithShape({x:p[0],y:p[1]+1.1,z:p[2]},q,capsule);
   const floor=world.castRay(new RAPIER.Ray({x:p[0],y:p[1]+.25,z:p[2]},{x:0,y:-1,z:0}),.55,true);
   report.checks++;
   if(hit||!floor)report.failures.push({label,p,blocker:hit?names.get(hit.parent().handle):null,floor:!!floor});
  }
 }
}
const crest=[]; for(let x=182.5;x<=207.5;x+=.5)crest.push([x,1.18+3.05*Math.sin(Math.PI*(x-182.5)/25)**2,-692]);
route([[177,.39,-692],...crest,[212,1.18,-692],[212,1.18,-685.14],[215.5,1.18,-685.14],[221.5,.32,-685.14],[225,.32,-685.14]],'street-plaza-casino');
route([[212,1.18,-715],[212,1.18,-665]],'plaza waterfront promenade');
route([[223,6.32,-644],[241,6.32,-644]],'Rialto wing opening');
// Torso-height rays verify the continuous safety infill, above the low plinth.
for(const z of [-698,-695,-692,-689,-686]){
 const hit=world.castRay(new RAPIER.Ray({x:200,y:1.9+3.05*Math.sin(Math.PI*(200-182.5)/25)**2,z},{x:0,y:0,z:-1}),Math.abs(z+701.15)+1,true);
 report.railChecks++;if(!hit)report.failures.push({label:'north stem safety rail',z});
}
world.free();
fs.writeFileSync('build/strip-landmarks/venetian-plaza-audit.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
assert.equal(report.failures.length,0);
