"""Batch the preserved source in its original coordinates, then georeference
positions. Classification therefore never depends on distorted/world AABBs."""
import bpy,sys,json,os,math
from pathlib import Path
import numpy as np
import sys as _sys; _sys.path.insert(0, 'tools/lib'); from paths import python312 as PY312  # a Python 3.12 on this machine (tools/lib/paths.py)
sys.path.insert(0,'tools/geographic-strip')
import mapping
# Reuse the audited portal/mesh classifier, without changing its legacy output.
s=Path('tools/level/visibility_export.py').read_text()
s=s.replace('import bpy,json,os,re,math,hashlib','import bpy,json,os,re,math,hashlib\nimport mapping')
s=s.replace("g=groups.setdefault(key,dict(v=[],f=[],uv=[],smooth=[]))", "geo=mapping.owner(obj.name,(lo+hi)/2) or mapping.owner('',(lo+hi)/2)\n   if not geo or geo=='cosmopolitan':continue\n   key=(*key,geo)\n   g=groups.setdefault(key,dict(v=[],f=[],uv=[],smooth=[]))")
s=s.replace("g['v'].extend(tuple(world[i]) for i in used)", "g['v'].extend((q[0],-q[2],q[1]) for i in used for q in [mapping.point(game[i],geo)])")
s=s.replace("for (zone,kind,material,tower,cell),g in groups.items():", "for (zone,kind,material,tower,cell,geo),g in groups.items():")
s=s.replace("name=f'VIS_{zone}_{kind}_{material}_{tower}'", "name=f'VIS_{zone}_{kind}_{material}_{tower}_{geo}'")
s=s.replace("o['visibilityKind']=kind;", "o['visibilityKind']=kind;o['geographicOwner']=geo;")
s=s.replace("if tower:o['visibilityTower']=tower", "if tower:o['visibilityTower']=tower\n  if geo.startswith('veer-') and tower:o['visibilityTower']=geo")
ns={};exec(compile(s,'geographic_visibility_export','exec'),ns)
bpy.ops.wm.open_mainfile(filepath=str(mapping.BASE/'build/hotels/staged-vegas.blend'))
from carve_veer import carve_meshes
carve_meshes()
# Old invented district roads and large flat grounds must never survive below
# the mapped street network. Preserve named property architecture and fixtures.
removed=[]
for o in list(bpy.data.objects):
 n=o.name.lower()
 if o.type!='MESH':continue
 if any(t in n for t in ['district ground','citycenter / streets','continuous foundation','district edge']) or n.startswith(('lamp arm','lamp post','lamp bulb','streetlight','street palm','sidewalk palm')):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Both Veer towers share material batches. Split polygons at their authored gap
# before choosing transforms; this is ownership, not geometric simplification.
for o in list(bpy.data.objects):
 if o.type!='MESH' or 'CityCenter / Veer /' not in o.name:continue
 me=o.data;co=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',co);co=co.reshape((-1,3));w=co@np.array(o.matrix_world)[:3,:3].T+np.array(o.matrix_world)[:3,3]
 for key,right in [('veer-east',True),('veer-west',False)]:
  ps=[p for p in me.polygons if (w[list(p.vertices),0].mean()>-157)==right]
  if not ps:continue
  used=sorted({i for p in ps for i in p.vertices});idx={v:i for i,v in enumerate(used)}
  m=bpy.data.meshes.new(key);m.from_pydata([tuple(co[i]) for i in used],[],[tuple(idx[i] for i in p.vertices) for p in ps]);m.update()
  for mat in me.materials:m.materials.append(mat)
  uv=m.uv_layers.new();data=[tuple(me.uv_layers.active.data[i].uv) if me.uv_layers.active else (0,0) for p in ps for i in p.loop_indices];uv.data.foreach_set('uv',[c for v in data for c in v])
  for p,old in zip(m.polygons,ps):p.material_index=old.material_index;p.use_smooth=old.use_smooth
  obj=bpy.data.objects.new(o.name+' '+key,m);bpy.context.scene.collection.objects.link(obj);obj.matrix_world=o.matrix_world
  for k,v in o.items():obj[k]=v
 bpy.data.objects.remove(o,do_unlink=True)
ns['export_visibility']('build/geographic-strip/detailed.glb',data_path=str(mapping.BASE/'build/hotels/staged-vegas.mesh-level.json'),manifest_path='build/geographic-strip/source-visibility.json',stats_path='build/geographic-strip/detailed-stats.json',version_path='build/geographic-strip/detailed-version.json',interior_cell=16)
Path('build/geographic-strip/removed-invented-streets.json').write_text(json.dumps(removed))
print('GEOGRAPHIC DETAILED EXPORT DONE',flush=True)

# Reapply the local exterior owner after a deliberate legacy re-export.
if Path("build/strip-landmarks/planetHollywood-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-planet.py")

# Preserve the authored Waldorf exterior owner after legacy regeneration.
if Path("build/strip-landmarks/waldorfExterior-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-waldorf.py")

# Preserve mapped Caesars tower ownership and its existing guest-core fit.
if Path("build/strip-landmarks/caesarsExterior-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-caesars.py")

# Retain the mapped Flamingo wings, marquee and fitted existing guest core.
if Path("build/strip-landmarks/flamingoExterior-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-flamingo.py")
 if Path("tools/city-exteriors/install-flamingo-podium.py").exists():runpy.run_path("tools/city-exteriors/install-flamingo-podium.py")
 runpy.run_path("tools/city-exteriors/install-horseshoe.py")

# Preserve the reviewed Crystals folded roof when regenerating legacy shells.
if Path("build/strip-landmarks/crystalsRoof-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-crystals-roof.py")

# Preserve the separate 63 CityCenter exterior ownership at the north boundary.
if Path("build/strip-landmarks/citycenter63-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/trim-crystals-63.py")

# Preserve the mapped upper Crystals lift exit after an intentional legacy export.
if Path("build/strip-landmarks/crystalsPedestrianLift-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/open-crystals-lift-portal.py")

# Keep the mapped outdoor garden clear after re-exporting retained casino data.
if Path("build/strip-landmarks/flamingoGarden-exterior.glb").exists():
 import subprocess
 subprocess.run([PY312(), "tools/city-exteriors/cut-flamingo-garden.py"],check=True)

# Preserve the April2025 Versailles south-frontage decorative replacement.
if Path("build/city-exteriors/versailles-south-cut.json").exists():
 import subprocess
 subprocess.run([PY312(), "tools/city-exteriors/replace-versailles-south-frontage.py"],check=True)
