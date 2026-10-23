import * as THREE from 'three';
import {MeshBasicNodeMaterial} from 'three/webgpu';
import {cameraPosition, fog, positionWorld, smoothstep} from 'three/tsl';

// The mapped Strip is over eight kilometres long. This also leaves room for
// diagonal views from either end and the editor's aerial viewpoints.
export const SKYLINE_DISTANCE = 20_000;

export function extendSkylineCamera(camera:THREE.PerspectiveCamera|THREE.OrthographicCamera):void {
    camera.far=SKYLINE_DISTANCE;
    camera.updateProjectionMatrix();
}

/** Use the visible sky's actual direction, rotation, color decoding, seam blend
 * and brightness as the haze color. A fixed sunset-orange fog makes buildings
 * orange even when the sky behind them is blue. Sharing the sky's color node
 * also keeps atmosphere changes made in the editor consistent with the haze.
 * Classic WebGL retains world.json's much lighter, neutral fallback fog. */
export function matchHazeToSky(scene:THREE.Scene, sky:THREE.Object3D|undefined):()=>void {
    const previous=scene.fogNode;
    if(scene.fog instanceof THREE.Fog && sky instanceof THREE.Mesh && sky.material instanceof MeshBasicNodeMaterial && sky.material.colorNode){
        // Radial distance avoids stronger/weaker haze at the edge of the frame
        // as the player turns their camera past the same distant building.
        scene.fogNode=fog(sky.material.colorNode,
            smoothstep(scene.fog.near,scene.fog.far,positionWorld.sub(cameraPosition).length()));
    }
    return ()=>{scene.fogNode=previous;};
}

const NEAR_DETAILS=new Set(['paint','yellow-paint','shrub','bridge-metal','bridge-glass','bridge-light']);

/** OSM buildings already are coarse skyline meshes. Retain those, roads,
 * landscape and bridge silhouettes at every distance, but stop drawing tiny
 * railings, lamps, shrubs and road paint beyond 1.2 km. LOD updates from the
 * render camera, so it works in the editor as well as on foot/in the jeep.
 * Bounds compensation prevents an 800 m batch's nearest edge vanishing early.
 * Shadow proxies are separate and do not participate in this visual LOD. */
export function addStreetDetailLods(root:THREE.Object3D):number {
    const meshes:THREE.Mesh[]=[];
    root.traverse(o=>{if(o instanceof THREE.Mesh && NEAR_DETAILS.has(String(o.userData.osmMaterial??'')))meshes.push(o);});
    for(const mesh of meshes){
        const parent=mesh.parent!;
        mesh.geometry.computeBoundingBox();
        const bounds=mesh.geometry.boundingBox!.clone().applyMatrix4(mesh.matrix);
        const center=bounds.getCenter(new THREE.Vector3());
        const radius=bounds.getSize(new THREE.Vector3()).length()/2;
        const lod=new THREE.LOD();lod.name='Street detail LOD / '+mesh.name;
        lod.position.copy(center);parent.add(lod);
        mesh.position.sub(center);mesh.updateMatrix();
        lod.addLevel(mesh,0);
        lod.addLevel(new THREE.Group(),1200+radius,.12);
    }
    return meshes.length;
}
