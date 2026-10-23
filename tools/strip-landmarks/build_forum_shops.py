"""Build only the missing shopping mall; keep all other venues and city assets."""
from common import *
from forum_shops import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all()
vp=OUT/'venues.json';venues=json.loads(vp.read_text());venues=[v for v in venues if v['key']!=KEY];venues.append(meta);vp.write_text(json.dumps(venues,separators=(',',':')))
print('Forum Shops',len(B.groups),'groups',sum(len(g['faces']) for g in B.groups.values()),'triangles; mapped area',footprint('way/34068416').area)
