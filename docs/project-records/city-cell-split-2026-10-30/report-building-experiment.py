import json,hashlib
from pathlib import Path
root=Path('.bitmagic/city-cells/building-experiment'); clone=Path('/tmp/vegas-cell-split-validation-2a868a1'); live=Path('runtime-assets')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changes={}
for name,before,after in [('visual',root/'cells',live/'geographic-strip/cells'),('collision',root/'collision-cells',live/'geographic-strip/collision-cells'),('lod',clone/'build/baked/cells',live/'baked/cells')]:
 index=json.loads((after/'manifest.json').read_text());rows=[]
 for c in index['cells']:
  file=c['file'];prior=before/file
  if name=='visual':
   # All unrelated source cells were independently proven identical, so only this cell was optimized again.
   if file!='cell-0_-4.glb':continue
   prior=root/'cell-before.glb'
  if sha(prior)!=sha(after/file):rows.append({'file':file,'newBytes':(after/file).stat().st_size,'oldBytes':prior.stat().st_size})
 changes[name]=rows
manifestBytes=sum((live/f/'manifest.json').stat().st_size for f in ['geographic-strip/cells','geographic-strip/collision-cells','baked/cells'])
legacyBytes=sum(p.stat().st_size for p in [Path('build/optimized/build/geographic-strip/city.glb'),Path('build/geographic-strip/city-colliders.bin'),Path('build/baked/city-lod.bin')])
report={'building':'way/464694104','change':'Remove 16 owned shell triangles with matching collision; existing detailed building unchanged','changed':changes,'newCellObjectBytes':sum(x['newBytes'] for rows in changes.values() for x in rows)+manifestBytes,'manifestBytesUpperBound':manifestBytes,'legacyNewObjectBytes':legacyBytes,'excluded':'unchanged detailed building; asset-pack catalog; network compression; one-time migration'}
(root/'storage-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
