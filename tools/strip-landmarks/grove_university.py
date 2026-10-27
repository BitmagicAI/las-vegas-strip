"""Grove/Society original exterior; mapped envelope, February2026 east reference.
Dimensions above the footprint are photographic estimates. No inferred interior.
"""
from common import *
KEY='groveUniversity';ID='way/1382446129'
def build(B):
 p=footprint(ID);B.property=KEY+'-exterior';B.source='podium/grove-university';B.detail=0
 B.shell(p,.12,4.6,'gu-block',roof=False);B.planar('gu-roof',p,4.61)
 # North parking frontage; stop at Double Down's shared wall.
 N=Frame(B,2011.004,1174.844,0,y=0)
 for x in [0.18,5.7,11.4,17.1,22.8]:N.box('gu-brick',(x,1.92,-.12),(.28,3.6,.20))
 N.box('gu-dark',(11.5,.8,-.10),(22.8,1.35,.12))
 for x in [2.9,8.55,14.25,19.9]:
  N.box('gu-glass',(x,1.92,-.20),(4.9,2.25,.08))
  for dx in [-2.5,0,2.5]:N.box('gu-metal',(x+dx,1.92,-.27),(.06,2.36,.06))
  for y in [.76,3.08]:N.box('gu-metal',(x,y,-.27),(5.06,.06,.06))
 # Door leaf detail retained as closed storefront; no invented public room.
 for x in [7.85,9.25]:
  N.box('gu-metal',(x,1.8,-.29),(1.36,2.12,.06));N.box('gu-glass',(x,1.82,-.34),(1.24,1.98,.03))
  N.tube('gu-metal',(x+.42,1.15,-.40),(x+.42,1.65,-.40),.025,8)
 N.box('gu-green',(11.5,4.08,-.18),(23,.95,.32))
 for i in range(12):
  a=i*math.pi/24;b=(i+1)*math.pi/24
  B.face('gu-green',[N.p(x,4.53+.32*math.sin(t),.15-.32*math.cos(t)) for x,t in [(0,a),(23,a),(23,b),(0,b)]])
 N.box('gu-sign',(11.5,4.05,-.38),(21.4,.72,.06));N.text('SOCIETY',(11.5,3.87,-.43),.50,'gu-dark');N.text('ELEVATED LOUNGE',(11.5,3.65,-.43),.16,'gu-dark')
 N.box('gu-concrete',(11.5,.12,-.7),(22.9,.18,1.2),True)
 # East street elevation: dark masonry and horizontal timber entrance tower.
 E=Frame(B,2047.0,1175.05,-math.pi/2,y=0)
 E.box('gu-block',(7.12,2.38,-.11),(14.15,4.44,.12))
 E.box('gu-wood',(9.7,4.0,-.35),(3.15,7.4,.54),True)
 for y in np.arange(.55,7.7,.20):E.box('gu-wood-light',(9.7,y,-.66),(3.22,.055,.055))
 E.box('gu-dark',(9.7,5.75,-.70),(2.72,2.9,.07))
 E.text('THE',(9.7,6.3,-.76),.30,'gu-sign');E.text('GROVE',(9.7,5.7,-.76),.54,'gu-sign')
 E.text('LAS VEGAS',(9.7,5.25,-.76),.20,'gu-sign')
 E.text('4647',(5.1,4.14,-.20),.23,'gu-sign')
 # Low timber canopy, open underneath, with beam depth and soffit.
 E.box('gu-wood',(10.5,3.15,-1.05),(7.3,.32,1.9))
 for y in [3.02,3.15,3.28]:E.box('gu-wood-light',(10.5,y,-2.02),(7.38,.035,.06))
 for x in [13.95,6.95]:E.box('gu-metal',(x,1.6,-1.85),(.12,3.05,.12),True)
 for x in [13.5,12.2,10.9,8.5,7.2]:
  E.box('gu-glass',(x,1.52,-.19),(1.18,2.55,.08))
  for dx in [-.62,.62]:E.box('gu-metal',(x+dx,1.52,-.25),(.05,2.65,.05))
 E.box('gu-concrete',(10.3,.12,-1.2),(8.0,.18,2.3),True)
 for x in [12.5,11.3]:E.tube('gu-metal',(x,1.1,-.29),(x,1.6,-.29),.025,8)
 # Coping and roof services: behind parapet; not speculative decorated back doors.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  B.tube('gu-metal',(a[0],4.66,a[1]),(b[0],4.66,b[1]),.075,6)
 for x,z in [(2018,1182),(2027,1182),(2038,1182)]:
  B.box('gu-metal',(x,4.98,z),(2.4,.72,1.8))
  for dz in np.arange(-.7,.8,.18):B.box('gu-dark',(x,5.35,z+dz),(2,.025,.06))
  B.tube('gu-metal',(x,4.62,z+2),(x,5.10,z+2),.14,10)
 for x in [2011.1,2046.9]:B.tube('gu-metal',(x,.18,1189.5),(x,4.6,1189.5),.05,8)
 return dict(key=KEY,name='The Grove / Society frontage',center=[2029,0,1182],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
