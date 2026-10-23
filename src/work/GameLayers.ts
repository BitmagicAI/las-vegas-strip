import type * as THREE from 'three';
import type {EngineLike} from 'types/game.js';
import type {PlayerController} from 'engine/PlayerController.js';
import type {VehicleManager} from 'engine/VehicleManager.js';
import type {GameHUD} from './GameHUD.js';
import type {GroundSurfaceIndex} from './GroundSurfaceIndex.js';
import type {NearbyLights} from './NearbyLights.js';
import type {Film,FilmHost} from './film/Film.js';
import type {FilmLook} from './film/FilmLook.js';

/**
 * The seam between the city and a game built on it. The city runs with no layer at all: walking, the jeep, doors,
 * lifts, the coaster, streaming and the film tools. A game adds its own systems (characters, missions, combat, HUD) as a
 * layer and lists its factory in GAME_LAYERS below; that one line is the only city file a game edits, so city updates
 * merge into the game cleanly. Example: `[() => import('./mygame/MyGame.js').then(m => new m.MyGame())]`.
 */
export interface CityContext {
    engine:EngineLike;
    player:THREE.Object3D;
    playerController:PlayerController;
    hud:GameHUD;
    groundSurfaces:GroundSurfaceIndex;
    /** Boot-allocated stand-in lights for close, moving objects (AGENTS.md: never change the light set at runtime). */
    nearbyLights:NearbyLights;
    vehicleManager:VehicleManager;
    /** First person, riding the coaster or seated in a vehicle: a third-person body should hide. */
    playerViewHidesBody():boolean;
    sprinting():boolean;
    grounded():boolean;
    verticalVelocity():number;
}
/** Local filming only (tools/film): what a layer gets when the film director is on. */
export interface CityFilm {
    film:Film;
    look:FilmLook;
}
export interface GameLayer {
    /** Once the city has loaded, before the first frame. */
    load(city:CityContext):Promise<void>;
    /** With the film director on: film scenarios (tools/film takes with `scenario`) and any film-only controls. */
    filmReady?(film:CityFilm):Promise<Partial<Pick<FilmHost,'scenarioLoad'|'scenarioUpdate'>>&{jeepPose?():{x:number;y:number;z:number;fx:number;fy:number;fz:number;speed:number}|null}>;
    /** Start of the frame, after the film director advanced (driving physics that the camera follows). */
    tick?(dt:number):void;
    /** After the player and the city updated. */
    update(dt:number,player:THREE.Object3D):void;
    /** After visibility is decided (atmosphere, HUD). */
    render?(dt:number):void;
    /** Hide what a building in front of the camera covers (BuildingVisibility). */
    setRenderVisibility?(test:(p:THREE.Vector3)=>boolean):void;
    /** A streaming job holds the game: freeze physics the layer owns. */
    setStreamingHeld?(held:boolean):void;
    dispose():void;
}
export type GameLayerFactory=()=>Promise<GameLayer>;

/** The game layers this build runs. The city ships with none. */
export const GAME_LAYERS:readonly GameLayerFactory[]=[];
