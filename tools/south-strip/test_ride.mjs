import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {CoasterTrack,CoasterRun} from '../../build/south-strip/test/CoasterTrack.js';
const route=JSON.parse(readFileSync('build/south-strip/route.json'));
const track=new CoasterTrack(route),run=new CoasterRun(track),p=new THREE.Vector3(),q=new THREE.Quaternion();
let maxSpeed=0,minUp=1,maxTurn=0,lastQ=null,flips=0,inverted=false;
for(let s=0;s<route.length;s+=.5){
 track.sample(s,p,q);assert.ok(Number.isFinite(p.length())&&Number.isFinite(q.length()));assert.ok(Math.abs(q.length()-1)<1e-5);
 const up=new THREE.Vector3(0,1,0).applyQuaternion(q);minUp=Math.min(minUp,up.y);
 const next=up.y<-.5;if(next&&!inverted)flips++;inverted=next;
 if(lastQ)maxTurn=Math.max(maxTurn,lastQ.angleTo(q));lastQ=q.clone();
 const nextP=new THREE.Vector3();track.sample(s+.1,nextP,new THREE.Quaternion());const forward=new THREE.Vector3(0,0,1).applyQuaternion(q);
 assert.ok(forward.dot(nextP.sub(p).normalize())>.93,'train facing backward or broken track frame at '+s);
}
const liftStart=route.points.find(p=>p.lift).s;
for(let i=0;i<600*60&&!run.finished;i++){run.advance(1/60);maxSpeed=Math.max(maxSpeed,run.speed);assert.ok(run.speed<=29.95169);if(run.distance<liftStart)assert.ok(run.speed<=4.001,'station approach accelerates before the lift');}
assert.ok(run.finished,'ride failed to return to station');assert.equal(run.distance,route.length);assert.ok(minUp<-.9,'no inversion');assert.ok(maxTurn<.18,'abrupt camera twist');
const a=new THREE.Vector3(),b=new THREE.Vector3(),qa=new THREE.Quaternion(),qb=new THREE.Quaternion();track.sample(0,a,qa);track.sample(route.length-.001,b,qb);assert.ok(a.distanceTo(b)<.01);assert.ok(qa.angleTo(qb)<.01);
// Crossing runs must have room for the train, not just separated rail centers.
let minCrossingClearance=Infinity;
const samples=route.points.filter((_,i)=>i%3===0);
for(let i=0;i<samples.length;i++)for(let j=i+1;j<samples.length;j++){
 const a=samples[i],b=samples[j],arc=Math.abs(a.s-b.s);
 if(Math.min(arc,route.length-arc)<22)continue;
 minCrossingClearance=Math.min(minCrossingClearance,Math.hypot(...a.position.map((v,k)=>v-b.position[k])));
}
assert.ok(minCrossingClearance>3.3,'overlapping train clearance at a track crossing');
const report={lengthMetres:route.length,publishedLength:route.published.length,simulatedSeconds:run.elapsed,maxSpeedKmh:maxSpeed*3.6,invertedSections:flips,minUp,maxTurnDegrees:maxTurn*180/Math.PI,closedSeam:true,minCrossingClearance};writeFileSync('build/south-strip/ride-audit.json',JSON.stringify(report,null,2));console.log(report);
