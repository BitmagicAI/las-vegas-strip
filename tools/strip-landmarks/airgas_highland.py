"""Airgas Highland: original measured-footprint shell and inferred public retail layout."""
from common import *
from shapely.geometry.polygon import orient
KEY='airgas-highland'
def build(B):
 p=orient(footprint('way/464694104'),sign=1);F=Frame(B,324.6665,-2934.7325,-.5203,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(5,.15,0),yaw=F.yaw,width=1.7,height=2.65,name='Airgas retail entrance',venue=KEY)
 windows=[dict(p=F.p(u,.6,0),yaw=F.yaw,width=w,height=2.3)for u,w in [(-6,4.5),(9,2.3)]]
 B.shell(p,0,4.7,'ag-cream',openings=[door]+windows,roof=False);B.planar('ag-membrane',p,4.68)
 F.box('ag-cream',(0,3.95,-.15),(25.6,1.5,.38));F.text('Airgas',(0,3.43,-.37),1.12,'ag-blue')
 for u in [-8.7,8.7]:F.box('ag-blue',(u,3.92,-.36),(6.5,.35,.025))
 for c in [door]+windows:
  # Convert opening centre back to this facade frame.
  dx,dz=c['p'][0]-F.p(0,0,0)[0],c['p'][2]-F.p(0,0,0)[2];u=dx*math.cos(F.yaw)-dz*math.sin(F.yaw)
  y=c['p'][1];h=c['height'];w=c['width'];isdoor=c is door
  F.box('ag-clear',(u,y+h/2,.03),(w-.04,h-.04,.025),not isdoor)
  for du in [-w/2,w/2]:F.box('ag-alloy',(u+du,y+h/2,-.025),(.06,h+.06,.09))
  for yy in [y,y+h,y+h*.76]:F.box('ag-alloy',(u,yy,-.025),(w,.055,.09))
  if isdoor:F.tube('ag-alloy',(u-.55,1,-.13),(u-.55,1.5,-.13),.025,10)
  else:F.box('ag-alloy',(u,y+h/2,-.025),(.05,h,.09))
 F.box('ag-sign',(0,1.9,-.055),(5.7,1.1,.08));F.text('GASES - WELDING',(0,2.04,-.11),.36,'ag-blue');F.text('& SAFETY PRODUCTS',(0,1.62,-.11),.30,'ag-blue')
 F.text('2600',(11,3.04,-.12),.32,'ag-blue')
 # Vertical groove finish limited to the solid frontage piers; no courses over glazing.
 for lo,hi in [(-12.5,-8.4),(-3.65,4.08),(6,7.8),(10.25,12.5)]:
  for u in np.arange(lo,hi,.18):F.box('ag-groove',(float(u),1.6,-.018),(.014,3.1,.024))
 # Bollards stand outside the clear doorway route.
 for u in [-11,-7,-2,2.8,7.4,11.7]:
  F.lathe('ag-yellow',u,-1.7,[(0,.13),(.95,.13),(1.1,.07),(1.13,0)],16)
  F.box('ag-foot',(u,.04,-1.7),(.42,.08,.42),True)
 for u in [-9,0,9]:
  F.box('ag-dark',(u,4.46,-.42),(.4,.23,.25));F.box('ag-lamp',(u,4.35,-.44),(.32,.025,.18))
 F.box('ag-paving',(5,.075,-.7),(2.3,.15,1.4),True)
 B.upface('ag-paving',[F.p(3.85,0,-2.4),F.p(6.15,0,-2.4),F.p(6.15,.15,-1.4),F.p(3.85,.15,-1.4)],True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);R.box('ag-coping',(0,4.78,0),(math.dist(a,b),.13,.28))
 for u,v in [(-6,6),(7,7)]:
  F.box('ag-equipment',(u,5.02,v),(1.6,.65,1.5));F.lathe('ag-dark',u,v,[(5.35,.44),(5.4,.44)],16)
  for q in range(6):F.box('ag-alloy',(u+.82,5.02,v-.6+q*.23),(.025,.4,.045))
 # Public sales area only. Back service/stock spaces are not represented as accessible rooms.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=Polygon([(F.p(u,0,v)[0],F.p(u,0,v)[2])for u,v in [(-12.2,.18),(12.2,.18),(12.2,10.9),(-12.2,10.9)]]).intersection(p.buffer(-.1))
 B.planar('ag-tile',room,.15,True);B.shell(room,.15,3.35,'ag-wall',openings=[door]+windows,roof=False,solid=True)
 for t in triangles(room):
  pts=[(x,3.35,z)for x,z in list(t.exterior.coords)[:-1]];ar=np.array(pts);B.face('ag-ceiling',pts if np.cross(ar[1]-ar[0],ar[2]-ar[0])[1]<0 else list(reversed(pts)))
 for u in np.arange(-11.5,12,.6):F.box('ag-grid',(float(u),3.325,5.5),(.018,.025,10.4))
 for v in np.arange(.3,10.8,.6):F.box('ag-grid',(0,3.325,float(v)),(23,.025,.018))
 for u in [-8,-2,4,9]:
  for v in [2.4,7.8]:F.box('ag-lamp',(u,3.3,v),(.56,.03,1.16))
 for u in np.arange(-11,12,1):F.box('ag-grout',(float(u),.154,5.5),(.008,.006,10.2))
 for v in np.arange(1,10.8,1):F.box('ag-grout',(0,.154,float(v)),(23,.006,.008))
 # Two low island displays leave wide walking routes around all four sides.
 for u in [-7,-1]:
  F.box('ag-dark',(u,.24,5.5),(.95,.18,4.5),True);F.box('ag-slat',(u,1.18,5.5),(.14,1.8,4.4),True)
  F.box('ag-blue',(u,2.12,5.5),(.19,.10,4.5))
  for side in [-1,1]:
   F.box('ag-shelf',(u+side*.29,.34,5.5),(.48,.08,4.4),True)
   for y in np.arange(.55,2.06,.15):F.box('ag-groove',(u+side*.078,float(y),5.5),(.018,.014,4.4))
   for v in np.arange(3.6,7.5,.48):
    for y in [.95,1.64]:
     F.tube('ag-alloy',(u+side*.09,float(y)+.13,float(v)),(u+side*.24,float(y)+.13,float(v)),.013,6)
     mat='ag-yellow'if int(v*10)%2 else 'ag-glove'
     # Original glove silhouettes: palm, cuff and five soft-ended fingers.
     F.box(mat,(u+side*.23,float(y),float(v)),(.065,.19,.17))
     F.box(mat,(u+side*.23,float(y)+.15,float(v)),(.065,.13,.2))
     for j in range(4):F.box(mat,(u+side*.23,float(y)-.15,float(v)-.06+j*.04),(.06,.14-.012*abs(j-1),.032))
     F.box('ag-paper',(u+side*.23,float(y)+.22,float(v)),(.075,.08,.23))
 # Back-wall shelf stock uses original blank package designs, no copied branding.
 for u in [-10,-7,-4,-1,2]:
  F.box('ag-slat',(u,1.25,10.55),(2.7,2.15,.12),True)
  for yy in [.4,.9,1.4,1.9]:
   F.box('ag-shelf',(u,yy,10.2),(2.7,.055,.65),True)
   for j in range(7):
    F.box('ag-paper'if j%2 else'ag-blue',(u-1.05+j*.34,yy+.18,10.18),(.25,.3,.35));F.box('ag-label',(u-1.05+j*.34,yy+.18,9.995),(.17,.06,.02))
 F.box('ag-counter',(8, .7,8.6),(5,1.1,.9),True);F.box('ag-dark',(8,1.28,8.6),(5.1,.08,1.0),True)
 F.box('ag-dark',(8,1.57,8.6),(.6,.45,.10));F.box('ag-blue',(8,1.57,8.535),(.52,.36,.02))
 routes=[dict(name='Store entrance and sales aisle',points=[F.p(u,y,v)for u,y,v in [(5,0,-4),(5,0,-2.4),(5,.15,-1.4),(5,.15,1),(5,.15,5),(5,.15,7.4)]]),dict(name='Display circulation',points=[F.p(u,.15,v)for u,v in [(5,2),(2,2),(-4,2),(-10,2),(-10,8.4),(-4,8.4),(2,8.4),(3,5)]])]
 return dict(key=KEY,name='Airgas Highland',center=F.p(0,0,5.5),bounds=list(p.buffer(5).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.15,.15),yaw=F.yaw,width=24.4,depth=10.8,height=3.2)],lights=[dict(p=F.p(u,3,v),color=0xf5f6ed,power=.8,range=12)for u,v in [(-7,3),(6,3),(-7,8),(6,8)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
