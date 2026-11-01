"""Original historical arrival pavilion; December 2022 references, inferred sections.
Keep the existing 17 x 28 m canopy envelope and drive; median/entry layout deferred.
"""
from common import *

def arrival(B):
 B.property='mirageArrival-exterior';B.source='mirage-arrival';B.detail=0
 x=-43.;z=-587.7;eave=6.35
 # Pale fascia grid, with the roadway remaining completely open below it.
 for xx in [x-8.15,x+8.15]:B.box('ma-cream-paint',(xx,eave-.25,z),(.7,.5,28),True)
 for zz in [z-13.65,z,z+13.65]:B.box('ma-cream-paint',(x,eave-.25,zz),(17,.5,.7),True)
 for xx in [x+7.0]:
  for zz in [z-12,z+12]:
   B.box('ma-stone',(xx,2.98,zz),(.9,5.96,.9),True)
   B.box('ma-stone-cap',(xx,.22,zz),(1.08,.44,1.08),True)
   B.box('ma-stone-cap',(xx,5.87,zz),(1.12,.28,1.12))
   # Original irregular stone courses, no reference texture copied.
   rng=random.Random(int((xx+1000)*100+zz))
   for side in range(4):
    for j in range(14):
     yy=.48+j*.38;w=.38+rng.random()*.15
     for k in [-1,1]:
      offset=k*.22+rng.uniform(-.035,.035)
      if side<2:B.box('ma-stone-light' if (j+side+k)%3 else 'ma-stone-dark',(xx+offset,yy,zz+(-1 if side==0 else 1)*.458),(w,.31,.025))
      else:B.box('ma-stone-light' if (j+side+k)%3 else 'ma-stone-dark',(xx+(-1 if side==2 else 1)*.458,yy,zz+offset),(.025,.31,w))
 # Two low hip pavilions with open grid gaps; exact roof subdivision is inferred.
 for cz in [z-6.65,z+6.65]:
  hw=7.45;hd=5.65;rise=2.15;ridge=hw-hd
  a=(x-hw,eave,cz-hd);b=(x+hw,eave,cz-hd);c=(x+hw,eave,cz+hd);d=(x-hw,eave,cz+hd)
  l=(x-ridge,eave+rise,cz);r=(x+ridge,eave+rise,cz)
  faces=[[a,b,r,l],[b,c,r],[c,d,l,r],[d,a,l]]
  for face in faces:
   B.upface('ma-roof-shingle',face,True)
   B.face('ma-timber',[(px,py-.09,pz)for px,py,pz in reversed(face)])
  # Roof course lines are thin original timber/shingle strips, batched geometry.
  for t in np.linspace(.03,.95,15):
   for u,v,topu,topv in [(a,b,l,r),(d,c,l,r),(a,d,l,l),(b,c,r,r)]:
    aa=np.array(u)*(1-t)+np.array(topu)*t;bb=np.array(v)*(1-t)+np.array(topv)*t
    aa[1]+=.025;bb[1]+=.025;B.tube('ma-roof-edge',aa,bb,.025,4)
  # Exposed underside rafters along all four roof planes.
  for side in [-1,1]:
   for xx in np.linspace(x-hw+.3,x+hw-.3,29):
    topx=min(x+ridge,max(x-ridge,xx));B.tube('ma-rafter',(xx,eave-.16,cz+side*hd),(topx,eave+rise-.16,cz),.075,4)
   for zz in np.linspace(cz-hd+.3,cz+hd-.3,19):
    B.tube('ma-rafter',(x+side*hw,eave-.16,zz),(x+side*ridge,eave+rise-.16,cz),.075,4)
  for xx in [x-hw,x+hw]:B.box('ma-timber',(xx,eave-.13,cz),(.18,.26,hd*2))
  for zz in [cz-hd,cz+hd]:B.box('ma-timber',(x,eave-.13,zz),(hw*2,.26,.18))
  B.tube('ma-roof-edge',l,r,.12,6)
 # Short pale joists cross the open strips between pavilion roofs and fascia.
 for xx in np.arange(x-7.5,x+8,.85):
  for zz,depth in [(z,1.8),(z-13.05,1.2),(z+13.05,1.2)]:B.box('ma-cream-paint',(xx,eave-.15,zz),(.18,.3,depth))
 return {'envelope':[17,28],'eaveM':eave,'ridgeM':eave+rise,'columns':[[xx,zz]for xx in [x+7]for zz in [z-12,z+12]],'inferred':'Retains installed footprint; sections, roof subdivisions and stone courses estimated. Reference median and exact hotel entrance connection deferred to preserve existing roads and interior ownership.'}
if __name__=='__main__':
 B=Meshes();meta=arrival(B);B.save_all();Path('build/city-exteriors/mirage-arrival-geometry.json').write_text(json.dumps(meta,indent=2));print(sum(len(g['faces'])for g in B.groups.values()),'triangles')
