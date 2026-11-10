"""Scoped sources only: preserve venue ownership, other buildings and interiors."""
from common import *
import akita_plaza,desert_oasis
for mod in [akita_plaza,desert_oasis]:
 B=Meshes();mod.exterior(B)
 for label in B.labels:label['detail']=0
 B.save_all();print(mod.KEY,len(B.groups),'batches')
