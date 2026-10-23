"""Targeted facade update. Existing public shell, colliders and all interiors survive."""
from common import *
from harrahs_facades import exterior
path=OUT/'harrahs-exterior.json';old=json.loads(path.read_text())
B=Meshes();B.property='harrahs-exterior';exterior(B)
def owned(s):return s=='harrahs-marquee' or s in ['harrahs-strip','harrahs-roof','harrahs-upper-roof','harrahs-showbill'] or s.startswith('tower/')
old['meshes']=[g for g in old['meshes'] if not owned(g['source'])]+list(B.groups.values())
old['labels']=[g for g in old['labels'] if not owned(g['source'])]+B.labels
path.write_text(json.dumps(old,separators=(',',':')))
p=OUT/'venues.json';v=json.loads(p.read_text());h=next(a for a in v if a['key']=='harrahs');h['views'].update({'strip':{'eye':[-18,3,-422],'target':[65,11,-390]},'facade-aerial':{'eye':[-190,135,-560],'target':[155,35,-384]}});p.write_text(json.dumps(v,separators=(',',':')))
print('Harrahs',len(old['meshes']),'groups',sum(len(g['faces']) for g in old['meshes']),'triangles; collision/interiors unchanged')
