from common import *
from oyo import exterior,KEY,IDS
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.update(IDS);p.write_text(json.dumps(sorted(ids)))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
# Sample accessible roof/deck interiors, excluding parapets and perimeter piers.
samples=[]
for ident,h in zip(IDS,[6,32,59,20,5]):
 p=footprint(ident).buffer(-1)
 for other,oh in zip(IDS,[6,32,59,20,5]):
  if oh>h:p=p.difference(footprint(other).buffer(1))
 levels=[.2,3.5,6.8,10.1,13.4,16.7,20] if h==20 else [h+.025]
 if h in [32,59]:p=p.difference(footprint(ident).buffer(-1.8))
 for x in np.arange(p.bounds[0]+.2,p.bounds[2],3):
  for z in np.arange(p.bounds[1]+.2,p.bounds[3],3):
   if p.contains(Point(x,z)):
    for y in levels:samples.append([float(x),y,float(z)])
(OUT/'oyo-roof-samples.json').write_text(json.dumps(samples))
