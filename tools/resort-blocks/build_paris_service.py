"""Surgical Paris rear podium dressing from Earth2022 and owner conference plan.
Keeps the ballroom shell, all interiors, public routes and collision intact.
"""
import sys,copy,json,math
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from forum_shops import facade_frame
import common
out=Path('build/resort-blocks/paris');common.OUT=out;name='parisBlock-exterior'
backup=Path('.bitmagic/city-exterior-backups/paris-service-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
for suffix in ['.json','-collision.json']:
 p=out/(name+suffix)
 if not (backup/p.name).exists():(backup/p.name).write_bytes(p.read_bytes())
old=json.loads((backup/(name+'.json')).read_text());B=Meshes();B.property=name
for g in old['meshes']:
 g=copy.deepcopy(g)
 if g['source'].startswith('podium-structure@') and g['material']=='roof':g['material']='paris-membrane-paint'
 B.groups[(g['property'],g['source'],g['material'],g['detail'])]=g
B.labels=old['labels'];B.solids[name]=json.loads((backup/(name+'-collision.json')).read_text())
N=Meshes();N.property=name;N.source='podium-service-detail';site=footprint('way/33974140');tower=footprint('way/27831697');Y=10.65
roof=site.intersection(box(285,330,374,509)).difference(tower.buffer(4))
# Low perimeter coping and broad wall courses. No invented windows on ballrooms.
for poly in parts(site):
 pts=list(poly.exterior.coords)
 for a,b in zip(pts,pts[1:]):
  if min(a[0],b[0])<285 or math.dist(a,b)<1:continue
  F,L,nx,nz=facade_frame(N,a,b,site,0)
  N.detail=0
  F.box('paris-stone',(L/2,Y+.32,.04),(L,.64,.50))
  F.box('paris-service-metal',(L/2,Y+.68,.04),(L+.03,.08,.64))
  N.detail=1
  for y in [.8,4.2,7.4,10.0]:F.box('paris-joint',(L/2,y,-.045),(L,.045,.035))
  for x in np.arange(3,L,7.5):F.box('paris-joint',(x,5.1,-.05),(.045,9.6,.04))
# A few edge-mounted plant units and small exhaust stacks as seen in the aerial.
N.detail=1
for x,z in [(298,340),(300,355),(301,484),(322,488),(347,488),(352,338)]:
 if not roof.contains(box(x-2,z-1.3,x+2,z+1.3)):continue
 N.box('paris-service-metal',(x,Y+.68,z),(3.8,1.2,2.3))
 N.box('paris-iron',(x,Y+1.31,z),(3.5,.05,2.05))
 for dx in [-.9,.9]:N.lathe('paris-service-metal',(x+dx,z),[(Y+1.34,.66),(Y+1.42,.66)],12)
for x,z in [(321,367),(344,397),(319,452),(357,466)]:
 if not roof.contains(Point(x,z).buffer(.5)):continue
 N.lathe('paris-service-metal',(x,z),[(Y,.18),(Y+.65,.18),(Y+.66,.32),(Y+.74,.32)],10)
# Wide roof expansion seams, clipped to the membrane and away from tower/pool.
for z in [365,402,439,476]:N.planar('paris-service-joint',roof.intersection(box(285,z-.025,375,z+.025)),Y+.025)
# Same64m cells as the existing block. This remains static batched geometry.
for g in N.groups.values():
 for f in g['faces']:
  pts=[g['vertices'][i] for i in f];x=sum(p[0] for p in pts)/3;z=sum(p[2] for p in pts)/3
  key=(name,g['source']+f'@{math.floor(x/64)}_{math.floor(z/64)}',g['material'],g['detail'])
  dest=B.groups.setdefault(key,dict(property=name,source=key[1],material=g['material'],detail=g['detail'],vertices=[],faces=[]));n=len(dest['vertices']);dest['vertices'].extend(pts);dest['faces'].append([n,n+1,n+2])
B.save_all();print('Paris service',sum(len(g['faces']) for g in N.groups.values()),'newtri',len(B.groups),'total batches')
