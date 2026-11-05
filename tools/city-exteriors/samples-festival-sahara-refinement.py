import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from forum_shops import facade_frame
for name,ident,y in [('festival-grounds-service','way/568597552',4.9),('mcdonalds-sahara-canopy','way/1414999331',5.03)]:
 p=footprint(ident).buffer(-.35);x0,z0,x1,z1=p.bounds
 rows=[[float(x),y,float(z)] for x in np.arange(x0,x1,.8) for z in np.arange(z0,z1,.8) if p.contains(Point(x,z))]
 Path('build/city-exteriors/'+name+'-samples.json').write_text(json.dumps(rows));print(name,len(rows))
p=footprint('way/1414999331');B=Meshes();edges=[facade_frame(B,a,b,p,0)for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])];F,L,_,_=max([e for e in edges if e[3]>.6],key=lambda e:e[1]);depth=max((z-F.z)*F.co+(x-F.x)*F.si for x,z in p.exterior.coords)
routes=[[F.p(u,.18,.6),F.p(u,.18,depth*.55),F.p(u,.18,depth-1.6)]for u in [L*.25,L*.5,L*.75]]
Path('build/city-exteriors/mcdonalds-sahara-canopy-stairs.json').write_text(json.dumps(routes))
