from common import *
import rexford_ellen_courtyard,casino_center_1520
B=Meshes()
for module in [rexford_ellen_courtyard,casino_center_1520]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
