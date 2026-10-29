"""Original Denny's Flamingo exterior; December2022 frontage, estimated hidden sides."""
from common import *
KEY='dennys-flamingo';ID='way/1264703197'
def build(B):
 p=footprint(ID);F=Frame(B,-1691.4,105.9,0,y=0);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 B.shell(p,.10,4.1,'df-plaster',roof=False);B.planar('df-roof',p,4.1);B.planar('df-base',p,.13,True)
 # Shallow roof cornice and parapet follow the surveyed shell.
 for poly in parts(p):
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   
   if (a[1]+b[1])/2>105:continue
   L=math.dist(a,b);c=((a[0]+b[0])/2,4.1,(a[1]+b[1])/2);B.box('df-tan',c,(L,.28,.30),False,-math.atan2(b[1]-a[1],b[0]-a[0]));B.box('df-cap',(c[0],4.29,c[2]),(L,.09,.40),False,-math.atan2(b[1]-a[1],b[0]-a[0]))
 # White outward-flaring butterfly plane, with an actual window opening.
 facade=Polygon([(-7.8,5.7),(0,4.55),(7.8,5.7),(6.8,.25),(-6.8,.25)])
 facade=facade.difference(box(-4.7,.65,4.7,3.28))
 for t in triangles(facade):B.face('df-white',[F.p(x,y,.38) for x,y in list(t.exterior.coords)[:-1]])
 for a,b in [((-8,5.95),(0,4.78)),((0,4.78),(8,5.95))]:
  F.path('df-red',[(a[0],a[1],.44),(b[0],b[1],.44)],.11,4)
  B.face('df-red',[F.p(a[0],a[1]+.18,.5),F.p(b[0],b[1]+.18,.5),F.p(b[0],b[1]-.38,.5),F.p(a[0],a[1]-.38,.5)])
 # Recessed glazing, blind slats and metal mullions. No public interior claimed.
 def glazing(u,v,w):
  F.box('df-glass',(u,2.03,v),(w,.0+2.34,.07))
  for x in np.linspace(u-w/2,u+w/2,max(2,round(w/1.6)+1)):F.box('df-frame',(float(x),2.03,v+.07),(.075,2.46,.12))
  for y in [.84,2.05,3.22]:F.box('df-frame',(u,y,v+.07),(w+.12,.08,.12))
  for y in np.arange(1.03,3.15,.11):F.box('df-blind',(u,float(y),v+.025),(w-.06,.07,.025))
 glazing(0,.43,9.4)
 for u in [-5.05,5.05]:F.box('df-tan',(u,2.05,.53),(.62,2.9,.24))
 F.box('df-tan',(0,3.43,.53),(10.75,.42,.24))
 F.text("AMERICA'S DINER",(0,3.96,.55),.40,'df-red',back=True)
 # Original sign lettering on a shallow crest (reference disk is blurred).
 F.box('df-red',(0,5.35,.52),(2.9,.85,.20));F.text("Denny's",(0,5.4,.66),.48,'df-letter',back=True)
 # Low stone plinth: staggered individual masonry, no imported photo pixels.
 rng=random.Random(320)
 for row in range(5):
  for k in range(28):
   x=-4.65+k*.34+(row%2)*.17
   if x<4.65:F.box('df-stone-'+str(rng.randrange(4)),(x,.25+row*.105,.54),(.32,.095,.12))
 # Side wings sit back from central frontage, with a red canopy and left entrance.
 for u,w in [(-10.0,3.7),(9.25,3.4)]:
  glazing(u,-1.20 if u<0 else -1.9,w);F.box('df-red',(u,3.45,-1.48),(w+.3,.15,1.15))
  F.box('df-stone-1',(u,.54,-1.82),(w,.65,.18))
 # Entry tower at west end, slatted screen above glazing.
 F.box('df-red',(-10.0,4.78,-2.35),(3.8,3.0,.20))
 for h in np.arange(3.45,6.23,.12):F.box('df-slat',(-10.0,float(h),-2.18),(3.85,.045,.17))
 for u in [-11.85,-10.95,-10.05,-9.15,-8.25]:F.box('df-slat',(u,4.78,-2.07),(.04,2.8,.05))
 F.box('df-glass',(-9.25,1.42,-1.04),(1.05,2.45,.09),True)
 for u in [-9.8,-8.7]:F.box('df-frame',(u,1.42,-.94),(.075,2.52,.11))
 F.box('df-frame',(-9.25,2.7,-.94),(1.17,.09,.11));F.text('3881',(-9.25,2.93,-.89),.21,'df-letter',back=True);F.tube('df-frame',(-8.86,1.15,-.84),(-8.86,1.65,-.84),.018,8)
 # Small access apron entirely inside the site; roads and parking not regenerated.
 F.box('df-paving',(-9.2,.07,-.65),(3.8,.14,2.15),True)
 for u in [-11.1,-7.4]:F.tube('df-frame',(u,.14,-.45),(u,3.4,-.45),.035,10)
 # Estimated roof plant and rear service fittings, kept within mapped envelope.
 for u,v in [(-5,-9),(4,-11),(0,-5)]:
  F.box('df-metal',(u,4.45,v),(1.8,.65,1.25));F.box('df-cap',(u,4.82,v),(1.9,.09,1.35))
  for k in range(7):F.box('df-frame',(u-.7+k*.23,4.79,v),(.035,.02,1.02))
 F.box('df-metal',(7.5,1.22,-17.6),(1.0,2.1,.1))
 route=[F.p(u,.14,v) for u,v in [(-10,1.5),(-9.25,.7),(-9.25,-.5)]]
 return dict(key=KEY,name="Denny's West Flamingo",center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-1,p.bounds[1]-1,p.bounds[2]+1,p.bounds[3]+1],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],hotelSources=[],routes=[dict(name='Public entrance approach',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
