import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import footprint,Point,np,Meshes
import perception_museum
F=perception_museum.frame(Meshes())
plant=F.poly([(5.7,11),(13.5,11),(13.5,24),(5.7,24)])
for name,ident,y in [('wyoming-17-frontage','way/689003952',4.7),('perception-museum','way/364843228',7.7)]:
 p=footprint(ident).buffer(-.35);x0,z0,x1,z1=p.bounds
 rows=[[float(x),6.8 if name=='perception-museum' and plant.contains(Point(x,z)) else y,float(z)] for x in np.arange(x0,x1,.8) for z in np.arange(z0,z1,.8) if p.contains(Point(x,z))]
 Path('build/city-exteriors/'+name+'-samples.json').write_text(json.dumps(rows));print(name,len(rows))
