from common import *
import st_louis_office_515,city_market_liquor
B=Meshes()
for module in [st_louis_office_515,city_market_liquor]:module.exterior(B)
for label in B.labels:label["detail"]=0
B.save_all()
