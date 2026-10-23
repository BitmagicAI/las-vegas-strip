"""Replace TI tower render ownership only; keep arrival, ship, guest rooms and collision."""
from common import *
from ti_facades import exterior
path=OUT/'ti-exterior.json';old=json.loads(path.read_text());B=Meshes();B.property='ti-exterior';exterior(B)
old['meshes']=[g for g in old['meshes'] if not g['source'].startswith('tower/')]+list(B.groups.values())
old['labels']=[g for g in old['labels'] if not g['source'].startswith('tower/')]+B.labels
for g in old['meshes']:
 if g['material']=='roof':g['material']='ti-roof'
path.write_text(json.dumps(old,separators=(',',':')))
vp=OUT/'venues.json';vs=json.loads(vp.read_text());v=next(v for v in vs if v['key']=='ti')
v['views'].update({'strip':{'eye':[272,3,-964],'target':[102,57,-966]},'facade-aerial':{'eye':[335,142,-845],'target':[87,58,-964]}})
vp.write_text(json.dumps(vs,separators=(',',':')))
print('TI',len(old['meshes']),'groups',sum(len(g['faces']) for g in old['meshes']),'triangles; retained collision and interiors')
