"""Scoped source build; shared data installation/bake are separate."""
from common import *
import dennys_1822, main_1700
B=Meshes()
for module in [dennys_1822,main_1700]:module.exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
