from common import *
import carpets_galore,rexford_courtyard_1701
B=Meshes()
for module in [carpets_galore,rexford_courtyard_1701]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
