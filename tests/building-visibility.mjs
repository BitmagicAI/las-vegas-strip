import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
const fixture=JSON.parse(fs.readFileSync('src/work/vegas-visibility.json','utf8'));
fixture.zones.unshift({id:'test-room',name:'Windowed guest room',building:'test-hotel',center:[1000,3,1000],size:[8,6,8],yaw:0,windowed:true,room:true,corridor:false},{id:'test-corridor',name:'Corridor',building:'test-hotel',center:[1008,3,1000],size:[8,6,8],yaw:0,windowed:false,room:false,corridor:true});
const source=fs.readFileSync('src/work/BuildingVisibility.ts','utf8').replace("import manifest from './vegas-visibility.json';",`const manifest=${JSON.stringify(fixture)};`);
const output=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
fs.writeFileSync('build/visibility-test-module.mjs',output);
const {visibilityState}=await import('../build/visibility-test-module.mjs?'+Date.now());
const p=(x,y,z)=>({x,y,z}), closed=()=> 'closed';
let s=visibilityState(p(-42,1.2,0),p(-42,3,4),closed);
assert.equal(s.outside,true);assert.equal(s.buildings.size,0);
s=visibilityState(p(-150,1.2,-40),p(-150,3,-44),closed);
assert.equal(s.outside,false);assert.deepEqual([...s.buildings],['bellagio']);
s=visibilityState(p(-150,1.2,-40),p(-130,3,-44),closed);
assert.equal(s.outside,true,'camera outside must preserve city');
s=visibilityState(p(-155,1.2,-78),p(-155,3,-81),id=>id==='bellagio_south_entrance'?'opening':'closed');
assert.deepEqual([...s.buildings],['bellagio']);assert.equal(s.outside,true);
s=visibilityState(p(-150,1.2,-40),p(-150,3,-44),id=>id==='bellagio_south_entrance'?'closing':'closed');
assert.equal(s.outside,true,'closing door still exposes outside');
s=visibilityState(p(93,142,-39),p(93,143,-39),closed);
assert.equal(s.outside,true,'observation deck sees outdoors');
s=visibilityState(p(110,1.2,-82),p(110,3,-82),()=> 'open');
assert.equal(s.outside,true);assert.equal(s.buildings.size,1,'outdoor connector chooses nearest interior');
for (const [x,z,b] of [[145,-237,'flamingo'],[110,-116,'horseshoe'],[131,223,'planet-hollywood'],[-131,-276,'caesars'],[-100,234,'cosmopolitan'],[100,-35,'paris']]) {
 s=visibilityState(p(x,1.2,z),p(x,3,z),closed);assert.equal(s.outside,false,b);assert.ok(s.buildings.has(b));
}
s=visibilityState(p(1000,1.2,1000),p(1000,3,1000),closed);
assert.equal(s.outside,true);assert.equal(s.zone.room,true);assert.ok(s.buildings.has('test-hotel'));
for (const [x,z,b] of [[-90,391,'crystals'],[-300,242,'vdara'],[-77,570,'waldorf'],[-266,450,'aria']]) {
 s=visibilityState(p(x,1.2,z),p(x,3,z),closed);
 assert.ok(s.buildings.has(b),`CityCenter owner ${b}`);
 assert.equal(s.outside,true,`${b} glazing preserves the skyline`);
}
s=visibilityState(p(-360,1.2,440),p(-360,3,440),closed);
assert.equal(s.outside,false,'Aria enclosed casino culls the city');assert.deepEqual([...s.buildings],['aria']);
s=visibilityState(p(-208,1.2,396),p(-208,3,396),()=> 'open');
assert.ok(s.buildings.has('crystals'),'connector belongs to Crystals, despite Aria in its name');
s=visibilityState(p(-281,1.2,396),p(-281,3,396),()=> 'open');
assert.ok(s.buildings.has('aria') && s.buildings.has('crystals'),'open shared doorway displays both connected interiors');
s=visibilityState(p(8,1.2,516),p(8,3,516),closed);
assert.equal(s.outside,true);assert.equal(s.buildings.size,0,'Aria Place does not activate distant interiors');
console.log('Visibility policy: 22 scenarios passed, including CityCenter glazing, casino culling and shared connectors.');
