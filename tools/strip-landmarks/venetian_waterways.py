"""Outdoor gondola clearance shared by architecture and review metadata.
OSM fixes the channel banks. Metre elevations and clearance allowances are design
estimates, not surveyed levels. Indoor Level 2 remains a separate water system.
"""
import math
import numpy as np
from shapely.geometry import Polygon,box
from common import Frame,parts,triangles

WATER_Y=.31
NORTH_CHANNEL=box(223,-729.2,246.5,-722.9)
SOUTH_CHANNEL=box(219,-658.0,246,-650.5)

def plaza_height(x):
 base=.24+max(0,min(1,(221.5-x)/6))*.86
 if 182.5<x<207.5:base+=3.05*math.sin(math.pi*(x-182.5)/25)**2
 return base

def plaza_soffit(x):
 if not 186<x<204:return .04
 return min(plaza_height(x)-.38,.08+3.52*math.sqrt(max(0,1-((x-195)/9)**2)))

def surface(B,mat,polygon,offset=0,solid=False,underside=False):
 """Split before triangulation, so slabs, inlays and underside share the grade."""
 if polygon.is_empty:return
 lo,_,hi,_=polygon.bounds
 stations=sorted(set([lo,hi,182.5,186,195,204,207.5,215.5,221.5]+list(np.arange(182.5,208,.5))))
 fn=plaza_soffit if underside else plaza_height
 for a,b in zip(stations,stations[1:]):
  for p in parts(polygon.intersection(box(a,-1000,b,0))):
   for tri in triangles(p):B.upface(mat,[(x,fn(x)+offset,z) for x,z in list(tri.exterior.coords)[:-1]],solid)

def side_bridge(B,x0=228.2,x1=232.8,z0=-731.0,z1=-721.7):
 """Small covered crossing over the north canal throat, open below its arch."""
 B.source='venetian-canal-bridge';B.detail=0
 mid=(z0+z1)/2;r=3.45;spring=1.35;rise=3.05
 curve=[(mid+r*math.cos(t),spring+rise*math.sin(t)) for t in np.linspace(math.pi,0,41)]
 hole=Polygon([(mid-r,-2)]+curve+[(mid+r,-2)])
 wall=box(z0,.04,z1,4.9).difference(hole)
 for p in parts(wall):
  for tri in triangles(p):
   for x in [x0,x1]:B.face('ivory',[(x,y,z) for z,y in list(tri.exterior.coords)[:-1]],True)
 for (z,y),(zz,yy) in zip(curve,curve[1:]):B.face('palazzo-stone',[(x0,y,z),(x1,y,z),(x1,yy,zz),(x0,yy,zz)],True)
 B.planar('marble',box(x0,z0,x1,z1),4.9,True)
 for x in [x0-.02,x1+.02]:
  B.path('ivory',[(x,y,z) for z,y in curve],.13,8)
  F=Frame(B,x,mid,math.pi/2,y=4.9)
  for z in np.linspace(z0+.9,z1-.9,4):
   F=Frame(B,x,z,math.pi/2,y=4.9)
   F.arch(0,0,1.65,2.55,'ivory',.12,0)
  B.box('ivory',(x,7.64,mid),(.44,.32,z1-z0+.4))
 B.box('ivory',((x0+x1)/2,7.94,mid),(x1-x0+.65,.28,z1-z0+.7))

def water_review():
 return dict(waterY=WATER_Y,boatLength=9.2,boatWidth=2.3,airHeight=2.6,
             testedEnvelope=dict(length=10.4,width=2.7,aboveWater=2.9),indoorConnected=False,
             routes=[dict(name='main-plaza-crossing',points=[[195,-714],[195,-677]]),
                     dict(name='north-channel',points=[[229,-725.45],[239.5,-725.45]]),
                     dict(name='south-channel',points=[[215,-654.2],[236.5,-654.2]])])
