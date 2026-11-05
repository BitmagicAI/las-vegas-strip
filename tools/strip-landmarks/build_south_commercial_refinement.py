from common import *
import south_commercial_364846558,south_commercial_annex
B=Meshes()
for module in [south_commercial_364846558,south_commercial_annex]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
