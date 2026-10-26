"""Generate staged geometry only; does not register a partly reviewed venue."""
from common import *
from hofbrauhaus import exterior
B=Meshes();meta=exterior(B);B.save_all()
(OUT/'hofbrauhaus-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Hofbrauhaus staged:',len(B.groups),'batches;',sum(len(g['faces']) for g in B.groups.values()),'triangles')
