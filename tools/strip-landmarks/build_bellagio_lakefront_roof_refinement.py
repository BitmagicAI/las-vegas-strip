"""Scoped pair build; preserve shared metadata and collision."""
from common import *
import bellagio_arcade_piers, bellagio_curved_roofs
for module in [bellagio_arcade_piers, bellagio_curved_roofs]:
 B=Meshes();module.exterior(B)
 collision=OUT/(module.KEY+'-exterior-collision.json');before=collision.read_bytes()
 B.save_all()
 assert collision.read_bytes()==before, 'Decorative refinement changed collision: '+module.KEY
 print(module.KEY,sum(len(g['faces']) for g in B.groups.values()),'faces; collision byte-identical')
