"""Original underdeck fixture study from December 2022 garage Street View.
Fixture repetition and dimensions are inferred; no runtime lights are added.
"""
from common import *
from rio_amenities import AmenityMeshes
RECORD=Path('docs/project-records/royale-carnaval-refinement')

def build(B):
 B.property='royaleGarageRefinement-exterior';B.source='royale-garage-refinement';B.detail=0
 F=Frame(B,201.764,-491.77,math.atan2(1.394,51.853),y=.24);count=0
 # Below the five covered decks; avoid ramp on east side and retain 2.85m clearance.
 for level in range(5):
  y=3.2*level+2.94
  for x in [-8,2]:
   for z in [-20,-10,0,10,20]:
    F.box('rgr-housing',(x,y,z),(.18,.1,1.3))
    F.box('rgr-diffuser',(x,y-.055,z),(.13,.018,1.2))
    for dz in [-.5,.5]:F.tube('rgr-metal',(x,y+.05,z+dz),(x,3.2*(level+1)-.1,z+dz),.014,4)
    count+=1
 audit={'underdeckFixtures':count,'lowestFixtureClearanceM':2.876,'runtimeLightsAdded':0,'limitations':['Photograph supports rectangular fixtures but internal spacing/count is inferred.','No stair-core or internal-circulation survey.','Actual vehicle route still requires review.','Source only, not installed.']}
 (RECORD/'garage-geometry.json').write_text(json.dumps(audit,indent=2)+'\n');return audit
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
