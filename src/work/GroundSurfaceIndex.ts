import * as THREE from 'three';

const CELL=4;
const MAX_CELLS_PER_TRIANGLE=64;
/** Packs integer cell coordinates (±16383 cells an axis, i.e. ±65 km) into one exact double. */
const cellKey=(x:number,y:number,z:number)=>((x+16384)*32768+(y+16384))*32768+(z+16384);
interface Surface {
    /** Visibility only: grounding follows the mesh (or its LOD block) being shown. */
    mesh:THREE.Mesh;
    /** Walkable triangles in world space, 9 floats each. */
    triangles:Float32Array;
    /** Sorted cell keys; cellStart[k]..cellStart[k+1] indexes cellTriangles. */
    cellKeys:Float64Array;
    cellStart:Uint32Array;
    cellTriangles:Uint32Array;
    /** Triangles spanning too many cells to list in each. */
    broad:Uint32Array;
    bounds:THREE.Box3;
}

/** Growable typed buffers for building, so registration allocates no per-triangle JS arrays. */
class Floats {array=new Float32Array(4096);length=0;push9(a:THREE.Vector3,b:THREE.Vector3,c:THREE.Vector3):void{if(this.length+9>this.array.length){const n=new Float32Array(this.array.length*2);n.set(this.array);this.array=n;}const t=this.array,i=this.length;t[i]=a.x;t[i+1]=a.y;t[i+2]=a.z;t[i+3]=b.x;t[i+4]=b.y;t[i+5]=b.z;t[i+6]=c.x;t[i+7]=c.y;t[i+8]=c.z;this.length+=9;}}
class Uints {array=new Uint32Array(1024);length=0;push(v:number):void{if(this.length===this.array.length){const n=new Uint32Array(this.array.length*2);n.set(this.array);this.array=n;}this.array[this.length++]=v;}}
class Doubles {array=new Float64Array(1024);length=0;push(v:number):void{if(this.length===this.array.length){const n=new Float64Array(this.array.length*2);n.set(this.array);this.array=n;}this.array[this.length++]=v;}}

/** Exact upward-facing render triangles, spatially indexed once on residency.
 * Never scans the city's triangle buffers during gameplay and adds no physics
 * bodies. It copies the walkable triangles it needs (flat typed arrays, no
 * per-cell JS arrays) and keeps no reference to the source vertex buffers, so the
 * renderer may release those after upload. Registered roots must be static;
 * unregister before moving/evicting. */
export class GroundSurfaceIndex {
    private surfaces=new Set<Surface>();
    private a=new THREE.Vector3();
    private b=new THREE.Vector3();
    private c=new THREE.Vector3();
    private point=new THREE.Vector3();
    private ray=new THREE.Ray(new THREE.Vector3(),new THREE.Vector3(0,-1,0));
    register(root:THREE.Object3D):()=>void {
        root.updateWorldMatrix(true,true);
        const owned:Surface[]=[];
        const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3(),ab=new THREE.Vector3(),ac=new THREE.Vector3();
        const triangles=new Floats(),keys=new Doubles(),refs=new Uints(),broad=new Uints();
        root.traverse(object=>{
            if(!(object instanceof THREE.Mesh) || object instanceof THREE.SkinnedMesh || !object.layers.isEnabled(0))return;
            const g=object.geometry,positions=g.getAttribute('position'),index=g.index;
            if(!positions||!(('isInterleavedBufferAttribute' in positions&&positions.isInterleavedBufferAttribute)?positions.data.array.length:positions.array.length))return;
            const count=index?.count??positions.count;
            triangles.length=0;keys.length=0;refs.length=0;broad.length=0;
            const bounds=new THREE.Box3();
            const materials=Array.isArray(object.material)?object.material:[object.material];
            const groups=Array.isArray(object.material)?g.groups:[{start:0,count,materialIndex:0}];
            for(const group of groups){
                const material=materials[group.materialIndex??0];
                if(!material || material.transparent || !material.visible || material.side===THREE.BackSide)continue;
                const start=Math.max(group.start,g.drawRange.start),end=Math.min(count,group.start+group.count,g.drawRange.start+g.drawRange.count);
                for(let i=start;i+2<end;i+=3){
                    a.fromBufferAttribute(positions,index?index.getX(i):i).applyMatrix4(object.matrixWorld);
                    b.fromBufferAttribute(positions,index?index.getX(i+1):i+1).applyMatrix4(object.matrixWorld);
                    c.fromBufferAttribute(positions,index?index.getX(i+2):i+2).applyMatrix4(object.matrixWorld);
                    ab.subVectors(b,a);ac.subVectors(c,a);ab.cross(ac);
                    // Same walkable-face threshold as the old downward raycast.
                    if(ab.y<=0 || ab.y*ab.y<=.65*.65*ab.lengthSq())continue;
                    const t=triangles.length/9;triangles.push9(a,b,c);
                    bounds.expandByPoint(a).expandByPoint(b).expandByPoint(c);
                    const x0=Math.floor(Math.min(a.x,b.x,c.x)/CELL),x1=Math.floor(Math.max(a.x,b.x,c.x)/CELL);
                    const y0=Math.floor(Math.min(a.y,b.y,c.y)/CELL),y1=Math.floor(Math.max(a.y,b.y,c.y)/CELL);
                    const z0=Math.floor(Math.min(a.z,b.z,c.z)/CELL),z1=Math.floor(Math.max(a.z,b.z,c.z)/CELL);
                    // Huge terrain/slab triangles stay in a small broad list,
                    // rather than allocating thousands of duplicate cell entries.
                    if((x1-x0+1)*(y1-y0+1)*(z1-z0+1)>MAX_CELLS_PER_TRIANGLE){broad.push(t);continue;}
                    for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++){keys.push(cellKey(x,y,z));refs.push(t);}
                }
            }
            if(!triangles.length)return;
            // Sort (key, triangle) pairs by key, then compress into a CSR table.
            const n=keys.length,order=new Uint32Array(n);for(let i=0;i<n;i++)order[i]=i;
            const k=keys.array;order.sort((p,q)=>k[p]!-k[q]!);
            let unique=0;for(let i=0;i<n;i++)if(i===0||k[order[i]!]!==k[order[i-1]!]!)unique++;
            const cellKeys=new Float64Array(unique),cellStart=new Uint32Array(unique+1),cellTriangles=new Uint32Array(n);
            for(let i=0,u=-1;i<n;i++){const key=k[order[i]!]!;if(u<0||cellKeys[u]!==key){u++;cellKeys[u]=key;cellStart[u]=i;}cellTriangles[i]=refs.array[order[i]!]!;}
            cellStart[unique]=n;
            const surface:Surface={mesh:object,triangles:triangles.array.slice(0,triangles.length),cellKeys,cellStart,cellTriangles,broad:broad.array.slice(0,broad.length),bounds};
            this.surfaces.add(surface);owned.push(surface);
        });
        return ()=>{for(const surface of owned)this.surfaces.delete(surface);owned.length=0;};
    }
    height(x:number,z:number,top:number,bottom:number):number|undefined {
        let best=-Infinity;
        this.ray.origin.set(x,top,z);
        const cx=Math.floor(x/CELL),cz=Math.floor(z/CELL);
        for(const s of this.surfaces){
            if(x<s.bounds.min.x || x>s.bounds.max.x || z<s.bounds.min.z || z>s.bounds.max.z || s.bounds.min.y>top || s.bounds.max.y<bottom)continue;
            let visible=true;
            for(let p:THREE.Object3D|null=s.mesh.userData.groundVisibilityRoot??s.mesh;p;p=p.parent)if(!p.visible){visible=false;break;}
            if(!visible)continue;
            for(let cy=Math.floor(bottom/CELL);cy<=Math.floor(top/CELL);cy++){
                const cell=this.find(s.cellKeys,cellKey(cx,cy,cz));
                if(cell>=0)best=this.highest(s,s.cellTriangles,s.cellStart[cell]!,s.cellStart[cell+1]!,bottom,best);
            }
            best=this.highest(s,s.broad,0,s.broad.length,bottom,best);
        }
        return best===-Infinity?undefined:best;
    }
    private find(keys:Float64Array,key:number):number {
        let lo=0,hi=keys.length-1;
        while(lo<=hi){const mid=(lo+hi)>>1,v=keys[mid]!;if(v===key)return mid;if(v<key)lo=mid+1;else hi=mid-1;}
        return -1;
    }
    private highest(surface:Surface,list:Uint32Array,from:number,to:number,bottom:number,best:number):number {
        const t=surface.triangles;
        for(let j=from;j<to;j++){
            const o=list[j]!*9;
            this.a.set(t[o]!,t[o+1]!,t[o+2]!);this.b.set(t[o+3]!,t[o+4]!,t[o+5]!);this.c.set(t[o+6]!,t[o+7]!,t[o+8]!);
            const hit=this.ray.intersectTriangle(this.a,this.b,this.c,true,this.point);
            if(hit && hit.y>=bottom && hit.y>best)best=hit.y;
        }
        return best;
    }
    get stats():{meshes:number;triangles:number;cells:number;references:number;megabytes:number}{
        let triangles=0,cells=0,references=0,bytes=0;
        for(const s of this.surfaces){triangles+=s.triangles.length/9;cells+=s.cellKeys.length;references+=s.cellTriangles.length+s.broad.length;bytes+=s.triangles.byteLength+s.cellKeys.byteLength+s.cellStart.byteLength+s.cellTriangles.byteLength+s.broad.byteLength;}
        return {meshes:this.surfaces.size,triangles,cells,references,megabytes:Math.round(bytes/1048576)};
    }
    dispose():void{this.surfaces.clear();}
}
