"""Quick bridge/circulation audit without rebuilding county pavement."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
source=Path('tools/geographic-strip/prepare.py').read_text().split('county_road,county_walk,county_counts=county_geometry')[0]
exec(compile(source,'tools/geographic-strip/prepare.py','exec'))
def bridgephys(key,v,f):phys(str(active[0])+'/'+street.collision_material,v,f)
active=[0]
street=StreetBuilder(mesh,bridgephys,polygons,CELL);street.indoor=unary_union([access.upper_mask,access.ramp_mask]);street.access_footprint=unary_union([p['void'] for p in access.plans]).buffer(.8)
clearance=prep(unary_union([LineString(r['points']).buffer(r['width']/2+1) for r in roads if r['highway'] in DRIVE]))
for r in roads:
 h=r.get('heights',[elev[n] for n in r['nodes']])
 if max(h)>.015 and not r.get('verticalLink'):
  active[0]=r['id'];street.bridge(r,elev,nodeways,clearance,Polygon())
(OUT/'bridge-only-colliders.json').write_text(json.dumps([dict(id=k,**v) for k,v in physics.items()],separators=(',',':')))
(OUT/'bridge-only-details.json').write_text(json.dumps(dict(bridgeChecks=street.bridge_checks),separators=(',',':')))
(OUT/'bridge-only-meshes.json').write_text(json.dumps(list(meshes.values()),separators=(',',':')))
print('Bridge preview complete',flush=True)

basephys=phys
def phys(key,v,f):basephys(active_building[0],v,f)
active_building=['']
# Audit the original OSM wall/roof geometry against every new circulation route.
for f in SURVEY['buildings']:
 if f['id'] in replacement_ids:continue
 shape=unary_union([Polygon([(x,-z) for x,z in p[0]],[[(x,-z) for x,z in ring] for ring in p[1:]]).buffer(0) for p in f['polygons']])
 if not access.tree.query(shape).size:continue
 active_building[0]=f['id']
 building_mesh(shape.difference(cut),f['height'],f['base'],'building-estimated',f['id'],f['tags'])
(OUT/'bridge-building-colliders.json').write_text(json.dumps([dict(id=k,**v) for k,v in physics.items()],separators=(',',':')))
