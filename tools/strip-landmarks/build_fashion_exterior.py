from pathlib import Path
import sys
sys.path.insert(0,'tools/strip-landmarks')
s=Path('tools/strip-landmarks/build.py').read_text();pre=s[:s.index("enter('linq');")];a=s.index("enter('fashion');");b=s.index("enter('fashion','interior');",a)
segment=s[a:b]
# Preserve the entrance/arrival assembly and Cloud lens. Replace the solid shell,
# not the interior or venue metadata. Original small support tubes are enclosed.
segment=segment.replace("B.shell(p,.15,16.5,'ivory',[glazed],interior=(F.poly([(-21.9,.3),(21.9,.3),(21.9,108),(-21.9,108)]),16.4));",'')
ns={};exec(compile(pre+segment,'<Fashion exterior>','exec'),ns)
from fashion_exterior import exterior
B=ns['B'];areas=exterior(B,ns['p'],ns['F'],ns['glazed']);B.save_all()
print('fashion',len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
print([(n,round(q.area),h) for n,q,h,m in areas])

import json
from common import np,Point
checks=[]
for name,q,h,mat in areas:
 for x in np.arange(q.bounds[0]+2,q.bounds[2],6):
  for z in np.arange(q.bounds[1]+2,q.bounds[3],6):
   if q.buffer(-.5).contains(Point(x,z)):checks.append([x,h,z])
Path('build/city-exteriors/fashion-roof-samples.json').write_text(json.dumps(checks))
