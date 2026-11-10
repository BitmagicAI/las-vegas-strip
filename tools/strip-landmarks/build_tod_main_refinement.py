"""Scoped two-frontage source build; preserve ownership and other buildings."""
from common import *
import tod_motel, main_street_1511
B=Meshes()
for module in [tod_motel,main_street_1511]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
