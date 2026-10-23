"""Strip retail elevation from archived AD photograph; dimensions/registration estimated.
Independent exterior only; existing Palazzo arrival/interiors remain untouched.
"""
import math
import numpy as np
from common import Frame

def frontage(B):
 B.source='palazzo-retail-front';B.detail=0
 F=Frame(B,344,-850,math.atan2(35,19),y=.24)
 def curve(x):return -1.2-2.0*(1-(x/16)**2)
 # Raised public terrace and wide stair; not an invented interior connection.
 F.box('sandstone',(0,1.45,-5),(32,2.9,7),True)
 F.floor(32,7,z=-5,mat='marble',y=3.0)
 from palazzo_steps import stairs,barrier
 stairs(B,F)
 # Curved stone envelope entirely in front of the inherited podium skin.
 for a,b in zip(np.linspace(-16,16,65),np.linspace(-16,16,65)[1:]):
  za,zb=curve(a),curve(b)
  B.face('sandstone',[F.p(a,3,za),F.p(b,3,zb),F.p(b,14.4,zb),F.p(a,14.4,za)],True)
  for y,depth,height in [(3.15,.15,.2),(12.6,.2,.18),(13.6,.35,.22),(14.35,.5,.25)]:
   B.face('ivory',[F.p(a,y,za-depth),F.p(b,y,zb-depth),F.p(b,y+height,zb-depth),F.p(a,y+height,za-depth)])
 # Five bays: tall center storefronts, framed flanking shop windows.
 for x in [-6,0,6]:
  z=curve(x)-.18;W=4.8
  F.box('darkglass',(x,7.55,z),(W,8.5,.10))
  for side in [-1,1]:F.box('ivory',(x+side*(W/2+.12),7.15,z-.1),(.25,8.1,.25))
  F.path('ivory',[(x+(W/2+.12)*math.cos(a),11.2+.8*math.sin(a),z-.1) for a in np.linspace(0,math.pi,33)],.16)
  for xx in [x-W/2,x,x+W/2]:F.box('brass',(xx,7.45,z-.10),(.07,8.6,.10))
  for y in [3.35,6.7,10.8]:F.box('ivory',(x,y,z-.12),(W,.12,.13))
  # Projecting black fabric awning with scalloped valance.
  B.face('blackiron',[F.p(x-2.5,7,z-.3),F.p(x+2.5,7,z-.3),F.p(x+2.5,5.9,z-2.2),F.p(x-2.5,5.9,z-2.2)])
  F.box('blackiron',(x,5.76,z-2.2),(5,.28,.07))
  B.detail=1
  for xx in [x-2.5,x+2.5]:F.tube('bronze',(xx,4.9,z-.1),(xx,5.9,z-2.2),.04,6)
  for j in range(12):
   xx=x-2.35+j*.42
   F.path('ivory',[(xx+.2*math.cos(a),5.72-.12*math.sin(a),z-2.25) for a in np.linspace(0,math.pi,9)],.016,4)
  # Recessed frieze frame with repeating stone scrollwork.
  F.box('champagne',(x,12.25,z),(5.1,.7,.10))
  for yy in [11.91,12.59]:F.box('ivory',(x,yy,z-.16),(5.2,.08,.12))
  for xx in np.arange(x-2.2,x+2.3,.55):
   F.path('ivory',[(xx+.22*math.cos(a),12.25+.23*math.sin(a),z-.2) for a in np.linspace(0,math.tau,17)],.027,4)
  B.detail=0
 for x in [-12,12]:
  z=curve(x)-.2
  F.box('darkglass',(x,5.1,z),(4.3,4.0,.1))
  F.arch(x,z-.12,4.5,8.0,'ivory',.16,3.1)
  F.path('ivory',[(x+1.05*math.cos(a),10.5+1.05*math.sin(a),z-.13) for a in np.linspace(0,math.tau,49)],.12)
  for a,b in zip(np.linspace(0,math.tau,49),np.linspace(0,math.tau,49)[1:]):
   B.face('darkglass',[F.p(x,10.5,z-.08),F.p(x+math.cos(a),10.5+math.sin(a),z-.08),F.p(x+math.cos(b),10.5+math.sin(b),z-.08)])
  F.box('ivory',(x,10.5,z-.15),(.055,2,.06));F.box('ivory',(x,10.5,z-.15),(2,.055,.06))
 F.text('P A L A Z Z O' ,(0,13.05,curve(0)-.6),.62,'bronze')
 # Terrace rail leaves the central stairs open. Balusters are near detail.
 for a,b in [(-16,-13.85),(-10.15,10.15),(13.85,16)]:
  barrier(B,[F.p(a,3.0,-8.5),F.p(b,3.0,-8.5),F.p(b,4.27,-8.5),F.p(a,4.27,-8.5)])
  for yy in [3.1,4.18]:F.box('ivory',((a+b)/2,yy,-8.5),(b-a,.19,.42))
  for x in np.arange(a+.3,b,.48):
   B.detail=1;F.lathe('ivory',x,-8.5,[(3.2,.1),(3.35,.14),(3.55,.075),(3.85,.10),(4.08,.07)],10)
  B.detail=0
 for x in [-15.5,-10.2,10.2,15.5]:
  F.box('ivory',(x,3.6,-8.5),(.55,1.2,.55))
  F.lathe('ivory',x,-8.5,[(4.2,.35),(4.4,.23),(4.7,.50),(4.8,.52)],24)
 from palazzo_dining import patio
 patio(B,F)
 return dict(eye=F.p(0,6,-38),target=F.p(0,8,0))
