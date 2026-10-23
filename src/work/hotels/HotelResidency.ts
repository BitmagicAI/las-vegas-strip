/** Live scene residency, not saved room state. Required entries cannot be evicted. */
export class HotelResidency<T> {
    readonly entries = new Map<string, {value:T; touched:number}>();
    readonly capacity:number;
    readonly grace:number;
    private release:(value:T)=>void;
    constructor(capacity:number, grace:number, release:(value:T)=>void){this.capacity=capacity;this.grace=grace;this.release=release;}
    reconcile(required:ReadonlyMap<string,()=>T>,now:number):void {
        if(required.size>this.capacity)throw new Error('Hotel residency capacity is smaller than the required support set');
        for(const key of required.keys()){const e=this.entries.get(key);if(e)e.touched=now;}
        for(const [key,e] of this.entries)if(!required.has(key)&&now-e.touched>this.grace)this.remove(key);
        for(const [key,create] of required){
            if(this.entries.has(key))continue;
            while(this.entries.size>=this.capacity){
                const oldest=[...this.entries].filter(([k])=>!required.has(k)).sort((a,b)=>a[1].touched-b[1].touched)[0];
                if(!oldest)throw new Error('No unpinned hotel instance can be evicted');
                this.remove(oldest[0]);
            }
            this.entries.set(key,{value:create(),touched:now});
        }
    }
    remove(key:string):void {const e=this.entries.get(key);if(e){this.release(e.value);this.entries.delete(key);}}
    dispose():void {for(const key of [...this.entries.keys()])this.remove(key);}
}
export interface RoomState {visited:boolean; visits:number; searched?:boolean}
/** Sparse persistent state: read one room on demand, keep at most 64 in RAM. */
export class RoomStateStore {
    private cache=new Map<string,RoomState>();
    private storage:Pick<Storage,'getItem'|'setItem'>|null;
    constructor(storage:Pick<Storage,'getItem'|'setItem'>|null){this.storage=storage;}
    get(id:string):RoomState {
        let state=this.cache.get(id);
        if(!state){
            try{const s=JSON.parse(this.storage?.getItem('afterlight.room.v1.'+id)??'null');
                if(s&&typeof s.visited==='boolean'&&Number.isFinite(s.visits))state={visited:s.visited,visits:Math.max(0,s.visits),...(typeof s.searched==='boolean'?{searched:s.searched}:{})};
            }catch{/* Storage can be disabled; scene residency still works. */}
            state??={visited:false,visits:0};
        }
        this.cache.delete(id);this.cache.set(id,state);
        if(this.cache.size>64)this.cache.delete(this.cache.keys().next().value!);
        return {...state};
    }
    set(id:string,state:RoomState):void {
        this.cache.delete(id);this.cache.set(id,{...state});
        if(this.cache.size>64)this.cache.delete(this.cache.keys().next().value!);
        try{this.storage?.setItem('afterlight.room.v1.'+id,JSON.stringify(state));}catch{/* Session-only if storage is unavailable. */}
    }
    get residentStates():number{return this.cache.size;}
}
