"""Extend Bellagio's collision-only guest void for its deeper King template.
Visual towers stay intact outdoors; HotelStreaming hides their shell indoors.
This is also called by prepare_hotel_shells.py on future complete rebuilds.
"""
import bpy,bmesh,json,math
from pathlib import Path
def extend():
    path=Path('build/hotels/staged-vegas.mesh-level.json');data=json.loads(path.read_text())
    towers=[t for t in json.loads(Path('src/work/hotels/towers.json').read_text()) if t['set']=='bellagio']
    def obj(name,verts,faces):
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
        ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return ob
    faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    cutters=[]
    for t in towers:
        c,s=math.cos(t['yaw']),math.sin(t['yaw']);ox,oy,oz=t['origin']
        verts=[(ox+c*x+s*z,-(oz-s*x+c*z),oy+y) for x in [-10.10,10.10] for y in [t['firstGuestFloor']*3.6-.15,t['floors']*3.6+.2] for z in [-4.8-t['bays']*6-.25,-4.65]]
        cutters.append(obj('Expanded Bellagio guest void',verts,faces))
    updated=[];changed=[]
    for record in data['colliders']:
        if not record['name'].startswith('Bellagio '):updated.append(record);continue
        if record['shape']=='box':
            x,y,z=record['position'];w,h,d=record['size'];c,s=math.cos(record.get('yaw',0)),math.sin(record.get('yaw',0))
            vs=[(x+c*xx+s*zz,-(z-s*xx+c*zz),y+yy) for xx in [-w/2,w/2] for yy in [-h/2,h/2] for zz in [-d/2,d/2]];fs=faces
        else:
            v=record['vertices'];vs=[(v[i],-v[i+2],v[i+1]) for i in range(0,len(v),3)]
            ix=record.get('indices',[]);fs=[ix[i:i+3] for i in range(0,len(ix),3)]
        if max(v[2] for v in vs)<min(t['firstGuestFloor']*3.6 for t in towers)-.2:updated.append(record);continue
        bounds=lambda a:([min(v[i] for v in a) for i in range(3)],[max(v[i] for v in a) for i in range(3)])
        lo,hi=bounds(vs);relevant=[]
        for cutter in cutters:
            cl,ch=bounds([v.co for v in cutter.data.vertices])
            if all(hi[i]>cl[i] and ch[i]>lo[i] for i in range(3)):relevant.append(cutter)
        if not relevant:updated.append(record);continue
        ob=obj('collision cut',vs,fs)
        if record['shape']=='convexHull':
            bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.convex_hull(bm,input=list(bm.verts));bm.to_mesh(ob.data);bm.free()
        bpy.context.view_layer.objects.active=ob
        for cutter in relevant:
            mod=ob.modifiers.new('Guest room clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.ops.object.modifier_apply(modifier=mod.name)
        ob.data.calc_loop_triangles()
        if ob.data.loop_triangles:
            updated.append({'name':record['name'],'shape':'trimesh','vertices':[a for v in ob.data.vertices for a in [v.co.x,v.co.z,-v.co.y]],'indices':[i for tri in ob.data.loop_triangles for i in tri.vertices]})
        changed.append(record['name']);bpy.data.objects.remove(ob,do_unlink=True)
    for ob in cutters:bpy.data.objects.remove(ob,do_unlink=True)
    data['colliders']=updated;data.setdefault('extras',{})['bellagioRoomCollisionDepth']=8.1
    path.write_text(json.dumps(data,indent=2))
    Path('build/hotels/bellagio-premier/collision-shell-report.json').write_text(json.dumps({'changed':changed,'colliders':len(updated)},indent=2))
    print('Extended Bellagio guest collision voids:',len(changed),flush=True)
if __name__=='__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True);extend()
