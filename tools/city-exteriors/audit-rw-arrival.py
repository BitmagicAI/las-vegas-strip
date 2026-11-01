import sys,json,numpy as np
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from resorts_world_arrival import BASE,NAME,cut_triangle
old=json.loads((BASE/(NAME+'.json')).read_text());new=json.loads(Path('build/strip-landmarks/'+NAME+'.json').read_text())
assert old['labels']==new['labels']
preserved=0
for a,b in zip(old['meshes'],new['meshes']):
 if a['source']!='podium/way/972129019':assert a==b;preserved+=1
known=set()
for g in old['meshes']:
 for f in g['faces']:
  t=np.array([g['vertices'][i]for i in f]);
  if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))<1e-8:known.add(tuple(t.flatten()))
errors=[];count=0;retainedDegenerate=0
for g in new['meshes']:
 v=np.array(g['vertices'],float)
 for f in g['faces']:
  t=v[f];count+=1
  if tuple(t.flatten()) in known:retainedDegenerate+=1
  elif not np.isfinite(t).all() or np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))<1e-8:errors.append([g['source'],f])
# Existing source collision is retained byte for byte as a prefix; new collision is appended.
a=json.loads((BASE/(NAME+'-collision.json')).read_text());b=json.loads(Path('build/strip-landmarks/'+NAME+'-collision.json').read_text())
assert b['vertices'][:len(a['vertices'])]==a['vertices'] and b['indices'][:len(a['indices'])]==a['indices']
report={'triangles':count,'preservedNonPodiumGroups':preserved,'oldCollisionTrianglesPreserved':len(a['indices'])//3,'newCollisionTriangles':(len(b['indices'])-len(a['indices']))//3,'retainedPreexistingDegenerateTriangles':retainedDegenerate,'errors':errors,'scope':'Finite nondegenerate source triangles, unchanged non-podium groups/labels, retained source collision prefix. Geographic collision clipping recorded separately.'}
Path('docs/project-records/rw-arrival/geometry.json').write_text(json.dumps(report,indent=2)+'\n');print(report);assert not errors
