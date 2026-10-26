import * as THREE from 'three';
/** sphere.bin (PackedRecords.ts): points are typed arrays */
type V3=Float32Array&readonly [number,number,number];
export interface SphereMeta {
    center:V3;radius:number;height:number;mainLevel:number;
    portals:{name:string;p:V3;direction:Float32Array&readonly [number,number];width:number;height:number}[];
    signs:{text:string;p:V3;yaw:number;width:number;height:number;section:string}[];
    /** five numbers per seat: x, y, z, yaw, and the generator's fifth */
    seats:Float32Array;
    /** x, y, z per light */
    lights:Float32Array;
    views:Record<string,{p:V3;target:V3}>;
}
export const SEAT_STRIDE=5;
export function disposeSphereRoot(root:THREE.Object3D):void {
    const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>(),textures=new Set<THREE.Texture>();
    root.traverse(o=>{if(o instanceof THREE.Mesh){geometries.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material]){materials.add(m);if(m instanceof THREE.MeshStandardMaterial || m instanceof THREE.MeshBasicMaterial){if(m.map)textures.add(m.map);if(m instanceof THREE.MeshStandardMaterial && m.emissiveMap)textures.add(m.emissiveMap);}}if(o instanceof THREE.InstancedMesh)o.dispose();}});
    for(const g of geometries)g.dispose();for(const m of materials)m.dispose();for(const t of textures)t.dispose();root.removeFromParent();
}
export function finishSphereMaterials(root:THREE.Object3D):void {
    root.traverse(o=>{if(o instanceof THREE.Mesh){o.castShadow=false;o.receiveShadow=true;const m=o.material;if(!(m instanceof THREE.MeshStandardMaterial))return;m.side=THREE.DoubleSide;if(o.userData.sphereSection==='interior')m.fog=false;
        // A little baked-in light preserves the dim venue's interior shapes
        // without dozens of real-time lights or a per-seat shadow pass.
        if(o.userData.sphereSection==='interior'){
            m.envMapIntensity=.15;
            if(!m.emissiveMap && m.emissiveIntensity<=1){m.emissive.copy(m.color).multiplyScalar(.11);m.emissiveIntensity=1;if(m.map)m.emissiveMap=m.map;}
        }
        if(o.userData.spherePart==='terrazzo'){
            // The Strip's bright sky reflection otherwise washes out this
            // windowless venue's black stone. Keep only the local highlights.
            m.color.setHex(0x667788);m.emissive.setHex(0x000000);m.metalness=.08;m.envMapIntensity=0;m.roughness=.32;
        }
        if(o.userData.spherePart==='glass'){m.transparent=true;m.opacity=.23;m.depthWrite=false;}
    }});
}
export function addSphereSigns(root:THREE.Group,meta:SphereMeta,section:string):void {
    for(const s of meta.signs.filter(s=>s.section===section)){
        const c=document.createElement('canvas');c.width=1024;c.height=128;const g=c.getContext('2d')!;g.fillStyle='#0c151c';g.fillRect(0,0,1024,128);g.fillStyle='#d5eff9';g.font='52px sans-serif';g.textAlign='center';g.textBaseline='middle';g.fillText(s.text,512,65,980);
        const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;
        for(const side of [0,1]){const mesh=new THREE.Mesh(new THREE.PlaneGeometry(s.width,s.height),new THREE.MeshBasicMaterial({map:t,toneMapped:false,side:THREE.FrontSide}));mesh.position.fromArray(s.p);mesh.rotation.y=s.yaw+side*Math.PI;mesh.translateZ(.15);root.add(mesh);}
    }
}
export function addSphereSeats(root:THREE.Group,meta:SphereMeta):void {
    const seatMaterial=new THREE.MeshStandardMaterial({color:0x29374e,roughness:.78,emissive:0x0b111c});
    const frameMaterial=new THREE.MeshStandardMaterial({color:0x26323d,roughness:.4,metalness:.6});
    const pieces:[THREE.Vector3,THREE.Vector3,THREE.Material][]=[
        [new THREE.Vector3(0,.43,0),new THREE.Vector3(.48,.13,.48),seatMaterial],
        [new THREE.Vector3(0,.83,-.20),new THREE.Vector3(.49,.77,.13),seatMaterial],
        [new THREE.Vector3(0,.18,0),new THREE.Vector3(.12,.36,.30),frameMaterial],
        [new THREE.Vector3(.28,.66,0),new THREE.Vector3(.07,.08,.5),frameMaterial],
    ];
    const q=new THREE.Quaternion(),p=new THREE.Vector3(),offset=new THREE.Vector3(),m=new THREE.Matrix4(),up=new THREE.Vector3(0,1,0);
    for(const [local,scale,material] of pieces){
        const count=meta.seats.length/SEAT_STRIDE,seats=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),material,count);seats.name='Sphere shared seating';
        for(let i=0,k=0;i<count;i++,k+=SEAT_STRIDE){q.setFromAxisAngle(up,meta.seats[k+3]!);offset.copy(local).applyQuaternion(q);p.set(meta.seats[k]!,meta.seats[k+1]!,meta.seats[k+2]!).add(offset);m.compose(p,q,scale);seats.setMatrixAt(i,m);}
        seats.instanceMatrix.needsUpdate=true;seats.computeBoundingBox();seats.computeBoundingSphere();seats.receiveShadow=false;seats.castShadow=false;root.add(seats);
    }
}
