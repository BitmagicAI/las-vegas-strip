"""Scoped source build; shared data installation/bake are separate."""
from common import *
import curaleaf_1736, white_cross_annex
B=Meshes()
for module in [curaleaf_1736,white_cross_annex]:module.exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
