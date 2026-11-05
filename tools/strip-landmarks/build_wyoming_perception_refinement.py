from common import *
import wyoming_17_frontage,perception_museum
B=Meshes()
for module in [wyoming_17_frontage,perception_museum]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
