import * as THREE from 'three';
import {cinematicSurfaceEnabled,stormDrivingEnabled} from './film/SceneSurface.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { ConvexGeometry } from 'three/addons/geometries/ConvexGeometry.js';
import data from './geographic/level.json';
import {releaseAfterUpload} from './CpuGeometryRelease.js';
import {mapPoint} from './geographic/Coordinates.js';
import {shadowSettings} from './ShadowSettings.js';

const WORLD_UP=new THREE.Vector3(0,1,0);

/** A focused receiver region with a long upstream caster volume. Tall silhouettes
 * remain in the shadow pass independent of camera visibility/player distance. */
export class AfterlightShadows {
    readonly sun: THREE.DirectionalLight;
    readonly proxies = new THREE.Group();
    private source: THREE.DirectionalLight;
    private sourceIntensity: number;
    private sourceVisible: boolean;
    private small: { mesh: THREE.Mesh; bounds: THREE.Box3 }[] = [];
    private material = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide });
    private direction = new THREE.Vector3();
    private center = new THREE.Vector3();
    private right = new THREE.Vector3();
    private up = new THREE.Vector3();
    /** Receiver region half-width (m), shadow-map texel (m) and the reach of the small nearby casters, from ShadowSettings. */
    private distance = 32; private texel = 64 / 4096; private smallReach = 60; private sunDistance = 900;
    private unsubscribe: () => void;
    /** `maxMapSize`: the renderer's largest 2D texture; a wide region uses an 8192 map where the device allows it. */
    constructor(private scene: THREE.Scene, level: THREE.Object3D, private maxMapSize = 8192) {
        let source: THREE.DirectionalLight | undefined;
        scene.traverse(o => { if (o instanceof THREE.DirectionalLight && o.name === 'DirectionalLight') source = o; });
        if (!source) throw new Error('Afterlight shadow sun not found');
        this.source = source; this.sourceIntensity = source.intensity; this.sourceVisible = source.visible;
        this.direction.subVectors(source.position, source.target.position).normalize();
        this.sun = new THREE.DirectionalLight(source.color, source.intensity);
        // Exclude the engine sun from the light list. Toggling castShadow on a
        // sun that rendered during loading destroys its WebGPU depth texture,
        // while already-compiled exterior materials can still reference it.
        source.visible = false;
        this.sun.name = 'Afterlight focused sun'; this.sun.castShadow = true;
        // Film mode needs its final allocation before any material binds the shadow texture.
        // Resizing after bloom/reflection contexts exist leaves their cached GPU bindings stale.
        this.filmMapSize=cinematicSurfaceEnabled()&&!stormDrivingEnabled()?Math.min(16384,Math.max(4096,this.maxMapSize)):0;
        this.sun.shadow.mapSize.set(this.filmMapSize||4096,this.filmMapSize||4096);
        Object.assign(this.sun.shadow.camera, { left: -32, right: 32, bottom: -32, top: 32, near: .5, far: 1900 });
        this.sun.shadow.camera.layers.enable(30); this.sun.shadow.camera.updateProjectionMatrix();
        this.unsubscribe = shadowSettings.subscribe(settings => {if(this.filmDistance===null)this.setDistance(settings.distance);});
        // Two centimetres clears the depth quantization on broad, shallow-angle
        // podium roofs without removing their received shadows (Bellagio A/B).
        this.sun.shadow.bias = -.000005; this.sun.shadow.normalBias = .02; this.sun.shadow.radius = 1;
        this.proxies.name = 'Afterlight shadow-only silhouettes'; scene.add(this.proxies, this.sun, this.sun.target);
        // Rendered architecture is untouched. Only its shadow representation changes.
        level.traverse(o => { if (o instanceof THREE.Mesh) o.castShadow = false; });
        for (const c of data.colliders) {
            if (c.name.startsWith('OSM district foundation') || /district edge|solid lower leg/.test(c.name)) continue;
            let geometry: THREE.BufferGeometry;
            if (c.shape === 'box' && 'size' in c && c.size) {
                geometry = new THREE.BoxGeometry(c.size[0], c.size[1], c.size[2]);
            } else if (c.shape === 'convexHull' && 'vertices' in c && c.vertices) {
                const points: THREE.Vector3[] = [];
                for (let i = 0; i < c.vertices.length; i += 3) points.push(new THREE.Vector3(c.vertices[i], c.vertices[i + 1], c.vertices[i + 2]));
                geometry = new ConvexGeometry(points);
            } else continue;
            const mesh = this.add(geometry);
            if (c.shape === 'box' && 'position' in c && c.position) { mesh.position.fromArray(c.position); mesh.rotation.y = c.yaw ?? 0; }
            mesh.updateMatrixWorld(true);
            const bounds = new THREE.Box3().setFromObject(mesh), size = bounds.getSize(new THREE.Vector3());
            if (Math.max(size.x, size.y, size.z) < 12 && bounds.max.y < 12) this.small.push({ mesh, bounds });
        }
        // The replacement Eiffel exterior owns its shadow geometry in ResortBlocks.
        this.batchProxies();
        this.update(new THREE.Vector3(...mapPoint([-42,0,0],'sanctuary')));
        console.log(`[AfterlightShadows] ${this.proxies.children.length} silhouette parts; ${this.small.length} nearby-only; ${this.sun.shadow.mapSize.x} map / ${this.distance * 2} m receiver region / 1900 m depth`);
    }
    /** Widen or narrow the receiver region. Up to ±48 m keeps the 4096 map (1.6-2.3 cm texels); wider regions
     * use an 8192 map where the device allows it, so ±96 m still has 2.3 cm texels. Applies on the next frame. */
    private filmMapSize=0;
    setDistance(distance: number, film = false): void {
        const d = Math.max(16, distance), requested = film ? Math.min(16384, Math.max(4096, this.maxMapSize)) : d > 48 ? Math.min(8192, Math.max(4096, this.maxMapSize)) : 4096;
        // Keep a filming allocation until page teardown. Shrinking it after a take destroys a texture still
        // referenced by the rain/reflection render contexts in three r185. Ordinary gameplay is unaffected.
        if(film)this.filmMapSize=Math.max(this.filmMapSize,requested);
        const size=Math.max(requested,this.filmMapSize);
        this.distance = d; this.texel = 2 * d / size; this.smallReach = Math.max(60, d + 28);
        this.sun.shadow.mapSize.set(size, size);
        // A wide (aerial film) region needs a deeper frustum and a receiver offset of about a texel and a half,
        // or broad roofs and roads acne at 10-30 cm texels; up to ±320 m these stay at their tuned values.
        this.sunDistance = Math.max(900, d + 700); this.sun.shadow.normalBias = Math.max(.02, this.texel * 1.5);
        Object.assign(this.sun.shadow.camera, { left: -d, right: d, bottom: -d, top: d, far: Math.max(1900, this.sunDistance + d * 1.2 + 300) });
        this.sun.shadow.camera.updateProjectionMatrix(); this.sun.shadow.needsUpdate = true;
    }
    private batchProxies(): void {
        this.proxies.updateMatrixWorld(true);
        const near = new Set(this.small.map(s => s.mesh));
        const groups = new Map<string, THREE.BufferGeometry[]>();
        for (const child of [...this.proxies.children]) {
            const mesh = child as THREE.Mesh;
            const center = new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3());
            const key = near.has(mesh) ? `${Math.floor(center.x/24)},${Math.floor(center.z/24)}` : 'far';
            const geometry = mesh.geometry.index ? mesh.geometry.toNonIndexed() : mesh.geometry.clone();
            geometry.deleteAttribute('uv'); geometry.applyMatrix4(mesh.matrixWorld);
            if (!groups.has(key)) groups.set(key, []);
            groups.get(key)!.push(geometry); mesh.geometry.dispose(); mesh.removeFromParent();
        }
        this.small = [];
        for (const [key, geometries] of groups) {
            const mesh = this.add(mergeGeometries(geometries)!);
            geometries.forEach(g => g.dispose());
            // Shadow-only: the CPU copy goes once the shadow pass has uploaded it.
            releaseAfterUpload(mesh.geometry);
            if (key !== 'far') this.small.push({ mesh, bounds: new THREE.Box3().setFromObject(mesh) });
        }
    }
    private add(geometry: THREE.BufferGeometry): THREE.Mesh {
        const mesh = new THREE.Mesh(geometry,this.material); mesh.castShadow = true; mesh.layers.set(30); this.proxies.add(mesh); return mesh;
    }
    /** Local filming: a receiver region wider than the settings allow (the owner, 2026-10-08: "shadows clip out too close to
     * the camera for the video (fine for runtime gameplay)"), on the largest map the device has; Game centres it ahead of
     * the film camera. null returns to the settings' distance. */
    private filmDistance:number|null=null;
    film(distance:number|null):void{
        if(distance===this.filmDistance)return;this.filmDistance=distance;
        this.setDistance(distance??shadowSettings.get().distance,distance!==null);
    }
    get filmReach():number|null{return this.filmDistance;}
    update(player: THREE.Vector3, exteriorVisible=true): void {
        // Engine continues updating its original sun; its lighting/shadows are
        // replaced here rather than fighting its short near/far configuration.
        this.source.visible = false;
        // Windowless interiors receive no direct sun. Keep shadow attachments
        // initialized across changing light lists; clear an empty layer indoors
        // instead of drawing the city's casters into the 4096² target.
        this.sun.intensity=exteriorVisible?this.sourceIntensity:0;
        this.sun.shadow.autoUpdate=true;
        // Three r185 can compile another shadow node when the visible light
        // list changes. Each must render before it is sampled: postponing its
        // first render leaves shared materials bound to a replaced GPU texture.
        this.sun.shadow.needsUpdate=true;
        this.sun.shadow.camera.layers.mask=exteriorVisible?((1<<30)|1):(1<<29);
        this.proxies.visible=exteriorVisible;
        if(!exteriorVisible)return;
        this.right.crossVectors(WORLD_UP,this.direction).normalize(); this.up.crossVectors(this.direction,this.right).normalize();
        const texel=this.texel;
        this.center.copy(player).addScaledVector(this.right,Math.round(player.dot(this.right)/texel)*texel-player.dot(this.right)).addScaledVector(this.up,Math.round(player.dot(this.up)/texel)*texel-player.dot(this.up));
        this.sun.target.position.copy(this.center); this.sun.position.copy(this.center).addScaledVector(this.direction,this.sunDistance);
        for(const item of this.small) item.mesh.visible = item.bounds.distanceToPoint(player) < this.smallReach;
    }
    dispose(): void {
        this.unsubscribe();
        this.source.intensity=this.sourceIntensity; this.source.visible=this.sourceVisible;
        this.proxies.traverse(o=>{if(o instanceof THREE.Mesh)o.geometry.dispose();}); this.material.dispose();
        this.proxies.removeFromParent();this.sun.removeFromParent();this.sun.target.removeFromParent();this.sun.shadow.dispose();
    }
}
