"""Scoped original geometry; preserve venue records and other properties."""
from common import *
import maverick_terminal,south_shell
for mod in [maverick_terminal,south_shell]:
 B=Meshes();mod.exterior(B)
 for label in B.labels:label['detail']=0
 B.save_all();print(mod.KEY,len(B.groups),'batches')
