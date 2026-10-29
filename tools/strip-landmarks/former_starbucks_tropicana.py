"""Original former cafe shell. Permanent exterior from site panorama; tenancy unverified."""
from common import *
KEY='former-starbucks-tropicana';IDS=['way/431504495']
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 p=footprint(IDS[0]);F=Frame(B,-1290.646,1707.875,-.01354,y=0);w=11.575;d=35.224
 B.shell(p,.02,4.85,'sb-stucco',roof=False);B.planar('sb-roof',p,4.55)
 B.shell(p.buffer(.035,join_style=2),.02,.96,'sb-plinth',roof=False,solid=False)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  G.box('sb-coping',(L/2,4.87,0),(L+.04,.14,.26));G.box('sb-trim',(L/2,4.68,-.03),(L,.04,.08))
 # Street-facing west facade. Shallow sloping metal canopy and glazed recessed bays.
 W=Frame(B,*[F.p(0,0,d)[i] for i in (0,2)],F.yaw+math.pi/2,y=0)
 for x,width in [(15.9,2.9),(19.6,2.5),(23.4,3.3),(27.8,3.4),(31.5,2.8)]:
  W.box('sb-recess',(x,2.05,-.06),(width,2.22,.12))
  W.box('sb-glass',(x,2.05,-.14),(width-.12,2.08,.045))
  for xx in [x-width/2,x,x+width/2]:W.box('sb-metal',(xx,2.05,-.18),(.055,2.24,.07))
  for y in [.95,3.16]:W.box('sb-metal',(x,y,-.18),(width+.05,.055,.07))
  W.box('sb-sill',(x,.91,-.15),(width+.2,.09,.24))
 # Closed entrance with visible double-door frame and handles; no fabricated interior.
 x=23.4
 W.box('sb-recess',(x,1.64,-.07),(2.35,2.65,.14));W.box('sb-glass',(x,1.64,-.17),(2.25,2.53,.055))
 for xx in [x-1.16,x,x+1.16]:W.box('sb-metal',(xx,1.64,-.23),(.065,2.65,.09))
 for yy in [.33,2.96]:W.box('sb-metal',(x,yy,-.23),(2.38,.065,.09))
 for xx in [x-.13,x+.13]:W.tube('sb-chrome',(xx,1.25,-.30),(xx,1.68,-.30),.018,8)
 W.text('3575',(x,3.08,-.25),.24,'sb-letter')
 a=14.0;b=33.3
 B.face('sb-canopy',[W.p(a,3.28,-1.25),W.p(b,3.28,-1.25),W.p(b,3.85,-.05),W.p(a,3.85,-.05)])
 B.face('sb-canopy',[W.p(a,3.25,-1.25),W.p(a,3.76,-.05),W.p(b,3.76,-.05),W.p(b,3.25,-1.25)])
 W.box('sb-canopy',((a+b)/2,3.26,-1.25),(b-a,.12,.11))
 for x in np.arange(a,b,.65):W.tube('sb-seam',(x,3.30,-1.26),(x,3.87,-.05),.009,5)
 for x in [14.3,18.4,22.2,26.6,30.9,33]:W.tube('sb-metal',(x,3.23,-1.1),(x,2.93,-.10),.023,8)
 # Lights are modeled fittings, not runtime-created emitters.
 for x in [13.2,18.0,21.5,25.7,30.0,34.1]:
  W.box('sb-metal',(x,2.75,-.12),(.18,.27,.18));W.box('sb-letter',(x,2.74,-.22),(.12,.17,.025))
 for z in [25,30,34]:F.box('sb-metal',(-.09,3.63,z),(.14,.18,.32))
 # North-end patio with railing, masonry sill and modest existing glazing.
 for x in [2.1,5.2,8.4]:
  F.box('sb-metal',(x,2.04,-.08),(2.62,2.23,.11));F.box('sb-glass',(x,2.04,-.15),(2.49,2.10,.04))
  F.box('sb-metal',(x,2.04,-.19),(.05,2.18,.06))
 F.box('sb-paving',(w/2,.245,-1.55),(w+.3,.15,3.1),True)
 W.box('sb-paving',(d/2,.245,-1.4),(d+.3,.15,2.8),True)
 # Patio edges deliberately leave a clear opening to the west apron.
 for a,b in [((.4,-2.8),(w-.3,-2.8)),((w-.3,-2.8),(w-.3,-.2))]:
  L=math.dist(a,b);n=max(1,int(L/.14))
  for i in range(n+1):
   x=a[0]+(b[0]-a[0])*i/n;z=a[1]+(b[1]-a[1])*i/n
   F.tube('sb-metal',(x,.33,z),(x,1.4,z),.012,6)
  F.tube('sb-metal',(a[0],1.4,a[1]),(b[0],1.4,b[1]),.03,8)
  F.tube('sb-metal',(a[0],.48,a[1]),(b[0],.48,b[1]),.025,8)
 # East drive-through glazing and protective sill, southern closed service door.
 E=Frame(B,*[F.p(w,0,0)[i] for i in (0,2)],F.yaw-math.pi/2,y=0)
 E.box('sb-metal',(8,2.05,-.10),(2.15,1.65,.15));E.box('sb-glass',(8,2.05,-.20),(2.01,1.50,.04));E.box('sb-metal',(8,2.05,-.24),(.05,1.6,.06));E.box('sb-sill',(8,1.2,-.35),(2.3,.12,.60))
 E.box('sb-canopy',(8,3.12,-.65),(2.7,.12,1.3))
 for z in [24,30]:
  F.box('sb-equipment',(6,5.0,z),(2.8,.9,2.0));F.box('sb-metal',(6,5.48,z),(2.95,.10,2.15))
  for zz in np.arange(z-.8,z+.8,.18):F.box('sb-seam',(6,5.0,zz),(2.83,.035,.035))
 S=Frame(B,*[F.p(w,0,d)[i] for i in (0,2)],F.yaw+math.pi,y=0)
 S.box('sb-metal',(3,1.45,-.06),(1.2,2.6,.12));S.box('sb-service',(3,1.45,-.15),(1.08,2.46,.05));S.tube('sb-chrome',(3.4,1.3,-.21),(3.4,1.56,-.21),.018,8)
 for x in [.2,w-.2]:F.tube('sb-coping',(x,.15,d-.1),(x,4.72,d-.1),.055,8)
 routes=[dict(name='West frontage and closed entrance',points=[W.p(x,.32,-1.65) for x in [2,12,23.4,33.5]]),dict(name='North patio',points=[F.p(x,.32,-1.4) for x in [1,5.7,10.5]])]
 return dict(key=KEY,name='3575 West Tropicana retail shell',center=[-1285,0,1724],bounds=[-1295,1704,-1276,1746],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
