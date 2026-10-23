import assert from 'node:assert/strict';
import {DrivingSpeedAssist, assistedAcceleration} from '../../src/work/DrivingSpeedAssist.ts';
const roads=[{id:1,width:20,highway:'primary',points:[[0,0,0],[0,0,200]]},{id:2,width:3.5,highway:'service',points:[[0,0,100],[100,0,100]]},{id:3,width:4,highway:'service',points:[[0,6,0],[0,6,200]]}];
const a=new DrivingSpeedAssist(roads);
assert.equal(a.targetAt(0,.55,50),24);assert.equal(a.targetAt(30,.55,100),10);
assert.equal(a.targetAt(0,6.55,50),10);assert.equal(a.targetAt(50,.55,50),10);
for(const y of [.7,4.1,7.5,10.9])assert.equal(a.targetAt(-280,y,550),10);
assert.equal(a.targetAt(-275,5,572),12);
assert.equal(assistedAcceleration(0,24,false),1);
assert(assistedAcceleration(0,10,false)>=.8);
assert(a.targetAt(-280,4.1,550)>8); // faster than configured fastRunSpeed
assert(assistedAcceleration(3.9,4,false)<assistedAcceleration(2,4,false));
assert.equal(assistedAcceleration(0,4,true),0);
console.log('Driving assistance: wide/narrow roads, vertically separated roads, all garage floors, access ramp, off-network and throttle taper passed');
