"""Export original FLEX surfaces, separately streamed room and shared PBR finishes."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
palette={'stucco':'666568','fascia':'45464a','roof':'777779','foundation':'858283','letter':'e8e7e4','awning':'25252b','metal':'686970','planter':'323337','leaf':'34452d','paving':'817c78','sign':'29282e','floor':'555558','ceiling':'252329','wall':'49464b','bar':'272329','frame':'202126','screen':'10151e','leather':'252329','stitch':'57515b','table':'3f302e','stone':'68656a','dark':'15141b','stage':'403a41','sink':'333740','red':'e63265','gold':'d7a338','green':'27ad65','blue':'568bfa','violet':'a642d2'}
for i,c in enumerate(['4e5055','585960','63636a','55565b']):palette['tile-'+str(i)]=c
for i,c in enumerate(['48494e','64646a','77757a']):palette['stone-'+str(i)]=c
for i,c in enumerate(['354d34','754530','685a36']):palette['bottle-'+str(i)]=c
E.colors.update({'fx-'+k:v for k,v in palette.items()})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('flex-twain-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.78
  if key in ['fx-metal','fx-sink']:bs.inputs['Metallic'].default_value=.75;bs.inputs['Roughness'].default_value=.3
  if key in ['fx-leather','fx-table'] or 'bottle' in key:bs.inputs['Roughness'].default_value=.34
  if key in ['fx-red','fx-gold','fx-green','fx-blue','fx-violet']:
   bs.inputs['Emission Color'].default_value=bs.inputs['Base Color'].default_value;bs.inputs['Emission Strength'].default_value=1.4
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('flex-twain-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('flex-twain-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED flex-twain-'+part)
