// GroundSurfaceIndex.register reads vertex arrays directly and sorts packed (cell, triangle) doubles (2026-10-24: the
// accessor calls and a comparator sort over millions of pairs cost ~10 s of the city's load). Its tables must stay
// exactly what the straightforward version built: same walkable triangles, cells and per-cell triangle order.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
import * as THREE from 'three';

fs.mkdirSync('.bitmagic/player-tests',{recursive:true});
const transpile=(from,to)=>fs.writeFileSync(to,ts.transpileModule(fs.readFileSync(from,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText);
transpile('src/work/FrameBudget.ts','.bitmagic/player-tests/FrameBudget.js');
transpile('src/work/GroundSurfaceIndex.ts','.bitmagic/player-tests/ground-surface-index-test-module.mjs');
const {GroundSurfaceIndex}=await import('../.bitmagic/player-tests/ground-surface-index-test-module.mjs?'+Date.now());

// The straightforward version (as of 2026-10-23), per mesh: walkable triangles, then a comparator-sorted CSR table.
const CELL=4,MAX=64,cellKey=(x,y,z)=>((x+16384)*32768+(y+16384))*32768+(z+16384);
function reference(object){
    const g=object.geometry,positions=g.getAttribute('position'),index=g.index,count=index?.count??positions.count;
    const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3(),ab=new THREE.Vector3(),ac=new THREE.Vector3();
    const tris=[],keys=[],refs=[],broad=[];
    for(let i=0;i+2<count;i+=3){
        a.fromBufferAttribute(positions,index?index.getX(i):i).applyMatrix4(object.matrixWorld);
        b.fromBufferAttribute(positions,index?index.getX(i+1):i+1).applyMatrix4(object.matrixWorld);
        c.fromBufferAttribute(positions,index?index.getX(i+2):i+2).applyMatrix4(object.matrixWorld);
        ab.subVectors(b,a);ac.subVectors(c,a);ab.cross(ac);
        if(ab.y<=0||ab.y*ab.y<=.65*.65*ab.lengthSq())continue;
        const t=tris.length/9;tris.push(a.x,a.y,a.z,b.x,b.y,b.z,c.x,c.y,c.z);
        const x0=Math.floor(Math.min(a.x,b.x,c.x)/CELL),x1=Math.floor(Math.max(a.x,b.x,c.x)/CELL);
        const y0=Math.floor(Math.min(a.y,b.y,c.y)/CELL),y1=Math.floor(Math.max(a.y,b.y,c.y)/CELL);
        const z0=Math.floor(Math.min(a.z,b.z,c.z)/CELL),z1=Math.floor(Math.max(a.z,b.z,c.z)/CELL);
        if((x1-x0+1)*(y1-y0+1)*(z1-z0+1)>MAX){broad.push(t);continue;}
        for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){keys.push(cellKey(x,y,z));refs.push(t);}
    }
    const order=keys.map((_,i)=>i).sort((p,q)=>keys[p]-keys[q]);
    const cellKeys=[],cellStart=[],cellTriangles=[];
    order.forEach((o,i)=>{if(!cellKeys.length||cellKeys[cellKeys.length-1]!==keys[o]){cellKeys.push(keys[o]);cellStart.push(i);}cellTriangles.push(refs[o]);});
    cellStart.push(keys.length);
    return {triangles:new Float32Array(tris),cellKeys:new Float64Array(cellKeys),cellStart:new Uint32Array(cellStart),cellTriangles:new Uint32Array(cellTriangles),broad:new Uint32Array(broad)};
}

// Random terrain-like meshes (one dense, so both the counting and the packed sort run): mostly gentle slopes (walkable) with some walls, a few huge slabs (the broad list),
// indexed (in reverse triangle order) and not, interleaved, quantized (normalized int16, the meshopt layout), rotated, scaled and translated.
let seed=7;const rand=()=>(seed=(seed*16807)%2147483647)/2147483647;
function mesh(kind){
    const n=3000,p=new Float32Array(n*9),w=kind==='dense'?30:400;
    for(let t=0;t<n;t++){
        const x=rand()*w-w/2,z=rand()*w-w/2,y=rand()*30,s=rand()<.02?120:1+rand()*6,wall=rand()<.25;
        const v=[[x,y,z],[x,y+(wall?s:rand()),z+(wall?0:s)],[x+s,y+(wall?0:rand()),z]];
        p.set(v.flat(),t*9);
    }
    let g=new THREE.BufferGeometry();
    if(kind==='interleaved'){const data=new THREE.InterleavedBuffer(new Float32Array(n*3*5),5);for(let i=0;i<n*3;i++)data.array.set(p.subarray(i*3,i*3+3),i*5+1);g.setAttribute('position',new THREE.InterleavedBufferAttribute(data,3,1));}
    else if(kind==='quantized'){const q=new Int16Array(n*9);for(let i=0;i<q.length;i++)q[i]=Math.round(p[i]/512*32767);g.setAttribute('position',new THREE.BufferAttribute(q,3,true));}
    else g.setAttribute('position',new THREE.BufferAttribute(p,3));
    if(kind==='indexed'){const order=[];for(let t=n-1;t>=0;t--)order.push(t*3,t*3+1,t*3+2);g.setIndex(order);}
    const material=new THREE.MeshStandardMaterial(),m=new THREE.Mesh(g,material);
    m.position.set(rand()*100,rand()*10,rand()*100);m.rotation.set(rand()*.3,rand()*6.28,rand()*.3);m.scale.setScalar(kind==='quantized'?512:.5+rand());
    return m;
}
const root=new THREE.Group();
for(const kind of ['plain','indexed','interleaved','quantized','dense'])root.add(mesh(kind));
const index=new GroundSurfaceIndex();index.register(root);
const surfaces=[...index.surfaces];
assert.equal(surfaces.length,5,'every mesh has walkable triangles');
for(const s of surfaces){
    const r=reference(s.mesh);
    for(const field of ['triangles','cellKeys','cellStart','cellTriangles','broad'])
        assert.deepEqual(Array.from(s[field]),Array.from(r[field]),`${field} matches the straightforward version`);
}
// Height queries agree too (a sample of points).
const ref=new GroundSurfaceIndex();ref.register(root);
for(let i=0;i<200;i++){const x=rand()*300-100,z=rand()*300-100;assert.equal(index.height(x,z,200,-50),ref.height(x,z,200,-50));}
// The sliced run (frame by frame in the game) builds the same tables.
const sliced=new GroundSurfaceIndex();await sliced.registerSliced(root);
const a=[...index.surfaces],b=[...sliced.surfaces];assert.equal(b.length,a.length);
for(let i=0;i<a.length;i++)for(const field of ['triangles','cellKeys','cellStart','cellTriangles','broad'])assert.deepEqual(Array.from(b[i][field]),Array.from(a[i][field]),`sliced ${field}`);
console.log('ground surface index: tables identical to the straightforward version, sliced or not');
