"""MGM conference exterior: official three-level plan + Earth2022–2024.
Heights estimated from those levels and the elevations; no invented public interior.
"""
from common import *
from forum_shops import facade_frame
KEY='mgmConference';IDS=['way/27897924','way/1425416645','way/133764577','way/435754002','way/401340340']
def exterior(B):
 B.property=KEY+'-exterior';B.source='mgm-conference';B.detail=0
 plans={i:footprint(i) for i in IDS};union=unary_union(list(plans.values()))
 for ident,p in plans.items():
  main=ident==IDS[0];extension=ident==IDS[1];marquee=ident==IDS[2]
  h=20 if main else (22 if extension else (15.5 if marquee else 5.5))
  core=box(694,1210,755,1337).intersection(p) if main else Polygon()
  B.planar('mgm-stone',p,.24,True);B.planar('lvw-roof',p.difference(core),h,True)
  if not core.is_empty:
   B.shell(core,h,26.4,'mgm-stone',roof=False);B.planar('mgm-stone',core,26.4,True)
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,0)
   if L<.25:continue
   mid=LineString([a,b]).interpolate(.5,normalized=True)
   neighbor=any(q.contains(Point(mid.x+nx*.12,mid.y+nz*.12)) for i,q in plans.items() if i!=ident)
   if neighbor:continue
   west=nx<-.6;public=(main and west) or (extension and west) or (marquee and nz<-.6)
   B.face('mgm-stone',[(a[0],.24,a[1]),(b[0],.24,b[1]),(b[0],h,b[1]),(a[0],h,a[1])],True)
   # Recessed dark window fields framed by warm masonry, deep piers and floor bands.
   if public:
    if main and L>2.4:
     gw=L*(.87 if 1252<mid.y<1297 else .62)
     F.box('ph-glass',(L/2,10,-.065),(gw,15,.1))
     for x in np.arange((L-gw)/2+.6,(L+gw)/2,1.5):F.box('mgm-bronze',(x,10,-.14),(.035,15,.035))
     for y in (3,7.7,12.3,17.5):F.box('mgm-bronze',(L/2,y,-.15),(gw,.055,.04))
    elif L>5:
     pitch=9 if marquee else 11
     for x in np.arange(pitch/2,L-1,pitch):
      w=min(pitch-2,L-x-.6)
      if w<1:continue
      F.box('ph-glass',(x,h*.52,-.07),(w,h*.62,.12))
      for xx in np.arange(x-w/2+.7,x+w/2,.95):F.box('mgm-bronze',(xx,h*.52,-.16),(.035,h*.62,.04))
      F.box('mgm-stone',(x-w/2-.35,h/2,-.42),(.55,h,.8))
      for y in np.arange(3,h*.83,3.5):F.box('mgm-bronze',(x,y,-.17),(w,.055,.05))
     if marquee:
      # Full-length white projecting eave, visibly supported by the piers.
      F.box('mgm-stone',(L/2,h-.8,-1.2),(L,.65,2.4))
   elif L>8:
    # Koval side is mostly solid service frontage, not a false curtain wall.
    for x in np.arange(2,L-2,8):
     F.box('mgm-joint',(x,h/2,-.03),(.035,h-.6,.04))
    if nx>.5:
     for x in np.arange(7,L-4,17):
      F.box('lvw-loading',(x,2.3,-.09),(4,4.1,.1))
      for y in np.arange(.5,4.1,.4):F.box('mgm-joint',(x,y,-.16),(3.9,.035,.05))
   for y in (h-.65,h-1.05):F.box('mgm-stone',(L/2,y,-.16),(L,.2,.28))
   for y in np.arange(1,h-1,2):F.box('mgm-joint',(L/2,y,-.025),(L,.018,.025))
   # Roof-edge parapet with physical upstand, independently owned outside edge.
   F.box('mgm-stone',(L/2,h+.3,0),(L,.6,.32),True)
  x0,z0,x1,z1=p.bounds
  if main:
   # Mechanical ring outside the raised ballroom roof.
   for z in np.arange(1215,1334,13):
    for x in (685,763):
     B.box('lvw-service',(x,h+.8,z),(4.8,1.6,3.2));B.box('lvw-frame',(x,h+1.65,z),(4.6,.08,3))
   # Central double-height arrival under the existing curved volume.
   F=Frame(B,670.5,1275,math.pi/2)
   F.box('mgm-stone',(0,4.8,-3),(19,.55,6))
   for x in (-8.5,8.5):F.box('mgm-stone',(x,2.5,-5.3),(.65,4.5,.65),True)
   B.planar('tile',box(661,1264,671,1286),.25,True)
   F.text('MGM GRAND',(0,7,-.7),1.05,'mgm-bronze')
  elif extension:
   for z in np.arange(1361,1417,12):B.box('lvw-service',(778,23,z),(4,2,5))
  elif marquee:
   F=Frame(B,594,1360.257,0);F.text('MARQUEE BALLROOM',(0,11,-.9),1.05,'mgm-bronze')
 return dict(key=KEY,name='MGM Grand conference and Marquee halls',center=[670,0,1317],bounds=list(union.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
