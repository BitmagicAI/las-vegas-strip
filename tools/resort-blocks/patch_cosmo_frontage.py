"""Targeted facade/roof-deck ownership patch; no road/interior regeneration."""
import sys,json,shutil,hashlib
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
import cosmo_frontage
out=Path('build/resort-blocks/cosmo');backup=Path('.bitmagic/city-exterior-backups/cosmo-frontage-2026-10-13');backup.mkdir(parents=True,exist_ok=True)
keys=['cosmo-exterior','cosmoL4-exterior','cosmoL4-interior','cosmoL14-exterior','cosmoL14-interior']
for key in keys:
 for suffix in ['.json','-collision.json']:
  p=out/(key+suffix)
  if not (backup/p.name).exists():shutil.copy2(p,backup/p.name)
b=Meshes()
for key in keys:
 d=json.loads((backup/(key+'.json')).read_text())
 for m in d['meshes']:b.groups[(m['property'],m['source'],m['material'],m['detail'])]=m
 b.labels.extend(d['labels']);b.solids[key]=json.loads((backup/(key+'-collision.json')).read_text())
removed=cosmo_frontage.update_builder(b)
for key in keys:
 (out/(key+'.json')).write_text(json.dumps({'meshes':[m for m in b.groups.values() if m['property']==key],'labels':[l for l in b.labels if l['property']==key]},separators=(',',':')))
 (out/(key+'-collision.json')).write_text(json.dumps(b.solids[key],separators=(',',':')))
report={'removedFrontTriangles':removed,'newFacadeTriangles':sum(len(m['faces']) for m in b.groups.values() if m['source']==cosmo_frontage.SOURCE),'movedOutdoorTriangles':sum(len(m['faces']) for m in b.groups.values() if m['property'] in ['cosmoL4-exterior','cosmoL14-exterior']),'unchangedMainCollision':hashlib.sha256((backup/'cosmo-exterior-collision.json').read_bytes()).hexdigest()==hashlib.sha256((out/'cosmo-exterior-collision.json').read_bytes()).hexdigest(),'backup':str(backup)}
(out/'frontage-refinement-report.json').write_text(json.dumps(report,indent=2));print(report)
