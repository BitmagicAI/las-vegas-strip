import * as THREE from 'three';

/** Matte, fine turf remains beneath the blades when their LOD fades out. */
export function applyLawnMaterial(root:THREE.Group):void {
    let material:THREE.MeshStandardMaterial|undefined;
    root.traverse(o=>{
        if(!(o instanceof THREE.Mesh)||o.userData.source!=='south-arrival-landscape'||o.userData.surface!=='sage')return;
        if(!material){
            const canvas=document.createElement('canvas');canvas.width=canvas.height=512;
            const ctx=canvas.getContext('2d')!;
            ctx.fillStyle='#596b35';ctx.fillRect(0,0,512,512);
            let seed=8106;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
            // Fine overlapping blades, not broad glossy color patches.
            for(let i=0;i<42000;i++){
                const x=random()*512,y=random()*512,v=random();
                ctx.strokeStyle=v<.3?'#40572b':v<.7?'#65783d':'#7b8848';ctx.lineWidth=.6+random()*.7;
                ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+(random()-.5)*4,y-2-random()*5);ctx.stroke();
            }
            const map=new THREE.CanvasTexture(canvas);map.colorSpace=THREE.SRGBColorSpace;map.wrapS=map.wrapT=THREE.RepeatWrapping;map.anisotropy=4;
            const bump=map.clone();bump.colorSpace=THREE.NoColorSpace;bump.needsUpdate=true;
            material=new THREE.MeshStandardMaterial({name:'Matte maintained turf',color:0xffffff,map,bumpMap:bump,bumpScale:.012,roughness:1,metalness:0,envMapIntensity:0,side:THREE.DoubleSide});
        }
        // Dedicated lawn geometry: world-sized repeat, independent of parcel size.
        const geometry=o.geometry.clone(),position=geometry.getAttribute('position');
        const uv=new Float32Array(position.count*2);
        for(let i=0;i<position.count;i++){uv[i*2]=position.getX(i)/1.6;uv[i*2+1]=position.getZ(i)/1.6;}
        geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2));o.geometry.dispose();o.geometry=geometry;o.material=material;
    });
}
