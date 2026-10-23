import bpy,json,math,hashlib,numpy as np
from pathlib import Path
OUT=Path('build/sphere');meta=json.loads((OUT/'sphere.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for name,(color,metal,rough,glow) in meta['materials'].items():
 srgb=[int(color[i:i+2],16)/255 for i in (1,3,5)];rgb=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in srgb);m=bpy.data.materials.new('Sphere / '+name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if glow:bs.inputs['Emission Color'].default_value=(*rgb,1);bs.inputs['Emission Strength'].default_value=glow
 if name=='glass':bs.inputs['Alpha'].default_value=.24;m.surface_render_method='DITHERED';m.use_backface_culling=False
 if name=='terrazzo':
  rng=np.random.default_rng(71);pixels=np.ones((512,512,4),dtype=np.float32);base=np.array([22,30,38])/255;pixels[:,:,:3]=base+rng.uniform(-.012,.012,(512,512,1));flecks=rng.random((512,512))<.07;pixels[flecks,:3]*=rng.uniform(1.3,2.1,(int(flecks.sum()),1));im=bpy.data.images.new('Sphere black terrazzo',512,512);im.pixels.foreach_set(pixels.ravel());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 if name in ['shell','screen']:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str((OUT/('exosphere-poster.jpg' if name=='shell' else 'immersive-poster.jpg')).resolve()));m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.9;bs.inputs['Base Color'].default_value=(0,0,0,1)
 materials[name]=m
for section in ['exterior','interior']:
 data=json.loads((OUT/(section+'.json')).read_text());bpy.ops.object.select_all(action='DESELECT')
 for part in data['meshes']:
  mat=part['material'];me=bpy.data.meshes.new(section+' / '+mat);me.from_pydata([(x,-z,y) for x,y,z in part['vertices']],[],part['faces']);me.materials.append(materials[mat]);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);o['spherePart']=mat;o['sphereSection']=section;o.select_set(True)
  uv=me.uv_layers.new()
  for loop in me.loops:uv.data[loop.index].uv=part['uv'][loop.vertex_index]
  if mat in ['shell','screen']:
   for p in me.polygons:p.use_smooth=True
 bpy.ops.export_scene.gltf(filepath=str((OUT/(section+'.glb')).resolve()),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
# Seats and signs in the editable review scene; runtime uses four shared instanced meshes.
seatparts=[((0,.43,0),(.48,.13,.48),'seat'),((0,.83,-.20),(.49,.77,.13),'seat'),((0,.18,0),(.12,.36,.30),'dark-metal')]
seatmeshes=[]
for p,size,mat in seatparts:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0));o=bpy.context.object;o.scale=size[0],size[2],size[1];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(materials[mat]);seatmeshes.append((o.data.copy(),p));bpy.data.objects.remove(o,do_unlink=True)
# Only review a spaced subset to keep editable scene light; full runtime has all seats.
for j,(x,y,z,yaw,tier) in enumerate(meta['seats']):
 if j%2:continue
 for me,p in seatmeshes:
  o=bpy.data.objects.new('Seat',me);bpy.context.collection.objects.link(o);xx=p[0]*math.cos(yaw)+p[2]*math.sin(yaw);zz=-p[0]*math.sin(yaw)+p[2]*math.cos(yaw);o.location=(x+xx,-z-zz,y+p[1]);o.rotation_euler[2]=yaw
for s in meta['signs']:
 for side in [0,1]:
  yaw=s['yaw']+side*math.pi;cu=bpy.data.curves.new('Wayfinding','FONT');cu.body=s['text'];cu.align_x='CENTER';cu.align_y='CENTER';cu.size=s['height']*.8;cu.extrude=.001;o=bpy.data.objects.new(cu.name,cu);bpy.context.collection.objects.link(o);x,y,z=s['p'];o.location=(x+.15*math.sin(yaw),-z-.15*math.cos(yaw),y);o.rotation_euler=(math.pi/2,0,yaw);cu.materials.append(materials['white-light'])
bpy.ops.wm.save_as_mainfile(filepath=str((OUT/'sphere.blend').resolve()))
(OUT/'version.json').write_text(json.dumps({'revision':hashlib.sha256((OUT/'exterior.glb').read_bytes()+(OUT/'interior.glb').read_bytes()+(OUT/'sphere.json').read_bytes()).hexdigest()[:12]}))
print('Sphere exported',flush=True)
