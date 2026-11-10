"""Scoped sources only: preserve venue ownership, other buildings and interiors."""
from common import *
import laughing_jackalope,nirvana_ancillary
for mod in [laughing_jackalope,nirvana_ancillary]:
 B=Meshes();mod.exterior(B)
 for label in B.labels:label['detail']=0
 B.save_all();print(mod.KEY,len(B.groups),'batches')
