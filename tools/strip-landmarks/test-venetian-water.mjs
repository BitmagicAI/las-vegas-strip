// A boat-sized solid envelope, tested against actual collision AND visible
// architecture. Pedestrian route tests cannot detect a bridge damming a canal.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import RAPIER from '@dimforge/rapier3d-compat';
await RAPIER.init();
const read=p=>JSON.parse(fs.readFileSync(p));
const world=new RAPIER.World({x:0,y:0,z:0}),names=new Map();
function add(vertices,indices,name){if(!indices.length)return;const c=world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(vertices),new Uint32Array(indices)));names.set(c.handle,name);}
for(const layer of ['exterior','interior']){const c=read(`build/strip-landmarks/venetian-${layer}-collision.json`);add(c.vertices,c.indices,`${layer} collision`);}
for(const c of read('build/geographic-strip/city-colliders.json'))if(c.center[0]>100&&c.center[0]<350&&c.center[1]>-850&&c.center[1]<-550)add(c.vertices,c.indices,'city/'+c.center);
for(const g of read('build/strip-landmarks/venetian-exterior.json').meshes){
 if(g.material==='water'||(g.source==='venetian-canal'&&['charcoal','velvet','gold'].includes(g.material)))continue;
 const faces=g.faces.filter(f=>{const v=f.map(i=>g.vertices[i]);return v.some(p=>p[0]>175&&p[0]<251&&p[2]>-752&&p[2]<-644&&p[1]>.35&&p[1]<5);});
 add(g.vertices.flat(),faces.flat(),`${g.source}/${g.material}`);
}
world.step();
const routes=[{name:'main-plaza-crossing',a:[195,-714],b:[195,-677]},{name:'north-channel',a:[229,-725.45],b:[239.5,-725.45]},{name:'south-channel',a:[215,-654.2],b:[236.5,-654.2]}];
const water=.31,shape=new RAPIER.Cuboid(1.35,1.40,5.2),failures=[],report={waterY:water,clearEnvelopeM:{length:10.4,width:2.7,aboveWater:2.9},samples:0,failedSamples:0,failures};
for(const route of routes){const dx=route.b[0]-route.a[0],dz=route.b[1]-route.a[1],length=Math.hypot(dx,dz),yaw=Math.atan2(dx,dz),q={x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)};
 for(let s=0;s<=length;s+=.3){const p={x:route.a[0]+dx*s/length,y:water+1.5,z:route.a[1]+dz*s/length};const hits=[];world.intersectionsWithShape(p,q,shape,c=>{hits.push(names.get(c.handle));return true;});report.samples++;if(hits.length){report.failedSamples++;if(failures.length<24)failures.push({route:route.name,position:p,blockers:hits});}}
}
world.free();fs.writeFileSync('build/strip-landmarks/venetian-water-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));assert.equal(report.failedSamples,0,'Gondola envelope blocked');
