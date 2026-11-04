"""Rebuild only the two claimed exteriors, preserving venue order and other data."""
from common import *
import harley_dealership,pinball_hall
for mod in [harley_dealership,pinball_hall]:
 B=Meshes();mod.exterior(B)
 if mod.KEY=='pinballHall':
  for label in B.labels:label['detail']=0
 B.save_all()
 print(mod.KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'faces')
# No metadata, footprint or collider change is intended by this sign-only pass.
