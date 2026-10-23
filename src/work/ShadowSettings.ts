/** How far the focused sun's shadows reach around the player, in metres (the half-width of its receiver
 * region; with the low sunset sun a region reaches several times further along the sun's bearing). */
export interface ShadowPreferences {distance:number}
export const SHADOW_SETTINGS_KEY='afterlight:shadows:v1';
export const SHADOW_DISTANCE_MIN=32,SHADOW_DISTANCE_MAX=192,SHADOW_DISTANCE_DEFAULT=32;
export function normalizeShadowPreferences(value:unknown):ShadowPreferences {
    const v=(value&&typeof value==='object'?value:{}) as Partial<ShadowPreferences>;
    return {distance:typeof v.distance==='number'&&Number.isFinite(v.distance)?Math.min(SHADOW_DISTANCE_MAX,Math.max(SHADOW_DISTANCE_MIN,Math.round(v.distance))):SHADOW_DISTANCE_DEFAULT};
}
export class ShadowSettingsStore {
    private value:ShadowPreferences={distance:SHADOW_DISTANCE_DEFAULT};private listeners=new Set<(value:ShadowPreferences)=>void>();
    constructor(private storage?:Pick<Storage,'getItem'|'setItem'>){try{this.value=normalizeShadowPreferences(JSON.parse(storage?.getItem(SHADOW_SETTINGS_KEY)??'null'));}catch{}}
    get():ShadowPreferences{return {...this.value};}
    set(patch:Partial<ShadowPreferences>):void {this.value=normalizeShadowPreferences({...this.value,...patch});try{this.storage?.setItem(SHADOW_SETTINGS_KEY,JSON.stringify(this.value));}catch{}for(const listener of this.listeners)listener(this.get());}
    subscribe(listener:(value:ShadowPreferences)=>void):()=>void {this.listeners.add(listener);listener(this.get());return ()=>this.listeners.delete(listener);}
}
function localStorageOrUndefined():Storage|undefined {try{return typeof localStorage==='undefined'?undefined:localStorage;}catch{return undefined;}}
export const shadowSettings=new ShadowSettingsStore(localStorageOrUndefined());
