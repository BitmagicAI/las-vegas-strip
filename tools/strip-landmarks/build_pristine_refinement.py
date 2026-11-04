"""Scoped source only; preserve ownership and other buildings."""
from common import *
import pristine_hangar
B=Meshes();pristine_hangar.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
