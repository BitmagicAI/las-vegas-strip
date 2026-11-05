import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import footprint,Point,np,unary_union
for name,idents,y in [('rexford-ellen-courtyard',['way/1236725808','way/1236725807'],7.2),('casino-center-1520',['relation/9575763'],7.2)]:
 p=unary_union([footprint(i) for i in idents]).buffer(-.35);x0,z0,x1,z1=p.bounds
 rows=[[float(x),y,float(z)] for x in np.arange(x0,x1,.8) for z in np.arange(z0,z1,.8) if p.contains(Point(x,z))]
 Path('build/city-exteriors/'+name+'-samples.json').write_text(json.dumps(rows));print(name,len(rows))
