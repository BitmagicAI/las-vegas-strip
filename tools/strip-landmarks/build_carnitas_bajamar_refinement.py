"""Scoped two-frontage source build; preserve ownership and other buildings."""
from common import *
import carnitas_1601, bajamar
B=Meshes()
for module in [carnitas_1601,bajamar]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
