"""Original Paradise retail exterior. February2023frontage, no claimed interior."""
from common import *
KEY='paradiseShop';ID='way/1127963483'
def build(B):
 p=footprint(ID);F=Frame(B,2000.393,1174.81,-math.atan2(.034,10.611),y=0)
 B.property=KEY+'-exterior';B.source='podium/paradise-smoke-shop';B.detail=0
 B.shell(p,.08,4.6,'ps-block',roof=False);B.planar('ps-roof',p,4.61)
 F.box('ps-brown',(5.30,.63,-.08),(10.6,1.06,.12))
 F.box('ps-panel',(5.30,2.1,-.09),(10.6,1.88,.14))
 F.box('ps-stone',(5.3,3.25,-.12),(10.6,.40,.18))
 F.box('ps-green',(5.3,4.02,-.18),(10.6,1.12,.32))
 for i in range(12):
  a=i*math.pi/24;b=(i+1)*math.pi/24
  B.face('ps-green',[F.p(x,4.54+.27*math.sin(t),.12-.34*math.cos(t)) for x,t in [(0,a),(10.6,a),(10.6,b),(0,b)]])
 for x in [.14,10.45]:F.box('ps-brick',(x,1.62,-.20),(.28,3.0,.24))
 for x in [.45,.75,1.05,9.5,9.8,10.1]:F.box('ps-joint',(x,2.1,-.17),(.012,1.82,.015))
 F.box('ps-sign',(5.3,4.04,-.38),(8.1,.89,.06));F.text('SMOKE SHOP',(5.3,3.80,-.43),.67,'ps-ink')
 F.text('SMOKE SHOP',(5.3,2.94,-.25),.48,'ps-gold')
 # Glazing with independent door leaf, mullions and metal handles.
 for x in [2.65,5.3,7.95]:
  F.box('ps-glass',(x,1.65,-.19),(2.55,2.20,.07))
  for dx in [-1.30,1.30]:F.box('ps-metal',(x+dx,1.65,-.25),(.055,2.28,.08))
  for y in [.52,2.77]:F.box('ps-metal',(x,y,-.25),(2.62,.05,.08))
 for x in [6.60,7.80]:F.box('ps-metal',(x,1.65,-.28),(.055,2.20,.07))
 F.tube('ps-metal',(7.57,1.04,-.35),(7.57,1.53,-.35),.023,10)
 # Abstract original display sheets evoke the busy windows without copied ads.
 for i,(u,y,w,h) in enumerate([(1.95,2.2,.9,.7),(3.0,2.17,.85,.8),(4.0,2.1,.7,.95),(5.0,2.25,.9,.65),(5.9,1.1,.7,.75),(8.35,2.15,.9,.85),(2.0,1.1,1.1,.8),(3.3,1.15,.9,.7),(4.45,1.1,1.1,.75),(8.6,1.1,.6,.8),(7.2,2.2,.75,.7)]):
  F.box('ps-display'+str(i%3),(u,y,-.235),(w,h,.018))
 F.box('ps-concrete',(5.3,.12,-.65),(10.6,.18,1.2),True)
 for x in [2.4,5.2,8.0]:F.box('ps-stop',(x,.15,-2.3),(1.45,.16,.16),True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('ps-metal',(a[0],4.66,a[1]),(b[0],4.66,b[1]),.05,6)
 B.box('ps-metal',(2005.4,4.95,1183),(2.0,.65,1.5))
 for z in np.arange(1182.4,1183.7,.16):B.box('ps-ink',(2005.4,5.29,z),(1.7,.02,.06))
 B.tube('ps-metal',(2010.6,.12,1189.18),(2010.6,4.5,1189.18),.04,8)
 return dict(key=KEY,name='Paradise retail shop',center=[2005.7,0,1182],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
