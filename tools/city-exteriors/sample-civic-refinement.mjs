// Derive half-metre support/headroom samples from the actual installed walk route.
// Keep the existing independent Rapier checks reproducible on a fresh checkout.
import fs from 'node:fs';
const source=fs.readFileSync('tools/city-exteriors/walk-civic-refinement.js','utf8');
const meta=JSON.parse(source.match(/const meta=(.*);/)[1]);
for(const [index,route] of meta.routes.entries()){
 const samples=[];
 for(let i=1;i<route.points.length;i++){
  const a=route.points[i-1],b=route.points[i],n=Math.ceil(Math.hypot(b[0]-a[0],b[2]-a[2])/.5);
  for(let k=0;k<=n;k++)samples.push(a.map((v,j)=>v+(b[j]-v)*k/n));
 }
 const id=index===0?'south-central-police':'fire-station-11';
 fs.writeFileSync(`build/city-exteriors/${id}-samples.json`,JSON.stringify(samples));
 console.log(id,samples.length,'support/headroom samples');
}
