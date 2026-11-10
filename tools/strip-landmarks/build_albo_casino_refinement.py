from common import *
import albo_dinos_frontage,casino_center_courtyard
B=Meshes()
for module in [albo_dinos_frontage,casino_center_courtyard]:module.exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
