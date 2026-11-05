import sys,json,math
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from shapely.geometry import shape
G=Frame(Meshes(),1917.7103,-3789.8341,yaw=math.atan2(12.47194,32.0537),y=0)
env=G.poly([(-1,0),(35,0),(35,18),(-1,18)])
blocked=unary_union([shape(f['geometry']).intersection(env) for f in json.loads(Path('build/geographic-strip/surface-layers.geojson').read_text())['features'] if f['properties']['kind'] in ['road','sidewalk']])
orig=G.poly([(-1,0),(35,0),(35,10.3),(-1,10.3)])
p=env.difference(blocked.buffer(.025)).difference(unary_union([footprint(i) for i in ['way/1236725789','way/1236725788','way/1236725787']]))
p=unary_union([q for q in parts(p) if q.intersection(orig).area>1])
added=p.difference(orig)
samples=[]
for u in np.arange(0,35,.5):
 for v in np.arange(10.5,18,.5):
  x,y,z=G.p(float(u),.11,float(v))
  if added.buffer(-.25).contains(Point(x,z)):samples.append([x,y,z])
Path('build/city-exteriors/santa-paula-apron-samples.json').write_text(json.dumps(samples))
report={'areaM2':p.area,'addedM2':added.area,'bounds':p.bounds,'roadSidewalkOverlapM2':p.intersection(blocked).area,'supplementalSamples':len(samples),'localRows':{str(v):[u for u in range(35) if p.buffer(-.5).contains(Point(G.p(u,0,v)[::2]))] for v in [11,12,13,14,15,16]}}
Path('docs/project-records/santa-paula-st-louis-refinement/apron-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)

neighborOverlaps=[]
for ident in BYID:
 if ident in ['way/1236725789','way/1236725788','way/1236725787']:continue
 area=footprint(ident).intersection(added).area
 if area>0:neighborOverlaps.append({'id':ident,'areaM2':area})
assert all(q['areaM2']<1e-6 for q in neighborOverlaps)
report['neighborOverlaps']=neighborOverlaps
report['areaToleranceM2']=1e-6
Path('docs/project-records/santa-paula-st-louis-refinement/apron-audit.json').write_text(json.dumps(report,indent=2)+'\n')
