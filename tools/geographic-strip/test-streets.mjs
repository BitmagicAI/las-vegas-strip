import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '@dimforge/rapier3d-compat';
await R.init();
const read=p=>JSON.parse(fs.readFileSync(p));
const quick=process.argv.includes('--bridges-only');
const cells=read(`build/geographic-strip/${quick?'bridge-only':'city'}-colliders.json`),details=read(`build/geographic-strip/${quick?'bridge-only-details':'street-details'}.json`);
const corner=process.argv.includes('--bellagio-corner');
const selectedWay=Number(process.argv.find(v=>v.startsWith('--way='))?.split('=')[1]) || null;
const world=new R.World({x:0,y:0,z:0});
for(const cell of cells)world.createCollider(R.ColliderDesc.trimesh(new Float32Array(cell.vertices),new Uint32Array(cell.indices)));
for(const entry of read('build/geographic-strip/access/manifest.json')){const c=read(`build/geographic-strip/access/${entry.id}.json`).collision;world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));}
world.step();
const holes=[],obstructions=[];let checks=0,railHits=0,railProbes=0;
for(let i=0;i<details.bridgeChecks.length;i++){
    const check=details.bridgeChecks[i],point=check.point,[x,y,z]=point;
    if(selectedWay && check.way!==selectedWay)continue;
    if(y<.4)continue;
    if(corner && (x < -115 || x>115 || z<90 || z>300))continue;
    checks++;
    const hit=world.castRay(new R.Ray({x,y:y+.2,z},{x:0,y:-1,z:0}),.5,true);
    if(!hit || Math.abs(hit.timeOfImpact-.2)>.08)holes.push(check);
    if(world.intersectionWithShape({x,y:y+1.1,z},{x:0,y:0,z:0,w:1},new R.Cuboid(.25,.7,.25)))obstructions.push(check);
    const next=details.bridgeChecks[i+1];
    if(next?.way===check.way){
        const dx=next.point[0]-x,dz=next.point[2]-z,n=Math.hypot(dx,dz);
        if(n>.1)for(const sign of [-1,1]){
            const hit=world.castRay(new R.Ray({x,y:y+.65,z},{x:sign*-dz/n,y:0,z:sign*dx/n}),check.width/2+.5,true);railProbes++;if(hit)railHits++;
        }
    }
}
const report={checks,holes,obstructions,railHits,railProbes};
fs.writeFileSync(`build/geographic-strip/street-physics-${corner?'bellagio-corner':selectedWay??'test'}.json`,JSON.stringify(report,null,2));
console.log(JSON.stringify({checks,holes:holes.length,obstructions:obstructions.length,railHits,railProbes,firstObstructions:obstructions.slice(0,10),sphereHoles:holes.filter(c=>c.way===1197488766),sphereObstructions:obstructions.filter(c=>c.way===1197488766)},null,2));
world.free();
assert.equal(holes.length,0,'Missing pedestrian bridge surfaces');
assert.equal(obstructions.length,0,'Blocked pedestrian bridge centres');
assert(railHits>railProbes*.7,'Bridge edges lack physical railings');
