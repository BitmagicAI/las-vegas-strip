"""Original Sahara Annex four-unit exterior, fitted to January 2026 frontage."""
from common import *
from shapely.geometry.polygon import orient
from shapely.geometry import MultiPoint
from shapely.ops import voronoi_diagram
KEY='sahara-annex';IDS=['way/1371426377','way/1371426379','way/1371426378','way/943068963']
def stone(B,F,region,seed):
 rng=random.Random(seed)
 # Original irregular limestone polygons; no image tracing or copied textures.
 xmin,ymin,xmax,ymax=region.bounds
 points=[(float(x)+rng.uniform(-.25,.25),float(y)+rng.uniform(-.18,.18)) for y in np.arange(ymin-.6,ymax+.7,.5) for x in np.arange(xmin-.7,xmax+.8,.65)]
 cells=voronoi_diagram(MultiPoint(points))
 for cell in cells.geoms:
  q=cell.buffer(-.018,join_style=2).intersection(region);mat='sa-stone'+str(rng.randrange(5))
  for part in parts(q):
   for t in triangles(part):B.face(mat,[F.p(u,yy,-.11) for u,yy in list(t.exterior.coords)[:-1]])

def build(B):
 p=unary_union([footprint(i) for i in IDS]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 B.shell(p,.02,4.55,'sa-stucco',roof=False);B.planar('sa-membrane',p,4.55)
 for poly in parts(p):
  ring=list(poly.exterior.coords)
  for a,b in zip(ring,ring[1:]):
   L=math.dist(a,b)
   if L<.1:continue
   F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
   F.box('sa-coping',(0,4.61,0),(L+.03,.16,.23))
 # North unit fronts; window widths and sign spacing are fitted.
 units=[(-789.5,-3109.5,12.2,8.8,'karate'),(-779.3,-3109.6,3.8,2.9,'computer'),(-775.85,-3109.53,3.0,2.35,'psychic'),(-772.2,-3109.48,4.35,3.2,'barber')]
 routes=[]
 for k,(x,z,w,glass,kind) in enumerate(units):
  F=Frame(B,x,z,0,y=0);region=box(-w/2,.12,w/2,4.5).difference(box(-glass/2,.18,glass/2,3.0));stone(B,F,region,12+k)
  F.box('sa-glass',(0,1.59,-.14),(glass,2.82,.055))
  for u in np.arange(-glass/2,glass/2+.05,glass/max(2,round(glass/1.1))):F.box('sa-mullion',(float(u),1.59,-.2),(.055,2.84,.07))
  for y in [.18,2.45,3.0]:F.box('sa-mullion',(0,y,-.21),(glass,.055,.07))
  door=-glass*.22 if kind=='karate' else 0
  F.box('sa-mullion',(door,1.33,-.22),(.04,2.25,.08))
  for u in [door-.12,door+.12]:F.tube('sa-alloy',(u,1.05,-.29),(u,1.55,-.29),.018,8)
  F.box('sa-threshold',(0,.08,-.65),(w,.16,1.3),True)
  if kind=='karate':
   F.box('sa-blue',(0,3.83,-.26),(w+.08,1.0,.34));F.box('sa-red',(0,3.83,-.45),(w-1.65,.79,.045));F.box('sa-signwhite',(0,3.83,-.48),(w-1.82,.65,.035))
   F.text('LV SCHOOL OF SHOTOKAN KARATE',(0,3.87,-.51),.40,'sa-red');F.text('FAMILY TRADITIONAL KARATE TRAINING CENTER',(0,3.53,-.52),.20,'sa-blue')
   F.box('sa-blue',(-glass/2+.85,2.0,-.24),(1.6,1.7,.03));F.text('AUTHENTIC',(-glass/2+.85,2.5,-.27),.19,'sa-signwhite');F.text('JAPANESE',(-glass/2+.85,2.23,-.27),.19,'sa-signwhite');F.text('KARATE',(-glass/2+.85,1.96,-.27),.19,'sa-signwhite')
   F.box('sa-plywood',(1.15,.75,-.23),(1.6,1.1,.035))
   for u in np.arange(.38,1.95,.22):F.box('sa-woodgrain',(float(u),.75,-.252),(.012,1.04,.012))
  elif kind=='computer':
   F.box('sa-red',(0,3.8,-.3),(w,1.1,.4));F.box('sa-signwhite',(0,3.8,-.515),(w-.15,.96,.025))
   F.text('COMPUTER',(0,3.9,-.55),.44,'sa-red');F.text('REPAIR',(0,3.46,-.55),.40,'sa-red')
   F.box('sa-blue',(0,.55,-.24),(glass,.48,.025));F.text('COMPUTER REPAIR',(0,.48,-.27),.19,'sa-signwhite')
  elif kind=='psychic':
   F.box('sa-purple',(0,3.82,-.3),(w,1.2,.4));F.text('PSYCHIC',(0,4.04,-.53),.4,'sa-signwhite');F.text('READINGS',(0,3.66,-.53),.30,'sa-signwhite');F.text('TAROT CARDS',(0,3.32,-.53),.25,'sa-signwhite')
  else:
   F.box('sa-signwhite',(0,3.83,-.28),(w,1.1,.32));F.text('BARBER SHOP',(0,3.87,-.47),.43,'sa-red');F.text('NEXUS RETAIL CENTER',(0,3.48,-.47),.20,'sa-blue')
  routes.append(dict(name=kind+' public approach',points=[(x,0,z-3),(x,.08,z-1.3),(x,.08,z-.8)]))
 # West side visible from Richfield: stone cladding without invented display windows.
 F=Frame(B,-797.94,-3101.8,math.pi/2,y=0);stone(B,F,box(-6.5,.1,6.5,4.5),31)
 # Roof membrane seams and small service units seen in aerial; fitted, not surveyed.
 for x in np.arange(-797,-770,2.1):
  strip=box(float(x),-3108,float(x)+.035,-3095).intersection(p);B.planar('sa-roofjoint',strip,4.563)
 for x,z in [(-788,-3101),(-782,-3100),(-773,-3104)]:
  F=Frame(B,x,z,0,y=0);F.box('sa-service',(0,5.05,0),(1.2,.8,1));F.box('sa-alloy',(0,5.49,0),(1.3,.08,1.1))
  for u in np.arange(-.5,.6,.13):F.box('sa-vent',(float(u),5.05,-.515),(.04,.55,.04))
 # Rear plinth, rainwater pipes and metering enclosures: simplified service treatment.
 F=Frame(B,-783,-3094.65,math.pi,y=0)
 F.box('sa-plinth',(0,.25,0),(27,.5,.12))
 for u in [-11,-2,9]:
  F.tube('sa-alloy',(u,.1,-.14),(u,4.4,-.14),.045,8);F.box('sa-service',(u+.7,1.35,-.15),(.45,.7,.18))
 return dict(key=KEY,name='Sahara Annex shared retail',center=[-784,0,-3102],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
