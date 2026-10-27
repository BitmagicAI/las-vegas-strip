"""Original material maps and metre-space UVs for Ferraro’s exterior."""
import bpy,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'fr-stucco': '9e9687', 'fr-roof': 'a4a49a', 'fr-trim': 'b4ad98', 'fr-mortar': '827c6a', 'fr-stone0': 'a39072', 'fr-stone1': 'b3a184', 'fr-stone2': '8f826b', 'fr-glass': '36403e', 'fr-metal': '3f423b', 'fr-blind': '9c9877', 'fr-fabric': 'b9b58d', 'fr-stripe': '626952', 'fr-limestone': 'd0cbb6', 'fr-joint': 'b1ac98', 'fr-inset': 'aaa38a', 'fr-letter': '4b4c3e', 'fr-plaque': '51677d', 'fr-paving': 'b4b1a6', 'fr-patio': '6b6d62', 'fr-planter': '69685d', 'fr-leaf': '68764e', 'fr-counter': '77796f', 'fr-charcoal': '363936', 'fr-cushion': 'a3604d', 'fr-equipment': 'a4a79b'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('ferraros-exterior')
y,x=np.mgrid[:512,:512];rng=np.random.default_rng(248)
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.87
 if key=='fr-glass':bs.inputs['Roughness'].default_value=.26;bs.inputs['Metallic'].default_value=.25
 if not key.startswith('fr-stone') and key not in ['fr-stucco','fr-paving','fr-patio','fr-limestone']:continue
 c=np.array([int(E.colors[key][i:i+2],16)/255 for i in [0,2,4]])
 noise=(rng.random((512,512))-.5)*.10;s=1+noise
 rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=np.clip(s[:,:,None]*c,0,1)
 im=bpy.data.images.new('Original '+key,width=512,height=512);im.pixels.foreach_set(rgba.flatten());im.pack()
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
for o in bpy.context.scene.objects:
 if o.type=='FONT':
  fp=Path('/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf' if o.data.body=='Ferraro’s' else '/System/Library/Fonts/Supplemental/Arial Bold.ttf')
  if fp.exists():o.data.font=bpy.data.fonts.load(str(fp),check_existing=True)
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]))
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.y*.5,q.z*.5) if axis==0 else (q.x*.5,q.z*.5) if axis==1 else(q.x*.5,q.y*.5)
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'ferraros-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'ferraros-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED ferraros-exterior')
