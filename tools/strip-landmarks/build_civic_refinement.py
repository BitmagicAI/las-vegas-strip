"""Scoped civic sources; preserve venue ownership and all other buildings."""
from common import *
import south_central_police,fire_station_11
for mod in [south_central_police,fire_station_11]:
 B=Meshes();mod.exterior(B)
 for label in B.labels:label["detail"]=0
 B.save_all();print(mod.KEY,len(B.groups),"batches")
