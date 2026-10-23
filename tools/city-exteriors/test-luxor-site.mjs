import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const w=new R.World({x:0,y:-9.81,z:0});const data=JSON.parse(fs.readFileSync('build/strip-landmarks/luxorExterior-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(data.vertices),new Uint32Array(data.indices)));
for(const c of JSON.parse(fs.readFileSync('build/geographic-strip/city-colliders.json'))){if(c.center[0]<-650||c.center[0]>10||c.center[1]<2000||c.center[1]>2500)continue;w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));}w.step();let samples=0;const failures=[];
function floor(x,z,y,from){samples++;const hit=w.castRay(new R.Ray({x,y:from,z},{x:0,y:-1,z:0}),from+1,true);const found=hit?from-hit.timeOfImpact:null;if(found===null||Math.abs(found-y)>.05)failures.push({kind:'roof height/old shell',x,z,expected:y,found});}
for(let x=-272;x<-235;x+=3)for(let z=2098;z<2124;z+=3)floor(x,z,10.025,24);
for(let x=-402;x<-362;x+=5)for(let z=2370;z<2410;z+=5)floor(x,z,22.035,24);
for(let z=2370;z<2410;z+=5)floor(-425,z,26.035,28);
for(let x=-257;x<-250;x+=.5){samples++;const hit=w.castRay(new R.Ray({x,y:3,z:2090},{x:0,y:0,z:1}),8,true);if(hit)failures.push({kind:'north entrance blocked',x,hit:hit.timeOfImpact,collider:hit.collider.handle});}
for(let z=2060;z<2126;z+=2)floor(-254,z,5.24,8.5);
for(let x=-257;x<-251;x+=.5){samples++;const hit=w.castRay(new R.Ray({x,y:6.7,z:2085},{x:0,y:0,z:1}),16,true);if(hit)failures.push({kind:'elevated connector entrance blocked',x,hit:hit.timeOfImpact});}
for(const z of [2276.6,2293]){samples++;const hit=w.castRay(new R.Ray({x:-65,y:3,z},{x:-1,y:0,z:0}),35,true);if(!hit)failures.push({kind:'sphinx paw collision',z});}
for(const [x,z] of [[-437,2245],[-365,2232],[-410,2232]])floor(x,z,.64,2);
floor(-510,2224,12.035,15);
const report={samples,failures,scope:'New roof elevations, removal of old podium shell, north exterior opening and Sphinx collision with nearby city collision. Not a whole-resort route certification.'};fs.writeFileSync('build/city-exteriors/luxor-site-collision-test.json',JSON.stringify(report,null,2));console.log(report);w.free();assert.equal(failures.length,0);
