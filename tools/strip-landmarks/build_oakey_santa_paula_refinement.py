"""Scoped office source build; preserve shared metadata and other buildings."""
from common import *
import oakey_offices, santa_paula_office
B=Meshes()
for module in [oakey_offices,santa_paula_office]:module.exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
