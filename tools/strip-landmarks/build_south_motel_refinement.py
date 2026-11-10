"""Scoped motel detail rebuild; preserve existing metadata and unrelated geometry."""
from common import *
import diamond_inn,nirvana_hotel
for mod in [diamond_inn,nirvana_hotel]:
 B=Meshes();mod.exterior(B)
 for label in B.labels:label['detail']=0
 B.save_all();print(mod.KEY,len(B.groups),'batches')
Path('build/city-exteriors/diamond-refinement-trees.json').write_text(json.dumps(diamond_inn.TREE_PLACEMENTS))
