"""Original gateway ribbons; city dimensions, aerial-fitted placement (not survey)."""
from common import *
CENTER=(1594.,-3445.3)
SPAN=42.672
HEIGHT=24.384
DIRECTIONS=[(.434,.901),(.990,-.143)]
def gateway(B):
 B.property='stratGateway-exterior';B.source='strat-gateway';B.detail=0
 def point(d,t,offset=0,side=0):
  x=(t-.5)*SPAN;y=2.5+(HEIGHT-.675-2.5)*4*t*(1-t)
  slope=(HEIGHT-.675-2.5)*4*(1-2*t)/SPAN
  norm=math.sqrt(1+slope*slope);dx=-slope/norm*offset;dy=offset/norm
  return (CENTER[0]+d[0]*(x+dx)-d[1]*side,y+dy,CENTER[1]+d[1]*(x+dx)+d[0]*side)
 for d in DIRECTIONS:
  for i in range(80):
   a=i/80;b=(i+1)/80
   rings=[[point(d,t,off,side)for off,side in [(-.675,-.23),(.675,-.23),(.675,.23),(-.675,.23)]]for t in [a,b]]
   for k in range(4):B.face('sg-blue-paint',[rings[0][k],rings[1][k],rings[1][(k+1)%4],rings[0][(k+1)%4]],True)
   # Lamp lenses are batched flat geometry, not runtime lights; reduced count is deliberate.
   for side in [-.24,.24]:
    for off in [-.46,0,.46]:
     t=(a+b)/2;dt=.0013
     B.face('sg-lens',[point(d,t-dt,off-.055,side),point(d,t+dt,off-.055,side),point(d,t+dt,off+.055,side),point(d,t-dt,off+.055,side)])
  for t in [0,1]:
   p=point(d,t);B.box('sg-pier',(p[0],1.25,p[2]),(1.55,2.5,1.55),True)
   B.box('sg-metal',(p[0],2.52,p[2]),(1.7,.12,1.7))
 # The open suspended sign is an original script approximation, not a traced logo.
 F=Frame(B,*CENTER,-math.atan2(.48,.877),y=0)
 for side in [.16]:
  def stroke(points,r=.095):
   # Smooth original control strokes. Open lettering reads in reverse from behind.
   smooth=[]
   for k in range(len(points)-1):
    q=[np.array(points[max(0,min(len(points)-1,i))],float)for i in [k-1,k,k+1,k+2]]
    for t in np.linspace(0,1,5,endpoint=False):
     v=.5*((2*q[1])+(-q[0]+q[2])*t+(2*q[0]-5*q[1]+4*q[2]-q[3])*t*t+(-q[0]+3*q[1]-3*q[2]+q[3])*t*t*t)
     smooth.append((v[0] if side>0 else -v[0],v[1],side))
   smooth.append((points[-1][0] if side>0 else -points[-1][0],points[-1][1],side))
   F.path('sg-pink',smooth,r,6)
  # Flowing L and V with smaller linked letter strokes and baseline flourish.
  paths=[
   [(-5.9,17.5),(-5.5,17.9),(-4.7,18),(-4.3,17.8),(-4.6,15),(-5,14.2),(-5.5,14.3),(-5.5,14.6),(-4.9,14.8),(-3.5,14.7)],
   [(-3.3,15.7),(-3.6,16),(-4,15.8),(-4.2,15.2),(-4,14.8),(-3.6,15),(-3.2,15.9),(-3.4,14.9),(-3.1,14.8),(-2.7,15.1)],
   [(-2.1,15.8),(-2.5,16),(-2.9,15.7),(-2.7,15.4),(-2.3,15.2),(-2.5,14.8),(-3,14.7),(-3.1,14.9),(-2.1,15)],
   [(-1.9,18.1),(-1.5,18.4),(-1,18.3),(-1.1,16),(-.9,14.5),(-.5,14.4),(.1,15.7),(1,18.2)],
   [(.1,15.2),(.9,15.7),(.8,16),(.4,16),(.1,15.5),(.2,14.9),(.6,14.7),(1.3,15)],
   [(2.2,15.8),(1.8,16),(1.4,15.7),(1.3,15.1),(1.6,14.8),(2.1,15.2),(2.4,16),(2,13.8),(1.5,12.9),(.8,12.8),(.4,13.1),(.7,13.6),(1.8,14.1),(2.6,14.7)],
   [(3.6,15.7),(3.3,16),(2.8,15.7),(2.7,15.1),(3,14.8),(3.4,15.2),(3.8,16),(3.6,14.9),(3.9,14.8),(4.3,15.1)],
   [(5,15.8),(4.7,16),(4.3,15.7),(4.5,15.4),(4.9,15.2),(4.7,14.8),(4.2,14.7),(4.1,14.9),(5.3,15.2)],
   [(-5.6,14.1),(-2,13.7),(.2,13.6)],
  ]
  for p in paths:stroke(p)
  F.text('CITY OF',(-4.7,18.65,side),.48,'sg-pale',back=side<0)
  for x,y,s in [(4.6,18.4,.42),(5.4,17.8,.24),(4.2,17.6,.2)]:
   stroke([(x-s*.22,y),(x,y+s),(x+s*.22,y),(x,y-s),(x-s*.22,y)],.04)
 # Thin suspension stays and the minimal support frame, clear above the roadway.
 for x in [-5.7,0,5.7]:F.tube('sg-metal',(x,18.8,0),(0,HEIGHT-.7,0),.035,6)
 for x in [-5.7,5.7]:F.tube('sg-metal',(x,14,0),(x*2.5,19.3,0),.03,6)
 return {'center':CENTER,'span':SPAN,'height':HEIGHT,'pierCenters':[point(d,t) for d in DIRECTIONS for t in [0,1]],'inferred':'Ribbon1.35x0.46m, piers1.55x1.55x2.5m; script and reduced lamp sampling approximate.'}
if __name__=='__main__':
 B=Meshes();meta=gateway(B);B.save_all();Path('build/city-exteriors/strat-gateway-geometry.json').write_text(json.dumps(meta,indent=2));print(sum(len(g['faces'])for g in B.groups.values()),'triangles')
