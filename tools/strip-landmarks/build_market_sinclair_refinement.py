"""Scoped source build; installation and shared bake are separate."""
from common import *
import market_1700, sinclair_1705
B=Meshes()
for module in [market_1700,sinclair_1705]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
