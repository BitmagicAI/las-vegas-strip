"""Relocate only the existing Palms core; retain room layout and floor count."""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
origin=[-1824,.24,120];linear=[0,1,-1,0]
parent=footprint('relation/7655651');ray=LineString([(-1829,120),(-2400,120)]);hits=ray.intersection(parent.boundary)
xs=[q.x for q in getattr(hits,'geoms',[hits]) if q.geom_type=='Point' and q.x<-1920];extent=origin[0]-max(xs)
for filename in ['build/highrises/plan.json','src/work/hotels/highrise-towers.json']:
 p=Path(filename);backup=Path('build/city-exteriors/before')/('palms-'+p.name);backup.parent.mkdir(exist_ok=True,parents=True)
 if not backup.exists():backup.write_bytes(p.read_bytes())
 data=json.loads(p.read_text());towers=next(v for v in data if v['key']=='palms')['towers'] if 'plan.json' in filename else [v for v in data if v['building']=='palms']
 for t in towers:t.update(origin=origin,linear=linear,yaw=math.pi/2,lobbyFront=-extent)
 p.write_text(json.dumps(data,indent=2))
Path('tools/highrises/palms-core-fit.json').write_text(json.dumps(dict(origin=origin,linear=linear,yaw=math.pi/2,lobbyFront=-extent),indent=2))
print('Palms core',origin,'front',-extent)
