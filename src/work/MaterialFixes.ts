import * as THREE from 'three';

/** Corrections applied to every loaded asset (GltfDecoders' parse hook), before any interior conversion copies them.
 *
 * Carpets and rugs (and hotel room windows, below): the generated hotel room carpets (`*_roomcarpet`) were exported at roughness 0.4 and the casino
 * `Strip / *carpet` sets at 0.74, so they read as polished, mirror-like floors (and the screen-space reflections showed
 * the room in them). Pile fabric is fully rough with a weak specular response. */
const CARPET=/carpet|\brug\b|_rug|runner/i;
/** Hotel room windows (`*_glass_window`, Bellagio `glass_window_pk`): exported lit at roughness 0.15-0.4, a rough pane
 * spread the bright sky's reflection over the whole window (the view out read as milky haze), and a smooth one mirrors
 * the room's ceiling lamp as a white blob in the middle of the view. They become a faint unlit tint: the view through them
 * stays clear from inside and out. */
const ROOM_GLASS=/glass_window/i;
const roomGlass=new Map<THREE.Material,THREE.MeshBasicMaterial>();

export function fixLoadedMaterials(root:THREE.Object3D):void{
    const done=new Set<THREE.Material>();
    root.traverse(o=>{
        if(!(o instanceof THREE.Mesh))return;
        if(!Array.isArray(o.material)&&o.material instanceof THREE.MeshStandardMaterial&&ROOM_GLASS.test(o.material.name)){
            const src=o.material;let glass=roomGlass.get(src);
            if(!glass){glass=new THREE.MeshBasicMaterial({name:src.name,color:src.color,transparent:true,opacity:.07,depthWrite:false,side:THREE.DoubleSide});roomGlass.set(src,glass);}
            o.material=glass;return;
        }
        for(const m of Array.isArray(o.material)?o.material:[o.material]){
            if(!m||done.has(m))continue;done.add(m);
            if(CARPET.test(m.name)&&m instanceof THREE.MeshStandardMaterial){
                m.roughness=1;m.metalness=0;m.envMapIntensity=.25;
                if(m instanceof THREE.MeshPhysicalMaterial){m.specularIntensity=.3;m.clearcoat=0;}
                m.needsUpdate=true;
            }

        }
    });
}
