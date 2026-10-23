import {foliageSettings} from './FoliageSettings.js';
import * as THREE from 'three';
import {isGeometryReleaseSuspended} from 'engine/resources/GeometryCpuRelease.js';
import {filmDetail} from './FilmDetail.js';
/** Authored tree LODs: one selection per 40m grove, never per tree or leaf. */
export class GroveLod {
 private cells:{levels:THREE.Group[];box:THREE.Box3;level:number}[]=[];
 private last=0;private point=new THREE.Vector3();private scene:THREE.Scene|null=null;
 private previous:THREE.Scene['onBeforeRender']|null=null;
 private hook:THREE.Scene['onBeforeRender']|null=null;
 constructor(owner:THREE.Group){
  const groups=new Map<string,THREE.Mesh[]>();
  owner.traverse(o=>{if(o instanceof THREE.Mesh&&String(o.userData.source).startsWith('arrival-tree/')){const key=String(o.userData.source).split('/')[1]!;const g=groups.get(key)??[];g.push(o);groups.set(key,g);}});
  for(const meshes of groups.values()){
   const levels=[new THREE.Group(),new THREE.Group(),new THREE.Group()];
   for(const m of meshes){const n=Number(String(m.userData.source).split('/')[2]);owner.attach(m);levels[n]!.add(m);m.castShadow=true;}
   for(let i=0;i<3;i++){levels[i]!.visible=i===0;owner.add(levels[i]!);}
   this.cells.push({levels,box:new THREE.Box3().setFromObject(levels[0]!),level:0});
  }
  let root:THREE.Object3D=owner;while(root.parent)root=root.parent;
  if(!this.cells.length||!(root instanceof THREE.Scene))return;
  this.scene=root;this.previous=root.onBeforeRender;
  const previous=this.previous;
  this.hook=(...args)=>{previous.apply(root,args);if(root.overrideMaterial||performance.now()-this.last<180||isGeometryReleaseSuspended())return;this.last=performance.now();args[2].getWorldPosition(this.point);
   const settings=foliageSettings.get();for(const c of this.cells){const d=settings.enabled?c.box.distanceToPoint(this.point)/settings.distanceScale:Infinity;const limits=[100,240,650];let n=filmDetail.full&&settings.enabled?0:d<limits[0]! ? 0:d<limits[1]! ? 1:d<limits[2]! ? 2:3;
    if(n!==c.level){const boundary=limits[Math.min(n,c.level)]!;if(filmDetail.full||Math.abs(d-boundary)>=boundary*.08)c.level=n;}
    // Re-assert: the engine warm-up restores visibility recorded before this choice.
    for(let i=0;i<3;i++){const g=c.levels[i]!,v=i===c.level;if(g.visible!==v)g.visible=v;}}
  };root.onBeforeRender=this.hook;
 }
 dispose(){if(this.scene&&this.scene.onBeforeRender===this.hook&&this.previous)this.scene.onBeforeRender=this.previous;this.cells=[];}
}
