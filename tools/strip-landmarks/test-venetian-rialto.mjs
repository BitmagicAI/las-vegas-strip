import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
await RAPIER.init();
const world=new RAPIER.World({x:0,y:-9.81,z:0}), names=new Map();
function add(vertices,indices,name){const c=world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(vertices),new Uint32Array(indices)));names.set(c.handle,name);}
for(const layer of ['exterior','interior']){const c=JSON.parse(fs.readFileSync(`build/strip-landmarks/venetian-${layer}-collision.json`));add(c.vertices,c.indices,layer+' collision');}
// The Rialto route continues into the lobby and up to the Grand Canal Shoppes (separate streamed venues since 2026-10-23).
for(const key of ['grandCanal','venetianCasino']){const f=`build/strip-landmarks/${key}-interior-collision.json`;if(fs.existsSync(f)){const c=JSON.parse(fs.readFileSync(f));add(c.vertices,c.indices,key+' collision');}}
// Visible architecture must not block a route merely because it lacks collision.
for(const g of JSON.parse(fs.readFileSync('build/strip-landmarks/venetian-exterior.json')).meshes)
 if(['rialto-bridge','rialto-plaza-stair','palazzo-front','venetian-palace'].includes(g.source))add(g.vertices.flat(),g.faces.flat(),g.source+'/'+g.material);
world.step();
const report={samples:0,failures:[]}, capsule=new RAPIER.Capsule(.65,.29), q={x:0,y:0,z:0,w:1};
function route(points,label){for(let k=1;k<points.length;k++){const a=points[k-1],b=points[k],n=Math.max(1,Math.ceil(Math.hypot(...b.map((v,i)=>v-a[i]))/.20));for(let i=0;i<=n;i++){const p=a.map((v,j)=>v+(b[j]-v)*i/n),hit=world.intersectionWithShape({x:p[0],y:p[1]+1.15,z:p[2]},q,capsule),floor=world.castRay(new RAPIER.Ray({x:p[0],y:p[1]+.3,z:p[2]},{x:0,y:-1,z:0}),.7,true);report.samples++;if(hit||!floor)report.failures.push({label,p,blocker:hit?names.get(hit.handle):null,floor:!!floor});}}}
const meta=JSON.parse(fs.readFileSync('build/strip-landmarks/venues.json')).find(x=>x.key==='venetian');
route(meta.routes[1].points,'full Rialto into the lobby and the Shoppes');
const start=[174.96,-611.68],end=[225.85,-644],len=Math.hypot(end[0]-start[0],end[1]-start[1]),sin=(end[0]-start[0])/len,cos=(end[1]-start[1])/len;
const x=215,z=start[1]+(cos*(x-start[0])-5.6)/sin,s=sin*(x-start[0])+cos*(z-start[1]),y=7.84+(6.24-7.84)*(s-31)/22;
route([[215,1.18,-665],[215,1.18,-664],[215,4.58,-658],[215,4.58,-650.5],[215,y+.08,z]],'plaza side stair');
// Road beneath the arch must have usable vehicle clearance. These are actual
// underpass positions from the bridge axis, independent of render cameras.
for(const s of [22,26,30]){const px=start[0]+sin*s,pz=start[1]+cos*s;const h=world.castRay(new RAPIER.Ray({x:px,y:.5,z:pz},{x:0,y:1,z:0}),12,true);report.samples++;if(!h||h.timeOfImpact<3.3)report.failures.push({label:'underpass headroom',s,height:h?.timeOfImpact});}
world.free();fs.writeFileSync('build/strip-landmarks/venetian-rialto-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));assert.equal(report.failures.length,0);
