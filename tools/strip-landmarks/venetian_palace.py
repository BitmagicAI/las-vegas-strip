"""Doge's Palace frontage fitted to the mapped 66m canal-front wall.
Oct9 closer creator Google Earth captures establish two arcades, broad upper wall,
central ceremonial balcony, diamond stonework and adjacent distinct end wings.
"""
import math
import numpy as np
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
from common import Frame,parts,triangles

def palace(B):
 P=Frame(B,225.15,-690.7,math.pi/2);L=66.;bay=L/16
 B.source='venetian-palace';B.detail=0
 from venetian_plaza import DECK
 B.planar('marble',P.poly([(-L/2,-3.5),(L/2,-3.5),(L/2,3.5),(-L/2,3.5)]).difference(DECK),.24,True)
 # Both storeys have deep open arcades. Back wall belongs to the existing podium.
 for y,h,d in [(7.35,.55,8),(12.7,.55,8),(26.4,.4,9),(27,.4,9.4)]:P.box('ivory',(0,y,1),(L+.7,h,d))
 # Pierced spandrels in the façade plane, with real intrados depth.
 def arcade(cx,w,base,spring,rise,top,z=-3.7,pointed=False):
  r=w/2
  if pointed:
   curve=[(cx-r,spring)]+[(cx-r*(1-t)**2,spring+rise*t) for t in np.linspace(0,1,10)[1:]]+[(cx+r*t*t,spring+rise*(1-t)) for t in np.linspace(0,1,10)[1:]]
  else:curve=[(cx+r*math.cos(a),spring+rise*math.sin(a)) for a in np.linspace(math.pi,0,25)]
  hole=Polygon([(cx-r,base)]+curve+[(cx+r,base)])
  wall=box(cx-bay/2,base,cx+bay/2,top).difference(hole)
  for p in parts(wall):
   for tri in triangles(p):
    for zz in [z,z+.48]:B.face('ivory',[P.p(x,y,zz) for x,y in list(tri.exterior.coords)[:-1]])
  for (x,y),(xx,yy) in zip(curve,curve[1:]):B.face('ivory',[P.p(x,y,z),P.p(xx,yy,z),P.p(xx,yy,z+.48),P.p(x,y,z+.48)])
  P.path('ivory',[(x,y,z-.065) for x,y in curve],.10,8)
 for i in range(17):
  x=-L/2+i*bay
  P.lathe('ivory',x,-3.7,[(0,.30),(.25,.38),(.45,.28),(4.4,.22),(4.6,.36),(4.9,.42),(5.12,.36)],16)
  if i<16:arcade(x+bay/2,bay-.62,4.88,5.0,1.77,7.09)
 # Upper loggia at twice the bay frequency. Cutouts include quatrefoil tracery.
 for i in range(32):
  x=-L/2+(i+.5)*bay/2;w=bay/2-.30;r=w/2
  P.lathe('ivory',x-bay/4,-3.72,[(7.65,.14),(7.8,.21),(9.7,.13),(9.95,.24),(10.1,.22)],12)
  curve=[(x-r,9.93)]+[(x-r*(1-t)**2,9.93+1.35*t) for t in np.linspace(0,1,9)[1:]]+[(x+r*t*t,9.93+1.35*(1-t)) for t in np.linspace(0,1,9)[1:]]
  hole=Polygon([(x-r,7.5)]+curve+[(x+r,7.5)])
  q=unary_union([Point(x+math.cos(a)*.22,11.88+math.sin(a)*.22).buffer(.255,resolution=10) for a in [0,math.pi/2,math.pi,math.pi*1.5]])
  wall=box(x-bay/4,9.92,x+bay/4,12.6).difference(hole).difference(q)
  for p in parts(wall):
   for tri in triangles(p):B.face('ivory',[P.p(xx,yy,-3.75) for xx,yy in list(tri.exterior.coords)[:-1]])
  P.path('ivory',[(xx,yy,-3.84) for xx,yy in curve],.075,6)
  # Balusters are confined to the upper balcony, no ground-floor barrier.
  for dx in [-.63,-.21,.21,.63]:P.lathe('ivory',x+dx,-4.0,[(7.62,.05),(7.8,.075),(8.12,.045),(8.42,.07)],8)
 for yy in [7.62,8.52]:P.box('ivory',(0,yy,-4.0),(L,.14,.23))
 # Solid upper wall occupies the same plane as the arcade, with recessed windows.
 P.box('palace-limestone',(0,19.7,.30),(L,13.4,7.3))
 windows=[]
 for x in [-27.5,-16.5,-5.5,5.5,16.5,27.5]:
  w=2.6;r=w/2;lo=16.35;spring=18.75
  pts=[(x-r,lo),(x+r,lo),(x+r,spring)]+[(x+r*math.cos(a),spring+r*math.sin(a)) for a in np.linspace(0,math.pi,25)[1:]]
  windows.append(Polygon(pts).buffer(.23))
  B.face('darkglass',[P.p(xx,yy,-3.39) for xx,yy in pts]);P.path('ivory',[(xx,yy,-3.5) for xx,yy in pts+[pts[0]]],.085,6)
  P.box('ivory',(x,lo-.14,-3.5),(w+.4,.21,.40))
 # The visible diamond masonry is nested inlaid stone, not coarse wire geometry.
 B.detail=1
 masks=unary_union(windows).union(box(-3.5,15.3,3.5,27))
 for row in range(16):
  yy=13.3+row*.81
  for j in range(42):
   x=-32.6+j*1.6+(row%2)*.8
   if abs(x)>32.5:continue
   diamond=Polygon([(x,yy+.79),(x+.77,yy),(x,yy-.79),(x-.77,yy)])
   shape=diamond.difference(diamond.buffer(-.11)).intersection(box(-33,13,33,26.1)).difference(masks)
   for p in parts(shape):
    for tri in triangles(p):B.face('ivory',[P.p(xx,y,-3.362) for xx,y in list(tri.exterior.coords)[:-1]])
   p=diamond.buffer(-.27).difference(diamond.buffer(-.37)).difference(masks)
   for q in parts(p):
    for tri in triangles(q):B.face('ivory',[P.p(xx,y,-3.365) for xx,y in list(tri.exterior.coords)[:-1]])
 for x in np.arange(-29.3,31,5.5):
  P.path('ivory',[(x+.31*math.cos(a),23.9+.31*math.sin(a),-3.52) for a in np.linspace(0,math.tau,17)],.09,6)
  B.face('darkglass',[P.p(x+.26*math.cos(a),23.9+.26*math.sin(a),-3.38) for a in np.linspace(0,math.tau,17)])
 # Central ceremonial window and carved surround: major silhouette in the source.
 P.box('ivory',(0,16.0,-4.0),(5.3,.5,2.0));P.box('darkglass',(0,19.7,-3.49),(2.6,5.8,.07))
 for side in [-1,1]:
  P.lathe('ivory',side*1.9,-3.92,[(16.2,.24),(16.55,.34),(21.9,.22),(22.3,.40),(23.4,.28)],16)
  P.lathe('ivory',side*2.6,-3.73,[(20.7,.20),(21.0,.33),(23.8,.22),(24.2,.30),(25.8,0)],12)
 P.arch(0,-3.93,3.1,24.0,'ivory',.22,18.7)
 for yy,w in [(22.5,5.5),(24.4,4.6),(25.8,3.2)]:P.box('ivory',(0,yy,-3.94),(w,.30,1))
 P.lathe('ivory',0,-3.8,[(26,.3),(26.6,.45),(27.3,.22),(29,.12),(29.8,0)],12)
 for x in np.arange(-32.6,33,1.35):
  P.lathe('ivory',x,-3.75,[(27.2,.12),(27.48,.22),(27.7,.13),(28.15,0)],10)
  P.path('ivory',[(x+.12,27.3,-3.75),(x+.4,27.65,-3.75),(x+.67,27.47,-3.75),(x+1.,27.65,-3.75),(x+1.2,27.3,-3.75)],.065,6)
 B.detail=0
 # One tall promotional banner as in creator's closer reference.
 P.box('venetian-burgundy',(-20.3,19.4,-4.0),(2.8,12.0,.08));P.box('ivory',(-20.3,14.7,-4.055),(2.8,2.6,.03))
 for j,t in enumerate(['GRAND','CANAL','SHOPPES']):P.text(t,(-20.3,15.3-j*.5,-4.09),.36,'charcoal')
 P.tube('brass',(-22,25.45,-4),(-18.6,25.45,-4),.06)
 # Independent smaller facades north and south preserve both water side channels.
 for centre,width,height in [(-44,18,24),(41,12,28)]:
  W=Frame(B,229,-690.7+centre,math.pi/2,y=.24)
  if centre<0:
   # Follow the mapped north bank rather than placing an axis-aligned wing
   # through its diagonal approach. The street face stays 0.7m behind coping.
   a=(224.817,-747.288);b=(228.774,-728.375);length=math.dist(a,b)
   nx,nz=(b[1]-a[1])/length,-(b[0]-a[0])/length
   W=Frame(B,(a[0]+b[0])/2+nx*3.7,(a[1]+b[1])/2+nz*3.7,math.atan2(nx,nz),y=.24)
   width=length-.7
  wing=W.poly([(-width/2,-3),(width/2,-3),(width/2,9),(-width/2,9)])
  # The south wing surrounds the existing Rialto upper-level passage. Keep
  # the actual opening in the mesh as well as in the collision shell.
  passage=box(223,-646.6,242,-641.4) if centre>0 else None
  boat=[dict(p=[x,.04,-654.2],yaw=math.pi/2,width=6.8,height=4.3) for x in (226,238)] if centre>0 else []
  B.shell(wing,.24,height+.24,'palazzo-stone',openings=boat,roof=False,
          interior=(passage,12.6) if passage is not None else None)
  if centre>0:
   # A real ceiling in the boat passage, clear of the existing 6.24m public floor.
   B.planar('palazzo-stone',wing.intersection(box(218,-657.6,246,-650.8)),4.44,True)
  for y in [1,7.5,14.5,height]:
   left=-width/2-.25 if centre<0 or y>12.6 else -3.0
   right=width/2+.25
   if centre>0 and y<4.5:right=min(right,.9)
   if right>left:W.box('ivory',((left+right)/2,y,-3.25),(right-left,.35,.6))
  for x in np.arange(-width/2+2,width/2,3.5):
   for lo in [1,8.1,15.1]:
    if centre>0 and ((x< -1.6 and lo<12.6) or (x>-.4 and lo<4.5)):continue
    hi=min(lo+5.1,height-1)
    W.box('darkglass',(x,(lo+hi)/2,-3.05),(2.2,hi-lo,.07));W.arch(x,-3.2,2.5,hi,'ivory',.10,lo)
    for side in [-1,1]:W.lathe('ivory',x+side*1.3,-3.3,[(lo,.13),(lo+.2,.20),(hi-1,.12),(hi-.8,.24)],10)
  roof=[(-width/2-.4,-3.5),(width/2+.4,-3.5),(width/2+.4,9.5),(-width/2-.4,9.5)]
  for a,b in zip(roof,roof[1:]+roof[:1]):B.face('terracotta',[W.p(0,height+2,3),W.p(a[0],height,a[1]),W.p(b[0],height,b[1])])
 B.detail=0
