"""Preserve pre-existing TI assets and check review origins against mapped volumes."""
import json,sys,re
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
base=Path('.bitmagic/city-exterior-backups/ti-pool-court');out=Path('build/strip-landmarks')
a=json.loads((base/'ti-exterior.json').read_text());b=json.loads((out/'ti-exterior.json').read_text());assert b['meshes'][:len(a['meshes'])]==a['meshes'];assert b['labels']==a['labels']
c=json.loads((base/'ti-exterior-collision.json').read_text());d=json.loads((out/'ti-exterior-collision.json').read_text());assert d['vertices'][:len(c['vertices'])]==c['vertices'];assert d['indices'][:len(c['indices'])]==c['indices']
survey=json.loads(Path('build/strip-survey/survey.json').read_text())['buildings'];views=json.loads(re.search(r'const views=(.*);',Path('tools/city-exteriors/probe-ti.js').read_text()).group(1));inside=[]
for name,eye,target in views:
 for f in survey:
  if f['height']<=eye[1]:continue
  shape=unary_union([Polygon([(x,-z) for x,z in poly[0]], [[(x,-z) for x,z in ring] for ring in poly[1:]]).buffer(0) for poly in f['polygons']])
  if shape.contains(Point(eye[0],eye[2])):inside.append((name,f['id']))
assert not inside,inside
report={'oldVisualGroupsIdentical':len(a['meshes']),'oldVisualTrianglesIdentical':sum(len(m['faces']) for m in a['meshes']),'oldCollisionTrianglesIdentical':len(c['indices'])//3,'oldLabelsIdentical':True,'cameraOriginsOutsideMappedVolumes':len(views)}
Path('docs/project-records/ti-pool-court/preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
