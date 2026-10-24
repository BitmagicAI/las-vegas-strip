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

/** `out` = the vertex at `source[o..o+2]` through `e` (exactly Vector3.applyMatrix4, perspective divide included). */
function transform(source:ArrayLike<number>,o:number,e:ArrayLike<number>,out:THREE.Vector3):void{
    const x=source[o]!,y=source[o+1]!,z=source[o+2]!,w=1/(e[3]!*x+e[7]!*y+e[11]!*z+e[15]!);
    out.x=(e[0]!*x+e[4]!*y+e[8]!*z+e[12]!)*w;out.y=(e[1]!*x+e[5]!*y+e[9]!*z+e[13]!)*w;out.z=(e[2]!*x+e[6]!*y+e[10]!*z+e[14]!)*w;
}
const SPAN=32768,TRIANGLE_BITS=2**24;
let counts=new Uint32Array(1<<16);
/** The CSR table of `n` (cell key, triangle) pairs: cells in key order, each cell's triangles in insertion order. A
 * comparator sort over millions of pairs was a second or more per city block. Cells are numbered within the mesh's own
 * box: a box not much bigger than the pair count is counted cell by cell (linear); a sparser one packs each pair into
 * one double (cell, then triangle) and sorts those natively; a pair that cannot fit takes the comparator sort. */
function sortCells(k:Float64Array,refs:Uint32Array,n:number,triangleCount:number):{cellKeys:Float64Array;cellStart:Uint32Array;cellTriangles:Uint32Array}{
    let x0=Infinity,y0=Infinity,z0=Infinity,x1=-Infinity,y1=-Infinity,z1=-Infinity;
    for(let i=0;i<n;i++){const key=k[i]!,z=key%SPAN,r=(key-z)/SPAN,y=r%SPAN,x=(r-y)/SPAN;
        if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;if(z<z0)z0=z;if(z>z1)z1=z;}
    const ny=y1-y0+1,nz=z1-z0+1,cells=(x1-x0+1)*ny*nz;
    const global=(local:number):number=>{const z=local%nz,r=(local-z)/nz,y=r%ny,x=(r-y)/ny;return ((x+x0)*SPAN+(y+y0))*SPAN+(z+z0);};
    if(n&&cells<=n*4+65536){
        if(counts.length<cells+1)counts=new Uint32Array(Math.max(cells+1,counts.length*2));else counts.fill(0,0,cells+1);
        const local=new Uint32Array(n);let unique=0;
        for(let i=0;i<n;i++){const key=k[i]!,z=key%SPAN,r=(key-z)/SPAN,y=r%SPAN,x=(r-y)/SPAN,c=((x-x0)*ny+(y-y0))*nz+(z-z0);
            local[i]=c;const seen=counts[c+1]!;if(seen===0)unique++;counts[c+1]=seen+1;}
        const cellKeys=new Float64Array(unique),cellStart=new Uint32Array(unique+1),cellTriangles=new Uint32Array(n);
        for(let c=0,u=0;c<cells;c++){const size=counts[c+1]!;counts[c+1]=counts[c]!+size;if(size){cellKeys[u]=global(c);cellStart[u]=counts[c]!;u++;}}
        cellStart[unique]=n;
        for(let i=0;i<n;i++)cellTriangles[counts[local[i]!]!++]=refs[i]!;
        return {cellKeys,cellStart,cellTriangles};
    }
    let order:Uint32Array|null=null,packed:Float64Array|null=null;
    if(n&&cells*TRIANGLE_BITS<=2**53&&triangleCount<=TRIANGLE_BITS){
        packed=new Float64Array(n);
        for(let i=0;i<n;i++){const key=k[i]!,z=key%SPAN,r=(key-z)/SPAN,y=r%SPAN,x=(r-y)/SPAN;packed[i]=(((x-x0)*ny+(y-y0))*nz+(z-z0))*TRIANGLE_BITS+refs[i]!;}
        packed.sort();
    }else{
        order=new Uint32Array(n);for(let i=0;i<n;i++)order[i]=i;
        order.sort((p,q)=>k[p]!-k[q]!);
    }
    const keyAt=(i:number):number=>{
        return packed?global(Math.floor(packed[i]!/TRIANGLE_BITS)):k[order![i]!]!;
    };
    let unique=0;for(let i=0,last=NaN;i<n;i++){const key=keyAt(i);if(key!==last){unique++;last=key;}}
    const cellKeys=new Float64Array(unique),cellStart=new Uint32Array(unique+1),cellTriangles=new Uint32Array(n);
    for(let i=0,u=-1;i<n;i++){const key=keyAt(i);if(u<0||cellKeys[u]!==key){u++;cellKeys[u]=key;cellStart[u]=i;}
        cellTriangles[i]=packed?packed[i]!%TRIANGLE_BITS:refs[order![i]!]!;}
    cellStart[unique]=n;
    return {cellKeys,cellStart,cellTriangles};
}

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
            const interleaved='isInterleavedBufferAttribute' in positions&&positions.isInterleavedBufferAttribute;
            const source=interleaved?positions.data.array:positions.array,ia=index?.array;
            const stride=interleaved?positions.data.stride:positions.itemSize,offset=interleaved?positions.offset:0;
            const direct=!positions.normalized&&source instanceof Float32Array,e=object.matrixWorld.elements;
            triangles.length=0;keys.length=0;refs.length=0;broad.length=0;
            const bounds=new THREE.Box3();
            const materials=Array.isArray(object.material)?object.material:[object.material];
            const groups=Array.isArray(object.material)?g.groups:[{start:0,count,materialIndex:0}];
            for(const group of groups){
                const material=materials[group.materialIndex??0];
                if(!material || material.transparent || !material.visible || material.side===THREE.BackSide)continue;
                const start=Math.max(group.start,g.drawRange.start),end=Math.min(count,group.start+group.count,g.drawRange.start+g.drawRange.count);
                for(let i=start;i+2<end;i+=3){
                    // the same arithmetic as fromBufferAttribute + applyMatrix4, without the per-vertex calls (2026-10-24:
                    // registering the city spent ~10 s of the load in them); quantized positions take three's accessors
                    if(direct){
                        transform(source,(ia?ia[i]!:i)*stride+offset,e,a);transform(source,(ia?ia[i+1]!:i+1)*stride+offset,e,b);transform(source,(ia?ia[i+2]!:i+2)*stride+offset,e,c);
                    }else{
                        a.fromBufferAttribute(positions,index?index.getX(i):i).applyMatrix4(object.matrixWorld);
                        b.fromBufferAttribute(positions,index?index.getX(i+1):i+1).applyMatrix4(object.matrixWorld);
                        c.fromBufferAttribute(positions,index?index.getX(i+2):i+2).applyMatrix4(object.matrixWorld);
                    }
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
            const n=keys.length,{cellKeys,cellStart,cellTriangles}=sortCells(keys.array,refs.array,n,triangles.length/9);
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
