"""Local Blender export using the shared authored material library."""
import sys,runpy,json,hashlib,argparse
parser=argparse.ArgumentParser();parser.add_argument("--only",help="Comma-separated exact asset names");args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
sys.path.insert(0,"tools/resort-blocks")
import cosmo_palette
from pathlib import Path
ns=runpy.run_path('tools/strip-landmarks/export.py',run_name='resort_materials')
ns['colors']['cosmo-mirror']='74828e'
ns['colors'].update(cosmo_palette.COLORS)
base_material=ns['material']
def cosmo_material(k):
 m=base_material(k)
 if k=='cosmo-mirror':
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.92;bs.inputs['Roughness'].default_value=.095
 if k in ['cm-glass','cm-glass-light']:
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.28;bs.inputs['Roughness'].default_value=.23
 return m
ns['add'].__globals__['material']=cosmo_material
ns['add'].__globals__['OUT']=Path('build/resort-blocks/cosmo')
bpy=ns['bpy'];out=ns['add'].__globals__['OUT']
for venue in json.loads((out/'venues.json').read_text()):
 for layer in ['exterior','interior']:
  name=venue['key']+'-'+layer
  if args.only and name not in args.only.split(','):continue
  bpy.ops.wm.read_factory_settings(use_empty=True);ns['materials'].clear();ns['add'](name)
  bpy.ops.wm.save_as_mainfile(filepath=str((out/(name+'.blend')).resolve()))
  bpy.ops.export_scene.gltf(filepath=str((out/(name+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for p in sorted(out.glob('*.glb')):h.update(p.read_bytes())
h.update((out/'venues.json').read_bytes());(out/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
