import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {batchStaticMeshes,disposeCityMaterial} from './CityBatches.js';
import * as THREE from 'three';
export interface PassagePortal {p:[number,number];direction:[number,number];y:number;label:string;width?:number;height?:number;metal?:boolean}
export interface PassageEntry {id:string;name:string;bounds:[number,number,number,number];height:number;portals:PassagePortal[]}
export interface PassageData extends PassageEntry {
    lift?:[number,number]|null;
    liftButton?:[number,number];
    interior?:boolean;
    meshes:{material:string;vertices:number[][];faces:number[][];uv?:number[]}[];
    collision:{vertices:number[];indices:number[]};
    lights:number[][];
    signs:{text:string;position:[number,number,number];yaw:number;width:number;height:number}[];
}
const palette:Record<string,number>={'access-stone':0xc7ae85,'access-marble':0xdfd1b9,'access-plaster':0xe3d4bc,'access-bronze':0x665133,'access-carpet':0xffffff,'access-shop':0x293138,'access-vault':0x345453,'access-glazing':0xa6cbd1,'access-tread':0x626870,'access-light':0xffe6b3,'bridge-metal':0x41464b,'bridge-glass':0x95bfc7};
function texture(kind:string):THREE.CanvasTexture {
    const c=document.createElement('canvas');c.width=c.height=512;const g=c.getContext('2d')!;
    if(kind==='access-carpet'){
        g.fillStyle='#143c65';g.fillRect(0,0,512,512);
        for(let k=0;k<6;k++){
            g.strokeStyle=['#d6b968','#5f9bb0','#142b48'][k%3]!;g.lineWidth=k%2?3:6;
            for(const s of [-1,1]){g.beginPath();for(let i=0;i<=100;i++){const t=i*Math.PI/50,x=256+s*(80+k*10)*Math.cos(t)*(1+.30*Math.sin(t*4)),y=256+(80+k*10)*Math.sin(t)*(1+.30*Math.cos(t*4));i?g.lineTo(x,y):g.moveTo(x,y);}g.stroke();}
        }
        g.strokeStyle='#b99d58';g.lineWidth=6;g.strokeRect(12,12,488,488);g.lineWidth=2;g.strokeRect(25,25,462,462);
    }else{
        g.fillStyle='#e5dccb';g.fillRect(0,0,512,512);
        for(let k=-2;k<12;k++){g.beginPath();g.strokeStyle=k%2?'#b6aa9140':'#f8f0da90';g.lineWidth=k%3+1;for(let i=0;i<=512;i+=8){const x=k*65+25*Math.sin(i*.012+k)+8*Math.sin(i*.053);i?g.lineTo(x,i):g.moveTo(x,i);}g.stroke();}
        g.strokeStyle='#ad9d8070';g.lineWidth=1;g.strokeRect(0,0,512,512);
    }
    const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=4;return t;
}
/** Small architectural sets are loaded only near their bridge. No resident
 * hotel rooms, and one draw per material rather than per column/shopfront. */
export function createPassageGeometry(data:PassageData):{root:THREE.Group;dispose:()=>void}{
    const root=new THREE.Group();root.name=`Bridge concourse / ${data.name}`;
    const textures:THREE.Texture[]=[];
    const shared=new Map<string,THREE.MeshStandardMaterial>();
    for(const part of data.meshes){
        const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices.flat(),3));geo.setIndex(part.faces.flat());geo.computeVertexNormals();geo.computeBoundingSphere();
        const mat=shared.get(part.material)??new THREE.MeshStandardMaterial({color:palette[part.material]??0xbfb5a0,roughness:.65,side:THREE.DoubleSide});
        if(['access-bronze','access-vault','bridge-metal','access-tread'].includes(part.material)){mat.metalness=.6;mat.roughness=.36;}
        if(part.material==='access-light'){mat.emissive.setHex(0xffda99);mat.emissiveIntensity=1.2;}
        if(part.material==='bridge-glass'){mat.transparent=true;mat.opacity=.26;mat.depthWrite=false;}
        if(part.material==='access-glazing'){mat.emissive.setHex(0x648384);mat.emissiveIntensity=.18;mat.roughness=.24;mat.metalness=.25;}
        if(['access-carpet','access-marble','access-stone'].includes(part.material)){
            const uv=part.uv??part.vertices.flatMap(p=>[p[0]!/(part.material==='access-carpet'?4:2),p[2]!/(part.material==='access-carpet'?4:2)]);
            geo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));if(!mat.map){mat.map=texture(part.material);textures.push(mat.map);}mat.roughness=part.material==='access-carpet'?.95:.32;
        }
        shared.set(part.material,mat);
        const mesh=new THREE.Mesh(geo,mat);mesh.name=part.material;mesh.castShadow=!['access-light','bridge-glass','access-glazing'].includes(part.material);mesh.receiveShadow=true;root.add(mesh);
    }
    const sources=root.children.filter((o):o is THREE.Mesh=>o instanceof THREE.Mesh);
    root.add(batchStaticMeshes(sources,'Concourse architectural surfaces'));
    for(const mesh of sources)if(!mesh.parent)mesh.geometry.dispose();
    // All wayfinding signs share one atlas and one mesh, including the two
    // physically separated faces. Previously every face cost its own draw.
    const labels=[...new Set(data.signs.map(s=>s.text))];
    if(labels.length){
        const atlas=document.createElement('canvas'),cols=Math.min(4,labels.length);atlas.width=cols*1024;atlas.height=Math.ceil(labels.length/cols)*128;
        const g=atlas.getContext('2d')!;
        labels.forEach((text,i)=>{const x=i%cols*1024,y=Math.floor(i/cols)*128;g.save();g.translate(x,y);g.fillStyle='#292724';g.fillRect(0,0,1024,128);g.strokeStyle='#b19967';g.lineWidth=4;g.strokeRect(4,4,1016,120);g.fillStyle='#f2e2b8';g.font='48px Georgia';g.textAlign='center';g.textBaseline='middle';g.fillText(text,512,66,970);g.restore();});
        const t=new THREE.CanvasTexture(atlas);t.colorSpace=THREE.SRGBColorSpace;textures.push(t);
        const parts:THREE.BufferGeometry[]=[];
        for(const sign of data.signs)for(const side of [0,1]){
            const geo=new THREE.PlaneGeometry(sign.width,sign.height),uv=geo.getAttribute('uv'),i=labels.indexOf(sign.text),x=i%cols*1024,y=Math.floor(i/cols)*128;
            for(let v=0;v<uv.count;v++)uv.setXY(v,(x+2+uv.getX(v)*1020)/atlas.width,1-(y+2+(1-uv.getY(v))*124)/atlas.height);
            const o=new THREE.Object3D();o.position.set(...sign.position);o.rotation.y=sign.yaw+side*Math.PI;o.translateZ(.19);o.updateMatrix();geo.applyMatrix4(o.matrix);parts.push(geo);
        }
        const merged=mergeGeometries(parts,false)!;parts.forEach(g=>g.dispose());root.add(new THREE.Mesh(merged,new THREE.MeshBasicMaterial({map:t,toneMapped:false})));
    }
    return {root,dispose:()=>{root.traverse(o=>{if(o instanceof THREE.Mesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])disposeCityMaterial(m);}});textures.forEach(t=>t.dispose());shared.forEach(m=>m.dispose());root.removeFromParent();}};
}
