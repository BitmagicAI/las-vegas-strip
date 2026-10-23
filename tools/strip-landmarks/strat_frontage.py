"""The STRAT hotel / lower exterior; observation tower retained separately.
Earth imagery November2022–March2024. Facade spacing is photo-estimated.
"""
from common import *
from strat_observation import observation
from strat_arrival import arrival
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='stratExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/543641711','way/135456188','way/89469762','way/89469753','way/89469712','way/89469757','way/284940187','way/276427182']
 records=[dict(BYID[i],shape=footprint(i)) for i in ids]
 for r in records:
  if r['id']=='way/89469753':r['height']=26.0 # Level-eight pool platform, aligned to garage roof.
 # Casino podium height is an explicit photo estimate; source fallback6m was one storey.
 for r in records:
  if r['id']=='way/135456188':
   r['height']=18.0
   # The two footprint fingers are sloping canopy shoulders, not18m wall extrusions.
   wings=unary_union([Polygon([(1509.06,-3426.247),(1511.893,-3417.508),(1506.776,-3416.028),(1503.565,-3425.679)]),Polygon([(1533.367,-3444.526),(1540.858,-3437.802),(1537.351,-3433.605),(1530.283,-3440.151)])])
   r['shape']=r['shape'].difference(wings.buffer(.01)).buffer(0)
 surface=BuildingSurfaces(records);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='strat'))
 for r in records:
  ident=r['id'];p=r['shape'];h=r['height'];podium=ident=='way/135456188';tower=ident=='way/543641711';garage=ident=='way/89469762';small=ident in ['way/284940187','way/276427182'];B.source='tower/strat' if tower else 'podium/'+ident
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.1:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.20);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;mid=line.interpolate(.5,normalized=True)
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in surface.wall(ident,a,b,r['base'],h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.22):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]],(podium and y0>=6) or ident=='way/89469753')
    patch('st-white' if tower else 'st-stone',0,r['base'],L,6 if podium else h)
    if tower:
     if L>15:
      for y in np.arange(5,h-2,3.0):
       patch('st-glass',.5,y,L-.5,y+1.75,.27)
       patch('st-sill',0,y-.18,L,y+.02,.39)
      for x in np.arange(0,L,3.6):patch('st-white',x,4,min(x+.25,L),h-1.3,.41)
     else:patch('st-grey',.5,4,L-.5,h-1.3,.25)
     patch('st-white',0,h-1.2,L,h,.44)
     F.box('st-white',(L/2,h+.15,0),(L+.1,.3,.7))
     if nx>.5 and L>50:F.text('THE STRAT',(L/2,h-3.1,-.25),2.1,'st-blue')
    elif podium:
     # Continuous buff panelled upper casino wall, not storefront glazing.
     patch('st-stone',0,6,L,h,.24)
     for y in np.arange(7.5,h,1.15):patch('st-joint',0,y,L,y+.035,.27)
     for x in np.arange(.5,L,3.1):patch('st-joint',x,6.8,min(x+.04,L),h-.3,.28)
     for y in [5.6,6.45,17.65]:patch('st-white',0,y,L,y+.28,.44)
     if nx>.25 or nz>.25:
      for x in np.arange(.6,L-1,4.7):
       patch('st-glass',x,.7,min(L-.4,x+3.6),4.5,.29)
       patch('st-grey',x,4.5,min(L-.4,x+3.6),4.75,.35)
     F.box('st-white',(L/2,h+.14,0),(L+.04,.28,.75))
    elif garage:
     for y in np.arange(2,h-1,3.2):patch('st-shadow',0,y,L,y+1.55,.28)
     for x in np.arange(0,L,8.5):patch('st-white',x,0,min(x+.55,L),h,.36)
     patch('st-white',0,h-.5,L,h,.4)
    else:
     street=nx>.3 or small
     if street:
      for x in np.arange(.7,L-1,4.7):
       patch('st-glass',x,.6,min(L-.4,x+3.6),min(4.6,h-.7),.28)
       patch('st-white',x-.1,.4,x+.08,h-.5,.38)
      F.box('st-blue' if not small else 'st-red',(L/2,h-.7,-.5),(L,.22,1.25))
      if L>25 and ident=='way/135456188':F.text('THE STRAT',(L/2,h-1.65,-.72),1.0,'st-white')
      if L>15 and ident=='way/284940187':F.text("Carl's Jr.",(L/2,h-.2,-.75),.65,'st-red')
     else:
      for x in np.arange(0,L,5):patch('st-grey',x,.2,min(x+.08,L),h-.3,.25)
     for y in [1.1,h-.35]:patch('st-white',0,y,L,y+.16,.35)
   roof=surface.roof(ident,poly,h)
   if ident=='way/89469753':continue # Pool block owns the deck and recessed basins.
   B.planar('st-flat-roof',roof,h+.08,podium)
   if garage:
    # Roof parking replaces the former repeated HVAC units; stall layout is estimated.
    for x in np.arange(p.bounds[0]+5,p.bounds[2]-4,2.75):
     for z in np.arange(p.bounds[1]+8,p.bounds[3]-6,16):
      if roof.contains(box(x-1.4,z-2.8,x+1.4,z+2.8)):
       B.box('st-white',(x,h+.105,z),(.095,.025,5.2))
   if not tower and not garage:
    for x in np.arange(p.bounds[0]+6,p.bounds[2]-4,21):
     for z in np.arange(p.bounds[1]+6,p.bounds[3]-4,26):
      if roof.contains(box(x-2,z-1.2,x+2,z+1.2)):
       B.box('ph-metal',(x,h+.55,z),(4,.9,2.4));B.box('st-grey',(x,h+1.03,z),(3.7,.06,2.2))
 arrival(B)
 observation(B)
 return dict(key=KEY,name='The STRAT hotel and lower exteriors',center=[1490,0,-3500],bounds=[1320,-3680,1735,-3370],building='strat',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
