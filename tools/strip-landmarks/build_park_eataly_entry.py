"""Original Eataly entrance detailing from cited supplier photographs.

The existing mapped hall and all collision are preserved. This is exterior
interpretation, not a surveyed entrance or a new public interior connection.
"""
from common import *
from shapely.affinity import affine_transform
BASE=Path('.bitmagic/city-exterior-backups/park-eataly-entry')

def build():
 old=json.loads((BASE/'park-exterior.json').read_text())
 B=Meshes();B.property='park-exterior';B.source='eataly-entry-detail';B.detail=1
 k=math.sqrt(.5)
 def P(u,v,y):return ((u+v)*k,y,(-u+v)*k)
 hall=affine_transform(footprint('way/115664840'),[k,-k,k,k,0,0])
 porch=affine_transform(footprint('way/1437033263'),[k,-k,k,k,0,0])
 u0,v0,u1,v1=hall.union(porch).bounds;mid=(u0+u1)/2
 def roof(u):return 16.1-abs(u-mid)*.23
 # Glazed gable closes the gap above the earlier rectangular glass front.
 for a,b in [(u0,mid),(mid,u1)]:
  B.face('park-window',[P(a,890.4,11.81),P(b,890.4,11.81),P(b,890.4,roof(b)-.23),P(a,890.4,roof(a)-.23)])
 for u in np.arange(u0+.6,u1,1.55):
  B.tube('steel',P(u,890.47,11.8),P(u,890.47,roof(u)-.25),.055,4)
 # Original slender cross bracing under the existing open roof projection.
 for v in [890.55,896.55]:
  for a,b in [(mid-7.9,mid),(mid,mid+7.9)]:
   B.tube('steel',P(a,v,12.0),P(b,v,roof(b)-.35),.075,6)
   B.tube('steel',P(a,v,roof(a)-.35),P(b,v,12.0),.075,6)
  B.tube('steel',P(mid-7.9,v,12.0),P(mid+7.9,v,12.0),.09,6)
 # Door leaves are visible closed exterior leaves, not a claimed playable portal.
 # Retain the original glass skin and collider; fine frames sit just in front.
 for center in [mid-5.6,mid-2.8,mid,mid+2.8,mid+5.6]:
  for du in [-1.23,0,1.23]:
   B.tube('eataly-bronze',P(center+du,890.56,.28),P(center+du,890.56,3.5),.045,4)
  for h in [.32,3.5]:B.tube('eataly-bronze',P(center-1.23,890.56,h),P(center+1.23,890.56,h),.05,4)
  for du in [-.17,.17]:B.tube('eataly-bronze',P(center+du,890.65,1.05),P(center+du,890.65,1.8),.025,6)
 # A restrained original interpretation of the supplier's looping stone bands.
 # Kept on the existing pedestrian forecourt, no road or collider replacement.
 court=box(mid-12.5,890.45,mid+12.5,902.0).difference(hall)
 world=affine_transform(court,[k,k,-k,k,0,0])
 B.planar('eataly-cobble-field',world,.246)
 bands=[]
 for row,v in enumerate([892.8,898.4,904.0]):
  for u in np.arange(mid-15+(row%2)*2.8,mid+16,5.6):
   circle=Point(u,v).buffer(2.8,resolution=32)
   bands.append(circle.boundary.buffer(.105,resolution=2))
 band=unary_union(bands).intersection(court)
 B.planar('eataly-cobble-band',affine_transform(band,[k,k,-k,k,0,0]),.249)
 # Small staggered original stone joints; no photographed pixels or new shader.
 for j,v in enumerate(np.arange(890.5,902,.28)):
  for i,u in enumerate(np.arange(mid-12.5-(j%2)*.14,mid+12.5,.28)):
   tile=box(u+.012,v+.012,u+.26,v+.26).intersection(court)
   if tile.is_empty:continue
   B.planar('eataly-cobble-'+str((i*17+j*7)%3),affine_transform(tile.difference(band),[k,k,-k,k,0,0]),.248)
 groups=list(B.groups.values())
 (OUT/'park-exterior.json').write_text(json.dumps({'meshes':old['meshes']+groups,'labels':old['labels']},separators=(',',':')))
 (OUT/'park-exterior-collision.json').write_bytes((BASE/'park-exterior-collision.json').read_bytes())
 report={'preservedGroups':len(old['meshes']),'preservedTriangles':sum(len(g['faces']) for g in old['meshes']),'addedTriangles':sum(len(g['faces']) for g in groups),'collision':'byte-identical','courtUV':list(court.bounds),'limitations':'Closed door detail only; no new interior portal. Dimensions estimated from existing mapped hall and photographs.'}
 Path('docs/project-records/park-eataly-entry/source.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':build()
