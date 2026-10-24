import * as THREE from 'three';
import {MeshPhysicalNodeMaterial,MeshStandardNodeMaterial,type LightsNode,type Node} from 'three/webgpu';
import {lights,positionWorld,reference} from 'three/tsl';
import {interiorKey,INTERIOR_CASTERS,KEY_CUT_Y} from './InteriorKeyLight.js';
import {keyWithoutShadowNodes,sharedAlphaCutoff} from './ShaderSharing.js';

/** Interiors (hotel stairs, corridors, rooms and lobbies; landmark, resort and Sphere interiors) are lit
 * by a fixed list: sun, sky, ambient and their own local pool (the hotel's eight lights or the four shared
 * venue lights). With the renderer's full list every wall, carpet and fixture pixel also looped over the
 * ~43 street and casino fixture lights outside: hotel corridors, rooms and lobbies ran 15-25 fps at
 * 3010×1544 (86-196 ms of GPU) and landmark lobbies 34-51 fps; 60 fps with the local list, pictures
 * identical. A fixed node also keeps the light-set rule: the list never changes, only the pool lights'
 * intensity and position do. Street-facing shells (hotel entries) keep the full list. */
export function interiorLightsNode(scene:THREE.Scene,local:readonly THREE.Light[]):LightsNode {
    const list:THREE.Light[]=[];
    const sun=scene.getObjectByName('Afterlight focused sun');
    if(sun instanceof THREE.DirectionalLight)list.push(sun);else console.warn('[InteriorLighting] focused sun not found; interiors are lit without it');
    scene.traverse(o=>{if((o instanceof THREE.HemisphereLight||o instanceof THREE.AmbientLight)&&o.visible)list.push(o);});
    // the overhead key light: on only while the camera is inside, shadows from the interior geometry (InteriorKeyLight.ts)
    list.push(interiorKey.light);
    return lights([...list,...local]);
}

type ShadowMasked={maskShadowNode:Node<'bool'>|null};
const below=positionWorld.y.lessThan(KEY_CUT_Y) as unknown as Node<'bool'>;
/** Nothing above the key light's cut (head height + a metre) casts: ceilings, coffers, chandeliers (InteriorKeyLight).
 * Shadow-pass only, so it stays out of the material's shader key: every interior material of a kind shares one build. */
function cutShadow(m:ShadowMasked):void{
    m.maskShadowNode=m.maskShadowNode?(m.maskShadowNode as unknown as {and(n:Node<'bool'>):Node<'bool'>}).and(below):below;
    keyWithoutShadowNodes(m as unknown as THREE.Material);
}

/** A node-material copy of a standard/physical material that uses `node` for its lights. */
function interiorMaterial(source:THREE.Material,node:LightsNode,interior:boolean):THREE.Material {
    // Already a lit node material (any kind): just give it the list.
    const asNode=source as unknown as {isNodeMaterial?:boolean;lights?:boolean;lightsNode:LightsNode|null};
    if(asNode.isNodeMaterial){if(asNode.lights){asNode.lightsNode=node;if(interior)cutShadow(source as unknown as ShadowMasked);source.needsUpdate=true;}return source;}
    if(!(source instanceof THREE.MeshStandardMaterial))return source;
    const material=source instanceof THREE.MeshPhysicalMaterial?new MeshPhysicalNodeMaterial():new MeshStandardNodeMaterial();
    material.copy(source);material.name=source.name;material.lightsNode=node;
    // three r185's node copy drops alphaTest; use nodes so the shared shadow material's alphaTest
    // never toggles between casters (that re-keys every shadow caster's pipeline each frame).
    if(source.alphaTest>0){
        if(source.map){material.alphaTest=0;material.alphaTestNode=sharedAlphaCutoff(source.alphaTest) as unknown as Node<'float'>;material.maskShadowNode=(reference('map','texture',material) as unknown as Node<'vec4'>).a.greaterThan(source.alphaTest);}
        else material.alphaTest=source.alphaTest;
    }
    if(interior)cutShadow(material as unknown as ShadowMasked);else keyWithoutShadowNodes(material);
    return material;
}

/** Give every lit material under `root` the interior light list (materials shared inside the root are
 * converted once; the replaced originals are disposed), and put its opaque meshes in the key light's shadow. */
export function lightInterior(root:THREE.Object3D,node:LightsNode,interior=true):void {
    const converted=new Map<THREE.Material,THREE.Material>();
    const swap=(m:THREE.Material)=>{let c=converted.get(m);if(!c){c=interiorMaterial(m,node,interior);converted.set(m,c);}return c;};
    root.traverse(o=>{if(o instanceof THREE.Mesh)o.material=Array.isArray(o.material)?o.material.map(swap):swap(o.material);});
    if(interior)keyLightCasters(root);
    for(const [m,c] of converted)if(c!==m)m.dispose();
}

/** Put an interior's opaque meshes in the overhead key light's shadow (receiving it, and casting while it is on); glass
 * casts nothing. A cloned module (hotels) is registered per instance. */
export function keyLightCasters(root:THREE.Object3D):void {
    root.traverse(o=>{if(!(o instanceof THREE.Mesh))return;
        const opaque=!(Array.isArray(o.material)?o.material.some(m=>m.transparent):o.material.transparent);
        o.receiveShadow=true;if(opaque){o.userData.keyCaster=true;o.castShadow=false;o.layers.enable(INTERIOR_CASTERS);}});
    interiorKey.register(root);
}
