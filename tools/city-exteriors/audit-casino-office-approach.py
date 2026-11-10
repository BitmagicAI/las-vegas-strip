import sys,json,math
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from casino_center_courtyard import YAW
from shapely.geometry import shape
G=Frame(Meshes(),1837.868,-4107.689,yaw=YAW+math.pi/2,y=0)
planters=unary_union([G.poly([(a,-1.16),(b,-1.16),(b,-.28),(a,-.28)]) for a,b in [(1,4.8),(7.6,11.4)]])
layers=json.loads(Path('build/geographic-strip/surface-layers.geojson').read_text())['features']
blocked=unary_union([shape(f['geometry']) for f in layers if f['properties']['kind'] in ['road','sidewalk']])
overlap=planters.intersection(blocked).area
assert overlap<1e-6,overlap
points=[G.p(6.21,.18,w) for w in [-4,-2,-.65]]
samples=[G.p(u,.15,w) for u in [5.3,6.21,7.1] for w in np.arange(-4,-.5,.25)]
Path('build/city-exteriors/casino-office-approach-samples.json').write_text(json.dumps(samples))
Path('docs/project-records/albo-dinos-casino-courtyard-refinement/office-approach-audit.json').write_text(json.dumps({'points':points,'planterPavementOverlapM2':overlap,'clearApproachM':2.8,'samples':len(samples)},indent=2)+'\n')
s=Path('tools/city-exteriors/walk-albo-dinos-casino-courtyard-refinement.js').read_text();start=s.index('const meta=')+11;end=s.index(';',start);Path('tools/city-exteriors/walk-casino-office-approach.js').write_text(s[:start]+json.dumps({'routes':[{'name':'casino-office-approach','points':points}]})+s[end:])
