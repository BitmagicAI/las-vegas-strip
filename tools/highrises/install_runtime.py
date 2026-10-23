from pathlib import Path
import json
p=Path('src/work/hotels/HotelLayout.ts');s=p.read_text();keys=[x['key'] for x in json.loads(Path('build/highrises/plan.json').read_text())];s=s.replace("|'waldorf';","|'waldorf'|"+'|'.join(repr(k) for k in keys)+';');s=s.replace('    roomDepth?: number;','    roomDepth?: number;\n    lazy?: boolean;\n    lobbyFront?: number;\n    source?: string;');s=s.replace("hideTower:windowView?(t.building==='veer'?t.id:t.building):undefined","hideTower:windowView?(t.lazy?t.source:t.building==='veer'?t.id:t.building):undefined");p.write_text(s)
p=Path('src/work/hotels/HotelTemplates.ts');s=p.read_text().replace("|'corridor-end'}`;","|'corridor-end'}`|`${string}-lobby`;")
s=s.replace("const REVISION='resort-guest-sets-1';","const REVISION='mapped-highrises-1';")
s=s.replace('    async ensureGuest(set:HotelSet)', '''    async ensureCore(set:HotelSet):Promise<void>{await Promise.all(CORE.map(kind=>this.fetchModule(`${set}-${kind}`)));}
    async ensureLobby(id:string):Promise<void>{await this.fetchModule(`${id}-lobby`);}
    releaseLazy(set:HotelSet,id:string):void{
        const names=[...this.bases.keys()].filter(n=>n===`${id}-lobby` || CORE.some(k=>n===`${set}-${k}`));
        for(const n of names){if((this.references.get(n)??0)>0 || this.pending.has(n))continue;this.releaseResources([this.bases.get(n)!]);this.bases.delete(n);this.metadata.delete(n);this.references.delete(n);}
    }
    async ensureGuest(set:HotelSet)''')
p.write_text(s)
p=Path('src/work/hotels/HotelStreaming.ts');s=p.read_text().replace("import recipes from './towers.json';","import recipes from './towers.json';\nimport highrises from './highrise-towers.json';")
s=s.replace('export const HOTEL_TOWERS=recipes as Tower[];','export const HOTEL_TOWERS=[...recipes,...highrises] as Tower[];')
s=s.replace('    private ground:Chunk[]=[];', '''    private ground:Chunk[]=[];
    private lazyResidents=new Map<string,{lastNear:number;lobby:ModuleInstance;door:DoorHandle}>();
    private corePending=new Set<string>();''')
s=s.replace('HOTEL_TOWERS.map(t=>this.makeStair', 'HOTEL_TOWERS.filter(t=>!t.lazy).map(t=>this.makeStair').replace('HOTEL_TOWERS.map(t=>({tower:t,','HOTEL_TOWERS.filter(t=>!t.lazy).map(t=>({tower:t,')
s=s.replace('ready:()=>boolean=()=>true):DoorHandle','ready:()=>boolean=()=>true,height=2.65):DoorHandle').replace('height:2.65,thickness:.13','height,thickness:.13')
needle='    update(dt:number,player:Point,prepared=false):void{'
methods='''    private inLobby(t:Tower,p:Point):boolean {
        if(!t.lazy || t.lobbyFront===undefined || p.y<-.3 || p.y>6.7)return false;
        const front=-5.25-6*t.bays;
        return p.z>t.lobbyFront-.25 && p.z< -5.25 && Math.abs(p.x)<(p.z<front?1.9:9.3);
    }
    private async prepareCore(t:Tower):Promise<void>{
        if(!t.lazy || this.lazyResidents.has(t.id))return;
        await Promise.all([this.templates.ensureCore(t.set),this.templates.ensureLobby(t.id)]);
        if(this.disposed || this.lazyResidents.has(t.id))return;
        this.ground.push(this.makeStair(t,0));
        this.entries.push({tower:t,module:this.templates.instantiate(`${t.set}-entry`,this.matrix(t,{x:0,y:0,z:0},0,true))});
        this.closures.push({tower:t,top:this.templates.instantiate(`${t.set}-closure`,this.matrix(t,{x:0,y:0,z:0}),false),bottom:this.templates.instantiate(`${t.set}-closure`,this.matrix(t,{x:0,y:0,z:0}),false)});
        const lobby=this.templates.instantiate(`${t.id}-lobby`,this.matrix(t,{x:0,y:0,z:0}));
        const door=this.door(t,{x:0,y:2.15,z:t.lobbyFront!},0,2.5,t.name+' entrance',()=>{},()=>true,4.3);
        for(const o of door.visuals)if(o instanceof THREE.Mesh){const m=o.material;if(m instanceof THREE.MeshStandardMaterial){m.color.setHex(0x73959b);m.transparent=true;m.opacity=.24;m.depthWrite=false;m.metalness=.3;m.roughness=.2;}}
        this.lazyResidents.set(t.id,{lastNear:this.now,lobby,door});
    }
    private evictCore(t:Tower):void {
        const r=this.lazyResidents.get(t.id);if(!r)return;
        r.lobby.dispose();r.door.door.dispose();this.lazyResidents.delete(t.id);
        for(const c of this.ground.filter(c=>c.tower.id===t.id))c.dispose();this.ground=this.ground.filter(c=>c.tower.id!==t.id);
        for(const e of this.entries.filter(c=>c.tower.id===t.id))e.module.dispose();this.entries=this.entries.filter(c=>c.tower.id!==t.id);
        for(const c of this.closures.filter(c=>c.tower.id===t.id)){c.top.dispose();c.bottom.dispose();}this.closures=this.closures.filter(c=>c.tower.id!==t.id);
        this.templates.releaseLazy(t.set,t.id);
    }
'''
s=s.replace(needle,methods+needle)
s=s.replace('        const occupied=matches.find', '''        for(const {t,p} of matches){
            if(!t.lazy)continue;
            const near=insideTower(t,p)||this.inLobby(t,p)||p.y<8 && Math.abs(p.x)<28 && p.z>(t.lobbyFront??-30)-28 && p.z<28;
            const resident=this.lazyResidents.get(t.id);
            if(near){
                if(resident)resident.lastNear=this.now;
                else if(!this.corePending.has(t.id)){
                    this.corePending.add(t.id);
                    this.loading.enqueue('tower-core:'+t.id,t.name+' entrance and stairs',async()=>{try{await this.prepareCore(t);}finally{this.corePending.delete(t.id);}});
                }
            }else if(resident && this.now-resident.lastNear>30)this.evictCore(t);
        }
        const ready=matches.filter(({t})=>!t.lazy || this.lazyResidents.has(t.id));
        const occupied=ready.find''')
s=s.replace("const match=occupied??matches.find","const match=occupied??ready.find")
s=s.replace('        this.templates.trim();\n        const listener=', '''        for(const [id,r] of this.lazyResidents){
            const t=HOTEL_TOWERS.find(t=>t.id===id)!,p=localPoint(t,player);
            const visible=(!occupied || occupied.t.id===id && this.currentFloor===0) && p.y<10;
            r.lobby.root.visible=visible;for(const v of r.door.visuals)v.visible=visible;
            if(visible && (this.inLobby(t,p) || Math.hypot(p.x,p.z-t.lobbyFront!)<15))lightSites.push(...r.lobby.lights);
            if(Math.hypot(p.x,p.z-t.lobbyFront!)<3 && p.y<3 && !r.door.door.isOpen())r.door.door.open();
            if(Math.hypot(p.x,p.z-t.lobbyFront!)>8 && r.door.door.isOpen())r.door.door.close();
        }
        this.templates.trim();
        const listener=''')
s=s.replace('        const t=this.active;if(!t)return null;', '''        const lobbyTower=HOTEL_TOWERS.find(t=>this.lazyResidents.has(t.id)&&this.inLobby(t,localPoint(t,player)));
        if(lobbyTower){const p=localPoint(lobbyTower,player);return {building:lobbyTower.building,outside:p.z<lobbyTower.lobbyFront!+7,showGround:true};}
        const t=this.active;if(!t)return null;''')
s=s.replace('        if(floor>=t.firstGuestFloor)await this.templates.ensureGuest', '        await this.prepareCore(t);\n        if(floor>=t.firstGuestFloor)await this.templates.ensureGuest')
s=s.replace('        this.disposed=true;this.floors.dispose();','        this.disposed=true;for(const t of HOTEL_TOWERS)if(t.lazy)this.evictCore(t);this.floors.dispose();')
p.write_text(s)
