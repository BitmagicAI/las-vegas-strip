"""Scoped sources only: preserve venue ownership, other buildings and interiors."""
from common import *
import psychic_sessions,south_arco
for mod in [psychic_sessions,south_arco]:
 B=Meshes();mod.exterior(B)
 for label in B.labels:label['detail']=0
 B.save_all();print(mod.KEY,len(B.groups),'batches')
