"""Regression audit of generated surfaces, including the installed city bridge source.
Run with the project Python 3.12. Opposing/internal cap faces are deliberately not
labelled visual defects; test the independently authored floor and facade owners.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,'build/south-strip/python');sys.path.insert(0,'tools/film')
import numpy as np
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from collections import defaultdict
from clearance import triangles
from remove_old_rialto import fixture
meshes=json.load(open('build/strip-landmarks/venetian-exterior.json'))['meshes']
pairs=[('venetian-canal-plaza/plaza-paving-dark','venetian-palace/marble'),('venetian-canal-plaza/plaza-paving-dark','venetian-podium/tile'),('venetian-palace/marble','venetian-podium/tile'),('palazzo-front/plaster','venetian-podium/pinkstone')]
names={n for pair in pairs for n in pair};planes=defaultdict(list)
for tower in ['tower/way/111322067','tower/way/30618090']:
 for material in ['pinkstone','ivory']:pairs.append((tower+'/ivory','venetian-podium/'+material))
pairs.extend([('venetian-north-frontage/ivory','venetian-podium/pinkstone'),('palazzo-front/blackiron','palazzo-front/champagne')])
names={n for pair in pairs for n in pair}
for g in meshes:
 name=g['source']+'/'+g['material']
 if name not in names:continue
 T=np.asarray(g['vertices'])[g['faces']];N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);size=np.linalg.norm(N,axis=1)
 for t,n in zip(T[size>1e-7],N[size>1e-7]/size[size>1e-7,None]):
  ax=int(np.argmax(abs(n)));n*=np.sign(n[ax]);key=(*np.round(n,4),round(float(n@t[0]),3));p=Polygon(np.delete(t,ax,axis=1));planes[key].append((name,p))
areas={tuple(sorted(p)):0. for p in pairs}
for rows in planes.values():
 tree=STRtree([p for n,p in rows])
 for i,(a,p) in enumerate(rows):
  for j in tree.query(p):
   if j<=i:continue
   b,q=rows[j];pair=tuple(sorted((a,b)))
   if pair in areas:areas[pair]+=p.intersection(q).area
T,L,N=triangles('build/geographic-strip/city.glb');legacy=0
for i,name in enumerate(N):
 if 'OSM / bridge-' not in name:continue
 ts=T[L==i];c=ts.mean(1);ts=ts[(c[:,0]>168)&(c[:,0]<229)&(c[:,2]>-696)&(c[:,2]<-607)]
 legacy+=sum(fixture(t) for t in ts)
report={'independentSurfaceOverlapM2':{' versus '.join(k):v for k,v in areas.items()},'legacyBridgeTrianglesInReplacementCorridors':int(legacy)}
Path('build/strip-landmarks/venetian-overlap-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert max(areas.values())<.001 and legacy==0
