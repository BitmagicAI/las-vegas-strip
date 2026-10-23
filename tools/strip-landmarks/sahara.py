"""SAHARA exterior: official May 2026 map, Earth November 2022.
Missing tower plans and roof heights are explicit photographic estimates.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='saharaExterior'

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/135453935','way/276426484','way/543642782','way/395428060']
 records=[dict(BYID[i],shape=footprint(i)) for i in ids]
 # Two absent towers are fitted to Earth roof silhouettes, with the official map identifying their uses.
 marra=Polygon([(1550,-2921),(1603,-2918),(1602,-2903),(1575,-2905),(1572,-2850),(1550,-2851)])
 blanca=Polygon([(1487,-2907),(1503,-2907),(1503,-2899),(1535,-2897),(1534,-2880),(1501,-2882),(1500,-2876),(1486,-2877)])
 records.extend([dict(id='marra',shape=marra,base=6,height=85),dict(id='blanca',shape=blanca,base=6,height=44)])
 canopy=scale(Point(1371,-2904).buffer(1,48),xfact=31,yfact=28,origin=(1371,-2904))
 records[0]['shape']=records[0]['shape'].difference(canopy.buffer(6));surface=BuildingSurfaces(records)
 plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='sahara');access=Access(plan)
 for r in records:
  ident=r['id'];p=r['shape'];h=r['height'];tower=ident in ['marra','blanca','way/276426484'];alex=ident=='way/276426484';garage=ident=='way/543642782';replacement=ident=='way/135453935'
  B.source='tower/sahara' if alex else 'podium/'+ident
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.1:continue
     F,L,nx,nz=facade_frame(B,a,b,p,.2);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
     visible=surface.wall(ident,a,b,r['base'],h,access)
     if replacement:
      for tri in visible:B.face('sa-limestone',tri,True)
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in visible])
     def patch(mat,x0,y0,x1,y1,offset=.22):
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
     patch('sa-glass' if alex and L>30 else 'sa-limestone',0,r['base'],L,h)
     if tower:
      spacing=3.3 if alex else 3.7;count=max(1,round(L/spacing));step=L/count
      if L>25:
       for x in np.arange(step*.5,L,step):
        if alex:patch('sa-white',x-.10,7,x+.10,h-2,.37)
        else:
         for y in np.arange(7,h-2,2.95):
          patch('sa-glass',x-.95,y,x+.95,y+1.55,.27)
          patch('sa-sill',x-1.02,y-.18,x+1.02,y,.36)
       if alex:
        for y in np.arange(7,h-1,2.95):patch('sa-white',0,y,L,y+.36,.40)
       else:
        for x in np.arange(0,L,step*3):patch('sa-white',x,6,min(x+.35,L),h-1,.38)
      else:
       patch('sa-sand',1,r['base'],L-1,h-1,.27)
       if L>12 and ident=='marra':
        for j,ch in enumerate('SAHARA'):F.text(ch,(L/2,h-9-j*4.0,-.16),2.1,'sa-gold')
      patch('sa-white',0,h-1,L,h,.42)
      F.box('sa-white',(L/2,h+.2,0),(L+.1,.4,.8))
     elif garage:
      for y in np.arange(2,h-1,3.3):patch('sa-shadow',0,y,L,y+1.65,.29)
      for x in np.arange(0,L,8):patch('sa-white',x,0,min(x+.6,L),h,.36)
      if nz>.65 and L>55:patch('sa-white',L*.37,0,L*.62,h,.43)
     else:
      front=nx<-.4
      if front:
       for x in np.arange(.7,L-2,4.4):
        patch('sa-glass',x,.5,min(x+3.3,L-.3),h-1.0,.27)
        patch('sa-gold',x-.12,.4,x+.08,h-.5,.37)
       F.box('sa-shadow',(L/2,h-.7,-.6),(L,.22,1.4))
       if L>23:F.text('SAHARA',(L/2,h-1.8,-.8),.85,'sa-gold')
      else:
       for x in np.arange(1,L,6):patch('sa-sill',x,.5,min(x+.15,L),h-.5,.29)
      patch('sa-white',0,h-.5,L,h,.34)
   roof=surface.roof(ident,poly,h);B.planar('sa-flat-roof',roof,h+.06,replacement)
   if not tower and not garage:
    for x in np.arange(p.bounds[0]+8,p.bounds[2]-6,24):
     for z in np.arange(p.bounds[1]+8,p.bounds[3]-6,25):
      if roof.contains(box(x-2,z-1.5,x+2,z+1.5)):B.box('ph-metal',(x,h+.8,z),(4,1.4,3))
 from sahara_arrival import arrival
 arrival(B)
 # Open courtyard pool and its paving, fitted between the existing wings.
 B.source='pool-court';court=box(1406,-2919,1484,-2868);pool=box(1430,-2905,1467,-2894).buffer(2)
 B.planar('sa-paving',court.difference(pool),.28,True);B.planar('sahara_pool',pool,.14)
 B.planar('sa-white',pool.buffer(.55).difference(pool),.34)
 for x in np.arange(1411,1481,6):
  for z in [-2914,-2873]:
   F=Frame(B,x,z,0 if z==-2914 else math.pi,y=.28)
   F.box('ph-awning',(0,.42,0),(.68,.13,1.95));F.box('ph-metal',(0,.3,0),(.72,.08,2))
   for xx in [-.28,.28]:F.box('ph-metal',(xx,.14,.1),(.035,.28,1.65))
   B.face('ph-awning',[F.p(-.34,.49,-.3),F.p(.34,.49,-.3),F.p(.34,.95,-.94),F.p(-.34,.95,-.94)])
 return dict(key=KEY,name='SAHARA exterior',center=[1490,0,-2930],bounds=[1300,-3075,1660,-2780],building='sahara',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
