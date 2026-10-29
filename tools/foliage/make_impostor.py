"""Distant tree retains photographic alpha silhouette at 6 triangles."""
import bpy,math,json
from pathlib import Path
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Use the actual normalized model dimensions and rendered alpha proof.
bpy.ops.import_scene.gltf(filepath=str(Path('tools/foliage/models/tree-0.glb').resolve()))
from mathutils import Vector
points=[o.matrix_world@Vector(v) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.bound_box]
h=max(p.z for p in points);w=max(max(p.x for p in points)-min(p.x for p in points),max(p.y for p in points)-min(p.y for p in points))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Proof frame includes a 1.35 margin. Preserve it rather than stretching crown.
height=max(h,w)*1.35;width=height*800/900
mat=bpy.data.materials.new('Distant canopy silhouette');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(Path('tools/foliage/models/tree-proof.png').resolve()))
mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha']);bs.inputs['Roughness'].default_value=1
mat.surface_render_method='DITHERED';mat.use_backface_culling=False
for i in range(3):
 a=i*math.pi/3;dx,dy=math.cos(a)*width/2,math.sin(a)*width/2
 mesh=bpy.data.meshes.new('canopy');mesh.from_pydata([(-dx,-dy,h*.48-height/2),(dx,dy,h*.48-height/2),(dx,dy,h*.48+height/2),(-dx,-dy,h*.48+height/2)],[],[(0,1,2,3)]);mesh.materials.append(mat)
 uv=mesh.uv_layers.new();
 for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
 o=bpy.data.objects.new('Distant tree card',mesh);bpy.context.collection.objects.link(o)
bpy.ops.export_scene.gltf(filepath=str(Path('tools/foliage/models/tree-2.glb').resolve()),export_format='GLB')
p=Path('tools/foliage/models/tree-manifest.json');d=json.loads(p.read_text());d['lods']=[lod for lod in d['lods'] if lod['level']!=2];d['lods'].append(dict(level=2,triangles=6,materials=1,method='three intersecting alpha silhouette cards'));p.write_text(json.dumps(d,indent=2))
