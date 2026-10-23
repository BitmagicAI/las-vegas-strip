"""Rebuild only building surfaces; preserve expensive county pavement/landscape."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
prepare_source=Path('tools/geographic-strip/prepare.py').read_text()
exec(compile(prepare_source.split('county_road,county_walk,county_counts=county_geometry')[0],'prepare.py','exec'))

def is_building(material):return material in ('building-estimated','building-tagged','utility') or material.startswith('tag/')
def triangle_key(vertices):return tuple(sorted(tuple(round(c,4) for c in p) for p in vertices))
old=json.loads((OUT/'city-meshes.json').read_text())
old_building_faces={triangle_key([g['vertices'][i] for i in f]) for g in old if is_building(g['material']) for f in g['faces']}
old_physics=json.loads((OUT/'city-colliders.json').read_text())
styles.update(json.loads((OUT/'city-materials.json').read_text()))
# Passage trim is unchanged; don't rebuild the streets to calculate it again.
from shapely.geometry import shape as read_shape
surfaces={f['properties']['kind']:read_shape(f['geometry']) for f in json.loads((OUT/'surface-layers.geojson').read_text())['features']}
blocked=unary_union([surfaces['road'].buffer(.3),surfaces['sidewalk']])
start=prepare_source.index('@lru_cache(maxsize=None)\ndef local_mask')
end=prepare_source.index('# Flat support is continuous over the district.')
exec(compile(prepare_source[start:end],'prepare.py:buildings','exec'))
new_building_faces=sum(len(g['faces']) for g in meshes.values())
merged=[g for g in old if not is_building(g['material'])]+list(meshes.values())
for cell in old_physics:
 v=cell['vertices'];idx=cell['indices'];remaining=[]
 for k in range(0,len(idx),3):
  ids=idx[k:k+3]
  if triangle_key([v[i*3:i*3+3] for i in ids]) not in old_building_faces:remaining.extend(ids)
 replacement=physics.pop(cell['id'],dict(vertices=[],indices=[]));offset=len(v)//3
 cell['indices']=remaining+[i+offset for i in replacement['indices']];cell['vertices'].extend(replacement['vertices'])
for key,g in physics.items():old_physics.append(dict(id=key,center=[(int(k)+.5)*CELL for k in key.split(',')],**g))
(OUT/'city-meshes.json').write_text(json.dumps(merged,separators=(',',':')))
# Rebuilds append replacement vertices; drop obsolete indices' storage exactly.
from prune_collision_vertices import prune_cells
print('Collision storage',prune_cells(old_physics),flush=True)
# Replacing the last building in a cell can leave no triangles. Rapier cannot
# construct a trimesh for an empty cell; omit it rather than streaming an invalid shape.
old_physics=[cell for cell in old_physics if cell['indices']]
(OUT/'city-colliders.json').write_text(json.dumps(old_physics,separators=(',',':')))
(OUT/'city-materials.json').write_text(json.dumps(styles))
(OUT/'building-index.json').write_text(json.dumps(features,separators=(',',':')))
report=json.loads((OUT/'report.json').read_text());report.update(buildings=kept,trimmedBuildings=clipped,replacedBuildings=removed,triangles=sum(len(g['faces']) for g in merged),buildingSurfaces=building_surfaces.report())
(OUT/'report.json').write_text(json.dumps(report,indent=2))
print('Rebuilt building triangles',len(old_building_faces),'->',new_building_faces,flush=True)
