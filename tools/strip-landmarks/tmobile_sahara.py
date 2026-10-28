"""Original reference-supported closed storefront. Hidden services estimated."""
from common import *
KEY='tmobile-sahara';ID='way/926281499'
def build(B):
 p=footprint(ID);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,-1719.6,-3190.25,0,y=0)
 B.shell(p,.08,6.45,'ms-stucco',roof=False);B.planar('ms-roof',p,6.35);B.planar('ms-paving',p,.14,True)
 for poly in parts(p):
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   length=math.dist(a,b);yaw=-math.atan2(b[1]-a[1],b[0]-a[0]);cx=(a[0]+b[0])/2;cz=(a[1]+b[1])/2
   for y,h,w in [(6.42,.15,.22),(6.20,.09,.13)]:B.box('ms-trim',(cx,y,cz),(length,h,w),False,yaw)
 # Tan entrance bay wraps an arched glazed recess, as seen February2025.
 arch=Polygon([(-2.8,.18),(2.8,.18),(2.8,2.62)]+[(2.8*math.cos(a),2.62+1.35*math.sin(a)) for a in np.linspace(0,math.pi,33)]+[(-2.8,.18)])
 panel=box(-3.8,.18,3.8,6.85).difference(arch)
 for tri in triangles(panel):B.face('ms-tan',[F.p(u-4.4,y,.16) for u,y in list(tri.exterior.coords)[:-1]])
 # Opaque campaign panels are supported by the reference; no inferred room behind them.
 def glazing(G,u,z,w,h=2.7,base=.4):
  G.box('ms-frame',(u,base+h/2,z),(w,h,.09))
  G.box('ms-panel',(u,base+h/2,z+.06),(w-.12,h-.12,.035))
  for x in np.linspace(u-w/2,u+w/2,max(2,round(w/1.2)+1)):
   G.box('ms-frame',(float(x),base+h/2,z+.10),(.045,h,.07))
  G.box('ms-sill',(u,base-.04,z+.09),(w+.12,.09,.17))
  for x in np.arange(u-w/2+.6,u+w/2,.95):G.text('T',(float(x),base+h*.48,z+.105),.34,'ms-magenta',back=True)
 glazing(F,-4.4,.08,5.45,2.95,.18)
 F.path('ms-trim',[(-4.4+2.86*math.cos(a),2.62+1.40*math.sin(a),.23) for a in np.linspace(0,math.pi,36)],.055,10)
 for u in [-7.25,-1.55]:F.box('ms-trim',(u,1.40,.23),(.11,2.45,.12))
 glazing(F,3.9,.16,7.1,3.0,.38)
 F.box('ms-magenta',(-4.4,5.37,.25),(6.55,1.35,.16));F.text('T-Mobile',(-4.4,5.40,.35),.83,'ms-letter',back=True)
 F.text('3862',(7.3,5.6,.22),.30,'ms-dark',back=True)
 F.box('ms-trim',(-4.4,6.84,-1.9),(8.1,.18,4.7))
 F.box('ms-tan',(-4.4,6.64,-2.0),(7.8,.35,4.5))
 # Two tiled hipped caps, southwest and northeast, observed in the aerial.
 def hip(cx,cz,w,d,y):
  rise=.95;ridge=max(0,(w-d)/2)
  a=F.p(cx-w/2,y,cz+d/2);b=F.p(cx+w/2,y,cz+d/2);c=F.p(cx+w/2,y,cz-d/2);e=F.p(cx-w/2,y,cz-d/2)
  r0=F.p(cx-ridge,y+rise,cz);r1=F.p(cx+ridge,y+rise,cz)
  for points in [[a,b,r1,r0],[b,c,r1],[c,e,r0,r1],[e,a,r0]]:B.upface('ms-tile',points)
  # Shallow individual tile ribs follow both long slopes without coplanar skins.
  for u in np.arange(cx-w/2+.16,cx+w/2,.24):
   for sign in [-1,1]:
    limit=min(d/2,max(0,w/2-abs(float(u)-cx)))
    for v in np.arange(0,limit,.48):
     z=cz+sign*(d/2-float(v));z2=cz+sign*(d/2-min(float(v)+.5,limit))
     h=y+rise*float(v)/(d/2);h2=y+rise*min(float(v)+.5,limit)/(d/2)
     F.tube('ms-tile-'+str(int((u+100)*5+v)%3),(float(u),h+.025,z),(float(u),h2+.025,z2),.065,8)
 hip(-4.4,-1.9,8.1,4.7,6.95);hip(6.3,-28.7,7.0,5.2,6.55)
 # East-side sign and covered campaign glazing; setbacks inferred from map.
 E=Frame(B,-1710.626,-3202.367,1.4889,y=0)
 E.box('ms-magenta',(-1,4.7,.23),(6.6,1.35,.13));E.text('T-Mobile',(-1,4.72,.31),.83,'ms-letter',back=True)
 for u in [-7.5,0,7.5]:glazing(E,u,.20,5.1,2.6,.4)
 for u in [-4,2,6]:
  F.box('ms-metal',(u,6.7,-14),(1.3,.65,1.2));F.box('ms-dark',(u,7.06,-14),(1.4,.07,1.3))
 F.box('ms-paving',(-4.4,.07,1),(6.1,.14,2),True)
 # Low planting beds stay beside the entrance approach.
 rng=random.Random(326)
 for a,b in [(-8.0,-7.2),(-1.1,7.8)]:
  F.box('ms-gravel',((a+b)/2,.12,.7),(b-a,.12,1.2))
  for u in np.arange(a+.25,b,.72):
   F.lathe('ms-leaf',float(u),.8,[(.18,0),(.30,.34),(.65,.34),(.85,.16),(.88,0)],10)
 for u in [-7.7,7.4]:
  F.tube('ms-trunk',(u,.15,1.1),(u,2.5,1.1),.06,9)
  for k in range(8):
   angle=k*math.tau/8;F.tube('ms-trunk',(u,1.7,1.1),(u+math.cos(angle)*.7,2.9,1.1+math.sin(angle)*.7),.025,7)
 route=[F.p(u,.14,v) for u,v in [(-4.4,2),(-4.4,1),(-4.4,.5)]]
 return dict(key=KEY,name='T-Mobile Sahara',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-1,p.bounds[2]+1,p.bounds[3]+3],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='Closed storefront approach',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
