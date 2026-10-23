import * as THREE from 'three';
import {MeshStandardNodeMaterial,WebGPURenderer} from 'three/webgpu';
import ClusteredLightsNode from 'three/addons/tsl/lighting/ClusteredLightsNode.js';

interface LightingState {node:ClusteredLightsNode;frame:number;camera:THREE.Camera|null;overflow:boolean}
const nodes=new WeakMap<THREE.Scene,LightingState>();
/** Use the renderer's actual visible light list, including streamed interiors.
 * No lights are removed: point-light spheres are culled in screen/depth clusters.
 * Shadowed lights keep Three's normal path. Oversized lists and WebGL fall back.
 */
export function bindCityLighting(mesh:THREE.Mesh):void {
    mesh.onBeforeRender=(renderer,scene,_camera,_geometry,material)=>{
        if(!(renderer instanceof WebGPURenderer)||!('isWebGPUBackend' in renderer.backend)||renderer.backend.isWebGPUBackend!==true||scene.overrideMaterial||!(material instanceof MeshStandardNodeMaterial))return;
        let state=nodes.get(scene);
        if(!state){state={node:new ClusteredLightsNode(64,64,24,64),frame:-1,camera:null,overflow:false};nodes.set(scene,state);}
        // The list is populated by the renderer before the first mesh callback.
        // All blocks share this one list and one clustered compute pass.
        if(state.frame!==renderer.info.frame||state.camera!==_camera){
            const lights=renderer.lighting.getNode(scene).getLights();
            let points=0;for(const light of lights)if(light instanceof THREE.PointLight&&!light.castShadow)points++;
            state.overflow=points>64;
            if(!state.overflow)state.node.setLights(lights);
            state.frame=renderer.info.frame;state.camera=_camera;
        }
        material.lightsNode=state.overflow?null:state.node;
    };
}
