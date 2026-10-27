"""Original site-specific exterior, with concealed layouts left closed."""
from common import *
KEY='jack-tropicana';IDS=['way/431497410']
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,-1012.566,1735.337,-.0064,y=0);w=14.83;d=18.09
 B.shell(footprint(IDS[0]),.02,4.6,'jk-brick',roof=False);B.planar('jk-roof',footprint(IDS[0]),4.35)
 W=Frame(B,*[F.p(0,0,d)[i] for i in (0,2)],F.yaw+math.pi/2,y=0)
 E=Frame(B,*[F.p(w,0,0)[i] for i in (0,2)],F.yaw-math.pi/2,y=0)
 S=Frame(B,*[F.p(w,0,d)[i] for i in (0,2)],F.yaw+math.pi,y=0)
 # North and west glazed public fronts. Raised red corner at their shared NW edge.
 for G,L,bays in [(F,w,[2.1,5.8,9.5,12.75]),(W,d,[1.9,7.4,11.2,15.0])]:
  G.box('jk-fascia',(L/2,3.35,-.40),(L+.5,.65,.88))
  G.box('jk-stone',(L/2,4.05,-.055),(L,1.03,.11))
  G.box('jk-metal',(L/2,4.62,-.06),(L+.2,.14,.25))
  for x in bays:
   bw=2.65 if G is F else (2.2 if x==1.9 else 2.75)
   G.box('jk-timber',(x,1.65,-.09),(bw+.25,2.83,.18))
   G.box('jk-frame',(x,1.70,-.20),(bw,2.18,.07))
   G.box('jk-glass',(x,1.70,-.25),(bw-.10,2.07,.04))
   G.box('jk-frame',(x,1.70,-.29),(.045,2.15,.05))
  # Continuous supported footway; unrelated parking and roads remain intact.
  G.box('jk-paving',(L/2,.23,-1.55),(L+.45,.18,3.1),True)
 # Ribbed raised corner wraps north/west; strips clipped to panel borders.
 for G,start in [(F,.1),(W,d-8.9)]:
  length=8.8;low=3.72;high=5.86
  G.box('jk-red',(start+length/2,(low+high)/2,-.115),(length,high-low,.18))
  for offset in np.arange(-2.2,length,.22):
   x0=max(0,offset);x1=min(length,offset+2.14)
   if x1<=x0:continue
   y0=low+x0-offset;y1=low+x1-offset
   G.tube('jk-rib',(start+x0,y0,-.23),(start+x1,y1,-.23),.022,5)
  for x in [start,start+2.93,start+5.87,start+length]:G.box('jk-metal',(x,(low+high)/2,-.26),(.12,high-low+.22,.14))
  for y in [low,high]:G.box('jk-metal',(start+length/2,y,-.26),(length+.15,.12,.15))
 # A shared corner post closes the two raised panel returns.
 F.box('jk-metal',(0,4.79,0),(.52,2.35,.52))
 for G,x in [(F,1.55),(W,d-1.55)]:
  G.box('jk-metal',(x,4.83,-.35),(2.45,1.85,.17))
  G.box('jk-red',(x,4.83,-.46),(2.29,1.69,.08))
  G.text('Jack',(x,4.98,-.52),.65,'jk-letter')
  G.text('IN THE BOX',(x,4.29,-.52),.19,'jk-letter')
 # Closed public door on west face, away from corner. Silver rails and pull handle.
 W.box('jk-timber',(4.5,1.56,-.10),(1.4,2.85,.18))
 W.box('jk-frame',(4.5,1.56,-.23),(1.24,2.74,.08));W.box('jk-glass',(4.5,1.56,-.28),(1.12,2.60,.04))
 W.box('jk-frame',(4.5,.8,-.32),(1.16,.045,.06));W.tube('jk-chrome',(4.9,1.1,-.39),(4.9,1.65,-.39),.018,8)
 # Unseen rear elevations remain restrained service walls, not invented entrances.
 for G,L in [(E,d),(S,w)]:
  G.box('jk-stucco',(L/2,3.95,-.05),(L,1.3,.1));G.box('jk-metal',(L/2,4.62,-.03),(L+.15,.13,.25))
  G.box('jk-fascia',(L/2,3.3,-.16),(L,.28,.35))
 S.box('jk-frame',(3.4,1.5,-.07),(1.3,2.75,.14));S.box('jk-service',(3.4,1.5,-.16),(1.16,2.61,.06))
 # East drive-through window and its shallow hood (position inferred).
 E.box('jk-frame',(12.5,1.9,-.08),(2.0,1.5,.16));E.box('jk-glass',(12.5,1.9,-.19),(1.88,1.38,.04));E.box('jk-frame',(12.5,1.9,-.24),(.05,1.42,.06));E.box('jk-metal',(12.5,2.85,-.4),(2.35,.12,.85))
 for x,z in [(5,8),(10,12)]:
  F.box('jk-equipment',(x,4.85,z),(2.4,1,1.9));F.box('jk-metal',(x,5.38,z),(2.54,.10,2.03))
  for h in np.arange(4.5,5.2,.12):F.box('jk-frame',(x,h,z-1),(2.25,.035,.03))
 for G,x in [(F,14.2),(W,1.2),(E,5),(S,11)]:
  G.box('jk-metal',(x,2.85,-.2),(.28,.24,.35));G.box('jk-light',(x,2.72,-.2),(.20,.035,.25))
 # Address plate is original lettering, no copied logo artwork.
 F.box('jk-metal',(12.8,4.05,-.14),(1.2,.48,.08))
 F.text('3235',(12.8,4.05,-.20),.29,'jk-letter')
 routes=[dict(name='North public frontage',points=[F.p(x,.32,-1.8) for x in [1,5,10,14]]),dict(name='West entrance frontage',points=[W.p(x,.32,-1.8) for x in [1,5,10,16.5]])]
 return dict(key=KEY,name='Jack in the Box Tropicana',center=[-1005,0,1744],bounds=[-1017,1731,-995,1757],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
