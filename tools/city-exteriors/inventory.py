"""Read-only survey of every large building and the 200 m Strip frontage corridor."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"build/south-strip/python"))
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[2]
survey=json.loads((R/'build/strip-survey/survey.json').read_text())
strip=unary_union([LineString([(x,-z) for x,z in r['points']]) for r in survey['roads'] if 'Las Vegas Boulevard' in r['name']])
background={f['id']:f for f in json.loads((R/'build/geographic-strip/building-index.json').read_text())}
plans=json.loads((R/'build/highrises/plan.json').read_text())
owners={f['id']:p['key'] for p in plans for f in p['features']}
rows=[]
for f in survey['buildings']:
 p=unary_union([Polygon([(x,-z) for x,z in q[0]],[[(x,-z) for x,z in ring] for ring in q[1:]]).buffer(0) for q in f['polygons']])
 if p.is_empty:continue
 d=p.distance(strip);large=f['height']>=35 and p.area>=500
 if not large and d>200:continue
 if p.area<4:continue
 rows.append(dict(id=f['id'],name=f['name'],large=large,heightM=f['height'],heightSource=f['kind'],areaM2=round(p.area,1),stripDistanceM=round(d,1),bounds=list(p.bounds),center=[p.centroid.x,p.centroid.y],tags=f['tags'],owner=owners.get(f['id'],'mapped-background' if f['id'] in background else 'legacy-or-landmark'),status='needs-visual-audit'))
rows.sort(key=lambda r:(not r['large'],r['center'][1],r['id']))
out=R/'docs/project-records/city-exteriors-2026-10-12/inventory.json'
# Re-running the survey must not erase the visual review ledger.
previous={r['id']:r for r in json.loads(out.read_text()).get('buildings',[])} if out.exists() else {}
for row in rows:
 old=previous.get(row['id'],{})
 for key in ('owner','status','reviewEvidence','remaining','reviewedDate'):
  if key in old:row[key]=old[key]
# Explicitly reviewed additions outside the initial height/corridor filter remain
# part of the scope on later survey refreshes.
surveyed_ids={row['id'] for row in rows}
for ident,old in previous.items():
 if ident not in surveyed_ids and old.get('scopeExpansion'):rows.append(old)
out.write_text(json.dumps(dict(date='2026-10-12',scope='All mapped buildings at least35m tall and500m2, plus every mapped footprint within200m of Las Vegas Boulevard; expansions recorded explicitly.',buildings=rows),indent=2)+'\n')
print('Inventory:',len(rows),'large:',sum(r['large'] for r in rows),'mapped-background:',sum(r['owner']=='mapped-background' for r in rows))
for r in rows:
 if r['owner']=='mapped-background' and (r['name']!='Unnamed building' or r['areaM2']>10000):print(r['id'],r['name'],r['heightM'],r['areaM2'],r['center'])
