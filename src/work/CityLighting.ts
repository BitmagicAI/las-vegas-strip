import * as THREE from 'three';
import {MeshStandardNodeMaterial,WebGPURenderer} from 'three/webgpu';
import ClusteredLightsNode from 'three/addons/tsl/lighting/ClusteredLightsNode.js';

interface LightingState {node:ClusteredLightsNode;frame:number;camera:THREE.Camera|null;overflow:boolean;width:number;height:number}
const nodes=new WeakMap<THREE.Scene,LightingState>();
/** The cluster grid in use. three's ClusteredLightsNode builds a new grid, light-index buffer and compute pass whenever
 * the drawing buffer changes size (the recorder's 1920x1080, a resized window, a turned phone), but a compiled shader
 * keeps the buffers it was built with, and a material's own lightsNode is not part of three's shader key: after a resize
 * every city surface read a buffer nothing updated any more and lost its point lights (2026-10-26: a storm recording's
 * lamp pools and headlights). The bound materials carry the grid in their program key, so a resize rebuilds them. */
let grid=0;
const materialGrid=new WeakMap<THREE.Material,number>();
const drawingBuffer=new THREE.Vector2();
/** Put the grid in a material's program key (from binding on: the start-up warm-up compiles before any draw), or have a
 * material keyed to an older grid rebuilt. */
function keyGrid(material:THREE.Material):void {
    const built=materialGrid.get(material);
    if(built===grid)return;
    if(built===undefined){const key=material.customProgramCacheKey.bind(material);material.customProgramCacheKey=()=>`${key()}|grid${grid}`;}
    else material.needsUpdate=true;
    materialGrid.set(material,grid);
}
/** Use the renderer's actual visible light list, including streamed interiors.
 * No lights are removed: point-light spheres are culled in screen/depth clusters.
 * Shadowed lights keep Three's normal path. Oversized lists and WebGL fall back.
 */
export function bindCityLighting(mesh:THREE.Mesh):void {
    if(!Array.isArray(mesh.material))keyGrid(mesh.material);
    mesh.onBeforeRender=(renderer,scene,_camera,_geometry,material)=>{
        if(!(renderer instanceof WebGPURenderer)||!('isWebGPUBackend' in renderer.backend)||renderer.backend.isWebGPUBackend!==true||scene.overrideMaterial||!(material instanceof MeshStandardNodeMaterial))return;
        let state=nodes.get(scene);
        if(!state){state={node:new ClusteredLightsNode(64,64,24,64),frame:-1,camera:null,overflow:false,width:0,height:0};nodes.set(scene,state);}
        // The list is populated by the renderer before the first mesh callback.
        // All blocks share this one list and one clustered compute pass.
        if(state.frame!==renderer.info.frame||state.camera!==_camera){
            const lights=renderer.lighting.getNode(scene).getLights();
            let points=0;for(const light of lights)if(light instanceof THREE.PointLight&&!light.castShadow)points++;
            state.overflow=points>64;
            if(!state.overflow)state.node.setLights(lights);
            state.frame=renderer.info.frame;state.camera=_camera;
            renderer.getDrawingBufferSize(drawingBuffer);
            if(drawingBuffer.x!==state.width||drawingBuffer.y!==state.height){
                if(state.width)grid++;
                state.width=drawingBuffer.x;state.height=drawingBuffer.y;
            }
        }
        keyGrid(material);
        material.lightsNode=state.overflow?null:state.node;
    };
}
