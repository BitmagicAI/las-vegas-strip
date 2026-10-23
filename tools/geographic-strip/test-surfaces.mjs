import fs from 'node:fs';
import assert from 'node:assert/strict';
import R from '@dimforge/rapier3d-compat';
await R.init();
const read=name=>JSON.parse(fs.readFileSync(`build/geographic-strip/${name}.json`));
const world=new R.World({x:0,y:0,z:0});
for(const c of read('city-colliders'))world.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
world.step();
const failures=[],probes=read('surface-physics-probes');let approachOverlays=0;
for(const [x,y,z] of probes){
    const hit=world.castRay(new R.Ray({x,y:y+.025,z},{x:0,y:-1,z:0}),.08,true);
    // The last few centimetres of a bridge/ramp may sit above the street.
    // That's valid support; a missing or lower-than-asphalt floor isn't.
    if(!hit || hit.timeOfImpact>.030)failures.push({x,y,z,distance:hit?.timeOfImpact});
    else if(hit.timeOfImpact<.020)approachOverlays++;
}
world.free();
fs.writeFileSync('build/geographic-strip/surface-physics-test.json',JSON.stringify({probes:probes.length,approachOverlays,failures},null,2));
console.log({probes:probes.length,approachOverlays,failures:failures.length,first:failures.slice(0,5)});
assert.equal(failures.length,0,'Raised pavement must have matching physical floors');
