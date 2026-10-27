"""Original material maps and metre-space UVs for the Naked City facade."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'nc-stucco':'9c9988','nc-roof':'8e8e82','nc-frame':'8d9085','nc-glass':'293a3c','nc-joint':'858274','nc-dark':'292c28','nc-red':'a12e36','nc-fabric':'873e47','nc-letter':'d7d4c5','nc-awning':'b8987e','nc-metal':'777a70','nc-steel':'a0a299','nc-wood':'927052','nc-bulb':'d8c997','nc-lamp':'c3c0ac','nc-concrete':'949486','nc-soil':'3e382e','nc-leaf':'596d39'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('nakedCity-exterior')
y,x=np.mgrid[:512,:512];rng=np.random.default_rng(246)
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.87
 if key=='nc-glass':bs.inputs['Roughness'].default_value=.26;bs.inputs['Metallic'].default_value=.25
 if key=='nc-bulb':bs.inputs['Emission Color'].default_value=bs.inputs['Base Color'].default_value;bs.inputs['Emission Strength'].default_value=.6
 if key not in ['nc-stucco','nc-awning','nc-fabric','nc-wood','nc-concrete']:continue
 c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
 noise=(rng.random((512,512))-.5)*.10;s=1+noise
 if key=='nc-wood':s=.97+.035*np.sin(y*.3+np.sin(x*.035))+noise*.5
 if key=='nc-awning':s=.96+.08*np.sin(x*.028)*np.sin(y*.019)+noise*.35
 if key=='nc-fabric':s=1+noise*.3
 rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=np.clip(s[:,:,None]*c,0,1)
 im=bpy.data.images.new('Original '+key,width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
for o in bpy.context.scene.objects:
 if o.type=='FONT':
  fp=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
  if fp.exists():o.data.font=bpy.data.fonts.load(str(fp),check_existing=True)
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]))
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else(q.x*.5,q.y*.5)
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'nakedCity-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'nakedCity-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED nakedCity-exterior')
