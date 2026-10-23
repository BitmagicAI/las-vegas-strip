import * as THREE from 'three';
function imageFor(map:THREE.Texture):HTMLImageElement|HTMLCanvasElement|ImageBitmap|OffscreenCanvas {const i=map.image;if(i instanceof HTMLImageElement||i instanceof HTMLCanvasElement||i instanceof ImageBitmap||i instanceof OffscreenCanvas)return i;throw new Error('City atlas requires a loaded bitmap texture');}
export interface Atlas {texture:THREE.CanvasTexture;rects:Map<THREE.Texture|null,[number,number,number,number]>}
/** Uploads a texture now (`renderer.initTexture`). Set once the renderer is initialised. */
let upload:((texture:THREE.Texture)=>void)|null=null;
export function setCityAtlasUploader(fn:((texture:THREE.Texture)=>void)|null):void {upload=fn;}
/** Full source resolution, 32-pixel gutters, shared by a static block.
 * Repeating UVs wrap inside their tile in the shader, not across the atlas. */
export function makeCityAtlas(maps:Iterable<THREE.Texture|null>):Atlas|null {
    const unique=[...new Set(maps)];if(!unique.some(Boolean))return null;
    const pad=32,entries=unique.map(map=>{const image=map?imageFor(map):null;return {map,image,w:image?.width??1,h:image?.height??1,x:0,y:0};});
    let width=THREE.MathUtils.ceilPowerOfTwo(Math.max(256,...entries.map(e=>e.w+pad*2),Math.sqrt(entries.reduce((s,e)=>s+(e.w+pad*2)*(e.h+pad*2),0))));
    let height=0;
    const pack=()=>{let x=0,y=0,row=0;for(const e of entries){if(x+e.w+pad*2>width){x=0;y+=row;row=0;}e.x=x+pad;e.y=y+pad;x+=e.w+pad*2;row=Math.max(row,e.h+pad*2);}height=THREE.MathUtils.ceilPowerOfTwo(y+row);};
    pack();if(height>8192&&width<8192){width=8192;pack();}
    if(width>8192||height>8192)throw new Error('City atlas exceeds 8192px; split this architectural block');
    const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;const ctx=canvas.getContext('2d')!;ctx.fillStyle='#fff';ctx.fillRect(0,0,width,height);
    const rects=new Map<THREE.Texture|null,[number,number,number,number]>();
    for(const {map,image,w,h,x,y} of entries){
        if(image){ctx.drawImage(image,x,y,w,h);
            // Repeat edge texels in the gutter; explicit texture gradients keep
            // the UV wrap from selecting a blurry mip at every tile boundary.
            ctx.drawImage(image,0,0,1,h,x-pad,y,pad,h);ctx.drawImage(image,w-1,0,1,h,x+w,y,pad,h);
            ctx.drawImage(image,0,0,w,1,x,y-pad,w,pad);ctx.drawImage(image,0,h-1,w,1,x,y+h,w,pad);
            // Bilinear/mip samples at a repeated UV corner also need the
            // diagonal gutters. Leaving these white produces a bright grid
            // over dark roof textures even when all four edge strips exist.
            ctx.drawImage(image,0,0,1,1,x-pad,y-pad,pad,pad);
            ctx.drawImage(image,w-1,0,1,1,x+w,y-pad,pad,pad);
            ctx.drawImage(image,0,h-1,1,1,x-pad,y+h,pad,pad);
            ctx.drawImage(image,w-1,h-1,1,1,x+w,y+h,pad,pad);
        }
        rects.set(map,[x/width,y/height,w/width,h/height]);
    }
    const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.flipY=false;texture.anisotropy=4;
    // Upload now and drop the canvas: an 8192×4096 atlas is 128 MB of canvas memory that
    // V8 counts against its heap limit (1.6 GB for the Strip) and nothing reads after upload.
    // Three re-reads it only if the texture version changes or the renderer is rebuilt.
    if(upload){try{upload(texture);canvas.width=canvas.height=1;texture.userData.cpuReleased=true;}catch(error){console.warn('[CityAtlas] kept the canvas; upload failed',error);}}
    return {texture,rects};
}
