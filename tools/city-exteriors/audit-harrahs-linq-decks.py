"""Verify the additive courts and the narrowly removed conflicting Harrahs roof."""
import json,sys,re
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
survey=json.loads(Path('build/strip-survey/survey.json').read_text())['buildings']
shapes=[(b['id'],b['height'],unary_union([Polygon([(x,-z) for x,z in poly[0]], [[(x,-z) for x,z in ring] for ring in poly[1:]]).buffer(0) for poly in b['polygons']])) for b in survey]
base=Path('.bitmagic/city-exterior-backups/harrahs-linq-decks');root=Path('build/strip-landmarks');reports=[]
for key in ['harrahs','linq']:
 a=json.loads((base/(key+'-exterior.json')).read_text());b=json.loads((root/(key+'-exterior.json')).read_text());meta=json.loads((root/(key+'-deck-metadata.json')).read_text());deck=box(*meta['deckBounds']);kept=removed=0
 assert b['labels']==a['labels']
 for old,new in zip(a['meshes'],b['meshes']):
  assert (old['source'],old['material'],old['detail'])==(new['source'],new['material'],new['detail'])
  assert new['vertices'][:len(old['vertices'])]==old['vertices']
  faces={tuple(f) for f in new['faces']}
  for f in old['faces']:
   if tuple(f) in faces:kept+=1;continue
   pts=[old['vertices'][i] for i in f];assert key=='harrahs'
   allowed=(old['source']=='harrahs-roof' and deck.contains(Point(sum(p[0] for p in pts)/3,sum(p[2] for p in pts)/3)))
   allowed|=(old['source']=='harrahs-podium' and all(abs(p[1]-meta['deckY'])<.001 for p in pts) and Polygon([(p[0],p[2]) for p in pts]).intersection(deck).area>1e-8)
   assert allowed,(key,old['source'],f);removed+=1
 c=json.loads((base/(key+'-exterior-collision.json')).read_text());d=json.loads((root/(key+'-exterior-collision.json')).read_text());assert d['vertices'][:len(c['vertices'])]==c['vertices'];assert d['indices'][:len(c['indices'])]==c['indices']
 views=json.loads(re.search(r'const views=(.*);',Path('tools/city-exteriors/probe-'+key+'.js').read_text()).group(1));inside=[]
 for name,eye,target in views:
  inside += [[name,ident] for ident,height,shape in shapes if height>eye[1] and shape.contains(Point(eye[0],eye[2]))]
 assert not inside,inside
 reports.append({'cameraOriginsOutsideMappedBuildings':len(views),'key':key,'retainedOldTriangles':kept,'removedConflictingRoofTriangles':removed,'oldCollisionPrefixIdentical':True,'oldLabelsIdentical':True,'newTriangles':meta['addedTriangles']})
Path('docs/project-records/harrahs-linq-decks/preservation.json').write_text(json.dumps(reports,indent=2)+'\n');print(reports)
