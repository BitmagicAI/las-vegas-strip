import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(Path('build/south-strip/liberty-scan.glb').resolve()))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in meshes:
 matrix=o.matrix_world.copy();o.parent=None;o.matrix_world=matrix;o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
vs=[v.co.copy() for v in o.data.vertices];y0=min(v.y for v in vs);y1=max(v.y for v in vs)
for q in [.02,.08,.92,.98]:
 pts=[v for v in vs if y0+(q-.02)*(y1-y0)<v.y<y0+(q+.02)*(y1-y0)];print('PROFILE',q,[[min(v[k] for v in pts),max(v[k] for v in pts)] for k in [0,2]],flush=True)
# Scan has its long axis along Blender Y. Base lies at the positive end.
scale=45.72/(y1-y0);base=[v for v in vs if v.y>y1-.10*(y1-y0)];cx=(min(v.x for v in base)+max(v.x for v in base))/2;cz=(min(v.z for v in base)+max(v.z for v in base))/2
for v in o.data.vertices:
 x,y,z=v.co;v.co=((x-cx)*scale,(z-cz)*scale,(y1-y)*scale)
# Join the scanned chunks before simplification so seams remain welded.
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.002);bm.to_mesh(o.data);bm.free()
mod=o.modifiers.new('Game silhouette-preserving reduction','DECIMATE');mod.ratio=.075;bpy.ops.object.modifier_apply(modifier=mod.name)
o.data.materials.clear()
for name,col in [('pedestal',(.35,.36,.31)),('patinated copper',(.19,.43,.34)),('torch',(.65,.39,.10))]:
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=.5 if name!='pedestal' else 0;bs.inputs['Roughness'].default_value=.5;o.data.materials.append(m)
for p in o.data.polygons:
 h=sum(o.data.vertices[i].co.z for i in p.vertices)/len(p.vertices);p.material_index=0 if h<13.6 else 2 if h>44 else 1;p.use_smooth=h>=13.6
# Store centered at origin; south-Strip export places and rotates this asset.
o.name='Liberty / gomeasure3d / CC BY 4.0';o['property']='new-york';o['source']='liberty';o['detail']=0
for obj in list(bpy.context.scene.objects):
 if obj!=o:bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(Path('build/south-strip/liberty-optimized.blend').resolve()))
print('OPTIMIZED',len(o.data.polygons),'triangles',flush=True)
# Four angles identify facing without guessing asset coordinates.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=600;s.render.resolution_y=800;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.6,.7,.8,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.7
l=bpy.data.lights.new('sun','SUN');l.energy=3;ob=bpy.data.objects.new('sun',l);s.collection.objects.link(ob);ob.rotation_euler=(.4,-.7,0)
cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam
for i in range(4):
 a=i*math.pi/2;cam.location=(75*math.sin(a),-75*math.cos(a),26);cam.rotation_euler=(Vector((0,0,24))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=50;s.render.filepath=str(Path('build/south-strip/liberty-angle-'+str(i)+'.png').resolve());bpy.ops.render.render(write_still=True)
