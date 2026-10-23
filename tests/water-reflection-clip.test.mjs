import {PerspectiveCamera,WebGPUCoordinateSystem,Vector3,Vector4} from 'three';
import {clipWaterReflection} from '../src/work/WaterReflectionClip.ts';
for(const rev of [false,true])for(const height of [2,12,60]){
 const c=new PerspectiveCamera(60,1.6,.1,650);c.coordinateSystem=WebGPUCoordinateSystem;Reflect.set(c,'_reversedDepth',rev);c.position.set(0,-height,0);c.lookAt(0,3,-30);c.updateMatrixWorld();c.updateProjectionMatrix();clipWaterReflection(c,.31);
 for(const y of [-.02,.30,.32,2,20]){
 const p=new Vector4(0,y,-30,1).applyMatrix4(c.matrixWorldInverse).applyMatrix4(c.projectionMatrix);const inside=p.z>=0&&p.z<=p.w;if(inside!==(y>.31))throw Error(JSON.stringify({rev,height,y,p,inside}));
 }
}console.log('30 reflected clipping probes pass for normal and reversed WebGPU depth.');
