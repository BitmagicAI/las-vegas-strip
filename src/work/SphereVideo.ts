import * as THREE from 'three';
/** One hardware-decoded, local muted video per display. No frame-copy canvas,
 * per-frame texture upload flag, setInterval, or background playback. */
export class SphereVideo {
    readonly video:HTMLVideoElement;
    readonly material:THREE.MeshBasicMaterial;
    private texture:THREE.VideoTexture;
    private poster:THREE.Texture;
    private wanted=false;
    private disposed=false;
    private starting=false;
    private failed=false;
    private focused=document.hasFocus();
    private hidden=false;
    private onFocus=()=>{this.focused=true;this.sync();};
    private onBlur=()=>{this.focused=false;this.sync();};
    private onVisibility=()=>this.sync();
    private onPageHide=()=>{this.hidden=true;this.sync();};
    private onPageShow=()=>{this.hidden=false;this.focused=document.hasFocus();this.sync();};
    private onReady=()=>{if(!this.disposed){this.material.map=this.texture;this.material.needsUpdate=true;}};
    private onError=()=>{this.failed=true;this.video.pause();this.material.map=this.poster;this.material.needsUpdate=true;console.warn('[Sphere] Video unavailable; keeping poster',this.video.src);};
    constructor(url:string,posterUrl:string){
        this.poster=new THREE.TextureLoader().load(posterUrl);this.poster.colorSpace=THREE.SRGBColorSpace;this.poster.flipY=false;
        this.video=document.createElement('video');this.video.muted=true;this.video.defaultMuted=true;this.video.playsInline=true;this.video.loop=true;this.video.preload='metadata';this.video.src=url;
        this.video.setAttribute('playsinline','');this.video.setAttribute('aria-hidden','true');this.video.dataset.sphereDisplay=url.includes('exosphere')?'exterior':'interior';this.video.style.display='none';document.body.append(this.video);
        this.texture=new THREE.VideoTexture(this.video);this.texture.colorSpace=THREE.SRGBColorSpace;this.texture.flipY=false;this.texture.minFilter=THREE.LinearFilter;this.texture.magFilter=THREE.LinearFilter;
        this.material=new THREE.MeshBasicMaterial({map:this.poster,toneMapped:false,side:THREE.DoubleSide});
        this.video.addEventListener('loadeddata',this.onReady);this.video.addEventListener('error',this.onError);
        window.addEventListener('focus',this.onFocus);window.addEventListener('blur',this.onBlur);window.addEventListener('pagehide',this.onPageHide);window.addEventListener('pageshow',this.onPageShow);document.addEventListener('visibilitychange',this.onVisibility);
        // A blocked autoplay request gets one retry on the next real gesture.
        window.addEventListener('pointerdown',this.onVisibility);window.addEventListener('keydown',this.onVisibility);
    }
    setActive(active:boolean):void {if(this.wanted!==active){this.wanted=active;this.sync();}}
    private sync():void {
        if(this.disposed)return;
        const play=this.wanted && this.focused && !document.hidden && !this.hidden && !this.failed;
        if(!play){this.video.pause();return;}
        if(!this.video.paused || this.starting)return;
        this.starting=true;
        void this.video.play().catch(()=>{/* Poster remains until a user gesture allows playback. */}).finally(()=>{this.starting=false;if(!this.wanted || !this.focused || document.hidden || this.disposed)this.video.pause();});
    }
    dispose():void {
        this.disposed=true;this.video.pause();this.video.removeEventListener('loadeddata',this.onReady);this.video.removeEventListener('error',this.onError);this.video.removeAttribute('src');this.video.load();this.video.remove();
        window.removeEventListener('focus',this.onFocus);window.removeEventListener('blur',this.onBlur);window.removeEventListener('pagehide',this.onPageHide);window.removeEventListener('pageshow',this.onPageShow);document.removeEventListener('visibilitychange',this.onVisibility);window.removeEventListener('pointerdown',this.onVisibility);window.removeEventListener('keydown',this.onVisibility);
        this.material.dispose();this.texture.dispose();this.poster.dispose();
    }
}
