"""Original Hilton arrival canopy from official photograph and January 2025 Street View.
The footprint registration, dimensions and planting counts are inferred. Preserve the
existing guest entry kit, tower, pools, Conrad/Crockfords and Strip frontage.
"""
from common import *
BASE=Path('.bitmagic/city-exterior-backups/rw-arrival')
NAME='resortsWorldExterior-exterior'
MASK=(520.,-2179.,598.,-2142.)

def cut_triangle(t):
 """Subtract the vertical rectangle, retaining orientation and all outside pieces."""
 t=np.asarray(t,float)
 if t[:,0].max()<=MASK[0] or t[:,0].min()>=MASK[2] or t[:,2].max()<=MASK[1] or t[:,2].min()>=MASK[3]:return None
 remaining=list(t);out=[]
 for axis,bound,sign in [(0,MASK[0],-1),(0,MASK[2],1),(2,MASK[1],-1),(2,MASK[3],1)]:
  inside=[];outside=[]
  for p,q in zip(remaining,remaining[1:]+remaining[:1]):
   dp=(p[axis]-bound)*sign;dq=(q[axis]-bound)*sign
   (inside if dp<=1e-8 else outside).append(p)
   if dp*dq<0:
    v=p+(q-p)*dp/(dp-dq);inside.append(v);outside.append(v)
  for k in range(1,len(outside)-1):
   tri=np.array([outside[0],outside[k],outside[k+1]])
   if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-8:out.append(tri.tolist())
  remaining=inside
  if len(remaining)<3:return None
 return out

def clip_groups(groups):
 count=0
 for g in groups:
  if g['source']!='podium/way/972129019':continue
  old=g['vertices'];vertices=[];faces=[]
  for f in g['faces']:
   tri=[old[i]for i in f];pieces=cut_triangle(tri)
   if pieces is None:pieces=[tri]
   else:count+=1
   for t in pieces:
    n=len(vertices);vertices.extend(t);faces.append([n,n+1,n+2])
  g['vertices']=vertices;g['faces']=faces
 return count

def detail(B):
 B.property=NAME;B.source='rw-hilton-arrival';B.detail=0
 B.planar('rw-paving',box(*MASK),.235,True)
 # Keep the hotel's existing high-rise access kit and floor at y=.24.
 # Broad flat bronze roof, paired pale piers and recessed red/brown soffit.
 B.box('bronze',(559,8.05,-2160.5),(78,1.1,37),True)
 B.box('rw-flat-roof',(559,8.64,-2160.5),(77.6,.08,36.6))
 B.box('rw-red',(559,7.48,-2160.5),(77.6,.12,36.6))
 # Close the new cut at the retained podium; no unresearched lobby is opened.
 B.box('rw-stone',(559,10,-2141.9),(78,20,.2),True)
 for x in np.arange(523,598,4):
  B.box('rw-bronze',(x,3.55,-2142.04),(3.7,6.5,.06))
  B.box('rw-metal',(x-1.88,3.55,-2142.1),(.1,6.5,.07))
 for x in [524,546,570,594]:
  for dx in [-.62,.62]:B.box('rw-white',(x+dx,3.85,-2175.5),(.92,7.2,1.4),True)
  B.box('rw-metal',(x,1.05,-2175.5),(2.3,.18,1.55))
  B.box('rw-metal',(x,7.25,-2175.5),(2.6,.22,1.65))
 # Original coffer geometry, not image textures. No new scene lights.
 B.detail=1
 for x in np.arange(524,596,8):
  for z in [-2171,-2163,-2155,-2147]:
   B.box('bronze',(x,7.16,z),(7.1,.42,6.4))
   B.box('rw-white',(x,6.94,z),(6.55,.035,5.85))
   for dz in [-2.5,2.5]:B.box('rw-red',(x,6.88,z+dz),(6.15,.07,.12))
   for dx in [-2.9,2.9]:B.box('rw-red',(x+dx,6.88,z),(.12,.07,5))
   # Suspended square lanterns seen in the dated driveway panorama.
   if z in [-2171,-2155]:
    B.box('rw-metal',(x,6.35,z),(.07,1.1,.07))
    B.box('rw-red',(x,5.58,z),(1.05,.64,1.05))
    B.box('rw-white',(x,5.02,z),(.91,.45,.91))
    B.box('rw-metal',(x,4.76,z),(1.06,.08,1.06))
 B.detail=0
 # Planted island entirely outside the drive lanes, fitted to existing road island.
 B.source='rw-hilton-island'
 island=LineString([(552,-2193),(571,-2193)]).buffer(3.1,resolution=12)
 B.planar('rw-soil',island,.35)
 for q in parts(island):
  ps=list(q.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('rw-planter',[(a[0],.15,a[1]),(b[0],.15,b[1]),(b[0],.5,b[1]),(a[0],.5,a[1])],True)
 B.planar('rw-garden',island.buffer(-.3),.6)
 from hgv_sky_detail import palm
 for i,x in enumerate([552,558,565,571]):palm(B,x,-2193,8+i%2,i*.8)
 # Low benches stay on the island's south edge, off the vehicle lanes.
 for x in [555,568]:
  B.box('rw-white',(x,.68,-2189.4),(3.2,.18,.6),True)
  for dx in [-1.2,1.2]:B.box('rw-metal',(x+dx,.39,-2189.4),(.2,.4,.45),True)
 B.detail=0

def apply(B):
 clip_groups(B.groups.values());detail(B)

def build():
 old=json.loads((BASE/(NAME+'.json')).read_text());collision=json.loads((BASE/(NAME+'-collision.json')).read_text())
 clipped=clip_groups(old['meshes']);B=Meshes();detail(B);extra=B.solids[NAME];off=len(collision['vertices'])//3
 collision['vertices']+=extra['vertices'];collision['indices'] += [i+off for i in extra['indices']]
 (OUT/(NAME+'.json')).write_text(json.dumps({'meshes':old['meshes']+list(B.groups.values()),'labels':old['labels']+B.labels},separators=(',',':')))
 (OUT/(NAME+'-collision.json')).write_text(json.dumps(collision,separators=(',',':')))
 print({'oldPodiumTrianglesClipped':clipped,'addedTriangles':sum(len(g['faces']) for g in B.groups.values()),'addedCollisionTriangles':len(extra['indices'])//3})
if __name__=='__main__':build()
