"""Scoped pair build; preserve shared metadata and collision."""
from common import *
import nyny_irish_kiosk, nyny_arrival
for module in [nyny_irish_kiosk, nyny_arrival]:
 B=Meshes();module.exterior(B)
 collision=OUT/(module.KEY+'-exterior-collision.json');before=collision.read_bytes()
 B.save_all()
 assert collision.read_bytes()==before, 'Decorative refinement changed collision: '+module.KEY
 print(module.KEY,sum(len(g['faces']) for g in B.groups.values()),'faces; collision byte-identical')
