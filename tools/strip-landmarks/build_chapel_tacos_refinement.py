"""Scoped source build; installation and shared bake are separate."""
from common import *
import chapel_flowers, tacos_mexico
B=Meshes()
for module in [chapel_flowers,tacos_mexico]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
