"""Audit authored closed solids; signed volume catches inside-out shells hidden by two-sided renders."""
import bpy, bmesh, json, sys, struct
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='build/level/vegas.blend')
negative=[];checked=0;open_meshes=0;seen=set()
for o in bpy.data.objects:
 if o.type!='MESH' or o.get('preserve_uv') or o.data.as_pointer() in seen:continue
 seen.add(o.data.as_pointer());bm=bmesh.new();bm.from_mesh(o.data)
 if bm.faces and all(e.is_manifold for e in bm.edges):
  checked+=1;v=bm.calc_volume(signed=True)
  if v < -1e-8:negative.append({'name':o.name,'signedVolume':v})
 else:open_meshes+=1
 bm.free()
probes=[]
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
for z,y in [(-103,12),(-78,12),(-43,12),(7,12),(42,12),(67,12),(-18,40)]:
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(dg,Vector((-118,-z,y)),Vector((-1,0,0)),distance=100)
 probes.append({'z':z,'height':y,'hit':obj.name if hit else None,'outward':bool(hit and normal.x>.5)})
for z in [-128,-110,-90,-75,-60,-40,-18]:
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(dg,Vector((120,-z,40)),Vector((1,0,0)),distance=80)
 probes.append({'hotel':'Paris','z':z,'height':40,'hit':obj.name if hit else None,'outward':bool(hit and normal.x<-.5)})
for name,origin,direction,axis,sign in [('Caesars Augustus',(-149,165,40),(0,1,0),1,-1),('Caesars Palace',(-170,250,65),(-1,0,0),0,1),('Caesars Colosseum',(-30,273,12),(-1,0,0),0,1)]:
 hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(dg,Vector(origin),Vector(direction),distance=80)
 probes.append({'hotel':name,'hit':obj.name if hit else None,'outward':bool(hit and normal[axis]*sign>.5)})
with open('build/level/vegas.glb','rb') as f:
 f.seek(12);length,kind=struct.unpack('<II',f.read(8));glb=json.loads(f.read(length))
opaque_materials=[m for m in glb['materials'] if m['name'] in ['b_plaster','b_travertine','b_roof','p_wall','p_stone','p_slate','c_stone','c_red']]
culling=all(not m.get('doubleSided',False) for m in opaque_materials) and len(opaque_materials)==8
report={'facadeProbes':probes,'exportBackfaceCulling':culling,'closedSolids' :checked,'invertedCount':len(negative),'openDecorativeMeshes':open_meshes,'inverted':negative}
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if args:json.dump(report,open(args[0],'w'),indent=2)
print(json.dumps({**report,'inverted':negative[:12]},indent=2),flush=True)
if '--require-clean' in args and (negative or not culling or not all(p['outward'] for p in probes)):raise SystemExit(1)
