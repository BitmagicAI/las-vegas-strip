"""Scoped paired exterior build; preserve existing venue metadata and trees at export."""
from common import *
import bonita_terrace, siegel_paradise
B=Meshes()
for module in [bonita_terrace, siegel_paradise]:module.exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
