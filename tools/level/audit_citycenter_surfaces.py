"""Regression probes on the actual Blender render mesh, not collider overlaps.
Run with Blender -b --python tools/level/audit_citycenter_surfaces.py.
"""
import bpy, json, os, math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
# Test the first visible shell for the ceiling, shared partitions and gallery seams.
probes=[
 ('Aria north tower ceiling',(-300,2,408),(0,1,0),13.45),
 ('Aria south tower ceiling',(-350,2,421),(0,1,0),13.45),
 ('Aria clear ceiling',(-437,2,441),(0,1,0),13.45),
 ('Aria lobby shared partition',(-278,6,442),(-1,0,0),-281.725),
 ('Crystals connector west partition',(-278,6,399),(-1,0,0),-281.725),
 ('Crystals connector east partition',(-214,6,399),(1,0,0),-210.275),
 ('Crystals gallery bridge top',(-168,7,396),(0,-1,0),6.15),
 ('Crystals stair landing top',(-168,7,383),(0,-1,0),6.15),
 ('Crystals gallery bridge underside',(-168,2,396),(0,1,0),5.75),
 ('Crystals stair landing underside',(-168,2,383),(0,1,0),5.75),
 ('Crystals south escalator landing',(-101,7,448.7),(0,-1,0),6.15),
 ('Crystals north escalator landing',(-111,7,345.05),(0,-1,0),6.15),
 ('Crystals grand stair landing',(-163.6,7,383),(0,-1,0),6.15),
 ('Crystals marble floor',(-99,1,390),(0,-1,0),.075),
 ('Crystals opaque roof soffit',(-147,12,370),(0,1,0),None),
 ('Crystals glazed roof soffit',(-117,12,387),(0,1,0),None),
]
results=[]
for label, origin, direction, expected in probes:
 o=Vector((origin[0],-origin[2],origin[1]));d=Vector((direction[0],-direction[2],direction[1]));hits=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH' or not ob.name.startswith('CityCenter / '):continue
  me=ob.data;mat=ob.matrix_world
  # Matrix is identity for material batches, but retain correct transforms for signs.
  for f in me.polygons:
   normal=mat.to_3x3() @ f.normal
   if normal.dot(d)>-.001:continue
   vs=[mat @ me.vertices[i].co for i in f.vertices]
   axes=[a for a in range(3) if abs(d[a])<.5]
   if any(o[a]<min(v[a] for v in vs)-1e-5 or o[a]>max(v[a] for v in vs)+1e-5 for a in axes):continue
   for i in range(1,len(vs)-1):
    hit=intersect_ray_tri(vs[0],vs[i],vs[i+1],d,o,True)
    if hit is not None and (hit-o).dot(d)>.001:
     hits.append(((hit-o).length,ob.name,tuple(hit)));break
 hits.sort()
 assert hits, f'{label}: missing surface'
 first=hits[0];axis=next(i for i,v in enumerate(direction) if v);point=(first[2][0],first[2][2],-first[2][1])[axis]
 if expected is not None:assert abs(point-expected)<.002, f'{label}: wrong surface {point}, expected {expected}'
 # Two surfaces facing the observer within 3cm reproduce the reported flicker.
 assert len(hits)==1 or hits[1][0]-first[0]>.03, f'{label}: duplicate exposed surfaces {hits[:2]}'
 results.append(dict(probe=label,firstSurface=round(point,5),clearanceToNext=round(hits[1][0]-first[0],5) if len(hits)>1 else None,mesh=first[1]))
Path('build/citycenter/surface-audit.json').write_text(json.dumps(results,indent=2))
print('PASS: '+str(len(results))+' actual render-surface regression probes',flush=True)
