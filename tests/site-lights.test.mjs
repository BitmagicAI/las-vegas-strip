// The lit-light set must never change while the game runs: three.js hashes the id of every visible light into
// the shader cache key of every lit material, so adding, removing or hiding one light rebuilds every lit shader
// in view (15 to 86 programs, a 0.3 to 3 s freeze on the Strip; see docs/project-records/journal-2026-10-06.md).
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';
import * as THREE from 'three';

fs.mkdirSync('.bitmagic/player-tests',{recursive:true});
const source=fs.readFileSync('src/work/SiteLights.ts','utf8');
fs.writeFileSync('.bitmagic/player-tests/site-lights-test-module.mjs',ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText);
const {SiteLights}=await import('../.bitmagic/player-tests/site-lights-test-module.mjs?'+Date.now());

const site=(x,z,intensity=100,color=0xffffff,distance=18)=>({x,y:2,z,color,intensity,distance});
const lightIds=scene=>{const ids=[];scene.traverseVisible(o=>{if(o.isLight)ids.push(o.id);});return ids.sort((a,b)=>a-b);};

// 1. The pool exists up front, as four visible lights that stay in the scene.
const scene=new THREE.Scene();
const pool=new SiteLights(scene,4);
const initial=lightIds(scene);
assert.equal(initial.length,4,'four lights are created at boot');
assert.ok(pool.pool.every(l=>l.visible&&l.intensity===0&&!l.castShadow),'visible, dark and shadowless by default');

// 2. The nearest four sites win; everything else is dark; the set of visible lights never changes.
pool.offer('landmark:a',[site(0,0,500),site(50,0,400),site(900,0,300)]);
pool.offer('sphere',[site(10,0,1600),site(-10,0,650)]);
pool.apply({x:0,y:0,z:0});
assert.equal(pool.lit,4);
const lit=pool.pool.map(l=>[l.position.x,l.intensity]).sort((a,b)=>a[0]-b[0]);
assert.deepEqual(lit.map(l=>l[0]),[-10,0,10,50],'the four nearest sites are lit, the far one (900 m) is not');
assert.deepEqual(lightIds(scene),initial,'lighting sites never adds or hides a light');

// 3. Moving, withdrawing and re-offering changes intensity and position only.
pool.apply({x:900,y:0,z:0});
assert.equal(pool.pool.some(l=>l.position.x===900&&l.intensity===300),true,'the far site is lit once the player is there');
pool.offer('landmark:a',[]);pool.offer('sphere',[]);pool.apply({x:900,y:0,z:0});
assert.equal(pool.lit,0,'withdrawn offers go dark by intensity');
assert.ok(pool.pool.every(l=>l.visible),'dark lights stay visible');
assert.deepEqual(lightIds(scene),initial);

// 4. apply() is cheap while nothing changed, and recomputes when an offer changes or the player moves.
const a=[site(0,0,100)];pool.offer('x',a);pool.apply({x:0,y:0,z:0});
const first=pool.pool.find(l=>l.intensity>0);first.intensity=7;
pool.apply({x:0.5,y:0,z:0});assert.equal(first.intensity,7,'no recompute for a sub-2 m move with unchanged offers');
pool.offer('x',a);pool.apply({x:0.5,y:0,z:0});assert.equal(first.intensity,7,'offering the same list again is not a change');
pool.apply({x:5,y:0,z:0});assert.equal(first.intensity,100,'a 2 m or longer move recomputes');
pool.offer('x',[site(0,0,55)]);pool.apply({x:5,y:0,z:0});assert.equal(pool.pool.find(l=>l.intensity>0).intensity,55,'a new offer recomputes');

// 5. Disposal removes the lights.
pool.dispose();assert.equal(lightIds(scene).length,0);

// 6. Regression guard: nothing but the constant pools may create a point light (NearbyLights' eight stand-ins are made
//    once at boot and stay out of the scene graph; the film look's lamps are made once when filming starts, before any
//    take compiles), and the two streamed venues must not touch lights at all (they borrow SiteLights).
const allowed=new Set(['SiteLights.ts','GeographicPassages.ts','HotelStreaming.ts','NearbyLights.ts','SceneAtmosphere.ts']);
const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
for(const file of walk('src/work').filter(f=>f.endsWith('.ts'))){
 const text=fs.readFileSync(file,'utf8'),name=path.basename(file);
 if(/new (THREE\.)?PointLight\(/.test(text))assert.ok(allowed.has(name),`${file} creates a PointLight: use SiteLights or an intensity-driven pool created at boot`);
}
// Exactly one pool for the whole city: every extra pool is four more lights evaluated by every lit fragment forever.
const pools=walk('src/work').filter(f=>f.endsWith('.ts')).filter(f=>/new SiteLights\(/.test(fs.readFileSync(f,'utf8')));
assert.deepEqual(pools.map(f=>path.basename(f)),['GeographicCity.ts'],'only GeographicCity creates the shared pool');
for(const name of ['StripLandmarks.ts','SphereVenue.ts']){
 const text=fs.readFileSync('src/work/'+name,'utf8');
 assert.ok(!/PointLight/.test(text),`${name} must borrow SiteLights, not create lights`);
 assert.ok(!/\bl\.visible\s*=/.test(text)&&!/light\.visible\s*=/.test(text),`${name} must not toggle light visibility`);
}
console.log('site-lights: ok');
