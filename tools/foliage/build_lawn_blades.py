"""Short upright mown grass: opaque tapered blades, no alpha cards or twig mesh."""
import bpy,math,random,json
from pathlib import Path
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
rng=random.Random(8106)
blades=[]
for i in range(24):
 a=rng.random()*math.tau;r=.11*math.sqrt(rng.random())
 blades.append((math.cos(a)*r,math.sin(a)*r,rng.uniform(.18,.32),rng.uniform(.004,.009),rng.random()*math.tau))
mat=bpy.data.materials.new('Matte living lawn blades');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.19,.30,.075,1);bs.inputs['Roughness'].default_value=1;bs.inputs['Metallic'].default_value=0
bs.inputs['Emission Color'].default_value=(.08,.12,.025,1);bs.inputs['Emission Strength'].default_value=.3
color=mat.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='Blade greens'
mat.node_tree.links.new(color.outputs['Color'],bs.inputs['Base Color'])
mat.use_backface_culling=False
report=[]
for level in range(2):
 verts=[];faces=[]
 for x,y,h,w,a in (blades if level==0 else blades[::3]):
  dx,dy=math.cos(a)*w,math.sin(a)*w;bx,by=-math.sin(a)*h*.13,math.cos(a)*h*.13;k=len(verts)
  if level==0:
   verts.extend([(x-dx,y-dy,0),(x+dx,y+dy,0),(x-dx*.6+bx*.4,y-dy*.6+by*.4,h*.58),(x+dx*.6+bx*.4,y+dy*.6+by*.4,h*.58),(x+bx,y+by,h)])
   faces.extend([(k,k+1,k+2),(k+1,k+3,k+2),(k+2,k+3,k+4)])
  else:
   verts.extend([(x-dx,y-dy,0),(x+dx,y+dy,0),(x+bx,y+by,h)]);faces.append((k,k+1,k+2))
 mesh=bpy.data.meshes.new('Mown grass');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat)
 colors=mesh.color_attributes.new(name='Blade greens',type='FLOAT_COLOR',domain='POINT')
 for i,v in enumerate(mesh.vertices):
  t=min(1,v.co.z/.32);variation=.85+.3*rng.random();colors.data[i].color=((.075+.13*t)*variation,(.20+.19*t)*variation,(.018+.045*t)*variation,1)
 o=bpy.data.objects.new('Mown grass LOD'+str(level),mesh);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(Path('public/foliage/grass-'+str(level)+'.glb').resolve()),export_format='GLB',use_selection=True,export_yup=True)
 report.append(dict(level=level,triangles=len(faces),blades=24 if level==0 else 8));bpy.data.objects.remove(o,do_unlink=True)
Path('public/foliage/grass-manifest.json').write_text(json.dumps(dict(kind='mown-grass',source='tools/foliage/build_lawn_blades.py',lods=report),indent=2))
