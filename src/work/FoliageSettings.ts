export interface FoliagePreferences {enabled:boolean;distanceScale:number}
export const FOLIAGE_SETTINGS_KEY='afterlight:foliage:v1';
const defaults:FoliagePreferences={enabled:true,distanceScale:1};
export function normalizeFoliagePreferences(value:unknown):FoliagePreferences {
    const v=(value&&typeof value==='object'?value:{}) as Partial<FoliagePreferences>;
    return {enabled:typeof v.enabled==='boolean'?v.enabled:true,distanceScale:typeof v.distanceScale==='number'&&Number.isFinite(v.distanceScale)?Math.min(2,Math.max(.25,v.distanceScale)):1};
}
export class FoliageSettingsStore {
    private value={...defaults};private listeners=new Set<(value:FoliagePreferences)=>void>();
    constructor(private storage?:Pick<Storage,'getItem'|'setItem'>){try{this.value=normalizeFoliagePreferences(JSON.parse(storage?.getItem(FOLIAGE_SETTINGS_KEY)??'null'));}catch{}}
    get():FoliagePreferences{return {...this.value};}
    set(patch:Partial<FoliagePreferences>):void {this.value=normalizeFoliagePreferences({...this.value,...patch});try{this.storage?.setItem(FOLIAGE_SETTINGS_KEY,JSON.stringify(this.value));}catch{}for(const listener of this.listeners)listener(this.get());}
    subscribe(listener:(value:FoliagePreferences)=>void):()=>void {this.listeners.add(listener);listener(this.get());return ()=>this.listeners.delete(listener);}
}
function localStorageOrUndefined():Storage|undefined {try{return typeof localStorage==='undefined'?undefined:localStorage;}catch{return undefined;}}
export const foliageSettings=new FoliageSettingsStore(localStorageOrUndefined());
