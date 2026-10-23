"""South Tower Pool Garden, February2026 official pool map.
Level10 is documented; physical elevation34m and map registration are estimates.
"""
import math
import numpy as np
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from common import Frame

def courtyard(B):
 B.source='venezia-pool-garden';B.detail=0
 y=34.
 def w(x,z):return (278+(x-245)*.121,-505-(z-348)*.121)
 def poly(q):return Polygon([w(*p) for p in q])
 def slab(mat,p,lo,hi,solid=True):B.shell(p,lo,hi,mat,roof=False,solid=solid);B.planar(mat,p,hi,solid)
 deck=poly([(245,348),(835,348),(835,728),(245,728)])
 # Scalloped rectangular central pool, octagonal dry island, three satellite spas.
 main=poly([(482,382),(580,382),(580,408),(606,408),(606,537),(580,537),(580,565),(569,565),(569,610),(493,610),(493,565),(482,565),(482,537),(456,537),(456,408),(482,408)])
 island=poly([(521,448),(542,448),(557,463),(557,486),(542,501),(521,501),(505,486),(505,463)])
 main=main.difference(island)
 pools=[main,poly([(318,383),(367,383),(367,448),(318,448)]).buffer(.45).buffer(-.45),poly([(318,502),(367,502),(367,595),(318,595)]).buffer(.45).buffer(-.45),poly([(493,655),(568,655),(568,700),(591,726),(470,726),(493,700)])]
 wet=unary_union(pools)
 slab('sandstone',deck.difference(wet),17.08,y)
 for p in pools:
  B.planar('water',p,y-.18);B.planar('blue',p,y-1.1,True)
  B.shell(p,y-1.1,y-.18,'tile',roof=False)
  slab('ivory',p.buffer(.30).difference(p),y-.1,y+.10)
 # Octagon in centre is masonry, distinct from water basin.
 slab('ivory',island,y-.15,y+.13)
 # Broad axial garden paths and regularly clipped beds from mapped partitions.
 for px in [428,651]:
  x,z=w(px,490);T=Frame(B,x,z,y=y);T.box('tile',(0,.02,0),(1.05,.04,34))
 for xa,xb,za,zb in [(250,307,354,435),(250,307,515,586),(676,816,355,376),(676,816,592,622)]:
  bed=poly([(xa,za),(xb,za),(xb,zb),(xa,zb)])
  slab('ivory',bed,y,y+.44)
  B.detail=1
  a,b,c,d=bed.bounds
  for x in np.arange(a+.3,c,.65):
   for z in np.arange(b+.3,d,.65):
    B.sphere('foliage',(x,y+.62,z),.42,6,4,scale=(1,.85,1))
  B.detail=0
 # Chair groups in the open paved banks; dimensions are gameplay-scale estimates.
 B.detail=1
 for xa,xb,za,zb in [(400,412,397,454),(400,412,507,557),(625,637,398,453),(625,637,503,560),(677,756,398,452),(677,756,503,560),(267,476,663,674),(582,607,663,674)]:
  for px in np.arange(xa,xb,10):
   for pz in np.arange(za,zb,21):
    x,z=w(px,pz);T=Frame(B,x,z,y=y)
    if wet.buffer(.8).contains(Point(x,z)):continue
    T.box('white',(0,.4,0),(.68,.10,1.55))
    B.face('white',[T.p(-.34,.43,-.7),T.p(.34,.43,-.7),T.p(.34,.94,-1.12),T.p(-.34,.94,-1.12)])
    for s in [-1,1]:T.tube('blackiron',(s*.28,.06,.6),(s*.28,.38,.6),.035,5);T.tube('blackiron',(s*.28,.06,-.6),(s*.28,.38,-.6),.035,5)
 B.detail=0
 # Perimeter garden balustrade; upper tower walls remain untouched.
 a,b,c,d=deck.bounds
 for aa,bb in [((a,b),(c,b)),((a,d),(c,d))]:
  B.tube('ivory',(aa[0],y+1.08,aa[1]),(bb[0],y+1.08,bb[1]),.11,6)
  B.detail=1
  for xx in np.arange(a+.2,c,.55):B.lathe('ivory',(xx,aa[1]),[(y,.12),(y+.18,.09),(y+.5,.15),(y+.85,.07),(y+1,.11)],6)
  B.detail=0
 return dict(eye=[287,37,-538],target=[324,35,-520])
