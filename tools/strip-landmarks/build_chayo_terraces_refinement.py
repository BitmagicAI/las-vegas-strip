"""Build the scoped chayo without rewriting shared venue metadata."""
from common import *
import chayo_terraces as chayo
for module in [chayo]:
 B=Meshes(); module.exterior(B)
 collision=OUT/(module.KEY+'-exterior-collision.json')
 before=collision.read_bytes()
 B.save_all()
 assert collision.read_bytes()==before, 'Decorative refinement changed collision: '+module.KEY
 print(module.KEY, sum(len(g['faces']) for g in B.groups.values()), 'triangles; collision byte-identical')
