"""Original detail fitted to linked HGV photographs and October 2026 Sky Street View.
Exact furniture counts and entrance dimensions are inferred; existing shells retained.
"""
from common import *
BASE=Path('.bitmagic/city-exterior-backups/hgv-sky')

def palm(B,x,z,h,phase):
 B.path('bark',[(x,.32,z),(x+.15,h*.55,z),(x+.45,h,z+.2)],.19,8)
 B.box('bark',(x,1.32,z),(.34,2,.34),True)
 for j in range(16):
  a=phase+j*2.39996;L=2.6+(j%3)*.25
  def p(t,w=0):return (x+.45+L*t*math.cos(a)-w*math.sin(a),h+math.sin(math.pi*t)-.9*t,z+.2+L*t*math.sin(a)+w*math.cos(a))
  B.path('foliage',[p(k/6) for k in range(7)],.025,4)
  for k in range(1,13):
   t=k/14;w=.55*math.sin(math.pi*t)
   for s in [-1,1]:B.face('foliage',[p(t),p(t+.025,s*w*.45),p(min(1,t+.15),s*w),p(t+.06,s*w*.25)])

def hgv_detail(B):
 B.property='hgvExterior-exterior';B.source='hgv-court-furnishings';B.detail=1
 # Blue octagonal shade parasols and original dark woven-effect lounge seating.
 for x,z in [(1014,-2650),(1025,-2645),(1015,-2632),(1053,-2603)]:
  B.tube('steel',(x,.32,z),(x,3.25,z),.045,8)
  for j in range(8):
   a=j*math.tau/8;b=(j+1)*math.tau/8
   B.face('blue',[(x,3.25,z),(x+1.65*math.cos(a),2.75,z+1.65*math.sin(a)),(x+1.65*math.cos(b),2.75,z+1.65*math.sin(b))])
  B.lathe('charcoal',(x,z),[(.32,.35),(.4,.35),(.4,.01)],12)
 # Fire lounge is an interpretation of official photographed furnishings, not an exact seating plan.
 for cx,cz in [(1021,-2642),(1046,-2598)]:
  B.lathe('stone',(cx,cz),[(.32,.75),(.75,.85),(.83,.85),(.83,.5),(.76,.5)],20)
  B.planar('charcoal',Point(cx,cz).buffer(.48,quad_segs=8),.77)
  B.box('stone',(cx,.56,cz),(1.2,.48,1.2),True)
  for dx,dz,yaw in [(-1.6,0,math.pi/2),(1.6,0,-math.pi/2),(0,1.6,0)]:
   F=Frame(B,cx+dx,cz+dz,yaw,y=.32)
   F.box('charcoal',(0,.3,0),(1.4,.6,.75),True);F.box('sandstone',(0,.66,0),(1.3,.12,.68))
   F.box('charcoal',(0,.83,.4),(1.4,.55,.12),True)
   for xx in [-.68,.68]:F.box('charcoal',(xx,.7,0),(.12,.3,.8))
 # Terracotta urns on low pale piers at garden edges, observed in official photography.
 for x,z in [(1008,-2647),(1027,-2656),(1054,-2594)]:
  B.box('hgv-cream',(x,.69,z),(.8,.74,.8),True)
  B.lathe('copper2',(x,z),[(1.06,.24),(1.2,.28),(1.7,.48),(1.9,.42),(2,.46),(2.06,.46)],16)
  B.planar('bark',Point(x,z).buffer(.36,quad_segs=8),2.01)
 B.source='hgv-court-palms';B.detail=0
 for i,(x,z) in enumerate([(995,-2669),(996,-2651),(1003,-2631),(1012,-2620),(1025,-2611),(1036,-2604),(1056,-2591),(1053,-2619),(1039,-2656),(1028,-2669)]):
  B.planar('bark',Point(x,z).buffer(.9,quad_segs=10),.33)
  palm(B,x,z,7.5+i%4,i*.6)
 B.detail=0

def sky_detail(B):
 B.property='skyExterior-exterior';B.source='sky-arrival';B.detail=0
 F=Frame(B,1079,-2565,-math.pi/2,y=.12)
 # Central closed guardhouse, open lanes to both sides; no new public interior implied.
 F.box('sky-white',(0,1.5,0),(2.5,3,3.8),True)
 for x in [-1.27,1.27]:F.box('sky-glass',(x,1.85,-.1),(.05,1.5,3.4))
 F.box('sky-glass',(0,1.85,-1.93),(2.2,1.5,.05))
 for x in [-1.12,0,1.12]:F.box('silver',(x,1.85,-1.97),(.055,1.5,.06))
 F.box('sky-white',(0,4.1,.6),(2.5,2.2,2.6),True)
 F.box('sky-white',(0,5.3,.6),(2.8,.2,2.9))
 # Slotted horizontal portal canopy, square piers, clear lane headroom >3.5m.
 for x in [-9,9]:F.box('sky-white',(x,1.9,0),(.65,3.8,.75),True)
 for z in [-1,1]:F.box('silver',(0,3.95,z),(18.6,.45,.25),True)
 for x in np.arange(-9,9.01,.65):F.box('sky-white',(x,3.99,0),(.18,.28,2.3))
 # Low hedge islands leave both driveway lanes and existing sidewalk open.
 for x in [-10.5,10.5]:
  F.box('sky-white',(x,.25,.4),(1.6,.5,6),True)
  F.box('foliage',(x,.75,.4),(1.35,.6,5.6))
 # Original non-emissive bollard fixtures: no runtime lights are added.
 for x in [-8,8]:
  for z in [-3,3]:
   F.tube('silver',(x,0,z),(x,.9,z),.07,8)
   F.tube('sky-white',(x,.9,z),(x,1.03,z),.19,12,r2=.12)
 B.detail=0

def build():
 for key,detail in [('hgvExterior',hgv_detail),('skyExterior',sky_detail)]:
  name=key+'-exterior';old=json.loads((BASE/(name+'.json')).read_text());c=json.loads((BASE/(name+'-collision.json')).read_text())
  B=Meshes();detail(B);extra=B.solids[name];offset=len(c['vertices'])//3
  c['vertices']+=extra['vertices'];c['indices'] += [i+offset for i in extra['indices']]
  (OUT/(name+'.json')).write_text(json.dumps({'meshes':old['meshes']+list(B.groups.values()),'labels':old['labels']+B.labels},separators=(',',':')))
  (OUT/(name+'-collision.json')).write_text(json.dumps(c,separators=(',',':')))
  print(name,sum(len(g['faces']) for g in B.groups.values()),'added triangles',len(extra['indices'])//3,'collision triangles')
if __name__=='__main__':build()
