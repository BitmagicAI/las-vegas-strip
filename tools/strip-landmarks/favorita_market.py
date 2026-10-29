"""Original market reconstruction. Public arrangement inferred from dated photographs."""
from common import *
KEY='favorita-market';ID='way/390003968';YAW=math.pi+.0019

def build(B):
 p=footprint(ID);F=Frame(B,1980.9,-509.60,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=F.p(2,.16,.08),yaw=YAW,width=2.3,height=2.65,name='Market public entrance',venue=KEY)
 B.shell(p,.10,5.1,'fm-stucco',roof=False,openings=[entry]);B.planar('fm-roof',p,4.95);B.planar('fm-concrete',p,.16,True)
 # The eastern market frontage projects ahead of the western shop wing.
 for a,b,v in [(-20.5,20.5,0),(20.5,43.1,-4.25)]:
  F.box('fm-blue',((a+b)/2,4.17,v+.22),(b-a,1.55,.50))
  for h,th,d in [(3.38,.16,.85),(4.94,.12,.65),(5.08,.16,.95)]:F.box('fm-cream',((a+b)/2,h,v+.24),(b-a+.15,th,d))
  F.box('fm-concrete',((a+b)/2,.07,v+.8),(b-a,.14,1.65),True)
  for u in np.arange(a+.75,b-.5,1.5):
   if v==0 and .7<float(u)<3.3:continue
   F.box('fm-frame',(float(u),1.78,v+.12),(1.47,2.85,.12))
   F.box('fm-glass',(float(u),1.78,v+.21),(1.35,2.72,.025))
   F.box('fm-frame',(float(u),2.65,v+.24),(1.45,.045,.04))
   # Original window advertising panels; no reproduced artwork.
   if int(u)%4==0:
    F.box('fm-paper',(float(u),1.55,v+.25),(1.15,1.35,.022))
    F.box('fm-green',(float(u),2.05,v+.28),(1.03,.16,.018))
    for h in [1.25,1.5,1.75]:F.box('fm-red',(float(u),h,v+.28),(.78,.055,.018))
  for u in [a+.15,b-.15]:F.box('fm-stucco',(u,1.77,v+.22),(.28,3.25,.40),True)
 # Sign sizes estimated; plain original lettering stands in for owner logo art.
 F.text('La Favorita',(1,4.38,.55),.68,'fm-red',back=True)
 F.text('MARKET',(1,3.70,.56),.62,'fm-green',back=True)
 F.box('fm-paper',(13,4.20,.53),(9,1.24,.10));F.text('LIQUOR',(13,3.90,.61),.85,'fm-red',back=True)
 for u,t in [(-16,'CARNICERIA'),(-8,'PANADERIA')]:F.text(t,(u,4.35,.55),.40,'fm-red',back=True)
 F.box('fm-paper',(-11.5,3.85,.55),(14,.40,.06));F.text('FRESH PRODUCE & MEAT',(-11.5,3.71,.60),.34,'fm-green',back=True)
 F.text('MARKET SHOPS',(31,4.03,-3.68),.52,'fm-cream',back=True)
 for u in [-18,-5,8,19,29,40]:
  v=0 if u<20.5 else -4.25
  F.box('fm-frame',(u,3.25,v+.39),(.45,.12,.22));F.box('fm-lamp',(u,3.18,v+.40),(.38,.025,.18))
 for a,b in zip(list(p.exterior.coords)[:-1],list(p.exterior.coords)[1:]):B.tube('fm-cream',(a[0],5.07,a[1]),(b[0],5.07,b[1]),.065,8)
 for u,v in [(-15,-8),(-3,-20),(9,-14),(23,-18),(36,-12)]:
  F.box('fm-metal',(u,5.35,v),(1.7,.8,1.4))
  for k in range(7):F.box('fm-frame',(u,5.76,v-.55+k*.18),(1.45,.025,.04))
 # Public trading area only. Hidden preparation/stock rooms remain closed.
 B.property=KEY+'-interior';B.source='public/'+KEY
 F.box('fm-floor-dark',(0,.18,-10),(40,.025,19.8))
 for i,u in enumerate(np.arange(-19.75,20,.5)):
  for j,v in enumerate(np.arange(-19.75,0,.5)):
   if (i+j)%2==0:B.upface('fm-floor-light',[F.p(float(u)+x,.196,float(v)+z) for x,z in [(-.247,-.247),(.247,-.247),(.247,.247),(-.247,.247)]])
 for u in [-20,20]:F.box('fm-wall',(u,1.85,-10),(.18,3.4,20),True)
 F.box('fm-wall',(0,1.85,-19.9),(40,3.4,.18),True)
 F.box('fm-ceiling',(0,3.55,-10),(40,.12,20))
 for u in np.arange(-19.8,20,1.2):F.box('fm-grid',(float(u),3.48,-10),(.02,.025,19.8))
 for v in np.arange(-19.8,0,.6):F.box('fm-grid',(0,3.48,float(v)),(39.8,.025,.02))
 for u in [-15,-8,-1,6,13]:
  for v in [-3,-8,-13,-18]:
   F.box('fm-frame',(u,3.46,v),(.60,.04,1.16))
   for dx in [-.18,0,.18]:F.box('fm-lamp',(u+dx,3.42,v),(.07,.035,1.06))
 for u in np.arange(-19.3,19.5,1.5):
  if .6<u<3.4:continue
  F.box('fm-frame',(float(u),1.75,-.15),(1.48,2.9,.10));F.box('fm-glass',(float(u),1.75,-.22),(1.36,2.76,.025))
 # Shelf modules with varied original packages and simple price strips.
 def shelf(u,v,length):
  F.box('fm-frame',(u,1.23,v),(.12,2.10,length),True)
  for z in np.arange(-length/2,length/2+.01,1.25):F.box('fm-metal',(u,1.32,v+float(z)),(.065,2.3,.065))
  for level in range(5):
   h=.28+level*.40
   F.box('fm-metal',(u,h,v),(1.08,.04,length),True)
   for side in [-1,1]:
    F.box('fm-paper',(u+side*.54,h+.06,v),(.025,.09,length))
    for k,z in enumerate(np.arange(-length/2+.14,length/2-.10,.32)):
     colour='fm-pack-'+str((k+level*2+int(u))%6);height=.24+((k+level)%3)*.035
     if level in [1,2]:
      F.lathe(colour,u+side*.30,v+float(z),[(h+.025,.105),(h+.27,.105),(h+.28,.095)],10)
      F.lathe('fm-metal',u+side*.30,v+float(z),[(h+.27,.108),(h+.285,.108)],10)
      F.box('fm-paper',(u+side*.408,h+.14,v+float(z)),(.014,.075,.13))
     elif level==3:
      F.lathe(colour,u+side*.30,v+float(z),[(h+.025,.095),(h+.22,.095),(h+.28,.04),(h+.34,.04)],10)
      F.lathe('fm-metal',u+side*.30,v+float(z),[(h+.34,.044),(h+.37,.044)],8)
      F.box('fm-paper',(u+side*.395,h+.14,v+float(z)),(.014,.085,.13))
     else:
      F.box(colour,(u+side*.31,h+.04+height/2,v+float(z)),(.40,height,.25))
      F.box('fm-paper',(u+side*.515,h+.16,v+float(z)),(.012,.11,.20))
      F.box('fm-green',(u+side*.524,h+.18,v+float(z)),(.008,.027,.14))
      F.box('fm-red',(u+side*.524,h+.11,v+float(z)),(.008,.018,.12))
 for u in [-16,-11,-6,-1,4,9]:shelf(u,-10,11.0)
 # Refrigerated glass doors along the west side, with handles and bottle silhouettes.
 for v in np.arange(-17,-4,1.05):
  F.box('fm-frame',(18.8,1.3,float(v)),(1.6,2.2,1.0),True)
  F.box('fm-glass',(17.97,1.37,float(v)),(.03,1.98,.91))
  F.box('fm-metal',(17.91,1.37,float(v)+.35),(.07,.65,.035))
  for h in [.55,.92,1.29,1.66,2.02]:
   F.box('fm-metal',(17.9,h,float(v)),(.04,.035,.90))
   for k in range(4):F.lathe('fm-pack-'+str(k%6),17.84,float(v)-.32+k*.21,[(h+.025,.075),(h+.19,.075),(h+.23,.03),(h+.28,.03)],10)
 # Red/white refrigerated meat counter; public side, private area blocked behind.
 for u in [-15,-10,-5,0,5,10]:
  F.box('fm-red',(u,.55,-18.45),(4.9,.70,1.2),True)
  F.box('fm-paper',(u,.58,-17.83),(4.8,.28,.03))
  F.box('fm-metal',(u,.95,-18.45),(4.95,.08,1.3))
  F.box('fm-case-glass',(u,1.25,-17.84),(4.75,.53,.025))
  F.box('fm-metal',(u,1.53,-18.42),(4.95,.08,1.38))
  for dx in [-2.4,0,2.4]:F.box('fm-metal',(u+dx,1.24,-17.8),(.045,.55,.05))
  for dx in [-1.75,-.6,.6,1.75]:
   F.box('fm-paper',(u+dx,.78,-17.78),(.8,.26,.02));F.box('fm-pack-0',(u+dx,1.04,-18.10),(.85,.10,.55))
 # Checkout islands near entrance, out of the public route.
 for u in [7,12]:
  F.box('fm-frame',(u,.72,-2.3),(2.2,1.1,1.0),True);F.box('fm-metal',(u,1.3,-2.3),(2.35,.08,1.1))
  F.box('fm-display',(u+.6,1.53,-2.25),(.45,.38,.12));F.box('fm-frame',(u+.6,1.32,-2.25),(.12,.20,.10))
 F.text('CARNICERIA',(0,2.7,-19.72),.46,'fm-red',back=True)
 for u in [-12,0,12]:F.light(u,3.1,-10,power=55,range=17)
 route=[F.p(u,.16,v) for u,v in [(2,2),(2,-2),(1.5,-5),(1.5,-16.6),(13,-16.6),(14.5,-8)]]
 views={n:dict(eye=F.p(*e),target=F.p(*t)) for n,e,t in [('entrance',(2,1.8,3),(2,1.6,-6)),('aisle',(1.5,1.8,-5),(1.5,1.5,-14)),('counter',(13,1.8,-16.5),(2,1.2,-18.3)),('coolers',(14.5,1.8,-8),(18,1.4,-11))]}
 return dict(key=KEY,name='La Favorita Market',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-2,p.bounds[2]+1,p.bounds[3]+1],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(0,.16,0),yaw=YAW+math.pi,width=40,depth=20,height=3.4)],lights=B.lights,hotelSources=[],routes=[dict(name='Market entry, aisles, counter and coolers',points=route)],views=views)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
