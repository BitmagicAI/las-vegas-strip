"""Bonfire exterior: original geometry from Feb2026 Street View; dimensions estimated."""
from common import *
KEY='bonfire';ID='way/1017043832'
def build(B):
 p=footprint(ID);B.property=KEY+'-exterior';B.source='podium/bonfire';B.detail=0
 B.shell(p,.08,4.15,'bf-stucco',roof=False)
 B.shell(p,4.15,5.05,'bf-band',roof=False)
 B.planar('bf-roof',p,4.85)
 # South face is the narrow end of the irregular mapped footprint.
 S=Frame(B,2044.879,1136.438,math.pi-math.atan2(.089,12.41),y=0)
 S.box('bf-base',(6.2,.28,-.035),(12.4,.4,.07))
 S.text('THE',(5.8,3.90,-.075),.21,'bf-red')
 S.text('BONFIRE',(6.2,3.05,-.075),.75,'bf-red')
 S.text('BAR  LIVE MUSIC  GRILL',(6.2,2.78,-.075),.14,'bf-gold')
 S.box('bf-sign',(6.2,1.98,-.055),(2.8,1.18,.08));S.text('LIVE MUSIC',(6.2,2.13,-.103),.28,'bf-gold');S.text('FOOD  POOL  GAMES',(6.2,1.74,-.103),.14,'bf-cream')
 for x in [.5,11.8]:
  S.box('bf-metal',(x,3.70,-.10),(.19,.21,.17))
  S.tube('bf-conduit',(x,.30,-.08),(x,4.22,-.08),.025,8)
 # West parking frontage: modest sign and recessed canopy over closed entry.
 W=Frame(B,2032.469,1136.349,math.pi/2+math.atan2(.234,33.607),y=0)
 W.text('BONFIRE',(4.2,3.40,-.08),.64,'bf-red');W.text('BAR  LIVE MUSIC  GRILL',(4.2,3.12,-.08),.13,'bf-gold')
 for x in [10.2,11.4]:
  W.box('bf-door',(x,1.30,-.07),(1.12,2.4,.10))
  for dx in [-.58,.58]:W.box('bf-metal',(x+dx,1.3,-.14),(.06,2.48,.08))
  W.tube('bf-metal',(x+.35,.95,-.24),(x+.35,1.45,-.24),.022,8)
 W.box('bf-metal',(10.8,2.53,-.13),(2.5,.08,.10))
 B.face('bf-awning',[W.p(9.15,2.70,-1.5),W.p(12.45,2.70,-1.5),W.p(12.45,3.50,0),W.p(9.15,3.50,0)])
 for x in [9.15,12.45]:B.face('bf-awning',[W.p(x,2.70,-1.5),W.p(x,3.50,0),W.p(x,2.70,0)])
 W.box('bf-concrete',(16.7,.12,-.7),(33.4,.18,1.4),True)
 for x in [7.8,13.8]:W.box('bf-bin',(x,.45,-.5),(.45,.8,.45))
 # Eastern return at the south-end notch, with raised service threshold.
 E=Frame(B,2044.879,1136.438,-math.pi/2+.0068,y=0)
 E.box('bf-door',(-2.2,1.88,-.08),(1.1,2.35,.10))
 for x in [-2.78,-1.62]:E.box('bf-metal',(x,1.88,-.15),(.07,2.42,.10))
 E.box('bf-metal',(-2.2,3.11,-.15),(1.23,.08,.10));E.tube('bf-metal',(-1.82,1.52,-.24),(-1.82,2.0,-.24),.023,8)
 E.box('bf-concrete',(-2.2,.40,-.75),(2.0,.78,1.5),True)
 # Four concrete treads are decorative; a continuous ramp supports traversal.
 for i in range(4):E.box('bf-concrete',(-2.2,.10*(i+1),-2.9+.4*i),(2,.20*(i+1),.40))
 B.upface('bf-concrete',[E.p(-3.2,.05,-3.1),E.p(-1.2,.05,-3.1),E.p(-1.2,.79,-1.5),E.p(-3.2,.79,-1.5)],True)
 for x in [-3.2,-1.2]:
  E.path('bf-black',[(x,1.02,-3.1),(x,1.80,-1.5),(x,1.80,-.1)],.035,8)
  for z in np.arange(-3.05,-.09,.22):
   h=.80 if z>=-1.5 else .05+(-3.1-z)/(-1.6)*.74
   E.tube('bf-black',(x,h,z),(x,h+1,z),.014,6)
 E.box('bf-sign',(-5.8,2.6,-.055),(3.2,2.1,.08));E.text('BONFIRE',(-5.8,2.8,-.10),.43,'bf-red');E.text('BAR & GRILL',(-5.8,2.3,-.10),.20,'bf-gold')
 # Parapet coping, roof equipment and surface-mounted service conduits.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):B.tube('bf-coping',(a[0],5.07,a[1]),(b[0],5.07,b[1]),.055,6)
 for x,z in [(2038,1110),(2053,1110),(2039,1124)]:
  B.box('bf-metal',(x,5.22,z),(2.5,.76,1.8))
  for dz in np.arange(-.7,.8,.18):B.box('bf-black',(x,5.61,z+dz),(2.2,.025,.05))
 for x in [2053.2,2056.4]:
  B.tube('bf-conduit',(x,.25,1128.82),(x,4.6,1128.82),.04,8)
  B.box('bf-metal',(x,1.65,1128.88),(.6,.82,.20))
 for z in [1104,1124]:W.tube('bf-conduit',(1136.349-z,.15,-.10),(1136.349-z,4.8,-.10),.05,8)
 return dict(key=KEY,name='Bonfire Naples',center=[2044,0,1119],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
