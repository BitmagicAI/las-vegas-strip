"""Reversible film frontage detail. OSM footprint, official Jan 2026 MMS lease plan;
elevations/sign dimensions remain photographic estimates, not a completed resort rebuild.
Only writes build/film/storm/street-frontage.*; no roads, interiors or base GLBs.
"""
import sys,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/blender-level'))
from bmlevel import *
reset()
mat('Film frontage / dark granite',(.042,.046,.049),roughness=.62)
mat('Film frontage / brushed aluminum',(.24,.26,.28),metal=.65,roughness=.34)
mat('Film frontage / limestone',(.48,.45,.40),roughness=.8)
mat('Film frontage / shop glazing',(.017,.034,.045),metal=.15,roughness=.25)
mat('Film frontage / interior wood',(.25,.115,.048),roughness=.67)
mat('Film frontage / display warm',(.58,.32,.14),roughness=.6,glow=.45)
mat('Film frontage / neon white',(.62,.71,.77),glow=2)
mat('Film frontage / neon red',(.58,.012,.008),glow=1.8)
mat('Film frontage / neon violet',(.16,.024,.38),glow=1.4)
mat('Film frontage / inset',(.012,.014,.018),roughness=.68)
def d(n,p,s,m='dark granite',yaw=0,bevel=.02):decor(n,p,s,'Film frontage / '+m,yaw=yaw,bevel=bevel)
def label(n,value,p,size=.7,m='neon white',yaw=0):text(n,value,p,'Film frontage / '+m,size=size,yaw=yaw+math.pi,extrude=.016)

def storefront(name,width,height=7):
 # Depth offsets form actual recessed glazing, transoms, piers, doors, projecting canopies.
 d(name+' backing',(0,height/2,0),(width,height,.35))
 bays=max(2,round(width/2.1));bay=width/bays
 for i in range(bays):
  x=-width/2+(i+.5)*bay
  d('Recessed display',(x,2.65,.22),(bay-.13,4.5,.12),'shop glazing')
  d('Interior back panel',(x,1.8,.30),(bay-.44,2.4,.06),'interior wood')
  d('Display plinth',(x,.7,.43),(bay-.45,.32,.40),'limestone')
  d('Display wash',(x,4.74,.42),(bay-.28,.055,.18),'display warm')
  for y in [.36,2.5,4.96]:d('Glazing transom',(x,y,.46),(bay,.055,.12),'brushed aluminum',bevel=.006)
  d('Glazing mullion',(x-bay/2,2.65,.47),(.085,4.70,.18),'brushed aluminum',bevel=.008)
 d('Door threshold',(0,.22,.69),(2.45,.12,.92),'limestone')
 for x in [-.63,.63]:
  d('Door leaf',(x,1.55,.56),(1.14,2.60,.055),'shop glazing')
  d('Door handle',(x+(.39 if x<0 else -.39),1.48,.65),(.033,.60,.033),'brushed aluminum',bevel=.012)
 d('Sign fascia',(0,5.8,.39),(width-.12,1.45,.52))
 label(name+' lettering',name,(0,5.47,.73),min(.85,(width-1)/max(5,len(name))*.85))
 d('Canopy',(0,5.12,1.03),(width+.1,.20,2.10),'brushed aluminum')
 d('Under canopy light',(0,4.99,1.67),(width-.65,.035,.12),'neon white',bevel=0)
 for x in [-width/2+.15,width/2-.15]:d('Stone pier',(x,3.5,.40),(.25,6.6,.9),'limestone')

# Harmon frontage is a long retail/restaurant elevation, distinct from Strip signage.
for x,w,name in [(121,25,'PAMPAS'),(151,32,'GEN KOREAN BBQ'),(185,27,'NACHO DADDY'),(219,28,'MIRACLE MILE SHOPS'),(248,22,'BUFFALO WILD WINGS')]:
 with context(name,origin=(x,.15,859.25)):
  storefront(name,w)
  for y in [8,10.7,13.4,16.1,18.6]:d('Upper rainscreen joint',(0,y,-.01),(w,.07,.15),'brushed aluminum',bevel=0)
  for u in range(4):d('Vertical cladding seam',(-w/2+(u+.5)*w/4,13.7,.02),(.045,11,.12),'brushed aluminum',bevel=0)
  d('Roof edge',(0,19.7,.30),(w,.24,.75),'limestone')

# West facade follows the surveyed scalloped footprint, not a straight box through the sidewalk.
survey=json.load(open(R/'build/strip-survey/survey.json'))
poly=next(b for b in survey['buildings'] if b['id']=='relation/1606512')['polygons'][0][0]
west=[(p[0]-.42,-p[1]) for p in poly if 598<=-p[1]<=774 and p[0]<55]
for i,(a,b) in enumerate(zip(west,west[1:])):
 length=math.dist(a,b)
 if length>30:continue
 yaw=math.atan2(-(b[1]-a[1]),b[0]-a[0]);mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
 # Poly goes south; its exterior normal is west. The pane thickness avoids the old wall face.
 with context('Strip frontage bay',origin=(mid[0],.15,mid[1]),yaw=yaw):
  d('Lower granite',(0,1.0,.04),(length,1.7,.28))
  d('Retail glass',(0,3.7,.09),(length,3.6,.14),'shop glazing')
  d('Upper display housing',(0,12.4,.08),(length,9.2,.55))
  for h in [1.9,5.5,7.2,16.9,18.5]:d('Continuous metal reveal',(0,h,.51),(length,.10,.12),'brushed aluminum',bevel=.008)
  d('Neon ribbon',(0,17.15,.43),(length,.12,.10),'neon violet',bevel=0)
  for h in [9.0,11.6,14.2]:d('LED panel row',(0,h,.40),(length-.04,1.8,.07),'neon violet',bevel=0)
  d('Window jamb',(length/2-.15,3.7,.35),(.08,3.7,.22),'brushed aluminum',bevel=.005)

for x,z,w,name in [(49,550,19,'MIRACLE MILE SHOPS'),(35,644,22,'planet hollywood'),(46,705,18,'MIRACLE MILE SHOPS')]:
 with context(name,origin=(x,.15,z),yaw=-math.pi/2):
  storefront(name,w,8)
  d('Marquee lintel',(0,8.9,1.0),(w+1.8,1.8,3.0),'brushed aluminum')
  label('Marquee lettering',name,(0,8.5,2.55),min(1.0,w/len(name)*1.3),'neon red')
  for u in range(16):
   xx=-w/2+.35+u*(w-.7)/15
   d('Canopy rib',(xx,7.91,1.1),(.05,.14,3),'neon white',bevel=0)
  if 'MIRACLE' in name:label('Red M','M',(0,11.1,.95),5,'neon red')

export(str(R/'build/film/storm'),'street-frontage')
