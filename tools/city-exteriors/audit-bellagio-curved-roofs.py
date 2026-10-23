from pathlib import Path
import sys,json
sys.path.insert(0,'tools/strip-landmarks');from common import *
ps=[footprint(i)for i in ['way/114719022','way/114719023']];region=unary_union(ps);a=region.bounds;results=[]
for path in [Path('build/geographic-strip/city-meshes.json'),Path('build/resort-blocks/bellagio/bellagioBlock-exterior.json')]:
 data=json.loads(path.read_text());gs=data if isinstance(data,list)else data['meshes']
 for g in gs:
  if not g['faces']:continue
  q=np.asarray(g['vertices'])[np.asarray(g['faces'])];m=(q[:,:,0].min(1)<a[2])&(q[:,:,0].max(1)>a[0])&(q[:,:,2].min(1)<a[3])&(q[:,:,2].max(1)>a[1])&(q[:,:,1].min(1)<19)&(q[:,:,1].max(1)>11)
  if m.any():
   n=0
   for t in q[m]:
    if Polygon(t[:,[0,2]]).buffer(.005).intersects(region):n+=1
   if n:results.append(dict(file=str(path),source=g.get('source'),material=g['material'],triangles=n,minY=float(q[m,:,1].min()),maxY=float(q[m,:,1].max())))
Path('build/city-exteriors/bellagio-curved-roofs-owner-audit.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
