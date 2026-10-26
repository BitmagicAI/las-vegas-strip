// A player driving past an entrance gets no arrival-suite preview (nothing to stream); a pedestrian still does.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
const manifest=JSON.parse(fs.readFileSync('src/work/vegas-visibility.json','utf8'));
const source=fs.readFileSync('src/work/BuildingVisibility.ts','utf8').replace("import manifest from './vegas-visibility.json';",`const manifest=${JSON.stringify(manifest)};`);
fs.mkdirSync('.bitmagic/player-tests',{recursive:true});
fs.writeFileSync('.bitmagic/player-tests/passing-previews-test-module.mjs',ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText);
const {visibilityState,BuildingVisibility}=await import('../.bitmagic/player-tests/passing-previews-test-module.mjs?'+Date.now());
const closed=()=> 'closed';
// Every exterior entrance that has an arrival suite: standing 12 m in front of it, outdoors.
const entrances=manifest.portals.filter(p=>p.exterior&&p.arrivals.length>0);
assert.ok(entrances.length>0);
let checked=0;
for(const p of entrances){
 // Find a spot a few metres from the door that is outdoors and gets a preview when walking.
 for(const [dx,dz] of [[0,-12],[0,12],[-12,0],[12,0],[0,-8],[0,8],[-8,0],[8,0],[0,-20],[0,20]]){
  const player={x:p.position[0]+dx,y:p.position[1]-.8,z:p.position[2]+dz},camera={...player,y:player.y+1.5};
  const walking=visibilityState(player,camera,closed,true);
  if(walking.zone||walking.previews.size===0)continue;
  const passing=visibilityState(player,camera,closed,false);
  assert.equal(passing.previews.size,0,`${p.id}: no preview while passing`);
  assert.equal(passing.zone,walking.zone);assert.equal(passing.outside,walking.outside);
  checked++;break;
 }
}
assert.ok(checked>=3,`expected to exercise several entrances, exercised ${checked}`);
// The default stays "previews on", so every older caller behaves as before.
const p=entrances[0],at={x:p.position[0],y:p.position[1]-.8,z:p.position[2]-12};
assert.equal(visibilityState(at,at,closed).previews.size,visibilityState(at,at,closed,true).previews.size);
assert.equal(typeof BuildingVisibility.prototype.setPassing,'function');
console.log('passing-previews: ok ('+checked+' entrances)');
