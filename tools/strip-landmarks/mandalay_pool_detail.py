"""Mandalay's mapped pool contours, Earth/official-map guided surrounding structures.
OSM plan geometry is retained; pool depths and deck heights are authoring estimates.
"""
from common import *
from forum_shops import facade_frame
DATA=Path('tools/strip-landmarks/mandalay-pool-plans.json')
IDS=['way/'+s for s in ['399554455','364846554','364846552','399554420','118346756','399554453','399554456','399554454','128025409','399554425','399554412','364846555','398972297','364846556','364846557']]
IDS += ['way/398972293','way/399554457']
CABANAS=['way/'+s for s in ['399554413','399554415','399554416','399554417','399554419','399554421','399554422','399554423','399554426','399554427','399554430','399554431','399554433','399554434','399554435','399554436','399554437','399554438','399554439','399554440','399554441','399554442','399554446','399554447','399554448','399554450','399554451','399554452']]
def plans():return [(r,Polygon(r['outer'],r.get('holes',[])).buffer(0)) for r in json.loads(DATA.read_text())]
def structure(ident):
 p=footprint(ident)
 if ident=='way/502624676':
  court=unary_union([q.buffer(5.5) for r,q in plans() if r['id'] in ['way/116660352','way/399554380']])
  return p.difference(court)
 if ident=='way/364846556':
  return p.difference(next(q.buffer(.7) for r,q in plans() if r['id']=='way/128158102'))
 return p
def exterior(B):
 B.source='mandalay-pool-court';B.detail=0
 pools=plans();groundpools=[p for r,p in pools if r['deckY']<1]
 buildings=unary_union([structure(i) for i in IDS]+[structure(i) for i in ['way/116660358','way/502624676','way/116660354']])
 water=unary_union(groundpools)
 court=water.buffer(12,quad_segs=12).buffer(5).buffer(-5).difference(buildings.buffer(.2))
 deck=court.difference(water.buffer(.65));Y=.64
 B.planar('mandalay-pool-paving',deck,Y,True)
 B.shell(court,.2,Y,'mandalay-stone',roof=False,solid=False)
 # A continuous mapped lazy river, not a guessed solid pool.
 for r,p in pools:
  y=r['deckY'];B.source='pool/'+r['id']
  B.planar('mandalay-pool-tile',p,y-.4,True)
  B.planar('mandalay_pool',p,y-.19)
  B.planar('mandalay-white',p.buffer(.65).difference(p),y+.02,True)
  B.shell(p,y-.4,y,'mandalay-pool-tile',roof=False)
 # Broad sandy crescent at the wave pool shore; clipped to the deck and clear of buildings.
 wave=next(p for r,p in pools if r['name']=='Wave Pool')
 sand=wave.buffer(17).difference(wave.buffer(.7)).intersection(deck).intersection(box(-330,2880,-185,3035))
 B.planar('mandalay-sand',sand,Y+.025)
 # Mapped low-rise pavilion footprints around the court and south arrival.
 for ident in IDS:
  B.source='podium/'+ident;p=structure(ident);h=BYID[ident]['height'];roof=p.buffer(-1.2)
  if BYID[ident]['tags'].get('building')=='roof':
   # Roof-only records are open pavilions/covered walks, never enclosed boxes.
   B.planar('mandalay-white',p,h-.45,True)
   B.planar('mandalay-mint',p,h,True)
   B.shell(p,h-.45,h,'mandalay-white',roof=False)
   for poly in parts(p):
    ring=poly.exterior
    for at in np.arange(0,ring.length,max(6,ring.length/10)):
     q=ring.interpolate(at);B.box('mandalay-white',(q.x,(h-.45)/2,q.y),(.32,h-.45,.32),True)
   continue
  B.shell(p,.24,h,'mandalay-stone',roof=False)
  elevated=unary_union([q.buffer(.8) for r,q in pools if r['deckY']>1])
  B.planar('mandalay-roof',p.difference(elevated),h+.08,True)
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.12)
    F.box('mandalay-white',(L/2,h-.25,0),(L,.35,.55))
    if L<4:continue
    for x in np.arange(1.8,L-1,4.4):
     F.box('mandalay-window',(x,2.1,-.05),(2.7,2.8,.1))
     F.box('mandalay-white',(x-1.5,2.15,-.08),(.22,3.1,.35))
     F.box('mandalay-white',(x,3.65,-.16),(3.2,.18,.5))
    # Mint hipped eave strips observed around resort pool and Four Seasons buildings.
    if not roof.is_empty:
     c=roof.boundary.interpolate(roof.boundary.project(Point(*a)));d=roof.boundary.interpolate(roof.boundary.project(Point(*b)))
     B.face('mandalay-mint',[(a[0],h+.1,a[1]),(b[0],h+.1,b[1]),(d.x,h+.8,d.y),(c.x,h+.8,c.y)])
 # Surveyed roof-only cabanas: preserve the open sides seen in Earth.
 for ident in CABANAS:
  B.source='cabana/'+ident;p=footprint(ident);c=p.centroid
  B.planar('mandalay-shade',p,3.5)
  B.planar('mandalay-pool-paving',p,Y,True)
  for poly in parts(p):
   ps=list(poly.exterior.coords)[:-1]
   for a,b in zip(ps,ps[1:]+ps[:1]):
    B.tube('mandalay-chair-frame',(a[0],3.45,a[1]),(b[0],3.45,b[1]),.07,6)
    B.box('mandalay-chair-frame',(a[0],2.02,a[1]),(.12,2.76,.12))
   # Pale fabric panel over a thin supported canopy, not an enclosed utility box.
   for a,b in zip(ps,ps[1:]+ps[:1]):B.face('mandalay-shade',[(a[0],3.5,a[1]),(b[0],3.5,b[1]),(c.x,3.85,c.y)])
 # Furniture follows the water edge with clear paths; pooled materials, no per-chair colliders.
 B.source='mandalay-pool-furniture';count=0
 for poly in parts(water):
  ring=poly.buffer(3.6).exterior
  for at in np.arange(0,ring.length,3.2):
   p=ring.interpolate(at);n=poly.exterior.interpolate(poly.exterior.project(p));dx,dz=n.x-p.x,n.y-p.y
   if not deck.buffer(-1.4).contains(p):continue
   F=Frame(B,p.x,p.y,math.atan2(-dx,dz),Y)
   F.box('mandalay-chair-frame',(0,.30,0),(.77,.1,2.0));F.box('mandalay-cushion',(0,.39,-.25),(.70,.08,1.4))
   B.face('mandalay-cushion',[F.p(-.35,.42,.4),F.p(.35,.42,.4),F.p(.35,.88,.98),F.p(-.35,.88,.98)])
   for x in [-.32,.32]:F.box('mandalay-chair-frame',(x,.16,0),(.055,.30,1.6))
   count+=1
   if count%5==0:
    F.lathe('mandalay-chair-frame',1.0,0,[(0,.045),(2.35,.045)],6)
    F.lathe('mandalay-shade',1.0,0,[(2.3,1.5),(2.65,.07)],8)
 from mandalay_palms import plant
 palms=plant(B,water,buildings,deck)
 report={'palms':palms,'pools':len(pools),'waterAreaM2':round(sum(p.area for r,p in pools),1),'deckAreaM2':round(deck.area,1),'loungers':count,'pavilions':IDS,'cabanas':CABANAS,'heightEstimates':'Ground deck0.64m; rooftop pools5.64m. Pool depth0.4m is collision compromise; not survey-certified.'}
 Path('build/city-exteriors/mandalay-pool-report.json').write_text(json.dumps(report,indent=2))
 return IDS
