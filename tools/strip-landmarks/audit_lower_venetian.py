"""Find independent coplanar lower-facade owners; report, do not hide geometry."""
import sys,json
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
import numpy as np
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from collections import defaultdict
planes=defaultdict(list)
for asset in ['venetian-exterior','venetian-interior']:
 for g in json.load(open('build/strip-landmarks/'+asset+'.json'))['meshes']:
  T=np.asarray(g['vertices'])[g['faces']]
  T=T[(T[:,:,1].min(1)<18)&(T[:,:,1].max(1)>.1)]
  N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);size=np.linalg.norm(N,axis=1)
  for t,n in zip(T[size>.06],N[size>.06]/size[size>.06,None]):
   ax=int(np.argmax(abs(n)));n*=np.sign(n[ax]);key=(*np.round(n,4),round(float(n@t[0]),3))
   name=asset+'/'+g['source']+'/'+g['material']
   planes[key].append((name,Polygon(np.delete(t,ax,axis=1))))
areas=defaultdict(float);examples={}
for key,rows in planes.items():
 tree=STRtree([p for n,p in rows])
 for i,(a,p) in enumerate(rows):
  for j in tree.query(p):
   if j<=i:continue
   b,q=rows[j]
   if a==b:continue
   ar=p.intersection(q).area
   if ar<.01:continue
   pair=' vs '.join(sorted((a,b)));areas[pair]+=ar;examples[pair]=key
report=[dict(pair=p,areaM2=round(a,3),plane=examples[p]) for p,a in sorted(areas.items(),key=lambda x:-x[1])]
Path('build/strip-landmarks/lower-overlap-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report[:40],indent=2))
