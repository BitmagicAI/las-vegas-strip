"""Scoped pair build; preserve shared metadata and collision."""
from common import *
import paris_rooftop_bar, cvs_horseshoe
for module in [paris_rooftop_bar, cvs_horseshoe]:
 B=Meshes();module.exterior(B)
 collision=OUT/(module.KEY+'-exterior-collision.json');before=collision.read_bytes()
 B.save_all()
 assert collision.read_bytes()==before, 'Decorative refinement changed collision: '+module.KEY
 print(module.KEY,sum(len(g['faces']) for g in B.groups.values()),'faces; collision byte-identical')
