from common import *
import santa_paula_courtyard,st_louis_square_frontage
B=Meshes()
for module in [santa_paula_courtyard,st_louis_square_frontage]:module.exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
