import * as THREE from 'three';
import { Node } from 'three/webgpu';
import type { NodeBuilder, NodeFrame } from 'three/webgpu';
import {
    Loop, NodeUpdateType, getDistanceAttenuation, int, mix, normalWorld, positionView,
    renderGroup, smoothstep, uniform, uniformArray, vec3,
} from 'three/tsl';
import type { BatchedLightType } from './LightBatching.js';

/**
 * Every batched light of a scene in ONE uniform array, shaded by one loop per light type.
 *
 * three's `DynamicLighting` addon keeps 2–4 uniform arrays per light type, and each array is
 * its own uniform-buffer binding. With directional, point, spot and hemisphere lights that is
 * 12 bindings on top of the material's own two — 14, over WebGPU's per-stage limit of 12
 * (`maxUniformBuffersPerShaderStage`, 12 on Apple and most phones), so every lit pipeline
 * failed to build. Packing all of them into one `vec4` array costs one binding.
 *
 * Layout, `vec4`s per light, types in this order:
 *   directional ×2  [color·intensity, –]        [direction (view), –]
 *   point       ×2  [color·intensity, decay]    [position (view), cutoff distance]
 *   spot        ×4  [color·intensity, decay]    [position (view), cutoff distance]
 *                   [direction (view), cos(angle)] [cos(angle·(1 − penumbra)), –, –, –]
 *   hemisphere  ×3  [sky·intensity, –]          [ground·intensity, –]  [direction (world), –]
 * Ambient lights are summed into one render-group colour. The counts are render-group ints,
 * so a light arriving or leaving changes uniform values only — never the shader.
 *
 * The shading math is the addon's, line for line (distance attenuation, the smoothstep cone,
 * the hemisphere mix), so a batched light looks exactly like three's own.
 */

export interface BatchedLightCaps {
    DirectionalLight: number;
    PointLight: number;
    SpotLight: number;
    HemisphereLight: number;
}

const STRIDE = { DirectionalLight: 2, PointLight: 2, SpotLight: 4, HemisphereLight: 3 } as const;

/** A node the loops accumulate into. */
interface AssignableNode {
    addAssign(value: unknown): unknown;
}

/** The lighting-context members the loops write into. three's typings leave them loose. */
interface LightingContext {
    lightingModel: {
        direct(input: Record<string, unknown>, builder: NodeBuilder): void;
    };
    reflectedLight: { directDiffuse: AssignableNode; directSpecular: AssignableNode };
    irradiance: AssignableNode;
    positionView?: typeof positionView;
}

const makeBuffer = (data: THREE.Vector4[]) => uniformArray(data, 'vec4' as const);
const makeCount = () => uniform(0, 'int');
const makeColor = (color: THREE.Color) => uniform(color);

const _a = new THREE.Vector3();
const _b = new THREE.Vector3();

export class BatchedLightsNode extends Node {
    static get type(): string {
        return 'BatchedLightsNode';
    }

    private readonly _caps: BatchedLightCaps;
    private readonly _base: Record<keyof BatchedLightCaps, number>;
    private readonly _data: THREE.Vector4[];
    private readonly _buffer: ReturnType<typeof makeBuffer>;
    private readonly _counts: Record<keyof BatchedLightCaps, ReturnType<typeof makeCount>>;
    private readonly _ambientColor = new THREE.Color();
    private readonly _ambient: ReturnType<typeof makeColor>;
    private readonly _lights = new Map<BatchedLightType, readonly THREE.Light[]>();

    constructor(caps: BatchedLightCaps) {
        super();
        this._caps = caps;
        let next = 0;
        const base = {} as Record<keyof BatchedLightCaps, number>;
        for (const type of ['DirectionalLight', 'PointLight', 'SpotLight', 'HemisphereLight'] as const) {
            base[type] = next;
            next += caps[type] * STRIDE[type];
        }
        this._base = base;
        this._data = Array.from({ length: Math.max(next, 1) }, () => new THREE.Vector4());
        this._buffer = makeBuffer(this._data);
        this._buffer.setGroup(renderGroup);
        this._counts = {
            DirectionalLight: makeCount(),
            PointLight: makeCount(),
            SpotLight: makeCount(),
            HemisphereLight: makeCount(),
        };
        for (const count of Object.values(this._counts)) count.setGroup(renderGroup);
        this._ambient = makeColor(this._ambientColor);
        this._ambient.setGroup(renderGroup);
        this.updateType = NodeUpdateType.RENDER;
    }

    /** The lights of one type to shade this frame — at most its cap; `EngineLightsNode` ranks them. */
    setLights(type: BatchedLightType, lights: readonly THREE.Light[]): void {
        this._lights.set(type, lights);
    }

    /** Copy every light into the array, in view space for the camera being rendered. */
    // eslint-disable-next-line game-conventions/update-method-signature -- three's Node.update(frame), once per render, not a dt tick
    override update(frame: NodeFrame): boolean | undefined {
        const camera = frame.camera;
        if (!camera) return undefined;
        const view = camera.matrixWorldInverse;
        const data = this._data;

        this._ambientColor.setRGB(0, 0, 0);
        for (const light of this._lights.get('AmbientLight') ?? []) {
            this._ambientColor.r += light.color.r * light.intensity;
            this._ambientColor.g += light.color.g * light.intensity;
            this._ambientColor.b += light.color.b * light.intensity;
        }

        const directional = this.listOf('DirectionalLight');
        for (let i = 0; i < directional.length; i++) {
            const light = directional[i] as THREE.DirectionalLight;
            const o = this._base.DirectionalLight + i * STRIDE.DirectionalLight;
            data[o]!.set(light.color.r * light.intensity, light.color.g * light.intensity, light.color.b * light.intensity, 0);
            _a.setFromMatrixPosition(light.matrixWorld).sub(_b.setFromMatrixPosition(light.target.matrixWorld)).transformDirection(view);
            data[o + 1]!.set(_a.x, _a.y, _a.z, 0);
        }

        const points = this.listOf('PointLight');
        for (let i = 0; i < points.length; i++) {
            const light = points[i] as THREE.PointLight;
            const o = this._base.PointLight + i * STRIDE.PointLight;
            data[o]!.set(light.color.r * light.intensity, light.color.g * light.intensity, light.color.b * light.intensity, light.decay);
            _a.setFromMatrixPosition(light.matrixWorld).applyMatrix4(view);
            data[o + 1]!.set(_a.x, _a.y, _a.z, light.distance);
        }

        const spots = this.listOf('SpotLight');
        for (let i = 0; i < spots.length; i++) {
            const light = spots[i] as THREE.SpotLight;
            const o = this._base.SpotLight + i * STRIDE.SpotLight;
            data[o]!.set(light.color.r * light.intensity, light.color.g * light.intensity, light.color.b * light.intensity, light.decay);
            _a.setFromMatrixPosition(light.matrixWorld);
            _b.copy(_a).applyMatrix4(view);
            data[o + 1]!.set(_b.x, _b.y, _b.z, light.distance);
            _a.sub(_b.setFromMatrixPosition(light.target.matrixWorld)).transformDirection(view);
            data[o + 2]!.set(_a.x, _a.y, _a.z, Math.cos(light.angle));
            data[o + 3]!.set(Math.cos(light.angle * (1 - light.penumbra)), 0, 0, 0);
        }

        const hemispheres = this.listOf('HemisphereLight');
        for (let i = 0; i < hemispheres.length; i++) {
            const light = hemispheres[i] as THREE.HemisphereLight;
            const o = this._base.HemisphereLight + i * STRIDE.HemisphereLight;
            data[o]!.set(light.color.r * light.intensity, light.color.g * light.intensity, light.color.b * light.intensity, 0);
            data[o + 1]!.set(light.groundColor.r * light.intensity, light.groundColor.g * light.intensity, light.groundColor.b * light.intensity, 0);
            _a.setFromMatrixPosition(light.matrixWorld).normalize();
            data[o + 2]!.set(_a.x, _a.y, _a.z, 0);
        }

        this.setCount('DirectionalLight', directional.length);
        this.setCount('PointLight', points.length);
        this.setCount('SpotLight', spots.length);
        this.setCount('HemisphereLight', hemispheres.length);
        return undefined;
    }

    override setup(builder: NodeBuilder): null {
        const context = builder.context as unknown as LightingContext;
        const { lightingModel, reflectedLight } = context;
        const surface = context.positionView ?? positionView;
        const buffer = this._buffer;
        const diffuse = vec3(0).toVar('batchedDiffuse');
        const specular = vec3(0).toVar('batchedSpecular');
        const direct = (lightDirection: unknown, lightColor: unknown): void => {
            lightingModel.direct({
                lightDirection,
                lightColor,
                lightNode: { light: {}, shadowNode: null },
                reflectedLight: { directDiffuse: diffuse, directSpecular: specular },
            }, builder);
        };

        context.irradiance.addAssign(this._ambient);

        Loop({ start: int(0), end: this._counts.DirectionalLight, type: 'int', condition: '<' }, ({ i }) => {
            const o = int(i).mul(int(STRIDE.DirectionalLight)).add(int(this._base.DirectionalLight));
            const color = buffer.element(o).xyz.toVar();
            const direction = buffer.element(o.add(int(1))).xyz.normalize().toVar();
            direct(direction, color);
        });

        Loop({ start: int(0), end: this._counts.PointLight, type: 'int', condition: '<' }, ({ i }) => {
            const o = int(i).mul(int(STRIDE.PointLight)).add(int(this._base.PointLight));
            const colorDecay = buffer.element(o);
            const positionCutoff = buffer.element(o.add(int(1)));
            const lightVector = positionCutoff.xyz.sub(surface).toVar();
            const lightDirection = lightVector.normalize().toVar();
            const attenuation = getDistanceAttenuation({
                lightDistance: lightVector.length(),
                cutoffDistance: positionCutoff.w,
                decayExponent: colorDecay.w,
            });
            direct(lightDirection, colorDecay.xyz.mul(attenuation).toVar());
        });

        Loop({ start: int(0), end: this._counts.SpotLight, type: 'int', condition: '<' }, ({ i }) => {
            const o = int(i).mul(int(STRIDE.SpotLight)).add(int(this._base.SpotLight));
            const colorDecay = buffer.element(o);
            const positionCutoff = buffer.element(o.add(int(1)));
            const directionCone = buffer.element(o.add(int(2)));
            const penumbra = buffer.element(o.add(int(3)));
            const lightVector = positionCutoff.xyz.sub(surface).toVar();
            const lightDirection = lightVector.normalize().toVar();
            const spotAttenuation = smoothstep(directionCone.w, penumbra.x, lightDirection.dot(directionCone.xyz));
            const distanceAttenuation = getDistanceAttenuation({
                lightDistance: lightVector.length(),
                cutoffDistance: positionCutoff.w,
                decayExponent: colorDecay.w,
            });
            direct(lightDirection, colorDecay.xyz.mul(spotAttenuation).mul(distanceAttenuation).toVar());
        });

        Loop({ start: int(0), end: this._counts.HemisphereLight, type: 'int', condition: '<' }, ({ i }) => {
            const o = int(i).mul(int(STRIDE.HemisphereLight)).add(int(this._base.HemisphereLight));
            const sky = buffer.element(o).xyz;
            const ground = buffer.element(o.add(int(1))).xyz;
            const direction = buffer.element(o.add(int(2))).xyz;
            const weight = normalWorld.dot(direction).mul(0.5).add(0.5);
            context.irradiance.addAssign(mix(ground, sky, weight));
        });

        reflectedLight.directDiffuse.addAssign(diffuse);
        reflectedLight.directSpecular.addAssign(specular);
        return null;
    }

    private listOf(type: keyof BatchedLightCaps): readonly THREE.Light[] {
        const lights = this._lights.get(type) ?? [];
        return lights.length > this._caps[type] ? lights.slice(0, this._caps[type]) : lights;
    }

    private setCount(type: keyof BatchedLightCaps, count: number): void {
        (this._counts[type] as unknown as { value: number }).value = count;
    }
}
