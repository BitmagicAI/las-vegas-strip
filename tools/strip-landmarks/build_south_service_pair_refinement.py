"""Scoped pair build; preserve shared metadata and collision."""
from common import *
import akita_rear_canopy, russell_service
for module in [akita_rear_canopy, russell_service]:
 B=Meshes();module.exterior(B)
 collision=OUT/(module.KEY+'-exterior-collision.json');before=collision.read_bytes()
 B.save_all()
 assert collision.read_bytes()==before, 'Decorative refinement changed collision: '+module.KEY
 print(module.KEY,sum(len(g['faces']) for g in B.groups.values()),'faces; collision byte-identical')
