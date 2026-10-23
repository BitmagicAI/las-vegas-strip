// Controller settings match engine/engine/physics/PhysicsWorld.ts.
// Match PhysicsBodyFactory: FIX_INTERNAL_EDGES (144) for trimeshes.
import fs from 'node:fs';import R from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));await R.init();const world=new R.World({x:0,y:-9.81,z:0});
const owners=new Map();for(const [ci,c] of [...read('build/geographic-strip/city-colliders.json'),...read('src/work/geographic/level.json').colliders,read('build/resort-blocks/bellagio/bellagioBlock-exterior-runtime-collision.json'),read('build/strip-landmarks/bellagioArcadePiers-exterior-collision.json')].entries())if(c.vertices?.length&&c.indices?.length){const hit=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices),144));owners.set(hit.handle,c.name??`collision ${ci}`);}
world.step();
const roads=read('build/resort-blocks/bellagio/south-arrival-report.json').roads;
const segments=[[[-57,588],[-106,583]],[[-106,583],[-137,565]],[[-137,565],[-167,545]],[[-167,545],[-190,529]]];
const dist=(x,z,a,b)=>{const dx=b[0]-a[0],dz=b[1]-a[1],t=Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)));return Math.hypot(x-a[0]-t*dx,z-a[1]-t*dz)};
const results=[];
for(const r of roads)for(let i=1;i<r.points.length-1;i++){const [x,y,z]=r.points[i];if(y>1||Math.min(...segments.map(([a,b])=>dist(x,z,a,b)))>2.8)continue;
const a=r.points[i-1],b=r.points[i+1],len=Math.hypot(b[0]-a[0],b[2]-a[2]);for(const side of [-.3,0,.3]){const px=x-(b[2]-a[2])/len*r.width*side,pz=z+(b[0]-a[0])/len*r.width*side;
const h=world.castRay(new R.Ray({x:px,y:y+.3,z:pz},{x:0,y:1,z:0}),4.4,true);results.push({road:r.id,x:px,z:pz,clear:!h,obstruction:h?owners.get(h.collider.handle):undefined});}}
world.free();const report={samples:results.length,failures:results.filter(x=>!x.clear),passed:results.length>0&&results.every(x=>x.clear)};fs.writeFileSync('build/city-exteriors/bellagio-mapped-bridge-clearance.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!report.passed)process.exitCode=1;
