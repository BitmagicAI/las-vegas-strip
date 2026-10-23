import * as THREE from 'three';

/** Repeated metre-scale pavement detail, shared by every streamed street cell. */
export function applyStreetMaterials(root:THREE.Object3D,reversedDepth=false):()=>void {
    const textures=new Map<string,THREE.CanvasTexture>();
    const make=(kind:string)=>{
        const canvas=document.createElement('canvas');canvas.width=canvas.height=512;
        const ctx=canvas.getContext('2d')!;const pixels=ctx.createImageData(512,512);
        const planted=['grass','planting','woodland'].includes(kind), gravel=kind==='gravel';
        let seed=71831;
        for(let i=0;i<pixels.data.length;i+=4){
            seed=(Math.imul(seed,1664525)+1013904223)>>>0;
            const shade=(planted?208:gravel?219:kind==='road'?221:240)+(seed/4294967296-.5)*(planted?60:gravel?80:kind==='road'?48:19);
            pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=shade;pixels.data[i+3]=255;
        }
        ctx.putImageData(pixels,0,0);
        if(['sidewalk','bridge-deck','median-curb'].includes(kind)){
            ctx.strokeStyle='#8b8985';ctx.lineWidth=1;
            for(const p of [0,256,512]){ctx.beginPath();ctx.moveTo(p,0);ctx.lineTo(p,512);ctx.moveTo(0,p);ctx.lineTo(512,p);ctx.stroke();}
        }
        if(planted || gravel){
            for(let i=0;i<6000;i++){
                seed=(Math.imul(seed,1664525)+1013904223)>>>0;const x=(seed&511),y=(seed>>>9)&511;
                const light=(seed>>>18)&1;ctx.strokeStyle=light?'#ffffff26':'#151b0b24';ctx.lineWidth=gravel?1.8:.8;
                ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+(gravel?1:2),y+(gravel?1:5));ctx.stroke();
            }
        }
        const texture=new THREE.CanvasTexture(canvas);texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;
        textures.set(kind,texture);return texture;
    };
    root.traverse(o=>{
        if(!(o instanceof THREE.Mesh))return;
        const kind=String(o.userData.osmMaterial??'');
        for(const material of Array.isArray(o.material)?o.material:[o.material]){
            if(!(material instanceof THREE.MeshStandardMaterial))continue;
            if(['road','sidewalk','bridge-deck','median-curb','grass','planting','woodland','gravel'].includes(kind)){
                material.map=textures.get(kind)??make(kind);material.roughness=kind==='road'?.96:.88;material.needsUpdate=true;
            }
            // Narrow road paint is a decal: its tiny physical height alone is
            // not enough depth separation from kilometre-scale editor views.
            if(['paint','yellow-paint','gutter'].includes(kind)){
                const towardCamera=reversedDepth?1:-1;
                material.polygonOffset=true;material.polygonOffsetFactor=towardCamera;material.polygonOffsetUnits=2*towardCamera;
            }
            if(kind==='bridge-glass'){material.transparent=true;material.depthWrite=false;material.side=THREE.DoubleSide;}
        }
    });
    return ()=>{for(const texture of textures.values())texture.dispose();};
}
