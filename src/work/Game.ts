import {stormDrivingEnabled} from './film/SceneSurface.js';
import { gltfSceneHooks, gltfUrlHooks } from './GltfDecoders.js';
import {filmDetail} from './FilmDetail.js';
import { RealisticWater } from './RealisticWater.js';
import { fixLoadedMaterials } from './MaterialFixes.js';
import { applyPbrDetail, loadPbrDetail } from './PbrDetail.js';
// Every loaded asset's water surfaces become realistic water (RealisticWater), whatever loader brought them in;
// exterior assets get scanned surface detail (PbrDetail).
gltfSceneHooks.push(scene => { fixLoadedMaterials(scene); RealisticWater.adopt(scene); });
gltfUrlHooks.push(applyPbrDetail);
if (typeof location !== 'undefined' && ['localhost', '127.0.0.1'].includes(location.hostname)) (window as unknown as { __afterlightWater?: unknown }).__afterlightWater = RealisticWater;
import { CollisionGroup } from 'engine/physics/CollisionLayers.js';
import {CityDetailRanges,cityEntranceDetails} from './CityDetailRanges.js';
import {CityLod} from './CityLod.js';
import {PerformancePanel} from './PerformancePanel.js';
import {ResortBlockReview} from './ResortBlockReview.js';
import {BigAppleCoaster} from './BigAppleCoaster.js';
import {GeographicCity} from './GeographicCity.js';
import geographicLevel from './geographic/level.json';
import geographicVersion from './geographic/version.json';
import {mapPoint,mapYaw,reviewDistrict} from './geographic/Coordinates.js';
import {StreamingWork} from './StreamingWork.js';
import {BackgroundActivity} from './BackgroundActivity.js';
import {configureSkylineDepth} from './SkylineDepth.js';
import {configureLightCaps} from './LightCaps.js';
import {extendSkylineCamera,matchHazeToSky} from './StripAtmosphere.js';
import {CameraObstruction} from './CameraObstruction.js';
import { GroundSurfaceIndex } from './GroundSurfaceIndex.js';
import { updateProfile } from './UpdateProfile.js';
import { SanctuaryJeep } from './SanctuaryJeep.js';
import { BuildingVisibility } from './BuildingVisibility.js';
import { PassingDetector } from './PassingDetector.js';
import { AfterlightShadows } from './AfterlightShadows.js';
import { interiorKey } from './InteriorKeyLight.js';
/** The interiors' overhead key light (InteriorKeyLight.ts), against the sun's ~5 and the interiors' ambient. */
const INTERIOR_KEY_INTENSITY = 4;
import { DoorKick } from './DoorKick.js';
import { GAME_LAYERS, type GameLayer, type CityContext } from './GameLayers.js';
import { MeshLevel, DEFAULT_MESH_LEVEL_OPTIONS } from 'engine/meshlevel/MeshLevel.js';
import { DEFAULT_FALL_RESCUE_OPTIONS } from 'engine/player/life/FallRescue.js';
import { ParisLift } from './ParisLift.js';
// AI editor note: This file is overridden by EVERY community template under
// /templates/<slug>/source/Game.ts — it's the one file all 6 templates
// commit a per-template version of. If you rename exports, change the
// constructor signature, or alter the GenreGameInterface this class
// implements, search every overlay for stale references and update them
// in lockstep (pnpm run check does NOT cover templates — drift lands
// silently). See ../../../../templates/README.md for the full contract.
import * as THREE from 'three';
import {HotelStreaming} from './hotels/HotelStreaming.js';
import type { WorldProfileData, EngineLike, GameData } from 'types/game.js';
import { PlayerController } from 'engine/player/PlayerController.js';
import { VoxelPlayerController } from './VoxelPlayerController.js';
import { ThirdPersonCamera } from 'engine/camera/ThirdPersonCamera.js';
import { CameraManager } from 'engine/camera/CameraManager.js';
import { WorldGenerator } from './WorldGenerator.js';
import { SkyboxLoader } from 'engine/sky/SkyboxLoader.js';
import { SkyboxMaterialHelper } from 'engine/sky/SkyboxMaterialHelper.js';
import { PlayerLoader } from 'engine/player/PlayerLoader.js';
import { AmbientLighting } from 'engine/lighting/AmbientLighting.js';
// DebugController is only available in development - handled dynamically
import { GameHUD } from './GameHUD.js';
import { bitmagicCharacterFactory, applyBitmagicModifications, updateBitmagicEyeBlink } from './BitmagicPlayerCharacter.js';
import type { GenreGameInterface } from 'engine/boot/GenreRegistry.js';
import { DEFAULT_PHYSICS } from './PhysicsConfig.js';
import { CONSTANTS } from './Constants.js';
import { VehicleManager } from 'engine/vehicle/VehicleManager.js';
import { Spawner } from 'engine/world/spawning/Spawner.js';
import { VehicleSpawner } from 'engine/vehicle/spawning/VehicleSpawner.js';
import { mergeCharacterConfig } from 'engine/character/CharacterConfig.js';
import { setCityAtlasUploader } from './CityAtlas.js';
import { sweepUploadedGeometry } from './CpuGeometryRelease.js';
import { glbUrl } from './OptimizedGlb.js';
import { NearbyLights } from './NearbyLights.js';
import { lights as lightsNode } from 'three/tsl';

export class VoxelGame implements GenreGameInterface {
    private performancePanel:PerformancePanel|null=null;
    private detailRanges:CityDetailRanges|null=null;
    private legacyLod:CityLod|null=null;
    private resortReview:ResortBlockReview|null=null;
    private backgroundActivity:BackgroundActivity|null=null;
    private releaseAtmosphere:(()=>void)|null=null;
    private releaseWaterFrame:(()=>void)|null=null;
    /** The game layers on top of the city (GameLayers.ts); none in the city itself. */
    private layers: GameLayer[] = [];
    /** BuildingVisibility's point test, made once (no per-frame closures). */
    private visibleTest=(p:THREE.Vector3):boolean=>this.buildingVisibility?.pointVisible(p)??true;
    private streamingWork:StreamingWork|null=null;
    private cameraObstruction=new CameraObstruction();
    private groundSurfaces=new GroundSurfaceIndex();
    private nearbyLights:NearbyLights|null=null;
    /** Driving past a building: its interior is not streamed (see PassingDetector). */
    private passingDetector=new PassingDetector();
    private sanctuaryJeep: SanctuaryJeep | null = null;
    private bigAppleCoaster:BigAppleCoaster|null=null;
    private buildingVisibility: BuildingVisibility | null = null;
    private hotelStreaming:HotelStreaming|null=null;
    private doorKick:DoorKick|null=null;
    /** Local filming only (tools/film). */
    private film:import('./film/Film.js').Film|null=null;
    /** Time of day and weather for film takes (take.look); local filming only. */
    private filmLook:import('./film/FilmLook.js').FilmLook|null=null;
    /** Film scenarios a game layer provides (car-chase takes). */
    private filmScenario:Awaited<ReturnType<NonNullable<GameLayer['filmReady']>>>|null=null;
    /** Analog drive input while a film take drives the jeep (see the film host's vehicleInput). */
    private filmVehicle={active:false,throttle:0,brake:0,patched:new WeakSet<object>()};
    /** Local only: the ?inspect= review placement, by name. */
    private placeInspect:((name:string|null)=>boolean)|null=null;
    private geographicCity:GeographicCity|null=null;
    private focusedShadows: AfterlightShadows | null = null;
    private shadowAhead = new THREE.Vector3();
    private viewHeld = false;
    private meshLevel: MeshLevel | null = null;
    private parisLift: ParisLift | null = null;
    private engine: EngineLike;
    private worldProfileData: WorldProfileData;
    private world: THREE.Object3D | null;
    private player: THREE.Object3D | null;
    private playerController: PlayerController | null;
    private cameraController: ThirdPersonCamera | null;
    private cameraManager: CameraManager | null = null;
    public worldGenerator: WorldGenerator | null = null;
    private skyboxLoader: SkyboxLoader;
    private playerLoader: PlayerLoader;
    private ambientLighting: AmbientLighting;
    private debugController: any | null = null;
    public hud: GameHUD;
    private vehicleManager: VehicleManager;
    private spawner: Spawner;
    private vehicleSpawner: VehicleSpawner;
    private gameId: string | null = null;

    private gameData: GameData | null = null;
    private walkingSpeed = 5;
    private runningSpeed = 10;
    private elapsedTime: number = 0; // Track elapsed time for animated textures
    private hemisphereLight: THREE.HemisphereLight | null = null;

    private wasRecordingFrames: boolean = false;
    private cullingWasEnabledBeforeRecording: boolean = false;
    private envCullingWasEnabledBeforeRecording: boolean = false;

    constructor(engine: EngineLike, worldProfileData: WorldProfileData, gameData?: GameData) {
        configureSkylineDepth(engine);
        configureLightCaps(engine);
        this.engine = engine;
        this.worldProfileData = worldProfileData;
        this.gameData = gameData || null;
        this.world = null;
        this.player = null;
        this.playerController = null;
        this.cameraController = null;

        // Require seed from worldProfileData - throw error if not found
        if (worldProfileData.worldSeed === undefined) {
            throw new Error('worldSeed is required in worldProfileData for consistent world generation');
        }

        try {
            console.log('Creating SkyboxLoader...', { engine: !!engine, worldProfileData: !!worldProfileData });
            this.skyboxLoader = new SkyboxLoader(engine, worldProfileData);
            console.log('SkyboxLoader created successfully:', !!this.skyboxLoader);
        } catch (error) {
            console.error('Failed to create SkyboxLoader:', error);
            throw error;
        }

        this.playerLoader = new PlayerLoader(engine, worldProfileData);

        // Expose playerLoader on engine for debug tools
        this.engine.setPlayerLoader?.(this.playerLoader);

        this.ambientLighting = new AmbientLighting(engine, this.skyboxLoader);
        // DebugController will be initialized lazily in load() method if available
        // gameName is required and must come from game.json (now at top level of gameData)
        const gameName = this.gameData?.gameName;
        if (!gameName) {
            console.error('[VoxelGame] gameData:', this.gameData);
            throw new Error('[VoxelGame] gameName is required in gameData but was not provided. Ensure game.json is loaded and merged correctly.');
        }
        this.hud = new GameHUD();
        this.vehicleManager = new VehicleManager(engine);
        this.spawner = new Spawner(engine);
        this.vehicleSpawner = new VehicleSpawner(this.spawner, this.vehicleManager);

        // Expose Spawner and VehicleSpawner on engine for easy access from templates
        this.engine.setSpawner?.(this.spawner);
        this.engine.setVehicleSpawner?.(this.vehicleSpawner);

        // Provide block character factory using new interface-based approach
        this.engine.blockCharacterFactory = bitmagicCharacterFactory;

        // Provide Bitmagic modifications callback for post-creation scaling/physics
        this.engine.applyCharacterModifications = applyBitmagicModifications;
    }

    async load(gameId: string): Promise<void> {
        this.backgroundActivity=new BackgroundActivity(this.engine);
        // Ambience is rendered in the editor even when gameplay's delta is zero.
        // This hook runs after the final camera pose and also honors recorded fixed steps.
        this.releaseWaterFrame=this.engine.registerBeforeRender?.(()=>{
            RealisticWater.everyFrame=!!this.film&&!stormDrivingEnabled()||!!(this.engine as unknown as {isRecordingFrames?:()=>boolean}).isRecordingFrames?.();
            RealisticWater.update(this.engine.getAmbienceTime?.()??0,this.engine.scene??null,this.engine.camera??null);
        })??null;
        try {
            // EXPERIMENT (local only): ?lighting=engine<cap> | clustered installs another renderer.lighting before
            // any lit material or shadow node exists. (Engine 3.1337 batches lights itself, LightCaps.ts sizes it; storm
            // takes no longer default to this experiment's older copy.)
            {const mode=['localhost','127.0.0.1'].includes(location.hostname)?(new URLSearchParams(location.search).get('lighting')??null):null;
                if(mode&&(mode.startsWith('engine')||mode==='clustered')){const R=this.engine.renderer as unknown as {init?:()=>Promise<unknown>;lighting:unknown;_renderLists?:{lighting:unknown;dispose:()=>void}};await R.init?.();
                    const instance=mode==='clustered'?new (await import('three/addons/lighting/ClusteredLighting.js')).ClusteredLighting(1024,32,24,64)
                        :await import('./experiments/engine-lighting/EngineLighting.js').then(m=>new m.EngineLighting({...m.DEFAULT_ENGINE_LIGHTING_OPTIONS,maxPointLights:Number(mode.slice(6))||64}));
                    const lighting=instance as unknown as {getNode:(scene:THREE.Object3D)=>unknown;createNode:()=>unknown},cache=new WeakMap<object,unknown>(),fallback=lighting.getNode.bind(lighting);
                    lighting.getNode=(scene)=>{if(!(scene as THREE.Scene).isScene&&!(scene as THREE.Group).isGroup)return fallback(scene);let n=cache.get(scene);if(!n){n=lighting.createNode();cache.set(scene,n);}return n;};
                    R.lighting=instance;if(R._renderLists){R._renderLists.lighting=instance;R._renderLists.dispose();}
                    console.info('[experiment] renderer.lighting =',mode);}}
            // City texture atlases upload as they are built and drop their canvases (see CityAtlas).
            const renderer=this.engine.renderer as unknown as {init?:()=>Promise<unknown>;initTexture:(t:THREE.Texture)=>void}|undefined;
            if(renderer){await renderer.init?.();setCityAtlasUploader(texture=>renderer.initTexture(texture));
                // scanned surface detail must be ready before the city batches and assets build their materials
                await loadPbrDetail(texture=>renderer.initTexture(texture));}
            // Store gameId for WorldGenerator
            this.gameId = gameId;

            // Bloom is now configured automatically from world.json in GameEngine.loadGame()

            // Create WorldGenerator now that we have gameId
            if (!this.worldGenerator) {
                // Determine initial world size from ground type settings if available, otherwise default to 128
                const initialWorldSize = this.worldProfileData.groundWorldSizeX
                    ? Math.max(this.worldProfileData.groundWorldSizeX, this.worldProfileData.groundWorldSizeZ || 128)
                    : 128;

                // worldSeed is already validated in constructor, so we know it's defined
                const seed = this.worldProfileData.worldSeed!;

                // Pass gameId and gameData to WorldGenerator so it can load saved heightmaps and pass data to systems
                this.worldGenerator = new WorldGenerator(initialWorldSize, seed, this.worldProfileData, this.engine, gameId, this.gameData);

                // Expose findValidVoxelSpawnPosition for proper animal/NPC spawning in voxel terrain
                this.engine.findValidVoxelSpawnPosition = (x: number, z: number, fromY?: number) => {
                    return this.worldGenerator?.findValidVoxelSpawnPosition(x, z, fromY) || null;
                };
            }

            // Always generate full world in Voxel mode
            await this.worldGenerator.generateWorld();
            this.world = this.worldGenerator.getWorld();

            if (!this.world) {
                throw new Error('WorldGenerator failed to create world object');
            }

            // Ground physics is now created automatically with visual chunks via generateGroundChunks()
            // which properly tracks both visual mesh and physics body together.
            // Physics bodies are added to physics world during chunk generation.

            // Add all other physics bodies (scenery, etc.) to physics world
            this.worldGenerator.getWorldBodies().forEach(body => {
                if (this.engine.physicsWorld && body) {
                    this.engine.physicsWorld.addRigidBody(body);
                }
            });


            await this.skyboxLoader.loadSkybox();
            const skyUniforms = SkyboxMaterialHelper.getUniformsFromMesh(
                this.engine.scene?.getObjectByName(SkyboxLoader.SKYBOX_NAME)
            );
            if (skyUniforms) {
                // Generated WebP skies are sRGB images, not linear HDR maps.
                // Decode correctly to retain the cover's rich sunset colors.
                skyUniforms.skyboxTexture.value.colorSpace = THREE.SRGBColorSpace;
                skyUniforms.skyboxTexture.value.needsUpdate = true;
                SkyboxMaterialHelper.setRotation(skyUniforms, 25);
            }
            this.ambientLighting.updateFromScene();
            if (this.engine.scene) this.engine.scene.environmentRotation.y = THREE.MathUtils.degToRad(25);
            // First/third person, vehicle and editor share the default camera.
            // Keep the close near plane for rooms; extend only the far plane.
            extendSkylineCamera(this.engine.getDefaultCamera());
            if(this.engine.camera)extendSkylineCamera(this.engine.camera);
            if(this.engine.scene)this.releaseAtmosphere=matchHazeToSky(this.engine.scene,
                this.engine.scene.getObjectByName(SkyboxLoader.SKYBOX_NAME));

            // Show the engine Play button (default behavior, made explicit so
            // state from a prior game that hid it doesn't carry over).
            this.engine.setPlayButtonVisible?.(true);

            // Sky/ground bounce keeps sunset shadows readable on mesh materials.
            this.setupVoxelLighting();

            // Physics step for terrain colliders is now done in WorldGenerator.generateWorld()
            // after finalizeTerrain(), so all physics bodies created afterward work correctly

            // Connect terrain system to DynamicObjectManager for chunk-based hibernation
            const voxelTerrain = this.worldGenerator.getVoxelTerrainSystem();
            if (voxelTerrain && this.engine.getDynamicObjectManager) {
                this.engine.getDynamicObjectManager().setTerrainSystem(voxelTerrain);
            }

            this.player = await this.playerLoader.loadHeadlessPlayer();

            // Enable bloom effect on player if configured
            this.engine.enableBloomOnObject?.(this.player);

            this.setupCamera();

            // Initialize DebugController if available (development only) - before setupPlayerController
            try {
                const { DebugController } = await import('engine/devtools/DebugController.js');
                this.debugController = new DebugController(this.engine);
            } catch (error) {
                // DebugController not available - this is fine for production builds
                console.log('DebugController not available (expected in production)');
            }

            await this.setupPlayerController();
            this.hud.createIconText('stream-loading-label',{anchor:'middle-center',icon:'',text:'Loading…'});
            this.hud.createProgressBar('stream-loading',{anchor:'middle-center',label:'Preparing area',width:320,initialValue:0,maxValue:2,format:(done,total)=>`${Math.round(100*done/total)}%`});
            this.hud.hideElement('stream-loading');this.hud.hideElement('stream-loading-label');
            let interactionsSuppressed=false,bodyEnabled=true;
            this.streamingWork=new StreamingWork({
                show:(label,done,total)=>{
                    this.hud.updateIconText('stream-loading-label',{text:label});
                    this.hud.updateProgressBar('stream-loading',done,total);
                    this.hud.showElement('stream-loading-label');this.hud.showElement('stream-loading');
                    this.hud.getElement('stream-loading')!.container.classList.toggle('hud-progress-bar--busy',done<total);
                },
                hide:()=>{this.hud.hideElement('stream-loading');this.hud.hideElement('stream-loading-label');},
                failed:error=>{console.error('[StreamingWork]',error);this.hud.showToast('Area could not be prepared. Please try again.',{variant:'error'});}
            },busy=>{
                this.sanctuaryJeep?.setStreamingHeld(busy);
                for(const layer of this.layers)layer.setStreamingHeld?.(busy);
                const body=this.playerLoader.getPlayerBody();
                if(busy){interactionsSuppressed=this.playerController!.areInteractionsSuppressed();bodyEnabled=body?.isEnabled()??true;}
                // The update gate holds movement without clearing held keys or
                // dropping pointer lock; walking resumes when loading finishes.
                this.playerController!.setInteractionsSuppressed(busy?true:interactionsSuppressed);
                // Hold the capsule exactly in place, including on stair slopes.
                // Restore its existing velocity and input state after the first render.
                if(body?.isValid())body.setEnabled(busy?false:bodyEnabled);
            },undefined,()=>this.refreshStreamingView());
            // The geographic city everywhere (2026-10-24): its runtime files stream from build/ on the dev server and
            // from the Bitmagic CDN in a published game (RuntimeAssets.ts). Before the CDN copy existed, published builds
            // fell back to the September level (`level-vegas`, vegas.mesh-level.json). The review and film switches
            // below stay local-only.
            const localLevelPreview = ['localhost', '127.0.0.1'].includes(location.hostname);
            this.meshLevel = new MeshLevel(this.engine, { glb: { url: new URL(await glbUrl(`/build/geographic-strip/detailed.glb?v=${geographicVersion.revision}`), location.origin).href },
                level: { data: geographicLevel } }, {
                ...DEFAULT_MESH_LEVEL_OPTIONS,
                lighting: { ...DEFAULT_MESH_LEVEL_OPTIONS.lighting, mode: 'exterior', spotShadowMapSize: 2048, pointLightPoolSize: 25 },
                shadows: 'dynamic'
            });
            const loadedLevel = await this.meshLevel.load();
            this.geographicCity=new GeographicCity(this.engine,this.groundSurfaces,this.streamingWork!);await this.geographicCity.load();
            // Grazing sunset light needs a small outward bias on the detailed facade.
            this.engine.scene?.traverse(object => {
                if (object instanceof THREE.DirectionalLight) {
                    object.shadow.bias = -0.0002;
                    object.shadow.normalBias = 0.18;
                }
            });
            // Desktop visual target: enable real shadows before materials compile.
            this.engine.renderer!.shadowMap.enabled = true;
            this.engine.renderer!.shadowMap.type = THREE.PCFShadowMap;
            const groundStart=performance.now();
            this.groundSurfaces.register(this.meshLevel.getRoot());
            console.info('[GroundSurfaceIndex] Static level ready',this.groundSurfaces.stats,`in ${(performance.now()-groundStart).toFixed(0)} ms`);
            this.focusedShadows = new AfterlightShadows(this.engine.scene!, this.meshLevel.getRoot(), (this.engine.renderer as unknown as {backend?:{device?:{limits?:{maxTextureDimension2D?:number}}}}).backend?.device?.limits?.maxTextureDimension2D ?? 8192);
            this.legacyLod=new CityLod(this.meshLevel.getRoot(),{key:m=>{
                const d=m.userData;if(!['shell','outside'].includes(d.visibilityKind))return null;
                return [d.geographicOwner,d.visibilityKind,d.visibilityZone,d.visibilityTower??''].join('/');
            },copyVisibility:true,facade:true});
            this.buildingVisibility = new BuildingVisibility(this.meshLevel.getRoot(),this.streamingWork);
            if(this.meshLevel.getExtras().streamedHotels){
                this.hotelStreaming=new HotelStreaming(this.engine,this.playerController!,this.hud,this.groundSurfaces,this.streamingWork,(yaw,pitch=0)=>{
                    this.cameraManager!.getFirstPersonCamera().setHorizontalAngle(yaw);
                    this.cameraManager!.getFirstPersonCamera().setVerticalAngle(pitch);
                });
                await this.hotelStreaming.load();
                this.doorKick=new DoorKick(this.playerController!,this.hotelStreaming);
            }
            const arrival = this.meshLevel.landmark('spawn');
            const spawnFloor = this.engine.physicsWorld!.raycast(
                new THREE.Vector3(arrival.position[0], arrival.position[1]+4, arrival.position[2]),
                new THREE.Vector3(0,-1,0), 6, CollisionGroup.TERRAIN | CollisionGroup.ENVIRONMENT);
            const spawnY = spawnFloor.hasHit && spawnFloor.hitNormal.y > .7 ? spawnFloor.hitPoint.y+.025 : arrival.position[1];
            this.playerController!.teleportTo(arrival.position[0], spawnY, arrival.position[2], arrival.yaw);
            this.playerController!.configureFallRescue({ ...DEFAULT_FALL_RESCUE_OPTIONS, killPlaneY: loadedLevel.bounds.minY - 30 });
            if (this.cameraManager?.getMode() === 'first-person') {
                const camera = this.cameraManager.getFirstPersonCamera();
                camera.setHorizontalAngle(-1.29);
                camera.setVerticalAngle(-0.40);
            }
            // Local review bookmarks keep remote architecture/door checks repeatable.
            if (['localhost', '127.0.0.1'].includes(location.hostname)) {
                // Also reachable as __afterlightProbe.inspect(name) (review and filming).
                const placeInspect=(shot:string|null):boolean=>{
                const positions: Record<string, [number, number, number]> = {
                    'bellagio-exterior': [-42, .25, -18],
                    'bellagio-door': [-134, .25, 34],
                    'bellagio-arrival-exterior': [-114, .25, 49],
                    'bellagio-arrival-vault': [-129, .25, 34],
                    'bellagio-gallery-exterior': [-118.8, .25, 34],
                    jeep: [-35, .25, 2.8],
                    'jeep-entry': [-40, .25, 6.4],
                    'forum-storefront': [-142, .25, -280],
                    caesars: [-50, .25, -242],
                    flamingo: [94, .25, -237],
                    horseshoe: [110, .25, -90],
                    'planet-hollywood': [95, .25, 218],
                    'planet-hollywood-exterior': [10, .25, 218],
                    'flamingo-exterior': [35, .25, -270],
                    'horseshoe-exterior': [42, .25, -153],
                    'miracle-mile': [174, .25, 250],
                    forum: [-119, .25, -262],
                    'forum-escalators': [-96.8, .25, -280],
                    'forum-upper': [-122, 6.5, -278],
                    'paris-shops': [120, .25, -39],
                    cosmopolitan: [-18, .25, 242],
                    'cosmopolitan-casino': [-35, .25, 242],
                    'cosmopolitan-service': [-185, .25, 242],
                    'citycenter-exterior': [10, .25, 516],
                    'crystals-exterior': [11, .25, 381],
                    'crystals-atrium': [-90, .25, 391],
                    'crystals-upper': [-105, 6.4, 452],
                    'veer-east-entry': [-123, .25, 453.4252],
                    'veer-west-entry': [-186, .25, 422.5748],
                    'veer-street-entry': [-93, .25, 480],
                    'veer-east-threshold': [-129.5, .25, 453.4252],
                    'veer-west-threshold': [-193.5, .25, 422.5748],
                    'aria-exterior': [-218, .25, 464],
                    'aria-casino': [-295, .25, 440],
                    'aria-ceiling': [-295, .25, 440],
                    'crystals-soffit': [-155, .25, 388],
                    'vdara-exterior': [-245, .25, 300],
                    'waldorf-exterior': [-15, .25, 615],
                    shadows: [-42, .25, 120],
                    'caesars-casino': [-98, .25, -242],
                    'caesars-service': [-158, .25, -250]
                };
                const position = shot ? positions[shot] : undefined;
                if (position) {
                    this.playerController!.teleportTo(...mapPoint(position,reviewDistrict(shot!)), Math.PI / 2);
                    const exteriorYaw: Record<string, number> = {
                        'bellagio-exterior': Math.PI / 2,
                        'bellagio-door': -Math.PI / 2,
                        'bellagio-arrival-exterior': .75,
                        'bellagio-arrival-vault': -Math.PI / 2,
                        'bellagio-gallery-exterior': Math.PI / 2,
                        jeep: 2.47,
                        'jeep-entry': Math.PI,
                        'forum-storefront': .3,
                        'planet-hollywood-exterior': -Math.PI / 2,
                        'flamingo-exterior': -1.87,
                        'horseshoe-exterior': -1.98,
                        'citycenter-exterior': 1.38,
                        'crystals-exterior': Math.PI / 2,
                        'crystals-atrium': 2.13,
                        'crystals-upper': .38,
                        'veer-east-entry': Math.PI / 2,
                        'veer-west-entry': Math.PI / 2,
                        'veer-street-entry': 0,
                        'aria-ceiling': 1.85,
                        'crystals-soffit': 1.99,
                        'aria-exterior': 1.21,
                        'vdara-exterior': 1.0,
                        'waldorf-exterior': 1.05
                    };
                    const reviewYaw = shot && exteriorYaw[shot] !== undefined ? exteriorYaw[shot]!
                        : shot === 'flamingo' || shot === 'planet-hollywood' ? -Math.PI / 2
                        : shot === 'horseshoe' || shot === 'miracle-mile' ? 0
                        : shot === 'forum-escalators' ? Math.PI
                        : shot === 'forum' ? .8 : Math.PI / 2;
                    this.cameraManager!.getFirstPersonCamera().setHorizontalAngle(mapYaw(reviewYaw,reviewDistrict(shot!)));
                    this.cameraManager!.getFirstPersonCamera().setVerticalAngle(shot === 'bellagio-arrival-vault' ? -.30 : shot === 'aria-ceiling' || shot === 'crystals-soffit' ? -.20 : shot?.endsWith('-exterior') ? -.29 : shot === 'caesars' || shot === 'cosmopolitan' ? -.22 : 0);
                }
                    return !!position;
                };
                this.placeInspect=placeInspect;placeInspect(new URLSearchParams(location.search).get('inspect'));
            }
            if(localLevelPreview){
                const view=new URLSearchParams(location.search).get('bridgeReview');
                const views:Record<string,[number,number,number,number]>={
                    bellagio:[-68.46,6.12,166,Math.PI],
                    door:[-68.44,6.12,172.1,Math.PI],
                    arcade:[-74,6.14,207.7,1.85],
                    escalators:[-47.95,6.14,199.8,Math.PI],
                    street:[-23,.22,222,Math.PI/2]
                };
                const p=view?views[view]:undefined;
                if(p){this.playerController!.teleportTo(p[0],p[1],p[2]);this.cameraManager!.getFirstPersonCamera().setHorizontalAngle(p[3]);this.cameraManager!.getFirstPersonCamera().setVerticalAngle(0);}
            }
            if(localLevelPreview){
                const view=new URLSearchParams(location.search).get('sphereReview');
                const point=view?this.geographicCity?.sphere.review(view):null;
                if(point){this.playerController!.teleportTo(point.position.x,point.position.y,point.position.z);this.cameraManager!.getFirstPersonCamera().setHorizontalAngle(point.yaw);this.cameraManager!.getFirstPersonCamera().setVerticalAngle(point.pitch);}
            }
            if(localLevelPreview){
                const q=new URLSearchParams(location.search),key=q.get('landmark');
                const point=key?(this.geographicCity?.resortBlocks.review(key,q.get('view')??'entrance')??this.geographicCity?.landmarks.review(key,q.get('view')??'entrance')):null;
                if(point){this.playerController!.teleportTo(point.position.x,point.position.y,point.position.z);this.cameraManager!.getFirstPersonCamera().setHorizontalAngle(point.yaw);this.cameraManager!.getFirstPersonCamera().setVerticalAngle(point.pitch);}
            }
            if(localLevelPreview && this.hotelStreaming){
                const q=new URLSearchParams(location.search),id=q.get('hotel');
                if(id){const p=await this.hotelStreaming.reviewPosition(id,Number(q.get('floor')??0),q.has('room')?Number(q.get('room')):null,q.get('roomView'));
                    if(p){this.playerController!.teleportTo(p.x,p.y,p.z);
                        this.cameraManager!.getFirstPersonCamera().setHorizontalAngle(p.yaw+(q.has('hotelLobby')?Math.PI:0));
                        this.cameraManager!.getFirstPersonCamera().setVerticalAngle(q.has('hotelLobby')?-.15:0);}}
            }
            if(localLevelPreview && new URLSearchParams(location.search).has('resortReview') && this.geographicCity){
                const visit=(key:string,view:string)=>{const p=this.geographicCity!.resortBlocks.review(key,view);if(!p)return;
                    this.streamingWork!.enqueue('resort-review',key,()=>{this.playerController!.teleportTo(p.position.x,p.position.y,p.position.z);if(this.cameraManager!.getMode()!=='first-person')this.toggleView();this.cameraManager!.getFirstPersonCamera().setHorizontalAngle(p.yaw);this.cameraManager!.getFirstPersonCamera().setVerticalAngle(p.pitch);});};
                this.resortReview=new ResortBlockReview(this.engine,this.geographicCity.resortBlocks,visit,()=>this.player!.position,()=>!!this.streamingWork?.busy,()=>this.sanctuaryJeep?.placeForGarageReview());
                visit(new URLSearchParams(location.search).get('landmark')??'cosmo','entrance');
            }
            this.geographicCity?.update(this.player!.position,true);
            this.parisLift = new ParisLift(this.playerController!, this.hud);
            // Stand-in lights for close, moving objects (the jeep, the player, a game's characters; see NearbyLights).
            this.nearbyLights=new NearbyLights(this.engine.scene!,this.engine.renderer as unknown as ConstructorParameters<typeof NearbyLights>[1]);
            this.sanctuaryJeep = new SanctuaryJeep(this.engine, this.vehicleManager, this.vehicleSpawner, this.playerController!, this.hud,
                { height: this.playerLoader.getCapsuleHeight(), radius: this.playerLoader.getCapsuleRadius() }, () => this.restoreWalkingCamera());
            await this.sanctuaryJeep.load();
            for(const root of this.sanctuaryJeep.lightRoots)this.nearbyLights.apply(root);
            for(const child of this.engine.scene!.children)if(child.name==='HeadlessPlayer')this.nearbyLights.apply(child);
            if(this.player)this.nearbyLights.apply(this.player);
            // A game built on the city adds itself here (GameLayers.ts); the city has none.
            const city:CityContext={engine:this.engine,player:this.player!,playerController:this.playerController!,hud:this.hud,
                groundSurfaces:this.groundSurfaces,nearbyLights:this.nearbyLights,vehicleManager:this.vehicleManager,
                playerViewHidesBody:()=>!!this.bigAppleCoaster?.riding||this.cameraManager?.getMode()==='first-person'||!!this.playerController?.isPlayerInVehicle(),
                sprinting:()=>!!this.playerController?.keys.sprint,grounded:()=>!!this.playerController?.isGrounded,
                verticalVelocity:()=>this.playerLoader.getPlayerBody()?.linvel().y??0};
            for(const make of GAME_LAYERS){const layer=await make();await layer.load(city);this.layers.push(layer);}
            this.bigAppleCoaster = new BigAppleCoaster(this.engine,this.playerController!,this.player!,this.hud,this.groundSurfaces,()=>this.restoreWalkingCamera());
            await this.bigAppleCoaster.load();
            if(localLevelPreview){const mode=new URLSearchParams(location.search).get('coasterReview');const point=mode?this.bigAppleCoaster.reviewPosition(mode):null;if(point)this.playerController!.teleportTo(point.x,point.y,point.z);}
            this.detailRanges=new CityDetailRanges(this.engine.scene!,cityEntranceDetails(this.engine.scene!));
            this.detailRanges.watchDoorParent(this.engine.getWorldGroup());
            // Local review probe (?probe): lets tools/probe-streaming.mjs move the player along a route and read what the streaming queue did. Never on a published page.
            // Local filming (tools/film): localStorage 'afterlight:film' = '1' turns on the probe and the film director.
            let filming=false;try{filming=localLevelPreview&&(stormDrivingEnabled()||localStorage.getItem('afterlight:film')==='1'||new URLSearchParams(location.search).get('film')==='1');}catch{/* no storage */}
            if(localLevelPreview && (filming||new URLSearchParams(location.search).has('probe')))(window as unknown as {__afterlightProbe?:unknown}).__afterlightProbe={
                teleport:(x:number,y:number,z:number)=>this.playerController!.teleportTo(x,y,z),
                position:()=>({x:this.player!.position.x,y:this.player!.position.y,z:this.player!.position.z}),
                streaming:()=>({busy:!!this.streamingWork?.busy,history:this.streamingWork?.history??[]}),
                inVehicle:()=>!!this.playerController?.isPlayerInVehicle(),
                renderer:()=>this.engine.renderer,
                passing:()=>({passing:this.passingDetector.passing,speed:this.passingDetector.metresPerSecond}),
                seatJeep:(x:number,y:number,z:number,heading:number)=>this.sanctuaryJeep?.seatForReview(x,y,z,heading)??false,
                jeep:()=>{const v=this.playerController?.getActiveVehicle();if(!v)return null;const p=v.getPosition(),f=v.getForwardDirection();return {x:p.x,y:p.y,z:p.z,fx:f.x,fy:f.y,fz:f.z,speed:v.getSpeed() as number};},
                engine:()=>this.engine,
                // Fixed first-person views for repeatable A/B captures (yaw/pitch in radians).
                look:(yaw:number,pitch:number)=>{if(this.cameraManager!.getMode()!=='first-person')this.toggleView();const c=this.cameraManager!.getFirstPersonCamera();c.setHorizontalAngle(yaw);c.setVerticalAngle(pitch);},
                /** A fixed light list for material experiments (TSL `lights`). */
                lightsNode:(list:THREE.Light[])=>lightsNode(list),
                inspect:(name:string)=>this.placeInspect?.(name)??false,
                /** Closed hotel room doors near the player (with a corridor-side kicking spot) and a kick from where the player stands. */
                kickDoors:()=>this.hotelStreaming?.kickableDoors()??[],
                kick:()=>{if(this.engine.camera&&this.player)this.doorKick?.kick(this.engine.camera,this.player.position);},
                // Same placement as the ?landmark= review URL (views: entrance, lobby, skyline, ...).
                landmark:(key:string,view:string)=>{const point=this.geographicCity?.resortBlocks.review(key,view)??this.geographicCity?.landmarks.review(key,view);if(!point)return null;this.playerController!.teleportTo(point.position.x,point.position.y,point.position.z);if(this.cameraManager!.getMode()!=='first-person')this.toggleView();const c=this.cameraManager!.getFirstPersonCamera();c.setHorizontalAngle(point.yaw);c.setVerticalAngle(point.pitch);return {x:point.position.x,y:point.position.y,z:point.position.z};},
                // Same placement as the ?hotel= review URL, without a reload (stair: room and view null).
                hotel:async(id:string,floor:number,room:number|null,roomView:string|null)=>{const p=await this.hotelStreaming?.reviewPosition(id,floor,room,roomView);if(!p)return null;this.playerController!.teleportTo(p.x,p.y,p.z);if(this.cameraManager!.getMode()!=='first-person')this.toggleView();const c=this.cameraManager!.getFirstPersonCamera();c.setHorizontalAngle(p.yaw);c.setVerticalAngle(0);return p;},
                resident:()=>({landmarks:this.geographicCity?.landmarks.stats.residentInteriors??[],resorts:this.geographicCity?.resortBlocks.stats.residentInteriors??[],guest:this.hotelStreaming?.stats??null,interiorBatches:this.buildingVisibility?.stats.enabledInteriorBatches??0}),
            };
            if(filming){
                const probe=(window as unknown as {__afterlightProbe:Record<string,(...a:never[])=>unknown>}).__afterlightProbe;
                const {Film}=await import('./film/Film.js');
                const {FilmLook}=await import('./film/FilmLook.js');
                this.filmLook=new FilmLook(this.engine as import('engine/GameEngine.js').GameEngine,this.groundSurfaces);
                this.film=new Film({
                    // a take with a scenario needs a game layer that provides it (GameLayers.ts filmReady); the city has looks only
                    scenarioLoad:scenario=>this.filmScenario?.scenarioLoad?.(scenario)??(scenario?Promise.reject(Error('No game layer provides film scenarios')):Promise.resolve()),
                    lookLoad:look=>this.filmLook!.look(look??null),
                    scenarioUpdate:(t,dt)=>this.filmScenario?.scenarioUpdate?.(t,dt),
                    engine:this.engine as unknown as {camera:THREE.PerspectiveCamera|null},
                    teleport:(x,y,z)=>this.playerController!.teleportTo(x,y,z),
                    position:()=>({x:this.player!.position.x,y:this.player!.position.y,z:this.player!.position.z}),
                    streamingBusy:()=>!!this.streamingWork?.busy,
                    // film pitch is positive up; the first-person camera's vertical angle is positive down
                    look:(yaw,pitch)=>{const c=this.cameraManager!.getFirstPersonCamera();c.setHorizontalAngle(yaw);c.setVerticalAngle(-pitch);},
                    view:mode=>{if((this.cameraManager?.getMode()==='first-person')!==(mode==='first'))this.toggleView();},
                    firstPerson:()=>this.cameraManager?.getMode()==='first-person',
                    jeep:()=>this.filmScenario?.jeepPose?.()??(probe.jeep as ()=>{x:number;y:number;z:number;fx:number;fy:number;fz:number;speed:number}|null)(),
                    // Analog throttle and brake for the film's drives: the player path only passes RT/A as booleans, and a
                    // speed held by pulsing full power rocked the chassis about twice a second (the owner: "as if there was a
                    // flat tire"). The vehicle takes analog values (VehicleControls.throttle / brakeAmount); they are merged
                    // into the controls the player path hands it, into one reused object.
                    hotelPin:(id,floor,bay,side)=>this.hotelStreaming?.filmPin(id,floor,bay,side)??Promise.resolve(false),
                    hotelDoors:(camera,forward,speed)=>{this.hotelStreaming?.filmDoors(camera,forward,speed);this.geographicCity?.landmarks.filmDoors(camera,forward,speed);},
                    vehicleInput:(throttle,brake)=>{
                        const film=this.filmVehicle;film.active=throttle!==null;film.throttle=throttle??0;film.brake=brake;
                        const v=this.playerController?.getActiveVehicle() as unknown as {updateControls?:(c:Record<string,unknown>,dt?:number)=>void}|null;
                        if(!v?.updateControls||film.patched.has(v))return;
                        film.patched.add(v);const original=v.updateControls.bind(v),merged:Record<string,unknown>={};
                        v.updateControls=(c,dt)=>{
                            if(!film.active){original(c,dt);return;}
                            for(const k in merged)delete merged[k];
                            Object.assign(merged,c);merged.throttle=film.throttle;merged.brakeAmount=film.brake;merged.forward=false;merged.brake=false;
                            original(merged,dt);
                        };
                    },
                    seatJeep:(x,y,z,heading)=>this.sanctuaryJeep?.seatForReview(x,y,z,heading)??false,
                    inVehicle:()=>!!this.playerController?.isPlayerInVehicle(),
                    exitVehicle:()=>{this.playerController?.exitVehicle();},
                    inspect:name=>this.placeInspect?.(name)??false,
                    landmark:(key,view)=>(probe.landmark as (k:string,v:string)=>unknown)(key,view),
                    hotel:(id,floor,room,view)=>(probe.hotel as (i:string,f:number,r:number|null,v:string|null)=>Promise<unknown>)(id,floor,room,view),
                    kickDoors:()=>this.hotelStreaming?.kickableDoors()??[],
                    prepareRoom:label=>this.hotelStreaming?.prepareRoom(label)??false,
                    kick:()=>{if(this.engine.camera&&this.player)this.doorKick?.kick(this.engine.camera,this.player.position);},
                    coasterRiding:()=>!!this.bigAppleCoaster?.riding,
                    rayDistance:(ox,oy,oz,dx,dy,dz,max)=>{const r=this.engine.physicsWorld?.raycast(new THREE.Vector3(ox,oy,oz),new THREE.Vector3(dx,dy,dz),max,CollisionGroup.TERRAIN|CollisionGroup.ENVIRONMENT);return r?.hasHit?r.hitDistance:max;},
                    // Motion-blur sub-frames: the engine's frame timer and physics step are private, so they are reached
                    // by name (engine 3.1337: GameEngine.frameLoop.timer / forceFixedDeltaTime, PhysicsWorld.FIXED_TIMESTEP).
                    // The recorder pins forceFixedDeltaTime (1/60) and BackgroundActivity restores it after every frame, so
                    // while sub-frames run the flag reads false (writes are kept for the restore).
                    stepping:(n)=>{
                        const e=this.engine as unknown as Record<string,unknown>&{frameLoop:{timer:Record<string,unknown>&{_ambienceTime:number}};physicsWorld?:Record<string,unknown>};
                        const timer=e.frameLoop.timer,physics=e.physicsWorld;
                        if(n>1){
                            const step=1/(60*n);
                            if(timer.subframeStep!==step){
                                timer.subframeStep=step;timer.tick=function(this:{_ambienceTime:number}){this._ambienceTime+=step;return step;};
                                let pinned=!!e.forceFixedDeltaTime;
                                Object.defineProperty(e,'forceFixedDeltaTime',{configurable:true,enumerable:true,get:()=>false,set:(v:boolean)=>{pinned=v;}});
                                e.subframeRestore=()=>{delete e.forceFixedDeltaTime;e.forceFixedDeltaTime=pinned;};
                            }
                            if(physics)physics.FIXED_TIMESTEP=step;
                        }else if(timer.subframeStep){
                            delete timer.tick;delete timer.subframeStep;(e.subframeRestore as ()=>void)();delete e.subframeRestore;
                            if(physics)physics.FIXED_TIMESTEP=1/60;
                        }
                    },
                    coaster:elapsed=>this.bigAppleCoaster?.film(elapsed),
                    coasterPose:(position,orientation)=>this.bigAppleCoaster?.filmPose(position,orientation)??false,
                    venuePin:keys=>this.geographicCity?.landmarks.filmPin(keys)??Promise.resolve(),
                    fullDetail:on=>{const capture=on&&!stormDrivingEnabled();filmDetail.full=capture;this.focusedShadows?.film(capture?320:null);this.filmAmbientOcclusion(capture);},
                });
                (window as unknown as {__afterlightFilm?:unknown}).__afterlightFilm=this.film;
                for(const layer of this.layers){const provided=await layer.filmReady?.({film:this.film,look:this.filmLook});if(provided)this.filmScenario={...this.filmScenario,...provided};}
                console.info('[film] director ready');
            }
            this.performancePanel=new PerformancePanel(this.engine,()=>({
                publicInteriors:[...(this.geographicCity?.landmarks.stats.residentInteriors??[]),...(this.geographicCity?.resortBlocks.stats.residentInteriors??[]),...(this.geographicCity?.sphere.stats.interior?['sphere']:[])],
                guest:this.hotelStreaming?.stats??{stairs:0,corridors:0,rooms:0},
                cityCells:this.geographicCity?.stats.residentCells??0,
                loading:!!this.streamingWork?.busy,
                legacyInteriorBatches:this.buildingVisibility?.stats.enabledInteriorBatches??0,
            }),(from,to)=>this.streamingWork?.activitySince(from,to)??null);
            this.hud.createActionRow('camera-view', { anchor: 'bottom-center', controls: [{ id: 'view', label: 'Switch view · V', onSelect: () => this.toggleView() }] });

            // Enable player gravity NOW that terrain is fully loaded
            // Physics won't actually step until GameState becomes PLAYING (on Play button click)
            this.playerLoader.enablePlayerGravity();

            console.log('✅ Game loaded - waiting for Play button');

            // Show the HUD
            this.hud.show();

            // VegasCharacter owns the supplied native clips; no template retargeting.

            console.log('Voxel game loaded successfully');
        } catch (error) {
            console.error('Failed to load Voxel game:', error);
            throw error;
        }
    }

    /** Complete the scene/camera switch under the loading panel, before its
     * first GPU frame. The regular update loop is held during preparation. */
    private refreshStreamingView():void {
        if(!this.player || !this.engine.camera || !this.meshLevel)return;
        if(!this.bigAppleCoaster?.riding&&!this.playerController?.handlesPlayerPositionSync())this.syncPlayerPhysics();
        this.hotelStreaming?.update(0,this.player.position,true);
        if(!this.bigAppleCoaster?.riding)this.playerController?.getCameraController()?.update(1/60);
        this.updateInteriorVisibility();
    }
    /** Where interiors stream and visibility is decided: the player, or during a film camera run the camera itself
     * (Film.focus), so a camera flying ahead of the player sees the lobby, stairs, corridor and room it flies through. */
    private streamFocus():THREE.Vector3{return this.film?.focus()??this.player!.position;}
    private updateInteriorVisibility():void {
        if(!this.player || !this.engine.camera || !this.meshLevel)return;
        const focus=this.streamFocus();
        // (a film camera run counts as passing: only pinned venues load their interiors, so nothing holds the take)
        const passing=this.passingDetector.passing||!!this.film?.focus();this.buildingVisibility?.setPassing(passing);this.geographicCity?.setPassing(passing);
        const hotelView=this.hotelStreaming?.getView(focus,this.engine.camera.position)??null;
        const interiorView=this.geographicCity?.sphere.getView(focus,this.engine.camera.position)??hotelView??this.geographicCity?.resortBlocks.getView(focus,this.engine.camera.position)??this.geographicCity?.landmarks.getView(focus,this.engine.camera.position)??null;
        this.buildingVisibility?.update(focus,this.engine.camera.position,
            id=>this.engine.getDoorSystem?.()?.getDoorState(id)??null,this.meshLevel.getLights(),interiorView);
        // inside: the overhead key light grounds furniture with contact shadows (InteriorKeyLight.ts)
        interiorKey.update(this.engine.camera,!!interiorView,INTERIOR_KEY_INTENSITY);
        // (a film camera that has just flown out of a room window is still inside the tower's exterior shell: Film.hide)
        this.geographicCity?.update(focus,this.buildingVisibility?.rendersOutside??true,hotelView?.hideTower??this.film?.hide()??undefined,!!hotelView?.hideTower);
        this.bigAppleCoaster?.setOutsideVisibility(this.buildingVisibility?.rendersOutside??true);
        // (filming: the wide film region sits half its reach ahead of the camera, so shadows run far down the view; an aerial
        // camera sees kilometres of city, so the region grows with its height, ±320 m at street level to ±2400 m, in 40 m steps)
        if(this.focusedShadows?.filmReach&&this.film?.focus())this.focusedShadows.film(Math.min(2400,Math.max(320,Math.round(this.engine.camera.position.y*5/40)*40)));
        const reach=this.focusedShadows?.filmReach;
        if(reach&&this.film?.focus()){this.engine.camera.getWorldDirection(this.shadowAhead);this.shadowAhead.y=0;this.shadowAhead.normalize().multiplyScalar(reach*.5).add(focus);}
        this.focusedShadows?.update(reach&&this.film?.focus()?this.shadowAhead:focus,this.buildingVisibility?.rendersOutside??true);
        this.sanctuaryJeep?.setRenderVisibility(this.visibleTest);
        for(const layer of this.layers)layer.setRenderVisibility?.(this.visibleTest);
    }

    /** Local filming: screen-space ambient occlusion (the engine's GTAO pass) for the takes only. It grounds furniture and
     * shapes reliefs, corners and street furniture, but costs ~12 ms of GPU at 3010x1544, so play keeps it off. GTAO's scale
     * is a power on the occlusion: 2 is what makes a bed, a slot bank or a column base visibly sit on the floor. */
    private filmAo=false;
    private filmAmbientOcclusion(on:boolean):void{
        if(on===this.filmAo)return;this.filmAo=on;
        // (engine 3.1337: the AO config lives on the engine's private post-FX owner, engine/core/PostFxPipeline.ts)
        (this.engine as unknown as {postFx:{applyAoConfig(c:{enabled:boolean;intensity?:number;radius?:number;scale?:number}):void}}).postFx.applyAoConfig(on?{enabled:true,intensity:1,radius:.8,scale:2}:{enabled:false});
    }

    private toggleView(): void {
        if (!this.cameraManager || !this.playerController || this.playerController.isPlayerInVehicle() || this.bigAppleCoaster?.riding) return;
        this.cameraManager.setMode(this.cameraManager.getMode() === 'first-person' ? 'third-person' : 'first-person');
        this.restoreWalkingCamera();
    }

    private restoreWalkingCamera(): void {
        if (!this.cameraManager || !this.playerController) return;
        const controller = this.cameraManager.getActiveController()!;
        this.playerController.setCameraController(controller);
        // Update the vehicle helper too; setCameraController only refreshes the parent reference.
        this.playerController.setVehicleManager(this.vehicleManager);
        if (this.cameraManager.getMode() === 'third-person') {
            // Lift the framing axis so the character occupies the lower half.
            this.cameraManager.getThirdPersonCamera().setShoulderOffset(0, .85);
        }
        // Switching controllers does not emit pointerlockchange. Transfer the
        // existing lock now so the newly created orbit camera receives mouse look.
        const lockElement = document.pointerLockElement;
        const locked = !!lockElement && (lockElement === this.engine.renderer!.domElement || lockElement.contains(this.engine.renderer!.domElement));
        // Embedded previews may not grant pointer lock; keep drag-to-orbit there.
        controller.setEditorModeCamera(!locked);
        controller.setPointerLocked(locked);
    }

    private setupCamera(): void {
        if (this.engine.camera && this.engine.renderer) {
            // Read camera mode from configuration, default to third-person
            const cameraMode = this.worldProfileData.cameraMode || 'third-person';
            
            // Create CameraManager with configured camera mode
            this.cameraManager = new CameraManager(
                this.engine.getDefaultCamera(),
                this.player!,
                this.engine.renderer.domElement,
                this.engine,
                cameraMode
            );

            // Get reference to the active camera controller (could be ThirdPerson, FirstPerson, or TopDown)
            // Fall back to ThirdPersonCamera for backward compatibility if no active controller
            this.cameraController = (this.cameraManager.getActiveController() as ThirdPersonCamera) 
                ?? this.cameraManager.getThirdPersonCamera();
        }
    }

    /**
     * Soft sky/ground fill for the exterior mesh level. MeshLevel exterior mode
     * does not create the hemisphere used by its interior preset.
     */
    private setupVoxelLighting(): void {
        if (!this.engine.scene) return;

        // Empty-3D override: neutral hemisphere light so the clean blue
        // background isn't tinted yellow. Baseline default is warm golden /
        // dark blue (sunset feel) which clashes with the solid-blue sky.
        this.hemisphereLight = new THREE.HemisphereLight(
            0xc5d7ed,  // Cool open-sky fill in sun shadows
            0x88745f,  // Desert/paving bounce
            1.15
        );
        this.engine.scene.add(this.hemisphereLight);

        console.log('✨ Voxel lighting setup complete');
    }

    /**
     * Get the hemisphere light for runtime adjustments.
     * 
     * Use this to adjust ambient lighting based on location (outdoors vs dungeon):
     * ```typescript
     * const hemi = game.getHemisphereLight();
     * if (hemi) {
     *     hemi.color.setHex(0xffeeb1);      // Sky color (surfaces facing up)
     *     hemi.groundColor.setHex(0x101010); // Ground color (surfaces facing down)
     *     hemi.intensity = 0.3;              // Overall intensity
     * }
     * ```
     */
    getHemisphereLight(): THREE.HemisphereLight | null {
        return this.hemisphereLight;
    }

    private async setupPlayerController(): Promise<void> {
        const playerBody = this.playerLoader.getPlayerBody();
        if (!playerBody) {
            throw new Error('Player physics body not created');
        }

        if (!this.engine.physicsWorld) {
            throw new Error('Physics world not initialized');
        }

        console.log('🎮 VoxelGame: Using VoxelPlayerController');
        this.playerController = new VoxelPlayerController(
            this.player!,
            playerBody,
            this.engine.physicsWorld,
            this.cameraController!,
            this.engine,
            DEFAULT_PHYSICS,
            this.worldGenerator,
            undefined, // movementSystem
            CONSTANTS
        );

        // Register playerController with engine for debug systems (NpcManager projectile detection)
        this.engine.registerPlayerController(this.playerController);

        // Use a walking pace normally and the configured run pace with Shift.
        const charConfig = mergeCharacterConfig(this.worldProfileData.characterConfig);
        this.walkingSpeed = 2;
        this.runningSpeed = charConfig.runSpeed;
        this.playerController.getMovementSystem().setMoveSpeed(this.walkingSpeed);
        this.playerController.registerCustomAction({
            action: 'sprint',
            desktop: { keys: ['ShiftLeft', 'ShiftRight'] },
            mobile: { label: 'RUN', behavior: 'continuous' }
        });

        this.playerController.registerCustomAction({ action: 'toggleView', desktop: { keys: ['KeyV'] }, mobile: { label: 'VIEW', behavior: 'tap' } });

        // Set the calculated capsule dimensions for accurate ground detection
        const capsuleHeight = this.playerLoader.getCapsuleHeight();
        const capsuleRadius = this.playerLoader.getCapsuleRadius();
        if (this.playerController) {
            this.playerController.setCapsuleDimensions(capsuleHeight, capsuleRadius);
            // Set voxel block size for step climbing (player + all dynamic objects)
            if (this.worldGenerator) {
                const voxelBlockSize = this.worldGenerator.getVoxelBlockSize();
                this.playerController.voxelBlockSize = voxelBlockSize;
                // Set for all dynamic objects (animals, NPCs) - both existing and future
                const dynamicObjectManager = this.engine.getDynamicObjectManager?.();
                if (dynamicObjectManager) {
                    dynamicObjectManager.setVoxelBlockSize(voxelBlockSize);
                }
            }
        }

        // Connect animation controller to player controller
        const animationController = this.playerLoader.getAnimationController();
        if (this.playerController) {
            this.playerController.setAnimationController(animationController);
        }

        // Connect PlayerLoader to PlayerController for character switching
        if (this.playerController) {
            this.playerController.setPlayerLoader(this.playerLoader);
        }

        // Connect vehicle manager to player controller
        this.playerController.setVehicleManager(this.vehicleManager);

        // Set up callback for when player object changes (for character switching)
        if (this.playerController) {
            this.playerController.setOnPlayerChangedCallback((newPlayer: THREE.Object3D) => {
                this.player = newPlayer;

                // Enable bloom effect on new player if configured
                this.engine.enableBloomOnObject?.(newPlayer);

                // Update camera target to follow new player
                if (this.cameraController) {
                    this.cameraController.setTarget(newPlayer);
                }

                console.log('VoxelGame: Player object and camera target updated for character switching');
            });
        }

        // Connect DebugController to Game for debug features (F8 animations, etc.)
        if (this.debugController) {
            this.debugController.setGame(this);
        }

        // Apply character modifications now that PlayerController is ready
        // The native metre-scale GLB uses the headless capsule, not the 1.3 m
        // mascot's scaling/physics hook. Still notify attachment subscribers.
        this.playerController.fireCharacterReady();

        // Connect HUD to PlayerController for dynamic control display
        this.hud.setPlayerController(this.playerController);
        // Set HUD reference on PlayerController so it can show controls when movement system changes
        this.playerController.hud = this.hud;
    }

    private async loadCustomAnimations(): Promise<void> {
        try {
            const animController = this.playerLoader.getAnimationController();
            if (!animController) {
                console.warn('No animation controller found');
                return;
            }
            await animController.loadAllAnimationAssets({ normalizeRootMotion: true, loop: false });
        } catch (error) {
            console.error('Failed to load custom animations:', error);
        }
    }

    public getAnimationController(): any {
        return this.playerLoader.getAnimationController();
    }

    update(deltaTime: number): void {
        const metricsStart=performance.now();
        try {
        sweepUploadedGeometry(this.engine.renderer as unknown as {backend:unknown});
        if(this.player)this.nearbyLights?.update(this.player.position);
        this.resortReview?.update();
        // (while streaming holds the game, a film take keeps its own camera: the player's view must never flash into a take)
        if(this.streamingWork?.busy){this.film?.applyCamera();return;}
        this.film?.update(deltaTime);
        for(const layer of this.layers)layer.tick?.(deltaTime);
        // Process deferred terrain chunks and foliage before gameplay starts.
        // Ensures all terrain is fully built before the player can see it.
        // Comment out for games with a tunnel/corridor start where terrain
        // can build progressively in the background while the player is hidden.
        const vt = this.worldGenerator?.getVoxelTerrainSystem();
        if (vt?.hasDeferredWork) {
            vt.processDeferredWork();
            return;
        }

        const profileFrame=updateProfile.start();
        let profilePart=profileFrame;
        // Track elapsed time for animated textures
        this.elapsedTime += deltaTime;

        if (this.playerController) {
            if (!this.playerController.isPlayerInVehicle()) {
                this.playerController.getMovementSystem().setMoveSpeed(
                    this.parisLift?.traveling ? 0 : (this.playerController.keys.sprint ? this.runningSpeed : this.walkingSpeed)
                );
            }
            if(!this.bigAppleCoaster?.riding)this.playerController.update(deltaTime);
        }

        updateProfile.end('player controller',profilePart);profilePart=updateProfile.start();
        const view = !!this.playerController?.keys.toggleView;
        if (view && !this.viewHeld) this.toggleView();
        this.viewHeld = view;

        // Update vehicles
        this.vehicleManager.update();

        // Update block character animation if present
        this.playerLoader.updateBlockCharacter();

        // Update Bitmagic eye blinking animation
        updateBitmagicEyeBlink(deltaTime);

        // Update voxel terrain animated textures (e.g., lava) and visibility culling
        if (this.worldGenerator) {
            const voxelTerrain = this.worldGenerator.getVoxelTerrainSystem();
            if (voxelTerrain) {
                voxelTerrain.update(this.elapsedTime);

                // Disable frustum culling during recording — the recording camera has a different
                // aspect ratio than the editor camera, so the frustum doesn't match and chunks
                // outside the editor frustum (but inside the recording frustum) get hidden.
                const isRecording = this.engine.isRecordingFrames?.() ?? false;
                if (isRecording && !this.wasRecordingFrames) {
                    this.cullingWasEnabledBeforeRecording = voxelTerrain.isCullingEnabled();
                    voxelTerrain.setCullingEnabled(false);
                    const envSys = this.worldGenerator.getEnvironmentObjectSystem();
                    if (envSys) {
                        this.envCullingWasEnabledBeforeRecording = envSys.isCullingEnabled();
                        envSys.setCullingEnabled(false);
                    }
                } else if (!isRecording && this.wasRecordingFrames) {
                    if (this.cullingWasEnabledBeforeRecording) {
                        voxelTerrain.setCullingEnabled(true);
                    }
                    const envSys = this.worldGenerator.getEnvironmentObjectSystem();
                    if (envSys && this.envCullingWasEnabledBeforeRecording) {
                        envSys.setCullingEnabled(true);
                    }
                }
                this.wasRecordingFrames = isRecording;

                if (this.engine.camera && !isRecording) {
                    voxelTerrain.updateVisibility(this.engine.camera, this.player?.position);
                }

                // Progressive chunk building for large worlds (lazy generation)
                // Builds 1 chunk per frame as player explores beyond initial radius
                if (this.player && !voxelTerrain.isLazyGenerationComplete()) {
                    voxelTerrain.buildPendingChunksNear(
                        this.player.position.x,
                        this.player.position.z,
                        1,  // Build 1 chunk per frame (~8ms overhead)
                        200 // Only build chunks within 200m of player
                    );
                }
            }

            // Per-frame LOD selection for baked chunked-VXL worlds (the
            // voxelize-as-level path). Drop-in alternative to the
            // chunk-grid `voxelTerrain` block above — only one of the two
            // systems is non-null per world. Without this call the level
            // still renders at LOD 0 (default-visible), but distance-based
            // LOD switching wouldn't happen.
            const vxlChunked = this.worldGenerator.getVxlChunkedTerrain();
            if (vxlChunked) {
                vxlChunked.update(this.elapsedTime);
                const isRecording = this.engine.isRecordingFrames?.() ?? false;
                if (this.engine.camera && !isRecording) {
                    vxlChunked.updateVisibility(this.engine.camera, this.player?.position);
                }
            }

            // Update foliage debris physics
            const foliageSystem = this.worldGenerator.getFoliageSystem();
            if (foliageSystem) {
                foliageSystem.updateDebris(deltaTime);
            }

            // Update environment object visibility culling (trees, rocks, buildings)
            const envSystem = this.worldGenerator.getEnvironmentObjectSystem();
            if (envSystem && this.engine.camera && !(this.engine.isRecordingFrames?.() ?? false)) {
                envSystem.updateVisibility(this.engine.camera);
            }
        }

        updateProfile.end('world / vehicles',profilePart);profilePart=updateProfile.start();
        // Only sync player physics from body when the movement system doesn't handle it.
        // Ski and vehicle movement systems sync player position themselves;
        // running syncPlayerPhysics would overwrite their position causing visual twitching.
        if (!this.bigAppleCoaster?.riding && !this.playerController?.handlesPlayerPositionSync()) {
            this.syncPlayerPhysics();
        }

        if (this.player) {
            this.parisLift?.update(deltaTime, this.player);
            this.sanctuaryJeep?.update(deltaTime, this.player.position);
            this.hotelStreaming?.update(deltaTime,this.streamFocus());
        }
        updateProfile.end('hotel / activities',profilePart);profilePart=updateProfile.start();
        // Sample displacement after physics/lift synchronization, not last frame's pose.
        if(this.player)for(const layer of this.layers)layer.update(deltaTime,this.player);

        updateProfile.end('characters total',profilePart);profilePart=updateProfile.start();
        // Let PlayerController handle camera updates (supports vehicle camera switching)
        if (!this.bigAppleCoaster?.riding && this.playerController && this.playerController.getCameraController) {
            const activeCamera = this.playerController.getCameraController();
            if (activeCamera && activeCamera.update) {
                activeCamera.update(deltaTime);
            }
        } else if (!this.bigAppleCoaster?.riding && this.cameraController) {
            // Fallback to direct camera update
            this.cameraController.update(deltaTime);
        }

        if(!this.bigAppleCoaster?.riding && this.cameraManager?.getMode()==='third-person' && !this.playerController?.isPlayerInVehicle() && this.player && this.engine.camera && this.engine.physicsWorld)
            this.cameraObstruction.update(this.engine.camera,this.player.position,this.engine.physicsWorld);
        this.doorKick?.update(deltaTime,this.engine.camera??null,this.player?.position??null,this.cameraManager?.getMode()==='first-person',
            !!this.bigAppleCoaster?.riding||!!this.parisLift?.traveling||!!this.playerController?.isPlayerInVehicle());
        this.bigAppleCoaster?.update(deltaTime);
        updateProfile.end('camera',profilePart);profilePart=updateProfile.start();
        if(this.player)this.passingDetector.update(this.player.position.x,this.player.position.z,performance.now(),!!this.playerController?.isPlayerInVehicle());
        // the film camera is posed before visibility is decided: what the take sees (the coaster's train within 300 m of the
        // camera, a building's interior) is judged from the film's camera, not the player's
        this.film?.applyCamera();
        this.updateInteriorVisibility();
        this.filmLook?.render(deltaTime);
        for(const layer of this.layers)layer.render?.(deltaTime);
        updateProfile.end('visibility / shadows',profilePart);
        updateProfile.end('total update',profileFrame);updateProfile.frame(deltaTime);
        } finally {this.performancePanel?.recordUpdate(performance.now()-metricsStart);}
    }

    private syncPlayerPhysics(): void {
        const playerBody = this.playerLoader.getPlayerBody();
        if (!playerBody || !this.player) return;

        // Use Rapier translation for position syncing
        const pos = playerBody.translation();

        const capsuleHeight = this.playerLoader.getCapsuleHeight();
        const halfHeight = capsuleHeight / 2;

        // Position the visual player so its feet align with the physics capsule bottom
        // Physics capsule center is at pos.y, so capsule bottom is at pos.y - halfHeight
        // For block characters, there's an offset from playerGroup origin to the actual feet
        const capsuleBottom = pos.y - halfHeight;
        const feetOffsetY = this.playerLoader.getFeetOffsetY();
        const playerGroupY = capsuleBottom - feetOffsetY;
        this.player.position.set(pos.x, playerGroupY, pos.z);

        if (this.playerController) {
            this.player.rotation.y = this.playerController.rotation;
        }
    }

    dispose(): void {
        for(const layer of this.layers)layer.dispose();this.layers=[];this.film?.release();this.filmLook?.reset();
        this.releaseWaterFrame?.();this.releaseWaterFrame=null;
        this.performancePanel?.dispose();this.performancePanel=null;
        this.detailRanges?.dispose();this.detailRanges=null;
        this.resortReview?.dispose();this.resortReview=null;
        this.releaseAtmosphere?.();this.releaseAtmosphere=null;
        this.backgroundActivity?.dispose();this.backgroundActivity=null;
        this.streamingWork?.dispose();this.streamingWork=null;
        updateProfile.dispose();
        this.hotelStreaming?.dispose();
        this.bigAppleCoaster?.dispose();
        this.sanctuaryJeep?.dispose();
        this.buildingVisibility?.dispose();
        this.focusedShadows?.dispose();
        this.geographicCity?.dispose();
        this.groundSurfaces.dispose();
        this.parisLift?.dispose();
        this.legacyLod?.dispose();this.legacyLod=null;
        this.meshLevel?.dispose();
        if (this.playerController) {
            this.playerController.dispose();
        }

        if (this.playerLoader) {
            this.playerLoader.dispose();
        }

        if (this.cameraManager) {
            this.cameraManager.dispose();
        } else if (!this.bigAppleCoaster?.riding && this.cameraController) {
            this.cameraController.dispose();
        }

        if (this.player && this.engine.scene) {
            this.engine.scene.remove(this.player);
        }

        this.ambientLighting.dispose();
        this.hemisphereLight?.removeFromParent();
        this.hemisphereLight?.dispose();
        if (this.debugController) {
            this.debugController.dispose();
        }
        this.hud.dispose();

        const playerBody = this.playerLoader.getPlayerBody();
        if (playerBody && this.engine.physicsWorld) {
            this.engine.physicsWorld.removeRigidBody(playerBody);
        }

        if (this.engine.physicsWorld && this.worldGenerator) {
            this.worldGenerator.getWorldBodies().forEach(body => {
                this.engine.physicsWorld!.removeRigidBody(body);
            });
        }
    }

    onWindowResize(): void {
        // Handle window resize if needed
        // Camera controller doesn't have a resize method, handled automatically by THREE.js
    }

    getWorldSeed(): number {
        if (!this.worldGenerator) {
            throw new Error('WorldGenerator not initialized');
        }
        return this.worldGenerator.getSeed();
    }

    getCurrentPlayer(): any | null {
        return this.playerController;
    }

    /**
     * Get the generic Spawner instance for spawning any type of entity
     * Use this for ground height detection and positioning of non-vehicle entities
     */
    getSpawner(): Spawner {
        return this.spawner;
    }

    /**
     * Get the VehicleSpawner instance for spawning vehicles
     * This is the recommended way to spawn vehicles - it handles all vehicle-specific logic
     */
    getVehicleSpawner(): VehicleSpawner {
        return this.vehicleSpawner;
    }
}

