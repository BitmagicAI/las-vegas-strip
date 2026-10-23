import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
const read=p=>JSON.parse(fs.readFileSync(p));
await RAPIER.init();const world=new RAPIER.World({x:0,y:-9.81,z:0});
for(const c of [...read('build/geographic-strip/city-colliders.json'),read('build/strip-landmarks/saharaExterior-exterior-collision.json')]){
 if(c.indices.length)world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));
}
const newWorld=new RAPIER.World({x:0,y:0,z:0});const c=read('build/strip-landmarks/saharaExterior-exterior-collision.json');newWorld.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));newWorld.step();
world.step();const capsule=new RAPIER.Capsule(.65,.29),q={x:0,y:0,z:0,w:1},blocked=[],newBlocked=[];
// The original straight line crossed the now-authored central water feature.
// Check the actual west-side circulation arc instead; retain the old central obstruction as expected.
const centralFeature=!!newWorld.intersectionWithShape({x:1364.8,y:.4,z:-2904},q,new RAPIER.Ball(.2));assert.ok(centralFeature);
let samples=0;for(let i=0;i<=106;i++){const a=Math.PI/2+Math.PI*i/106,x=1371+17*Math.cos(a),z=-2904+17*Math.sin(a);samples++;const ground=world.castRay(new RAPIER.Ray({x,y:5,z},{x:0,y:-1,z:0}),6,true);const y=ground?5-ground.timeOfImpact:0;if(world.intersectionWithShape({x,y:y+1.05,z},q,capsule))blocked.push({x,z});if(newWorld.intersectionWithShape({x,y:y+1.05,z},q,capsule))newBlocked.push({x,z});}
const report={samples,centralFeature,existingApproachObstructions:blocked,newExteriorObstructions:newBlocked,limitation:'Retained road-edge/slope contacts are reported, not waived as a full route pass. New west circulation arc avoids the physical central basin; full public circulation remains unverified.'};
fs.writeFileSync('build/city-exteriors/sahara-clearance.json',JSON.stringify(report,null,2));world.free();newWorld.free();console.log(report);assert.equal(newBlocked.length,0);
