"""Scoped two-frontage source build; preserve ownership and other buildings."""
from common import *
import boston_pizza, travelers_frontage
B=Meshes()
for module in [boston_pizza,travelers_frontage]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
