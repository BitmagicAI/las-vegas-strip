"""Original Twain laundry public room and exterior.
Street Dec2022 / public room Sep2026; tenant partition and dimensions inferred.
"""
from common import *
KEY='twain-laundry';ID='way/390003970';YAW=math.pi/2-.008412

def build(B):
 p=footprint(ID);F=Frame(B,1944.3455,-545.2265,YAW,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=F.p(19,.18,.1),yaw=YAW,width=2,height=2.75,name='Laundry public entrance',venue=KEY)
 B.shell(p,.12,5.2,'tl-stucco',roof=False,openings=[entry]);B.planar('tl-roof',p,5.1);B.planar('tl-concrete',p,.18,True)
 F.box('tl-concrete',(0,.08,1.0),(50.2,.16,2.1),True)
 F.box('tl-blue-fascia',(0,4.23,.36),(50.2,1.55,.72))
 for h,d,t in [(3.44,1.1,.16),(5.0,.85,.16),(5.15,1.08,.14)]:F.box('tl-cream',(0,h,.34),(50.45,t,d))
 # Continuous front glazing; north door is a real portal; southern retail stays closed.
 for a,b in [(-24.5,17.9),(20.1,24.5)]:
  count=math.ceil((b-a)/1.5);step=(b-a)/count
  for i in range(count):
   u=a+step*(i+.5);F.box('tl-frame',(u,1.82,.15),(step-.03,2.92,.12))
   F.box('tl-glass',(u,1.82,.24),(step-.12,2.78,.035))
   F.box('tl-frame',(u,2.76,.28),(step,.05,.04))
 for u in [-24.8,-10,7,24.8]:F.box('tl-brick',(u,1.8,.27),(.42,3.22,.50),True)
 F.text('24 HRS LAUNDROMAT',(6.0,4.12,.77),.66,'tl-red',back=True)
 F.box('tl-cream',(20,4.35,.75),(8.0,.92,.14));F.box('tl-red',(20,4.35,.84),(7.85,.78,.03))
 F.text('LAUNDROMAT & CLEANERS',(20,4.17,.88),.38,'tl-cream',back=True)
 F.text('PIZZA',(-18,4.15,.77),.65,'tl-gold',back=True)
 for u in [-22,-8,10,24]:
  F.box('tl-metal',(u,5.21,.30),(.16,.22,.22));F.box('tl-lamp',(u,5.08,.45),(.13,.10,.12))
 # Roof parapet and varied ventilation; service positions inferred from aerial.
 for a,b in zip(list(p.exterior.coords)[:-1],list(p.exterior.coords)[1:]):B.tube('tl-cream',(a[0],5.18,a[1]),(b[0],5.18,b[1]),.07,8)
 for u,v in [(-20,-9),(-12,-7),(-3,-10),(6,-6),(14,-10),(21,-7)]:
  F.box('tl-metal',(u,5.48,v),(1.25,.65,1.25))
  for k in range(6):F.box('tl-frame',(u,5.82,v-.45+k*.18),(1.05,.02,.035))
 for u in np.arange(-18,22,4):F.lathe('tl-metal',float(u),-12,[(5.1,.13),(5.6,.13),(5.65,.24)],12)
 # Public room occupies the northern tenant; exact room division is inferred.
 B.property=KEY+'-interior';B.source='public/'+KEY
 F.box('tl-grout',(7.5,.195,-6.9),(34,.025,13.7))
 # Small square tan tile with thin darker joints, no baked photographed surface.
 for u in np.arange(-9.3,24.4,.30):
  for v in np.arange(-13.6,-.2,.30):
   B.upface('tl-tile-'+str((int(round(u*10))+int(round(v*10)))%3),[F.p(float(u)+a,.217,float(v)+b) for a,b in [(-.145,-.145),(.145,-.145),(.145,.145),(-.145,.145)]])
 for u in [-9.6,24.6]:F.box('tl-wall-blue',(u,1.85,-7),(.20,3.35,14),True)
 F.box('tl-wall-blue',(7.5,1.85,-13.85),(34,3.35,.22),True)
 F.box('tl-ceiling',(7.5,3.55,-7),(34,.12,14))
 for u in np.arange(-9,25,1.2):F.box('tl-grid',(float(u),3.48,-7),(.025,.025,13.8))
 for v in np.arange(-13.5,0, .6):F.box('tl-grid',(7.5,3.48,float(v)),(33.9,.025,.025))
 for u in np.arange(-7,25,4):
  for v in [-3,-8,-12]:F.box('tl-lamp',(float(u),3.46,v),(.52,.035,1.1))
 # Inward reveals align with the street glazing; keep doorway clear.
 for a,b in [(-9.3,17.9),(20.1,24.4)]:
  for u in np.arange(a+.65,b-.45,1.5):
   F.box('tl-frame',(float(u),1.82,-.12),(1.48,2.92,.12));F.box('tl-glass',(float(u),1.82,-.20),(1.36,2.78,.025))
 # A dryer has a recessed black gasket, stainless rim, visible dark drum and controls.
 def machine(u,v,y,face=1,stack=False):
  F.box('tl-metal',(u,y+.51,v),(1.08,1.02,.88),True)
  z=v+face*.46
  # front circle lies in local XY plane
  for rad,mat,th in [(.37,'tl-frame',.035),(.335,'tl-chrome',.025),(.29,'tl-frame',.022)]:
   pts=[(u+rad*math.cos(a),y+.48+rad*math.sin(a),z+face*.025) for a in np.linspace(0,math.tau,33)]
   F.path(mat,pts,th,6)
  B.face('tl-drum',[F.p(u+.275*math.cos(a),y+.48+.275*math.sin(a),z) for a in np.linspace(0,math.tau,33)])
  # Curved inner drum highlight through dark door glass, no wheel-like spokes.
  F.path('tl-metal',[(u+.22*math.cos(a),y+.48+.22*math.sin(a),z+face*.012) for a in np.linspace(.25,2.3,18)],.009,5)
  F.box('tl-frame',(u,y+.93,z),(1.0,.13,.04))
  F.box('tl-display',(u-.27,y+.93,z+face*.03),(.20,.08,.025))
  for x in [.10,.25,.40]:F.box('tl-button',(u+x,y+.93,z+face*.03),(.055,.055,.025))
  F.box('tl-frame',(u+.37,y+.45,z+face*.07),(.08,.18,.065))
 # Rear stacked dryers leave a generous aisle before folding tables.
 for u in np.arange(-8.5,24,1.14):
  machine(float(u),-13.2,.24);machine(float(u),-13.2,1.28)
 # Two islands of front-loading washers, with cross aisle near entry.
 for a,b in [(-8,6),(10,16)]:
  for u in np.arange(a,b,1.15):
   machine(float(u),-5.0,.24,1);machine(float(u),-5.92,.24,-1)
 def table(u,v):
  F.box('tl-table-blue',(u,1.05,v),(2.5,.12,1.05),True)
  for x in [-1.03,1.03]:
   for z in [-.36,.36]:
    F.tube('tl-frame',(u+x,.24,v+z),(u+x*.85,1.0,v+z*.85),.025,8)
  for x in [-1.1,1.1]:F.tube('tl-metal',(u+x,1.1,v+.4),(u+x,1.95,v+.4),.02,8)
  F.tube('tl-metal',(u-1.1,1.95,v+.4),(u+1.1,1.95,v+.4),.02,8)
 for u in [-7,-2,3,8,13,22]:table(u,-9.0)
 # Wire laundry carts and simple public seating, as photographed.
 for u in [-5,5,13]:
  v=-10.7
  F.box('tl-metal',(u,.55,v),(.65,.04,.85))
  for x in [-.30,.30]:
   for z in [-.38,.38]:
    F.tube('tl-metal',(u+x,.35,v+z),(u+x,.95,v+z),.015,6)
    F.box('tl-frame',(u+x,.31,v+z),(.09,.13,.09))
  for h in [.6,.73,.86,.98]:F.path('tl-metal',[(u-.33,h,v-.44),(u+.33,h,v-.44),(u+.33,h,v+.44),(u-.33,h,v+.44),(u-.33,h,v-.44)],.012,6)
 for u in [-7,-2,3,8,13]:
  F.box('tl-red',(u,.65,-1.0),(.58,.12,.55),True);F.box('tl-red',(u,.96,-.75),(.58,.58,.10),True)
  for dx in [-.23,.23]:F.tube('tl-frame',(u+dx,.25,-1),(u+dx,.62,-1),.025,8)
 # Screen content is original abstract colour, no copied program footage.
 for u in [-2,13]:
  F.box('tl-frame',(u,2.95,-13.66),(1.7,1.0,.10));F.box('tl-display',(u,2.95,-13.59),(1.55,.84,.035))
 for u in [-5,6,19]:F.light(u,3.1,-7,power=65,range=15)
 route=[F.p(u,.18,v) for u,v in [(19,2),(19,-1),(19,-8),(18,-11),(5,-11)]]
 return dict(key=KEY,name='24 Hour Laundry Center',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-1,p.bounds[2]+2.5,p.bounds[3]+1],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(7.5,.18,0),yaw=YAW+math.pi,width=34,depth=14,height=3.4)],lights=B.lights,hotelSources=[],routes=[dict(name='Entrance to washers,folding and dryers',points=route)],views={name:dict(eye=F.p(*eye),target=F.p(*target)) for name,eye,target in [('entrance',(19,1.8,3),(19,1.8,-5)),('washers',(19,1.8,-3),(8,1.5,-5)),('folding',(18,1.8,-10),(8,1.5,-9)),('dryers',(18,1.8,-11),(12,1.6,-13))]})
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
