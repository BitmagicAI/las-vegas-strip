"""LINQ covered self parking: Earth 2022 exterior and mapped six-level footprint.
Internal ramp placement is a navigable approximation, not a surveyed floorplan.
"""
from common import *
from forum_shops import facade_frame
KEY='linqParking';IDS=['way/115771879']
PITCH=(20-.24)/6
SLOT=box(350,-301,357,-263)
def exterior(B):
 B.property=KEY+'-exterior';B.source='linq-parking';B.detail=0;p=footprint(IDS[0])
 for level in range(7):
  y=.24+level*PITCH;deck=p if level in [0,6] else p.difference(SLOT)
  B.planar('linq-membrane-paint' if level==6 else 'skg-deck',deck,y,True)
  B.shell(deck,y-.23,y,'skg-slab',roof=False)
  for poly in parts(deck):
   for tri in triangles(poly):B.face('skg-slab',[(x,y-.23,z) for x,z in reversed(list(tri.exterior.coords)[:-1])])
 # Five stacked ramps through one continuous slot; each floor loops back beside it.
 for level in range(5):
  lo=.24+level*PITCH;hi=lo+PITCH;z0,z1=-301,-263
  B.upface('skg-deck',[(350,lo,z0),(357,lo,z0),(357,hi,z1),(350,hi,z1)],True)
  for x in [350,357]:B.face('skg-slab',[(x,lo,z0),(x,hi,z1),(x,hi+.9,z1),(x,lo+.9,z0)],True)
  B.face('skg-slab',[(350,lo-.22,z0),(350,hi-.22,z1),(357,hi-.22,z1),(357,lo-.22,z0)])
 for pp in parts(p):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   for level in range(1,7):
    y=.24+level*PITCH
    F.box('st-white',(L/2,y+.36,-.08),(L,.72,.3),True)
    F.box('skg-slab',(L/2,y-.24,0),(L,.25,.5))
   for x in np.linspace(.3,L-.3,max(2,round(L/8)+1)):
    F.box('st-white',(x,10,0),(.45,20,.6),True)
   # Narrow coping ties the top perimeter together.
   F.box('st-white',(L/2,20.82,-.08),(L,.16,.38))
 # Interior columns and beams remain visible through open elevations.
 usable=p.buffer(-1).difference(SLOT.buffer(1))
 for x in [273,289,305,321,337,369]:
  for z in [-301,-285,-269,-253,-237,-221]:
   if usable.contains(Point(x,z)):B.box('skg-slab',(x,10,z),(.5,20,.5),True)
  for level in range(1,6):
   q=box(x-.15,-310,x+.15,-215).intersection(usable)
   B.shell(q,.24+level*PITCH-.5,.24+level*PITCH-.23,'skg-slab',roof=False)
 # East sign is on the observed entrance face; do not close ground-level bays.
 F=Frame(B,379.4,-273,math.pi*1.5,y=0)
 F.box('linq-blue',(0,5,-.3),(13,1.3,.25));F.text('THE LINQ',(0,4.9,-.45),.62,'white')
 F.text('SELF PARKING',(0,4.4,-.45),.25,'white')
 # Small access headhouse at the northeastern roof corner, visible in the aerial.
 B.box('st-white',(373.5,20.7,-302),(6,1.4,7));B.box('linq-membrane-paint',(373.5,21.48,-302),(6.4,.16,7.4))
 B.box('linq-service-paint',(377,20.8,-302),(.12,1.1,2))
 return dict(key=KEY,name='The LINQ self parking',center=[330,0,-270],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
