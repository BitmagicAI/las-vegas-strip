import fs from 'node:fs';
import R from '@dimforge/rapier3d-compat';
await R.init();
const manifest=JSON.parse(fs.readFileSync('build/geographic-strip/access/manifest.json'));
const quick=process.argv.includes('--quick');
const includeCity=process.argv.includes('--city')||quick;
const cells=includeCity?JSON.parse(fs.readFileSync(`build/geographic-strip/${quick?'bridge-building':'city'}-colliders.json`)):[];
const errors=[];let checks=0;
for(const entry of manifest){
 const data=JSON.parse(fs.readFileSync(`build/geographic-strip/access/${entry.id}.json`));
 const w=new R.World({x:0,y:-9.81,z:0});const c=data.collision;
 w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
 for(const cell of cells){const [x,z]=cell.center??[(entry.bounds[0]+entry.bounds[2])/2,(entry.bounds[1]+entry.bounds[3])/2];if(x+400<entry.bounds[0]||x-400>entry.bounds[2]||z+400<entry.bounds[1]||z-400>entry.bounds[3])continue;w.createCollider(R.ColliderDesc.trimesh(new Float32Array(cell.vertices),new Uint32Array(cell.indices)));}
 w.step();
 for(let ri=0;ri<data.routes.length;ri++){
  const route=data.routes[ri];
  for(let i=1;i<route.length;i++){
   const a=route[i-1],b=route[i],n=Math.max(1,Math.ceil(Math.hypot(...b.map((v,j)=>v-a[j]))/.4));
   for(let k=0;k<=n;k++){
    const [x,y,z]=a.map((v,j)=>v+(b[j]-v)*k/n);checks++;
    const floor=w.castRay(new R.Ray({x,y:y+.28,z},{x:0,y:-1,z:0}),.55,true);
    const body=w.intersectionWithShape({x,y:y+1.0,z},{x:0,y:0,z:0,w:1},new R.Capsule(.5,.28));
    if(!floor||body)errors.push({id:entry.id,route:ri,p:[x,y,z],floor:floor?.timeOfImpact,body:!!body});
   }
  }
 }
 w.free();
}
fs.writeFileSync(`build/geographic-strip/access/audit${includeCity?'-city':''}.json`,JSON.stringify({checks,errors},null,2));
console.log(JSON.stringify({checks,errors:errors.length,first:errors.slice(0,12)},null,2));
if(errors.length)process.exitCode=1;
