import * as THREE from 'three';
import {uniform} from 'three/tsl';

/** Interiors' overhead key light (2026-10-23: on the info video the owner found
 * interiors flat without shadows, the furniture seeming to float). Inside, the sun is off and the borrowed point lights cast no
 * shadows, so nothing grounds a bed, a chair or a slot bank. This directional light shines almost straight down and
 * casts a tight shadow map around the camera from the interior geometry only. It leans (64 degrees, toward the sun's
 * bearing) because a shadow straight down hides under its own object (layer INTERIOR_CASTERS, which
 * lightInterior() puts every interior mesh on).
 *
 * It belongs to the interiors' fixed light list (InteriorLighting) and never to the scene graph: the city's materials
 * never see it, and the list never changes; only its intensity, pose and shadow mask do (see AGENTS.md: never change
 * the set of lights). Interior materials discard their shadow-pass fragments above KEY_CUT_Y (CLEAR metres above the
 * camera; InteriorLighting sets their maskShadowNode), so ceilings, coffers and chandeliers above head height never
 * cast; furniture, fittings and the feet of walls do. */
export const INTERIOR_CASTERS = 27;
const EMPTY_LAYER = 25;
const CLEAR = 1.1;           // the cut: this far above the camera (a hotel ceiling is ~1.2 m above eye height)
/** World height above which interior geometry casts no shadow (no cut while the key light is off). */
export const KEY_CUT_Y = uniform(1e6);
const REACH = 28;            // half-width of the shadow region (m): a casino floor's slot banks and tables 30 m off (1.4 cm texels)
const ELEVATION = THREE.MathUtils.degToRad(64);   // leaning: a shadow straight down hides under its own object

class InteriorKey {
    readonly light = new THREE.DirectionalLight(0xfff1df, 0);
    /** Interior roots whose opaque meshes cast for the key light (lightInterior registers them); their casting is on only
     * while the key light is, so the outdoor sun's shadow pass never draws them. */
    private readonly roots = new Set<THREE.Object3D>();
    private readonly dir = new THREE.Vector3();
    private readonly ahead = new THREE.Vector3();
    private readonly at = new THREE.Vector3();
    private on = false;
    constructor() {
        const l = this.light;
        l.name = 'Interior overhead key light';
        l.castShadow = true;
        l.shadow.mapSize.set(4096, 4096);
        Object.assign(l.shadow.camera, {left: -REACH, right: REACH, bottom: -REACH, top: REACH, near: .5, far: 80});
        l.shadow.camera.updateProjectionMatrix();
        l.shadow.bias = -.0001; l.shadow.normalBias = .02; l.shadow.radius = 3;
        l.shadow.camera.layers.set(EMPTY_LAYER);
        this.setAzimuth(155);
    }
    /** The light's bearing (degrees, as world.json's sunAzimuthDeg): the few degrees it leans follow the sun. */
    setAzimuth(deg: number): void {
        const a = THREE.MathUtils.degToRad(deg);
        this.dir.set(Math.cos(ELEVATION) * Math.sin(a), Math.sin(ELEVATION), Math.cos(ELEVATION) * Math.cos(a)).normalize();
    }
    register(root: THREE.Object3D): void {
        this.roots.add(root);
        if (this.on) this.cast(root, true);
    }
    private cast(root: THREE.Object3D, on: boolean): void {
        root.traverse(o => { if (o instanceof THREE.Mesh && o.userData.keyCaster) o.castShadow = on; });
    }
    private castAll(on: boolean): void {
        for (const r of this.roots) { if (!r.parent) { this.roots.delete(r); continue; } this.cast(r, on); }
    }
    /** Every frame: `active` while the camera is inside an interior (a venue, resort, Sphere or hotel interior view). */
    update(camera: THREE.Camera, active: boolean, intensity: number): void {
        const l = this.light;
        if (!active) {
            if (this.on) { l.intensity = 0; l.shadow.camera.layers.set(EMPTY_LAYER); KEY_CUT_Y.value = 1e6; this.on = false; this.castAll(false); }
            return;
        }
        if (!this.on) { this.on = true; this.castAll(true); }
        l.intensity = intensity;
        l.shadow.camera.layers.set(INTERIOR_CASTERS);
        // the region sits a third of its width ahead of the camera, on the level of the camera
        camera.getWorldDirection(this.ahead); this.ahead.y = 0;
        if (this.ahead.lengthSq() > 1e-6) this.ahead.normalize().multiplyScalar(REACH / 3);
        camera.getWorldPosition(this.at).add(this.ahead);
        // geometry above the cut casts nothing; the light itself stands well back along its direction
        KEY_CUT_Y.value = this.at.y + CLEAR;
        l.position.copy(this.at).addScaledVector(this.dir, 30);
        l.target.position.copy(this.at);
        // (outside the scene graph: keep its matrices current by hand)
        l.updateMatrixWorld(true); l.target.updateMatrixWorld(true);
        l.shadow.needsUpdate = true;
    }
}

export const interiorKey = new InteriorKey();
