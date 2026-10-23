// Review shots of hotel towers for the film's hotel run: node tools/probe-eval.mjs tools/film/hotel-look.js --viewport 1280x720 --out build/film/hotel-look
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function settle(ms){const t=Date.now();while(Date.now()-t<60000&&probe.streaming().busy)await wait(250);await wait(ms);}
const out={};
for(const id of ['vanderpump-1','linq-1','bellagio-spa-1']){
  for(const [view,floor,room] of [['entrance',0,null],['lobby',0,null],['stair',0,null],['corridor',2,null],['room',2,0]]){
    const p=await probe.hotel(id,floor,room,view==='stair'?null:view==='room'?null:view);await settle(2500);
    if(view==='lobby'){probe.look(probe.position?0:0,0);}
    await __shot(`${id}-${view}`);out[`${id}-${view}`]=p;
  }
}
return out;
