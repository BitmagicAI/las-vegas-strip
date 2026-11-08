import sys,json,subprocess,copy,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
import common
out=Path('.bitmagic/bali-chapel-candidate');out.mkdir(parents=True,exist_ok=True)
main=Path('/Users/janisun/Development/GitFork/vegas-afterlight/build/strip-landmarks')
report=[]
for module,key in [('little_church_west','littleChurchWest'),('bali_hai_clubhouse','baliHaiClubhouse'),('bali_hai_service','baliHaiService')]:
 source=Path('tools/strip-landmarks')/(module+'.py')
 old=subprocess.check_output(['git','show','HEAD:'+str(source)],text=True)
 def build(code):
  ns={};exec(code,ns);b=common.Meshes();ns['exterior'](b)
  assert json.loads(json.dumps(b.solids[key+'-exterior']))==json.loads((main/(key+'-exterior-collision.json')).read_text()), (key,'collision changed')
  for label in b.labels:label['detail']=0
  return json.loads(json.dumps({'meshes':list(b.groups.values()),'labels':b.labels}))
 before=build(old);after=build(source.read_text());baseline=json.loads((main/(key+'-exterior.json')).read_text())
 assert before==baseline, (key,'generated original differs from preserved source')
 assert before['labels']==after['labels']
 (out/(key+'-exterior.json')).write_text(json.dumps(after,separators=(',',':')))
 shutil.copy2(main/(key+'-exterior-collision.json'),out/(key+'-exterior-collision.json'))
 report.append({'key':key,'originalGeneratedMatchesPreservedJSON':True,'labelsUnchanged':True,'collisionPreserved':True,'beforeTriangles':sum(len(g['faces']) for g in before['meshes']),'afterTriangles':sum(len(g['faces']) for g in after['meshes'])})
shutil.copy2('build/strip-landmarks/venues.json',out/'venues.json')
Path('docs/project-records/bali-chapel-refinement/candidate-source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
