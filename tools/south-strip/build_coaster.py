"""OSM track alignment + photo-reconstructed elevation/inversion profile.
The OSM plan is surveyed; this vertical profile is an approximation, not CAD.
"""
import sys,json,math
sys.path.insert(0,'build/south-strip/python')
from pathlib import Path
import numpy as np
from geometry import Builder
OUT=Path('build/south-strip');plan=json.load(open(OUT/'track-plan.json'));tracks={t['id']:t for t in plan['tracks']}
# Way order comes directly from OSM relation 19531865.
order=[115662438,1035252213,1035252211,1035251668,1035251667,1035252212,1035252215,1035251772,646113820,646113823,1035252214,646113825]
# Respect the mapped layer ordering at the overlapping return runs. The station
# and final brake run stay below the layer-3 front run and the layer-4 loop.
heights={
 115662438:[12,12,12,12,12],1035252213:[12,61.8744],
 1035252211:[61.8744,39,22,17.9832,28,32,34,35,36,37,47,42,40,38],
 1035251668:[38,38,38,38,32,26,24],1035251667:[24,24],
 1035252212:[24,24,24,27,30,30,30,30,30],
 1035252215:[30,26,28,29,30,32,34,35,35,31,29,27,26,24,23,22,23,25,27,28,26,24],
 1035251772:[24,24,23.7,23,22],646113820:[22,21.5,20.5,20,19,18.5,18],
 646113823:[18,17.5,16.5,15.5,14.5,13.5,13],
 1035252214:[13,13,13,12.8,12.4,12],646113825:[12,12,12,12,12,12,12,12]
}
controls=[];stationindex=0
for wid in order:
 t=tracks.get(wid) or tracks.get(str(wid));pts=t['points'];ys=heights[wid]
 if len(ys)!=len(pts):raise Exception((wid,len(pts),len(ys)))
 for i,((x,z),y) in enumerate(zip(pts,ys)):
  if controls and i==0:continue
  if wid==1035252212 and i==2:
   # Offset the entry and exit of the vertical loop for car clearance.
   for theta in np.linspace(.0,math.tau,65):
    zz=1556.19-14.8*math.sin(theta)-10*theta/math.tau;xx=-75.40-4.0*theta/math.tau
    controls.append([xx,24+14.8*(1-math.cos(theta)),zz,0,0,1])
  if wid==1035252215 and i==1:
   # Heartline twist on the front run, then descending roll-out into the return.
   start=controls[-1][:3];end=[x,y,z]
   for q in np.linspace(.05,.95,25):
    pos=np.array(start)*(1-q)+np.array(end)*q;pos[1]+=20*math.sin(math.pi*q)**2
    roll=math.tau*(q*q*(3-2*q));controls.append([*pos,roll,0,0])
  if wid==646113825 and math.dist([x,z],plan['station'])<.1:stationindex=len(controls)
  controls.append([x,y,z,0,1 if wid==1035252213 else 0,0])
# Remove repeated seam, rotate to station; all points use world metres.
if math.dist(controls[-1][:3],controls[0][:3])<.1:controls.pop()
controls=controls[stationindex:]+controls[:stationindex]
# Cubic cardinal spline, dense enough for sub-metre arc-length resampling.
pts=[];rolls=[];lifts=[];loops=[]
for i,p in enumerate(controls):
 p0=np.array(controls[(i-1)%len(controls)][:3]);p1=np.array(p[:3]);p2=np.array(controls[(i+1)%len(controls)][:3]);p3=np.array(controls[(i+2)%len(controls)][:3]);n=max(3,int(np.linalg.norm(p2-p1)*3))
 # Keep chain lift and first drop crest at the published maximum height.
 for t in np.linspace(0,1,n,endpoint=False):
  m1=(p2-p0)/max(1e-8,np.linalg.norm(p2-p0))*min(np.linalg.norm(p1-p0),np.linalg.norm(p2-p1));m2=(p3-p1)/max(1e-8,np.linalg.norm(p3-p1))*min(np.linalg.norm(p2-p1),np.linalg.norm(p3-p2));v=(2*t**3-3*t*t+1)*p1+(t**3-2*t*t+t)*m1+(-2*t**3+3*t*t)*p2+(t**3-t*t)*m2;v[1]=min(61.8744,v[1]);pts.append(v)
  a=p[3];b=controls[(i+1)%len(controls)][3]
  if a>5 and b==0:b=math.tau
  rolls.append(a+(b-a)*t);lifts.append(max(p[4],controls[(i+1)%len(controls)][4]));loops.append(max(p[5],controls[(i+1)%len(controls)][5]))
pts.append(pts[0]);rolls.append(rolls[0]);lifts.append(lifts[0]);loops.append(loops[0]);lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))];length=float(lengths[-1]);ds=np.linspace(0,length,int(length/.55)+1);xyz=np.array([[np.interp(s,lengths,np.array(pts)[:,k]) for k in range(3)] for s in ds]);rolls=np.interp(ds,lengths,np.unwrap(rolls));lifts=np.interp(ds,lengths,lifts);loops=np.interp(ds,lengths,loops)
# Smooth sub-metre digitizing corners before deriving rail frames.
for _ in range(8):
 xyz[:-1]=(np.roll(xyz[:-1],1,axis=0)+2*xyz[:-1]+np.roll(xyz[:-1],-1,axis=0))/4
 xyz[-1]=xyz[0]
xyz[:,1]=12+(xyz[:,1]-12)*(61.8744-12)/(max(xyz[:,1])-12)
ds=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xyz,axis=0),axis=1))];length=float(ds[-1])
def unit(v):return v/max(1e-8,np.linalg.norm(v))
tangents=np.array([unit(xyz[(i+1)%(len(xyz)-1)]-xyz[(i-1)%(len(xyz)-1)]) for i in range(len(xyz)-1)]);tangents=np.vstack([tangents,tangents[0]])
# Rotation-minimizing frame, transported through vertical rather than world-up flipping.
right=unit(np.cross(tangents[0],[0,1,0]));frames=[]
banks=[]
for i,t in enumerate(tangents):
 prev=tangents[max(0,i-4)];nxt=tangents[min(len(tangents)-1,i+4)];angle=math.atan2(np.cross(prev,nxt)[1],np.dot(prev,nxt));banks.append(0 if loops[i]>.5 else np.clip(-angle*3,-.52,.52))
banks=np.convolve(np.pad(banks,(10,10),mode='edge'),np.ones(21)/21,mode='valid')
for i,t in enumerate(tangents):
 right=unit(right-t*np.dot(right,t))
 if loops[i]<=.5:right=unit(right*.85+unit(np.cross(t,[0,1,0]))*.15)
 up=unit(np.cross(right,t));angle=rolls[i]+banks[i]
 r=right*math.cos(angle)+up*math.sin(angle);u=up*math.cos(angle)-right*math.sin(angle);frames.append((r,u))
frames[-1]=frames[0];xyz[-1]=xyz[0]
B=Builder();B.property='coaster';B.source='track';N=len(xyz)
# Swept tubular rails; continuous seams and material batching.
for side in [-1,1,0]:
 rad=.09 if side else .20;offset=.65*side
 for i in range(N-1):
  r,u=frames[i];rr,uu=frames[i+1];c=xyz[i]+r*offset-u*(0 if side else .43);cc=xyz[i+1]+rr*offset-uu*(0 if side else .43)
  for j in range(8):
   a=j*math.tau/8;b=(j+1)*math.tau/8
   B.face('trackred',[c+rad*(r*math.cos(a)+u*math.sin(a)),c+rad*(r*math.cos(b)+u*math.sin(b)),cc+rad*(rr*math.cos(b)+uu*math.sin(b)),cc+rad*(rr*math.cos(a)+uu*math.sin(a))])
B.source='ties';B.detail=1
for i in range(0,N-1,3):
 r,u=frames[i];p=xyz[i];B.tube('trackred',p-r*.7,p+r*.7,.07,5);B.tube('trackred',p-u*.43,p-r*.65,.07,5);B.tube('trackred',p-u*.43,p+r*.65,.07,5)
# Cream bents and diagonal braces, with space below for paths and hotel doors.
B.source='supports';B.detail=0
for s in np.arange(24,length-45,14):
 i=int(s/length*(N-1));p=xyz[i];r,u=frames[i]
 if p[1]<9 or abs(u[1])<.4:continue
 for sign in [-1,1]:
  top=p+np.array([sign*2.1, -.6,0]);base=top.copy();base[1]=.32
  B.tube('support',base,top,.23,10);B.box('pedestal',(base[0],.4,base[2]),(1.4,.8,1.4))
 B.tube('support',p+[-2.1,-.6,0],p+[2.1,-.6,0],.23,8)
 if p[1]>22:
  B.tube('support',p+[-2.1,-1,0],p+[2.1,-p[1]+4,0],.12,6)
# Station parallel to actual OSM platform/tunnel. Local forward is first tangent.
B.source='station';origin=xyz[0];r,u=frames[0];t=tangents[0];r[1]=0;r=unit(r);t[1]=0;t=unit(t)
def S(x,y,z):return origin+r*x+np.array([0,y,0])+t*z
def deck(a,b,width,mat='paving'):
 a,b=np.array(a),np.array(b);v=b-a;side=unit(np.cross(v,[0,1,0]))*width/2;top=[a-side,a+side,b+side,b-side];B.face(mat,top,True)
 for i in range(4):j=(i+1)%4;B.face('concrete',[top[i],top[j],top[j]-[0,.3,0],top[i]-[0,.3,0]],True)
platform=[S(1.1,.6,-15),S(6.7,.6,-15),S(6.7,.6,11),S(1.1,.6,11)];B.face('paving',platform,True)
for i in range(4):j=(i+1)%4;B.face('concrete',[platform[i],platform[j],platform[j]-[0,.4,0],platform[i]-[0,.4,0]],True)
for z in np.arange(-14,12,4):
 for x in [-2.2,7]:B.tube('steel',S(x,.6,z),S(x,4.6,z),.12,8)
B.face('stationroof',[S(-2.5,4.8,-16),S(7.3,4.8,-16),S(7.3,4.8,12),S(-2.5,4.8,12)])
for z in np.arange(-14,12,2):
 B.tube('yellow',S(1,.68,z),S(1,.68,z+1),.045,6)
# Guard the platform perimeter; leave the staircase and boarding openings clear.
for x in [6.8,-2.3]:
 for z0,z1 in [(-15,-3),(3,11)]:
  B.tube('steel',S(x,1.7,z0),S(x,1.7,z1),.055,8)
  for z in np.arange(z0,z1+.1,2):B.tube('steel',S(x,.6,z),S(x,1.7,z),.045,6)
# Entrance route under the podium and stairs up to station. Stairs have smooth ramp collision.
bottom=np.array([-69.,.32,1464.]);top=S(6.7,.6,0);deck([-29,.32,1464],bottom,5);delta=top-bottom;run=math.hypot(delta[0],delta[2]);steps=math.ceil(delta[1]/.17);horizontal=delta.copy();horizontal[1]=0;normal=unit(np.cross(horizontal,[0,1,0]));yaw=math.atan2(horizontal[0],horizontal[2]);
for i in range(steps):
 q=(i+.5)/steps;c=bottom+horizontal*q;c[1]=bottom[1]+delta[1]*(i+1)/steps-.10;B.box('paving',c,(4.2,.2,run/steps+.015),False,yaw)
deck(bottom,top,4.2)
for sign in [-1,1]:
 a=bottom+normal*sign*2.2+[0,1.05,0];b=top+normal*sign*2.2+[0,1.05,0];B.tube('steel',a,b,.055,8)
 for q in np.linspace(0,1,16):p=bottom*(1-q)+top*q+normal*sign*2.2;B.tube('steel',p,p+[0,1.05,0],.045,6)
# Wayfinding at the street opening and at the boarding gate.
B.box('stationroof',(-29.2,3.6,1464),(.6,1.9,6));B.text('BIG APPLE COASTER',(-28.85,3.8,1464),.42,math.pi/2);B.text('ENTRANCE  /  STAIRS',(-28.84,3.1,1464),.26,math.pi/2)
B.text('THE BIG APPLE COASTER',list(S(6.8,3.5,-7)),.48,math.atan2(r[0],r[2]));B.text('BOARD HERE',list(S(5,1.7,1)),.28,math.atan2(t[0],t[2]))
B.save(OUT/'coaster.json');(OUT/'coaster-collision.json').write_text(json.dumps(B.solids['coaster'],separators=(',',':')))
# A single six-seat NYC taxi car, cloned three times at runtime: 18 seats total.
B=Builder();B.property='train';B.source='car'
B.box('yellow',(0,.45,0),(1.85,.6,4.3));B.box('black',(0,.18,0),(1.5,.35,4.1));B.box('yellow',(0,1.0,1.75),(1.85,.45,.7))
for x in [-.87,.87]:
 B.box('yellow',(x,.95,0),(.12,.55,4.2))
 for z in np.arange(-1.7,1.8,.35):B.box('black',(x*1.015,.81,z),(.025,.16,.17))
for z in [-1.2,0,1.2]:
 for x in [-.43,.43]:
  B.box('seat',(x,.87,z),(.72,.18,.68));B.box('seat',(x,1.20,z-.30),(.72,.70,.17));B.tube('steel',(x-.28,1.52,z-.32),(x-.28,1.12,z+.3),.055);B.tube('steel',(x+.28,1.52,z-.32),(x+.28,1.12,z+.3),.055);B.tube('steel',(x-.28,1.12,z+.3),(x+.28,1.12,z+.3),.055)
for z in [-1.6,1.6]:
 for x in [-.7,.7]:B.tube('black',(x-.1,.03,z),(x+.1,.03,z),.18,12)
B.save(OUT/'train.json')
exit=S(4.5,.65,0)
data=dict(points=[dict(s=round(float(s),4),position=[round(float(v),5) for v in p],right=[round(float(v),7) for v in r],up=[round(float(v),7) for v in u],lift=bool(lift)) for s,p,(r,u),lift in zip(ds,xyz,frames,lifts)],length=length,station=origin.tolist(),exit=exit.tolist(),entrance=[-24,.35,1464],access=[[-29,.32,1464],bottom.tolist(),top.tolist(),S(4.5,.6,0).tolist()],published=dict(height=61.8744,drop=43.8912,length=1456.0296,speed=29.95168),provenance='OSM relation 19531865 horizontal alignment; photo-reconstructed vertical profile and inversions; not an engineering survey')
(OUT/'route.json').write_text(json.dumps(data,separators=(',',':')))
print('TRACK',length,'metres; sampled',N,'frames; exit',exit,flush=True)
