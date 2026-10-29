"""Generate the owned shell and public rooms; install-hofbrauhaus.py registers them."""
from common import *
from hofbrauhaus import exterior
from hofbrauhaus_interior import interior
B=Meshes();meta=interior(B,exterior(B));B.save_all()
(OUT/'hofbrauhaus-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Hofbrauhaus generated:',len(B.groups),'batches;',sum(len(g['faces']) for g in B.groups.values()),'triangles')
