"""Rebuild only the two claimed exteriors, preserving venue order and other data."""
from common import *
import ihop_north,oasis_motel
for mod in [ihop_north,oasis_motel]:
 B=Meshes();mod.exterior(B)
 B.save_all()
 print(mod.KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'faces')
# No metadata, footprint or collider change is intended by this detail-only pass.
