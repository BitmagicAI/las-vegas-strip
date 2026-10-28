"""Original Paradise Road McDonalds exterior; December2022 reference, dimensions estimated."""
from common import *
KEY='mcdonalds-paradise';ID='way/205499657'
def window(F,u,v,w,h=2.25,base=.6):
 F.box('mp-glass',(u,base+h/2,v),(w,h,.06))
 for x in np.linspace(u-w/2,u+w/2,max(2,round(w/1.3)+1)):F.box('mp-frame',(float(x),base+h/2,v+.045),(.055,h+.08,.08))
 for y in [base,base+h]:F.box('mp-frame',(u,y,v+.045),(w+.07,.065,.08))
def arches(F,u,h,v,scale=1):
 for sign in [-1,1]:
  pts=[]
  for t in np.linspace(0,math.pi,25):pts.append((u+sign*.4*scale+.4*scale*math.cos(t),h+1.45*scale*math.sin(t),v))
  F.path('mp-yellow',pts,.055*scale,10)
def build(B):
 p=footprint(ID);F=Frame(B,1670.6,-667.25,0,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 B.shell(p,.03,5.4,'mp-stucco',roof=False);B.planar('mp-roof',p,5.3);B.planar('mp-paving',p,.12,True)
 rng=random.Random(336)
 # Two irregular pale masonry panels framing the public facade.
 for u,w in [(-11.7,5.2),(0,7.3)]:
  F.box('mp-joint',(u,2.65,.14),(w,5.15,.25))
  for row in range(22):
   h=.25+row*.224;x=u-w/2
   while x<u+w/2:
    bw=min(rng.uniform(.28,.65),u+w/2-x)
    # Keep entrance and left window free of decorative stone.
    opening=(u==0 and x+bw>-.85 and x<1.05 and h<3.0) or (u<0 and x+bw>u-1.5 and x<u+1.5 and .55<h<2.95)
    if not opening:F.box('mp-stone-'+str(rng.randrange(4)),(x+bw/2,h,.3+rng.uniform(0,.025)),(max(.01,bw-.018),.199,.08))
    x+=bw
 # Glazed south entrance and windows, backed by structural shell (interior deferred).
 window(F,.1,.42,1.8,2.8,.13);F.box('mp-handle',(.65,1.35,.54),(.045,.55,.065))
 window(F,-11.7,.42,3,2.3,.58);window(F,-6.6,.18,4.8,1.9,.85)
 for u,w in [(.1,3.3),(-11.7,3.4)]:
  F.box('mp-cream',(u,3.22,.75),(w,.63,1.25))
  for x in np.arange(u-w/2+.14,u+w/2,.55):F.box('mp-yellow',(float(x),3.22,1.39),(.23,.61,.025))
  F.box('mp-trim',(u,2.89,.77),(w+.08,.07,1.32))
 F.text('Welcome',(.1,3.03,1.43),.26,'mp-dark',back=True)
 arches(F,2.55,3.8,.45,.8)
 # Thin bright cap and shallow curved roof eyebrow over the dining half.
 for u,w in [(-7.3,15),(7.6,14.6)]:F.box('mp-trim',(u,5.43,0),(w,.09,.36))
 for k in range(30):
  a=-14.5+k*.5;b=a+.5;ha=5.55+.55*math.sin((a+14.5)/15*math.pi);hb=5.55+.55*math.sin((b+14.5)/15*math.pi)
  B.upface('mp-cream',[F.p(a,ha,.5),F.p(b,hb,.5),F.p(b,hb,-.6),F.p(a,ha,-.6)])
  F.tube('mp-trim',(a,ha,.53),(b,hb,.53),.045,8)
 for u in [-13.8,-7.2,.2]:F.box('mp-frame',(u,5.68,-.05),(.08,.5,.09))
 F.box('mp-dark',(8.5,4.3,.2),(9.9,.85,.08));F.text('ORDER  PAY  PICK UP',(8.5,4.3,.27),.43,'mp-cream',back=True)
 F.box('mp-trim',(8.5,3.72,.17),(12,.08,.15))
 for u in [4.8,11.8]:F.box('mp-dark',(u,2.8,.25),(.16,.12,.25))
 # West glazing and drive-through service on north; only surfaces supported or inferred.
 W=Frame(B,1655.7,-674,-math.pi/2,y=0);window(W,0,.22,5.8,2.2,.65);W.box('mp-cream',(0,3.18,.6),(6.2,.16,1.0))
 N=Frame(B,1670.6,-681.15,math.pi,y=0);window(N,-7,.18,1.6,1.2,1.1);N.box('mp-cream',(-7,2.75,.55),(2.5,.15,.9));N.box('mp-steel',(-7,1.05,.4),(1.9,.1,.6))
 N.box('mp-dark',(5,1.3,.12),(1.1,2.4,.08))
 for u,v in [(-6,-6),(6,-6)]:
  F.box('mp-steel',(u,5.75,v),(2.0,.9,1.6));F.box('mp-dark',(u,6.23,v),(1.8,.05,1.4))
 # South approach slab and freestanding pylon; retain the existing roads.
 F.box('mp-paving',(0,.06,.95),(30,.12,1.9),True)
 P=Frame(B,1653.5,-662.2,0,y=0);P.box('mp-pole',(0,4,0),(.45,8,.45),True);P.box('mp-red',(0,7.8,0),(2.6,.8,.45));P.text("McDonald's",(0,7.8,.25),.34,'mp-cream',back=True);arches(P,0,8.2,.05,1.45)
 route=[F.p(.1,.12,v) for v in [2.5,1.3,.9]]
 return dict(key=KEY,name='McDonalds Paradise Road',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-4,p.bounds[1]-2,p.bounds[2]+2,p.bounds[3]+7],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='South public entrance approach',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
