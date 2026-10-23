import {Matrix4, Plane, Vector4, WebGPUCoordinateSystem, type PerspectiveCamera} from 'three';

const plane=new Plane(), q=new Vector4(), c=new Vector4(), inverse=new Matrix4();

/** Move the near clipping plane onto the water. In reversed Z the near plane is
 * w-z=0 (not z=0). Keeping x/y unchanged preserves the reflected image's alignment.
 * Scratch objects are shared: this runs sequentially, without per-frame allocation. */
export function clipWaterReflection(camera:PerspectiveCamera,height:number):void{
    plane.normal.set(0,1,0);plane.constant=-height;
    plane.applyMatrix4(camera.matrixWorldInverse);
    c.set(plane.normal.x,plane.normal.y,plane.normal.z,plane.constant);
    const reversed=camera.reversedDepth,gpu=camera.coordinateSystem===WebGPUCoordinateSystem;
    inverse.copy(camera.projectionMatrix).invert();
    q.set(Math.sign(c.x),Math.sign(c.y),reversed?0:1,1).applyMatrix4(inverse);
    c.multiplyScalar((gpu||reversed?1:2)/c.dot(q));
    const e=camera.projectionMatrix.elements;
    for(let i=0;i<4;i++){
        const v=i===0?c.x:i===1?c.y:i===2?c.z:c.w;
        e[i*4+2]=reversed?e[i*4+3]!-v:gpu?v:v-e[i*4+3]!;
    }
    camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
}
