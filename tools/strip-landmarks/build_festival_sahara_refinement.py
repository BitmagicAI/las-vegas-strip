from common import *
import festival_grounds_service,mcdonalds_sahara_canopy
B=Meshes()
for module in [festival_grounds_service,mcdonalds_sahara_canopy]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
