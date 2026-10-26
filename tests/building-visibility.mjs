// Building visibility (src/work/BuildingVisibility.ts): which interiors draw and whether the city stays visible. Every
// point is derived from the zones and portals in src/work/vegas-visibility.json (each zone maps from its source frame
// onto the geographic city through geoTransform), so the policy is checked wherever the map puts the buildings.
// Run: node tests/building-visibility.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
const fixture=JSON.parse(fs.readFileSync('src/work/vegas-visibility.json','utf8'));
const identity={linear:[1,0,0,1],translation:[0,0]};
const testZone=(id,name,center,flags)=>({id,name,building:'test-hotel',center,size:[8,6,8],yaw:0,windowed:false,room:false,corridor:false,
 sourceCenter:center,sourceSize:[8,6,8],sourceYaw:0,geoTransform:identity,...flags});
fixture.zones.unshift(testZone('test-room','Windowed guest room',[1000,3,1000],{windowed:true,room:true}),testZone('test-corridor','Corridor',[1008,3,1000],{corridor:true}));
const source=fs.readFileSync('src/work/BuildingVisibility.ts','utf8').replace("import manifest from './vegas-visibility.json';",`const manifest=${JSON.stringify(fixture)};`);
fs.mkdirSync('.bitmagic/player-tests',{recursive:true});
fs.writeFileSync('.bitmagic/player-tests/visibility-test-module.mjs',ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText);
const {visibilityState,zoneAt}=await import('../.bitmagic/player-tests/visibility-test-module.mjs?'+Date.now());
const closed=()=>'closed',zones=fixture.zones,portal=id=>fixture.portals.find(p=>p.id===id);
let checks=0;const ok=(cond,msg)=>{assert.ok(cond,msg);checks++;};

/** The world point at offset (ux, uy, uz) metres in zone z's own box frame. */
function world(z,ux=0,uy=0,uz=0){
 const co=Math.cos(z.sourceYaw),si=Math.sin(z.sourceYaw),sx=z.sourceCenter[0]+co*ux+si*uz,sz=z.sourceCenter[2]-si*ux+co*uz;
 const [a,b,c,d]=z.geoTransform.linear,[tx,tz]=z.geoTransform.translation;
 return {x:a*sx+b*sz+tx,y:z.sourceCenter[1]+uy,z:c*sx+d*sz+tz};
}
/** A point that resolves to zone z itself (earlier zones win where they overlap). */
function inside(z){
 const fractions=[0,.25,-.25,.5,-.5,.75,-.75,.9,-.9];
 for(const fx of fractions)for(const fz of fractions){const p=world(z,fx*z.sourceSize[0]/2,0,fz*z.sourceSize[2]/2);if(zoneAt(p)?.id===z.id)return p;}
 return null;
}
const lift=(p,dy=.5)=>({x:p.x,y:p.y+dy,z:p.z});
const far=(p)=>({x:p.x+400,y:p.y,z:p.z});

// 1. Every zone: standing in it with the camera beside you shows its building; the city stays visible only through glass.
for(const z of zones){
 const p=inside(z);ok(p,`${z.id} (${z.name}) has a point of its own`);
 const s=visibilityState(p,lift(p),closed);
 ok(s.zone?.id===z.id,`${z.id}: zoneAt`);ok(s.buildings.has(z.building),`${z.id}: draws ${z.building}`);
 ok(s.outside===!!z.windowed,`${z.id}: ${z.windowed?'glazing keeps the city':'an enclosed interior culls the city'}`);
}
// 2. The camera outside the building keeps the city, wherever the player stands.
const enclosed=zones.find(z=>!z.windowed&&z.building==='bellagio'),inBellagio=inside(enclosed);
ok(visibilityState(inBellagio,far(inBellagio),closed).outside===true,'camera outside preserves the city');
// 3. Outdoors, away from every door: nothing inside draws and nothing is previewed.
const street={x:-60,y:1.2,z:540};
ok(!zoneAt(street),'the street point is outdoors');
{const s=visibilityState(street,lift(street),closed);ok(s.outside&&s.buildings.size===0&&s.previews.size===0,'outdoors: no interiors');}
// 4. An exterior door opening beside the player shows that building; a closing door from inside still shows the city.
// a door sits on its arrival suite's edge: step out through it, away from the suite, to the first outdoor point
function outsideDoor(p){
 const c=world(zones.find(z=>z.id===p.arrivals[0])),dx=p.position[0]-c.x,dz=p.position[2]-c.z,l=Math.hypot(dx,dz);
 for(let m=1;m<=10;m++){const q={x:p.position[0]+dx/l*m,y:1.2,z:p.position[2]+dz/l*m};if(!zoneAt(q))return q;}
 return null;
}
const south=portal('bellagio_south_entrance'),atDoor=outsideDoor(south);
ok(atDoor,'a point outdoors at the Bellagio south entrance');
{const s=visibilityState(atDoor,lift(atDoor),id=>id===south.id?'opening':'closed');ok(s.buildings.has('bellagio')&&s.outside,'opening door shows the Bellagio');}
ok(visibilityState(inBellagio,lift(inBellagio),id=>id===south.id?'closing':'closed').outside===true,'closing door still exposes outside');
// 5. A glazed entrance previews its arrival suite before the doors open.
{const s=visibilityState(atDoor,lift(atDoor),closed);ok(south.arrivals.every(id=>s.previews.has(id)),'arrival suite previewed at the entrance');}
// 6. Open shared doorways draw every building they join: Aria and Crystals; the Horseshoe and Paris.
function nearPortal(p,buildings){
 for(let r=0;r<=11;r++)for(let k=0;k<24;k++){const a=k*Math.PI/12,q={x:p.position[0]+r*Math.cos(a),y:p.position[1],z:p.position[2]+r*Math.sin(a)},z=zoneAt(q);if(z&&buildings.includes(z.building))return q;}
 return null;
}
for(const [id,want] of [['CityCenter / Aria casino east 0',['aria','crystals']],['Interiors / Horseshoe south',['horseshoe','paris']]]){
 const p=portal(id),q=nearPortal(p,p.buildings);ok(q,`${id}: a point inside next to it`);
 const s=visibilityState(q,lift(q),d=>d===id?'open':'closed');ok(want.every(b=>s.buildings.has(b)),`${id} draws ${want.join(' and ')}`);
}
// 7. Authored outdoor courts carve the interior zones they cross (the Paris arrival court).
for(const v of fixture.exteriorVoids){
 const q={x:v.center[0],y:v.minY+1,z:v.center[1]},z=zoneAt(q);ok(!z||z.building!==v.building,`${v.id}: the court is not inside ${v.building}`);
}
// 8. The injected guest room (identity transform): windowed, a room, its own building.
{const s=visibilityState({x:1000,y:3,z:1000},{x:1000,y:3.5,z:1000},closed);ok(s.outside&&s.zone.room&&s.buildings.has('test-hotel'),'windowed guest room');}
console.log(`Visibility policy: ${checks} checks passed over ${zones.length} zones (enclosed and glazed interiors, doors, previews, shared doorways, outdoor courts).`);
