"""Patch cached exterior only; preserve roads, runtime interiors and all collision."""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
import bellagio_service
b=Meshes();bellagio_service.build(b)
p=Path('build/resort-blocks/bellagio/bellagioBlock-exterior.json');d=json.loads(p.read_text());d['meshes']=[g for g in d['meshes'] if g['source']!='service-refinement']+list(b.groups.values());p.write_text(json.dumps(d,separators=(',',':')))
print('Patched',sum(len(g['faces']) for g in b.groups.values()),'triangles in',len(b.groups),'batches')
