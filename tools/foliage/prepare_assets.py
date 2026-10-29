"""Normalize generated meshes, retain embedded PBR textures, bake bounded LODs."""
import bpy,sys,json,math,random
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];kind,path=args
out=Path('tools/foliage/models');out.mkdir(exist_ok=True,parents=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(Path(path).resolve()))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
if kind=='grass':
 keep=next(o for o in meshes if 'small_a' in o.name)
 for o in meshes:
  if o!=keep:bpy.data.objects.remove(o,do_unlink=True)
 meshes=[keep]
alpha=bpy.data.images.load(str((Path(path).parent/'textures/alpha.png').resolve()))
alpha.colorspace_settings.name='Non-Color'
for mat in bpy.data.materials:
 if not mat.use_nodes or not (kind=='grass' or 'leaves' in mat.name):continue
 bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=alpha
 mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Alpha'])
 mat.use_backface_culling=False
 mat['alphaMode']='MASK';mat.alpha_threshold=.45

for o in meshes:
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);span=hi-lo
factor=min(7/span.z,6.6/max(span.x,span.y)) if kind=='tree' else .18/span.z
center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
# Bake all source transforms into vertices before normalizing. Imported roots
# may have transforms, so export meshes without their source hierarchy.
for o in meshes:
 matrix=o.matrix_world.copy();o.parent=None;o.matrix_world.identity()
 for v in o.data.vertices:v.co=(matrix@v.co-center)*factor
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 for p in o.data.polygons:p.use_smooth=True
bpy.ops.object.join();source=bpy.context.object;source.name=kind+'-source'
source.data.update();triangles=sum(len(p.vertices)-2 for p in source.data.polygons)
report={'kind':kind,'sourceTriangles':triangles,'lods':[],'source':path}
for level,target in enumerate([250000,12000] if kind=='tree' else [833,100]):
 o=source.copy();o.data=source.data.copy();bpy.context.collection.objects.link(o);o.name=f'{kind}-lod{level}'
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 if kind=='tree' and level==1:
  # Each leaf is disconnected. Collapse cannot go below one triangle per
  # component; thin whole leaves, rather than mutilating every leaf triangle.
  parent=list(range(len(o.data.vertices)))
  def find(a):
   while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
   return a
  for edge in o.data.edges:
   a,c=map(find,edge.vertices);parent[a]=c
  import bmesh
  bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
  leaf_slots={i for i,m in enumerate(o.data.materials) if 'leaves' in m.name}
  remove=[f for f in bm.faces if f.material_index in leaf_slots and find(f.verts[0].index)%3!=0]
  bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
 if triangles>target:
  mod=o.modifiers.new('Distance LOD','DECIMATE');mod.ratio=target/triangles;bpy.ops.object.modifier_apply(modifier=mod.name)
 count=sum(len(p.vertices)-2 for p in o.data.polygons)
 bpy.ops.export_scene.gltf(filepath=str((out/f'{kind}-{level}.glb').resolve()),export_format='GLB',use_selection=True,export_yup=True)
 report['lods'].append({'level':level,'triangles':count,'materials':len(o.data.materials)})
 if level==0:proof=o.copy();proof.data=o.data.copy()
 bpy.data.objects.remove(o,do_unlink=True)
(out/f'{kind}-manifest.json').write_text(json.dumps(report,indent=2))
bpy.data.objects.remove(source,do_unlink=True);bpy.context.collection.objects.link(proof);source=proof
# Neutral lit asset proof, not the saturated sunset game lighting.
bpy.ops.object.select_all(action='DESELECT');source.select_set(True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.world.color=(.35,.35,.35)
height=(span*factor).z
for loc,power,size in [((4,-6,10),1600,6),((-5,1,7),1100,5)]:
 bpy.ops.object.light_add(type='AREA',location=tuple(v*height/7 for v in loc));bpy.context.object.data.energy=power*(height/7)**2;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size*height/7
bpy.ops.object.camera_add(location=(height*1.3,-height*1.7,height*.85));cam=bpy.context.object;direction=Vector((0,0,height*.48))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(height,(span*factor).x,(span*factor).y)*1.35;cam.data.clip_start=.001;scene.camera=cam
scene.render.resolution_x=800;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.filepath=str((out/f'{kind}-proof.png').resolve());bpy.ops.render.render(write_still=True)
print(json.dumps(report))
