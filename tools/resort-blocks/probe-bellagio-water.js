// Local browser regression body for tools/probe-eval.mjs. No persisted game state.
// Checks the editor (paused simulation), gameplay, and rotating-camera refresh.
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const check=(ok,message)=>{if(!ok)throw new Error(message);};
probe.teleport(-14,1,365);await delay(14000);
let eye=[-23,2.5,365],target=[-180,9,365],pan=0;
const release=engine.registerBeforeRender(()=>{
  engine.camera.position.set(...eye);engine.camera.lookAt(target[0],target[1],target[2]+pan);engine.camera.updateMatrixWorld();
});
const water=window.__afterlightWater, results=[];
async function sample(mode,moving){
  const start={frame:water.frame,time:water.time,mirrors:water.reflectionFrames};
  const intervals=[];let last=performance.now();
  for(let i=0;i<150;i++){
    await new Promise(requestAnimationFrame);const now=performance.now();intervals.push(now-last);last=now;
    if(moving)pan=30*Math.sin(i/150*Math.PI*2);
  }
  const frames=water.frame-start.frame,reflections=water.reflectionFrames-start.mirrors,seconds=water.time-start.time;
  intervals.sort((a,b)=>a-b);
  check(seconds>1,'Water clock stopped in '+mode);
  check(frames>=145,'Render clock did not advance in '+mode);
  const mirrored=water.mirrors.length>0;
  if(mirrored)check(reflections>=frames-2,'A visible mirror reused old camera frames in '+mode+': '+reflections+'/'+frames);
  const result={mode,moving,frames,reflections,seconds,medianMs:intervals[75],p95Ms:intervals[142],maxMs:intervals[149]};results.push(result);
}
try{
  await delay(3000);await sample('game',false);await __shot('game-water');
  engine.editorManager.enableEditorMode();
  const button=document.querySelector('.bm-editor-header-buttons button');if(button)button.click();
  await delay(4000);await sample('editor',false);
  await __shot('editor-water-0');await delay(500);await __shot('editor-water-1');
  await sample('editor',true);
  for(let i=0;i<5;i++){pan=(i-2)*12;await delay(200);await __shot('turn-'+i);}
  pan=0;eye=[-31,2.8,522];target=[6,0,517];await delay(1800);await __shot('roadside');
  eye=[-54,2.2,428];target=[10,.2,428];await delay(1800);await __shot('shore');
  eye=[-48,26,370];target=[-112,-1.1,360];await delay(1800);await __shot('water-above');
  return {results,waterMaterials:water.converted,mirrorSurfaces:water.mirrors.length,installedWaterTime:water.time};
}finally{release();}
