// A vehicle passing a building must not stream its interior; a walker, and a vehicle that stops, must.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
fs.mkdirSync('build',{recursive:true});
fs.writeFileSync('build/passing-detector-test-module.mjs',ts.transpileModule(fs.readFileSync('src/work/PassingDetector.ts','utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText);
const {PassingDetector}=await import('../build/passing-detector-test-module.mjs?'+Date.now());

/** Move at `speed` m/s along +z for `seconds` at 60 fps from (x0,z0,t0); returns the final state. */
function run(det,{z0=0,t0=0,speed,seconds,driving}){let z=z0,t=t0,passing=det.passing;for(let i=0;i<Math.round(seconds*60);i++){t+=1000/60;z+=speed/60;passing=det.update(0,z,t,driving);}return {z,t,passing};}

// A walker and a sprinter never count as passing.
let d=new PassingDetector(),r=run(d,{speed:1.4,seconds:5,driving:false});assert.equal(r.passing,false,'walking');
d=new PassingDetector();r=run(d,{speed:7,seconds:5,driving:false});assert.equal(r.passing,false,'sprinting');
// A vehicle at driving speed does, within a moment.
d=new PassingDetector();r=run(d,{speed:12,seconds:2,driving:true});assert.equal(r.passing,true,'jeep at 43 km/h');
d=new PassingDetector();r=run(d,{speed:20,seconds:2,driving:false});assert.equal(r.passing,true,'a scripted 72 km/h drive counts even without a vehicle flag');
// It does not flicker when the vehicle dips below the entry speed but stays above the exit speed (a junction).
d=new PassingDetector();r=run(d,{speed:12,seconds:2,driving:true});r=run(d,{...r,z0:r.z,t0:r.t,speed:3,seconds:3,driving:true});assert.equal(r.passing,true,'3 m/s is slow but not stopped');
// Stopping (below 2 m/s) clears it after the hold, not instantly.
d=new PassingDetector();r=run(d,{speed:12,seconds:2,driving:true});
r=run(d,{z0:r.z,t0:r.t,speed:0.5,seconds:0.3,driving:true});assert.equal(r.passing,true,'still passing for the first 0.3 s of a stop');
r=run(d,{z0:r.z,t0:r.t,speed:0.5,seconds:2,driving:true});assert.equal(r.passing,false,'stopped at an entrance');
// A teleport or a pause is not a speed.
d=new PassingDetector();d.update(0,0,0,false);d.update(0,5000,16,false);assert.equal(d.passing,false,'a 5 km jump is a teleport');
d.update(0,5000,60000,false);assert.equal(d.metresPerSecond,0,'a long pause resets the speed');
console.log('passing-detector: ok');
