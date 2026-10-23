import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
await RAPIER.init();const w=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/newYorkFrontage-exterior-collision.json')])if(c.indices.length)w.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
w.step();let samples=0;const failures=[],missingFloor=[],shape=new RAPIER.Capsule(.65,.29),q={x:0,y:0,z:0,w:1};
const segments=[[-29,1464,-69,1464],[-69,1464,-95,1479],[-95,1479,-103,1485],[-88,1407,-173,1405]];
for(const [ax,az,bx,bz] of segments){const n=Math.ceil(Math.hypot(bx-ax,bz-az)/.5);for(let i=0;i<=n;i++){
 const x=ax+(bx-ax)*i/n,z=az+(bz-az)*i/n;const ray=w.castRay(new RAPIER.Ray({x,y:2,z},{x:0,y:-1,z:0}),3,true);samples++;
 if(!ray)missingFloor.push({x,z});
 const floor=ray?2-ray.timeOfImpact:.24;if(w.intersectionWithShape({x,y:floor+1.04,z},q,shape))failures.push({x,z,reason:'blocked'});
}}
let roofSamples=0;for(const x of [-100,-115,-125]){const hit=w.castRay(new RAPIER.Ray({x,y:8,z:1420},{x:0,y:-1,z:0}),4,true);roofSamples++;if(!hit||Math.abs(8-hit.timeOfImpact-5.4)>.02)failures.push({x,reason:'roof-support'});}
const report={samples,roofSamples,failures,unverifiedFloorSamples:missingFloor.length,scope:'Static obstacle clearance on existing north casino entry and park promenade; three roof support samples. Ground absent from this test subset at reported points, so complete walkability is not asserted.'};fs.writeFileSync('build/city-exteriors/nyny-restaurants-collision.json',JSON.stringify(report,null,2));console.log(report);w.free();assert.equal(failures.length,0);
