"""Original rooftop furniture, based on the official daylight tour (2026-11-07).
Counts/layout and metre-scale sizes are inferred; no public vertical access claim.
Existing shade/core/deck remain. Keep the X47 walking corridor clear.
"""
from common import Frame


def chair(B, x, z, yaw=0, tall=False):
 F=Frame(B,x,z,yaw,y=12.84)
 seat=.76 if tall else .46
 mat='baz-red' if tall else 'baz-shade'
 for a in [-.21,.21]:
  for b in [-.21,.21]:F.box('baz-metal',(a,seat/2,b),(.035,seat,.035))
 F.box(mat,(0,seat,0),(.49,.07,.49),True)
 for a in [-.22,.22]:F.box('baz-metal',(a,seat+.23,.23),(.035,.46,.035))
 for y in [seat+.18,seat+.32,seat+.45]:F.box(mat,(0,y,.23),(.45,.055,.035))
 if tall:
  for a in [-.14,0,.14]:F.box(mat,(a,seat+.31,.23),(.025,.29,.035))
  for a in [-.21,.21]:F.box('baz-metal',(a,.3,0),(.025,.025,.45))


def table(B,x,z,tall=False):
 F=Frame(B,x,z,y=12.84);h=1.06 if tall else .75
 w=1.8 if tall else .86
 for a in [-w*.36,w*.36]:
  for b in [-.28,.28]:F.box('baz-metal',(a,h/2,b),(.045,h,.045))
 # Solid support lies immediately below the visible separated slats.
 F.box('baz-metal',(0,h-.025,0),(w,.04,.72),True)
 for b in [-.3,-.15,0,.15,.3]:F.box('baz-metal',(0,h+.006,b),(w,.035,.125))


def rooftop(B,bounds):
 x0,z0,x1,z1=bounds
 # Dining islands keep the established centre route and service core clear.
 for x in [40.5,51]:
  for z in [180.5,199,204]:
   table(B,x,z)
   chair(B,x,z-.95,3.141592653589793)
   chair(B,x,z+.95)
 # Perimeter high tables and red stools, inside existing west guard/shade.
 for z in [184.5,189,193.5]:
  table(B,x0+1.55,z,True)
  for dz in [-.6,.6]:chair(B,x0+2.7,z+dz,1.5707963267948966,True)
 # Red square-mesh screen in front of retained structural glass guard.
 # Keep old guard collision unchanged; this is a decorative refinement.
 F=Frame(B,0,0,y=12.84)
 for a,b in [((x0+.09,z0),(x0+.09,z1))]:
  length=b[1]-a[1]
  for yy in [.13,.31,.49,.67,.85,1.03,1.12]:F.box('baz-red',(a[0],yy,(a[1]+b[1])/2),(.025,.025,length))
  count=round(length/.18)
  for j in range(count+1):F.box('baz-red',(a[0],.625,a[1]+length*j/count),(.025,.99,.025))
  for j in range(round(length/2)+1):F.box('baz-red',(a[0],.56,a[1]+length*j/round(length/2)),(.065,1.12,.065))
