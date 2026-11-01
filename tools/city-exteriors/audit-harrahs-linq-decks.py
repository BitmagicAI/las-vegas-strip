"""Verify the additive courts and the narrowly removed conflicting Harrahs roof."""
import json,sys
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
from shapely.geometry import Polygon,Point,box
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
 reports.append({'key':key,'retainedOldTriangles':kept,'removedConflictingRoofTriangles':removed,'oldCollisionPrefixIdentical':True,'oldLabelsIdentical':True,'newTriangles':meta['addedTriangles']})
Path('docs/project-records/harrahs-linq-decks/preservation.json').write_text(json.dumps(reports,indent=2)+'\n');print(reports)
