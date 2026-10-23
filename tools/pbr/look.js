// A/B views for the scanned surface detail (PbrDetail): node tools/probe-eval.mjs tools/pbr/look.js --viewport 1920x1080 --out build/pbr/look/on
// (and --query pbr=off --out build/pbr/look/off). Pitch is positive DOWN here (probe.look).
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function settle(ms){const t=Date.now();while(Date.now()-t<90000&&probe.streaming().busy)await wait(250);await wait(ms);}
const out=[];
async function spot(name,x,y,z,views){
  probe.teleport(x,y,z);await settle(5000);
  for(const [i,[yaw,pitch]] of views.entries()){probe.look(yaw,pitch);await wait(900);await __shot(`${name}-${i}`);}
  out.push({name,at:probe.position()});
}
await spot('lvb',17,1.5,330,[[0,.12],[Math.PI/2,.1],[-Math.PI/2,.1],[0,.6]]);
await spot('paris',60,1.5,505,[[0,.05],[-Math.PI/2,-.1],[Math.PI/2,.05]]);
await spot('bellagio',-120,1.5,540,[[0,.1],[Math.PI/2,.1],[-Math.PI/2,.35]]);
return out;
