import fs from 'node:fs';import assert from 'node:assert/strict';import R from '@dimforge/rapier3d-compat';await R.init();
const w=new R.World({x:0,y:-9.81,z:0});const c=JSON.parse(fs.readFileSync('build/strip-landmarks/stratExterior-exterior-collision.json'));w.createCollider(R.ColliderDesc.trimesh(new Float32Array(c.vertices),new Uint32Array(c.indices)));w.step();let roofSamples=0,headroomSamples=0;const failures=[];
const model=JSON.parse(fs.readFileSync('build/strip-landmarks/stratExterior-exterior.json'));
for(const g of model.meshes){if(!['podium/way/135456188','strat-south-arrival'].includes(g.source)||g.material!=='st-flat-roof')continue;
 for(const f of g.faces){const a=g.vertices[f[0]],b=g.vertices[f[1]],d=g.vertices[f[2]],x=(a[0]+b[0]+d[0])/3,y=(a[1]+b[1]+d[1])/3,z=(a[2]+b[2]+d[2])/3;roofSamples++;
  if(!w.castRay(new R.Ray({x,y:y+.025,z},{x:0,y:-1,z:0}),.05,true))failures.push({kind:'roof',x,y,z});
  if(g.source==='strat-south-arrival'){
   for(let i=1;i<9;i++)for(let j=1;j<9-i;j++){const u=i/9,v=j/9,xx=a[0]*u+b[0]*v+d[0]*(1-u-v),zz=a[2]*u+b[2]*v+d[2]*(1-u-v);headroomSamples++;if(w.castRay(new R.Ray({x:xx,y:1,z:zz},{x:0,y:1,z:0}),6.9,true))failures.push({kind:'headroom',x:xx,z:zz});}
  }
 }
}
w.free();assert.ok(roofSamples>20);assert.ok(headroomSamples>=2);fs.writeFileSync('build/city-exteriors/strat-podium-test.json',JSON.stringify({roofSamples,headroomSamples,failures,scope:'New geometry only; surrounding road and interior collision unmodified. Public entrance route not claimed.'},null,2));assert.equal(failures.length,0);console.log({roofSamples,headroomSamples,failures:failures.length});
