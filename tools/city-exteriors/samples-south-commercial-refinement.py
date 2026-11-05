import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import footprint,Point,np
for name,ident,y in [('south-commercial-364846558','way/364846558',8),('south-commercial-annex','way/364846559',4.5)]:
 p=footprint(ident).buffer(-.35);x0,z0,x1,z1=p.bounds
 rows=[[float(x),y,float(z)] for x in np.arange(x0,x1,.8) for z in np.arange(z0,z1,.8) if p.contains(Point(x,z))]
 Path('build/city-exteriors/'+name+'-samples.json').write_text(json.dumps(rows));print(name,len(rows))
