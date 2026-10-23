import {Vector2} from 'three';
import type {GameEngine} from 'engine/GameEngine.js';
const KEY='afterlight:storm:render-height';
let height=900;
try{const saved=Number(localStorage.getItem(KEY));if(saved===720||saved===900||saved===1080)height=saved;}catch{/* local defaults */}
export function stormRenderHeight():number{return height;}
export function setStormRenderHeight(value:number):void {
 height=value===720?720:value===1080?1080:900;
 try{localStorage.setItem(KEY,String(height));}catch{/* browsing restrictions */}
}
/** Cap the 3D buffer, not the DOM/HUD. Retina displays must not silently turn
 * the performance profile into a 4K render. Keep the viewport aspect unchanged. */
export function limitStormResolution(engine:GameEngine):()=>void {
 const renderer=engine.renderer!,previous=renderer.getPixelRatio(),size=new Vector2();
 const apply=()=>{renderer.getSize(size);if(size.x<=0||size.y<=0)return;
  const ratio=Math.min(previous,1,height/size.y,(height*16/9)/size.x);
  if(Math.abs(renderer.getPixelRatio()-ratio)>.001)renderer.setPixelRatio(ratio);
 };
 const release=engine.registerBeforeRender(apply);apply();
 return ()=>{release();renderer.setPixelRatio(previous);};
}
