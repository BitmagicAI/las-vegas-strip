import {AttachedBindMode,type Object3D,type SkinnedMesh} from 'three';
/** The crowd owns its pose updates. Rendering the main view, shadows and reflections
 * must not recursively rebuild an unchanged skeleton for every pass. Explicit calls
 * after animation/physics still run the original Object3D update, including skins. */
export function ownScenePose(root:Object3D):()=>void {
 const flush=root.updateMatrixWorld.bind(root,true);
 root.updateMatrixWorld=()=>{};
 return flush;
}

/** After foot planting translates a direct child of the scene, every descendant
 * needs the same world-space offset. Reuse its already-computed animation pose. */
export function ownSceneTranslation(root:Object3D):(x:number,y:number,z:number)=>void {
 const nodes:Object3D[]=[],skins:SkinnedMesh[]=[];root.traverse(node=>{nodes.push(node);if((node as SkinnedMesh).isSkinnedMesh)skins.push(node as SkinnedMesh);});
 return (x,y,z)=>{
  root.updateMatrix();for(let i=0;i<nodes.length;i++){const m=nodes[i]!.matrixWorld.elements;m[12]+=x;m[13]+=y;m[14]+=z;}
  // SkinnedMesh normally refreshes this in updateMatrixWorld. Moving the cached
  // pose must also refresh the attached bind frame, or root motion applies twice.
  for(let i=0;i<skins.length;i++){const skin=skins[i]!;if(skin.bindMode===AttachedBindMode)skin.bindMatrixInverse.copy(skin.matrixWorld).invert();}
 };
}

/** The engine has finished physics, animation and camera work at its pre-render
 * hook. Share that world pose across beauty, MRT and shadow passes this frame. */
export function ownSceneFrame(scene:Object3D,register:(update:()=>void)=>()=>void):()=>void {
 const original=scene.matrixWorldAutoUpdate;
 scene.matrixWorldAutoUpdate=false;
 const release=register(()=>{
  if(scene.matrixAutoUpdate)scene.updateMatrix();
  if(scene.parent)scene.matrixWorld.multiplyMatrices(scene.parent.matrixWorld,scene.matrix);else scene.matrixWorld.copy(scene.matrix);
  // Hidden top-level interiors and resident casts cannot render this frame.
  // Do not prune inside a visible character: its skin may use hidden bones.
  for(let i=0;i<scene.children.length;i++){const child=scene.children[i]!;if(child.visible)child.updateMatrixWorld(true);}
 });
 return ()=>{release();scene.matrixWorldAutoUpdate=original;scene.updateMatrixWorld(true);};
}
