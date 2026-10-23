const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
const settle=async(n=90)=>{for(let i=0;i<n;i++)await frame();};
probe.teleport(-50,2,180);engine.editorManager.enableEditorMode();document.querySelector('.bm-editor-header-buttons button')?.click();
let eye=[-25,4,150],target=[83,18,102],mode='natural',owners=[];
const previous=scene.onBeforeRender;
scene.onBeforeRender=function(...args){previous.apply(this,args);if(scene.overrideMaterial||mode==='natural')return;for(const b of owners){b.children[0].visible=mode==='full';b.children[1].visible=mode==='coarse';}};
const release=engine.registerBeforeRender(()=>{engine.camera.position.set(...eye);engine.camera.lookAt(...target);engine.camera.updateMatrixWorld();});
const output=[];
const all=[];scene.traverse(o=>{if(o.userData.cityLod)all.push(o);});
for(const view of [
 {name:'cromwell-street',eye:[-25,4,150],target:[83,18,102],match:/vanderpump/},
 {name:'venetian',eye:[-40,225,-1050],target:[260,50,-650],match:/venetian|palazzo|venezia/i},
 {name:'bellagio',eye:[270,135,310],target:[-140,70,200],match:/bellagio/i},
 {name:'harrahs',eye:[-190,135,-560],target:[155,35,-384],match:/harrah/i}
]){
 eye=view.eye;target=view.target;owners=all.filter(b=>{for(let o=b;o&&o!==scene;o=o.parent)if(view.match.test(o.name))return true;return false;});
 for(const state of (view.name==='cromwell-street'?['natural']:['full','coarse'])){
  mode=state;await settle();await __shot(view.name+'-'+mode);
  output.push({view:view.name,mode,owners:owners.map(o=>o.name),render:{...renderer.info.render}});
 }
 mode='natural';await settle();
 const times=[];let last=performance.now();for(let i=0;i<120;i++){await frame();const now=performance.now();times.push(now-last);last=now;}times.sort((a,b)=>a-b);
 output.push({view:view.name,mode,median:times[60],p95:times[114],render:{...renderer.info.render}});
}
release();scene.onBeforeRender=previous;return {views:output,memory:performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize,limit:performance.memory.jsHeapSizeLimit}:null};
