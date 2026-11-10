"""Build the scoped marquee without rewriting shared venue metadata."""
from common import *
import wynn_marquee as marquee
for module in [marquee]:
 B=Meshes(); module.exterior(B)
 collision=OUT/(module.KEY+'-exterior-collision.json')
 before=collision.read_bytes()
 B.save_all()
 assert collision.read_bytes()==before, 'Decorative refinement changed collision: '+module.KEY
 print(module.KEY, sum(len(g['faces']) for g in B.groups.values()), 'triangles; collision byte-identical')
