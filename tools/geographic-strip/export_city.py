import bpy,json,math,hashlib,sys,re
from pathlib import Path
from collections import defaultdict
import sys as _sys; _sys.path.insert(0, 'tools/lib'); from paths import python312 as PY312  # a Python 3.12 on this machine (tools/lib/paths.py)
OUT=Path('build/geographic-strip')
if '--preserve-surfaces' not in sys.argv and Path('build/resort-blocks/cosmo/version.json').exists():
 import runpy
 runpy.run_path('tools/resort-blocks/replace_chelsea_drive.py')
if '--preserve-surfaces' not in sys.argv and Path('build/resort-blocks/bellagio/south-arrival-report.json').exists():
 import runpy
 runpy.run_path('tools/resort-blocks/cut_bellagio_arrival.py')
if '--preserve-surfaces' not in sys.argv and Path('build/resort-blocks/bellagio/garage-report.json').exists():
 import runpy
 runpy.run_path('tools/resort-blocks/cut_bellagio_garage.py')
# Ground-level garden paths must not regain the importer's false bridge decks.
if '--preserve-surfaces' not in sys.argv and Path('build/strip-landmarks/flamingoGarden-exterior.glb').exists():
 import subprocess
 subprocess.run([PY312(), 'tools/city-exteriors/remove-flamingo-garden-raised-paths.py'], check=True)
# Preserve the reviewed ground service apron beside CVS after intentional city regeneration.
if '--preserve-surfaces' not in sys.argv and Path('build/city-exteriors/cvs-east-apron-cut.json').exists():
 import subprocess
 subprocess.run([PY312(), 'tools/city-exteriors/replace-cvs-east-apron.py'], check=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
colors={'road':(.09,.105,.12),'paving':(.58,.56,.51),'verge':(.38,.36,.29),'plaza':(.46,.44,.40),'paint':(.77,.75,.63),'building-tagged':(.57,.59,.58),'building-estimated':(.62,.57,.49),'utility':(.44,.44,.41),'ground':(.29,.27,.23)}
materials={}
colors.update({'sidewalk':(.60,.58,.53),'gutter':(.40,.41,.40),'yellow-paint':(.86,.60,.12),'bridge-deck':(.55,.53,.49),'bridge-concrete':(.63,.62,.57),'bridge-metal':(.30,.34,.36),'bridge-light':(.91,.95,1),'bridge-glass':(.47,.67,.72),'bridge-roof':(.52,.55,.57)})
colors.update({'grass':(.095,.19,.043),'planting':(.12,.16,.055),'woodland':(.10,.145,.045),'gravel':(.39,.285,.18),'shrub':(.075,.16,.042),'median-curb':(.57,.55,.49)})
for name,color in colors.items():
 m=bpy.data.materials.new('OSM / '+name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.86;materials[name]=m
 if name=='bridge-metal':bs.inputs['Metallic'].default_value=.7;bs.inputs['Roughness'].default_value=.3
 if name=='bridge-glass':
  m.diffuse_color=(*color,.23);bs.inputs['Alpha'].default_value=.23;bs.inputs['Roughness'].default_value=.16;m.surface_render_method='DITHERED';m.use_backface_culling=False
 if name=='bridge-light':bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=2
for name,style in json.loads((OUT/'city-materials.json').read_text()).items():
 hexcolor=style['color'].lstrip('#');rgb=tuple(int(hexcolor[i:i+2],16)/255 for i in (0,2,4))
 m=bpy.data.materials.new('OSM / '+name);m.diffuse_color=(*rgb,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=.32 if style['material'] in ('glass','mirror') else .82;bs.inputs['Metallic'].default_value=.25 if style['material'] in ('glass','mirror','steel') else 0;materials[name]=m
# Rendering uses broad 800 m batches; collision residency uses independent
# 160 m cells. The two budgets are intentionally not tied together.
groups={}
for g in json.loads((OUT/'city-meshes.json').read_text()):
 cell=g['cell'];mat=g['material'];key='base' if cell=='base' else ','.join(str(math.floor(int(v)/5)) for v in cell.split(','))
 v,f=groups.setdefault((key,mat),([],[]));offset=len(v);v.extend((p[0],-p[2],p[1]) for p in g['vertices']);f.extend(tuple(offset+i for i in face) for face in g['faces'])
for (cell,mat),(v,f) in groups.items():
 # The generator emits independent primitives. Share coincident vertices
 # before export so a paved block does not store each junction many times.
 unique=[];lookup={};remap=[]
 for p in v:
  key=tuple(round(x,4) for x in p)
  if key not in lookup:lookup[key]=len(unique);unique.append(key)
  remap.append(lookup[key])
 f=[tuple(remap[i] for i in face) for face in f];f=[face for face in f if len(set(face))==3];v=unique
 me=bpy.data.meshes.new('OSM '+cell+' '+mat);me.from_pydata(v,[],f);me.update();me.materials.append(materials[mat]);obj=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(obj);obj['osmCell']=cell;obj['osmMaterial']=mat
 if mat in ('road','sidewalk','bridge-deck','median-curb','grass','planting','woodland','gravel'):
  uv=me.uv_layers.new(name='Metre grid')
  for loop in me.loops:
   p=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x/4,-p.y/4)
# Spatial runtime export is the default; --combined is retained for controlled comparisons.
if '--combined' not in sys.argv:
 # Split before compression: whole-city meshopt streams share buffer views across
 # cells, so copying those streams would duplicate unrelated geometry per file.
 # Keep the established group/material geometry and export each existing cell.
 cell_out=OUT/'cells';cell_out.mkdir(parents=True,exist_ok=True)
 cells=defaultdict(list)
 for obj in bpy.context.scene.objects:
  cells[obj['osmCell']].append(obj)
 # glTF export uses natural name ordering, not scene insertion order.
 node_order=sorted((obj.name for obj in bpy.context.scene.objects),key=lambda name:[int(t) if t.isdigit() else t for t in re.split(r'(\d+)',name)])
 manifest=[]
 for cell,objects in sorted(cells.items()):
  bpy.ops.object.select_all(action='DESELECT')
  for obj in objects:obj.select_set(True)
  name=('base' if cell=='base' else 'cell-'+cell.replace(',','_'))+'.glb'
  target=cell_out/name
  bpy.ops.export_scene.gltf(filepath=str(target.resolve()),use_selection=True,export_format='GLB',export_yup=True,export_lights=False,export_cameras=False,export_extras=True)
  data=target.read_bytes()
  manifest.append(dict(cell=cell,file=name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
 (cell_out/'manifest.json').write_text(json.dumps(dict(version=1,cellSize=800,cells=manifest,nodeOrder=node_order),indent=2)+'\n')
 print('CITY CELLS EXPORTED',len(cells),'cells',len(groups),'batches',flush=True)
else:
 bpy.ops.wm.save_as_mainfile(filepath=str((OUT/'city.blend').resolve()))
 bpy.ops.export_scene.gltf(filepath=str((OUT/'city.glb').resolve()),export_format='GLB',export_yup=True,export_lights=False,export_cameras=False,export_extras=True)
 (OUT/'city-version.json').write_text(json.dumps(dict(revision=hashlib.sha256((OUT/'city.glb').read_bytes()).hexdigest()[:16],batches=len(groups))))
 print('CITY EXPORTED',len(groups),'batches',flush=True)
