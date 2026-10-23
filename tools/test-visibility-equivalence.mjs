// The precompiled zone tables in BuildingVisibility must answer exactly as the original per-call
// transform code did. Compares against the pre-optimisation copy (backup) on points in and around
// every zone. Run: node --import ./tools/ts-register.mjs tools/test-visibility-equivalence.mjs [old.ts]
import assert from 'node:assert/strict';
import path from 'node:path';
import manifest from '../src/work/vegas-visibility.json' with {type:'json'};
const oldPath=path.resolve(process.argv[2]??'../_backups/vegas-afterlight-2026-10-07-pre-perf/src/work/BuildingVisibility.ts');
const before=await import(oldPath),after=await import('../src/work/BuildingVisibility.ts');
let seed=7;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
let checks=0,inside=0;
for(const z of manifest.zones){
  const [cx,cy,cz]=z.center,[sx,sy,sz]=z.size;
  for(let i=0;i<400;i++){
    const p={x:cx+(rnd()-.5)*sx*1.6,y:cy+(rnd()-.5)*sy*1.6,z:cz+(rnd()-.5)*sz*1.6},m=[0,.15,-.3][i%3];
    for(const zz of manifest.zones){const a=before.contains(zz,p,m),b=after.contains(after.zoneAt?zz:zz,p,m);assert.equal(b,a,`${zz.id} at ${JSON.stringify(p)} margin ${m}`);checks++;if(a)inside++;}
    const doors=id=>['closed','open','opening'][(id.length+i)%3];
    const sa=before.visibilityState(p,{x:p.x,y:p.y+1.8,z:p.z},doors),sb=after.visibilityState(p,{x:p.x,y:p.y+1.8,z:p.z},doors);
    assert.equal(sb.zone?.id,sa.zone?.id);assert.equal(sb.outside,sa.outside);assert.deepEqual([...sb.buildings],[...sa.buildings]);assert.deepEqual([...sb.previews],[...sa.previews]);
  }
}
assert.ok(inside>1000,'the sample must exercise inside points too');
console.log(`PASS: ${checks} zone tests (${inside} inside) and ${manifest.zones.length*400} visibility states identical to the original`);
