"""Public bridge-floor circulation from OSM corridor297110935 and owner plan.
Tenant interiors are retained outside the new corridor; no speculative shops.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import *
from harmon_east_lift import slab
B=Meshes();B.property='harmonBridgeConcourse';B.source='way/297110935';B.detail=0;H=6.035
path=LineString([(74.963,836.3),(76.71,810.01),(72.15,798.7),(63.03,788.95),(42.176,781.808)])
p=path.buffer(3,cap_style=2,join_style=2)
slab(B,p,H-.16,H,'access-tread')
# Actual corridor route; fine interior finishes remain an explicitly approximate pass.
for t in triangles(p):B.face('access-plaster',list(reversed([(x,9.5,z)for x,z in list(t.exterior.coords)[:-1]])))
openings=[Point(74.963,836.3).buffer(3.2),Point(40.8,781.8).buffer(3.2)]
for line in [path.offset_curve(3,join_style=2),path.offset_curve(-3,join_style=2)]:
 coords=list(line.coords)
 for a,b in zip(coords,coords[1:]):
  B.face('access-plaster',[(a[0],H,a[1]),(b[0],H,b[1]),(b[0],9.5,b[1]),(a[0],9.5,a[1])],True)
  B.tube('bridge-metal',(a[0],H+.12,a[1]),(b[0],H+.12,b[1]),.045,6)
for s in np.arange(2,path.length-2,5):
 q=path.interpolate(s);B.box('access-light',(q.x,9.45,q.y),(.6,.045,1.4))
ports=[dict(p=[74.963,835.1],direction=[0,-1],y=H,label='HARMON CORNER',width=4.8,height=3.1),dict(p=[42.2,781.8],direction=[1,0],y=H,label='PEDESTRIAN BRIDGE',width=4.8,height=3.1)]
data=dict(id='harmon-bridge-atrium',name='Harmon Corner bridge-floor passage',bounds=list(p.bounds),height=9.5,portals=ports,interior=True,meshes=list(B.groups.values()),collision=B.solids[B.property],lights=[[75,9,825],[76,9,810],[69,9,795],[52,9,785]],signs=[])
Path('build/city-exteriors/harmon-bridge-passage.pending.json').write_text(json.dumps(data,separators=(',',':')))
routes=[[[74.963,H,838],[74.963,H,835.1],[76.71,H,810.01],[72.15,H,798.7],[63.03,H,788.95],[42.176,H,781.808],[34.93,H,778.24],[29.09,H,778.02]]]
Path('build/city-exteriors/harmon-bridge-passage-routes.json').write_text(json.dumps(routes))
print('Harmon passage',sum(len(g['faces'])for g in B.groups.values()),'triangles',len(B.groups),'batches')
