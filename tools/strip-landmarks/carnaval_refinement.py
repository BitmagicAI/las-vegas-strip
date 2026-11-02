"""Original overhead rig study, official photo plus April 2025 Street View.
Equipment functions and dimensions inferred; not a surveyed fit-out.
"""
from common import *
from rio_amenities import AmenityMeshes
RECORD=Path('docs/project-records/royale-carnaval-refinement')
CX,CZ=100.515,-303.66

def build(B):
 B.property='carnavalRefinement-exterior';B.source='carnaval-refinement';B.detail=0
 F=Frame(B,CX,CZ,0,y=0)
 # Suspended central purple fascia, clear of staff and guest circulation below.
 for j in range(16):
  a=j*math.tau/16;b=(j+1)*math.tau/16
  def p(r,t,y):return F.p(r*math.cos(t),y,r*math.sin(t))
  B.face('ccr-purple',[p(3.15,a,3.9),p(3.15,b,3.9),p(3.15,b,4.65),p(3.15,a,4.65)])
  for y in [3.88,4.67]:B.tube('ccr-metal',p(3.18,a,y),p(3.18,b,y),.035,6)
  if j%4==0:B.tube('ccr-metal',p(3.1,a,4.65),p(3.1,a,7.3),.035,6)
 # Square open metal cages visible near the columns; keep them above head height.
 for j in range(6):
  a=(j+.5)*math.tau/6
  G=Frame(B,CX+9.4*math.cos(a),CZ+9.4*math.sin(a),-a,y=0)
  for y in [3.35,4.8]:
   G.path('ccr-dark',[(-.65,y,-.5),(.65,y,-.5),(.65,y,.5),(-.65,y,.5),(-.65,y,-.5)],.035,6)
  for x in [-.65,.65]:
   for z in [-.5,.5]:G.tube('ccr-dark',(x,3.35,z),(x,5.15,z),.03,6)
  for x in np.arange(-.52,.6,.13):
   for z in [-.5,.5]:G.tube('ccr-dark',(float(x),3.35,z),(float(x),4.8,z),.009,4)
  for y in np.arange(3.48,4.8,.16):
   for z in [-.5,.5]:G.tube('ccr-dark',(-.65,float(y),z),(.65,float(y),z),.009,4)
 # Rectangular suspended panels supported by the existing radial roof structure.
 for a in [math.pi*.65,math.pi,math.pi*1.35]:
  G=Frame(B,CX+7.4*math.cos(a),CZ+7.4*math.sin(a),-a,y=0)
  G.box('ccr-panel',(0,4.5,0),(1.4,1.2,.12))
  for x in [-.55,.55]:G.tube('ccr-metal',(x,5.1,0),(x,5.9,0),.02,6)
 audit={'meshCages':6,'suspendedPanels':3,'centralFasciaRadiusM':3.15,'minimumAddedHeightM':3.315,'runtimeLightsAdded':0,'limitations':['Rig spacing, dimensions and equipment functions inferred from photographs.','April 2025 Street View corroborates hanging panels/cages; full interior rig layout not surveyed.','Street-side kiosk and exact column veining remain outside this refinement.','Source only, installed view and circulation acceptance pending.']}
 (RECORD/'carnaval-geometry.json').write_text(json.dumps(audit,indent=2)+'\n');return audit
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
