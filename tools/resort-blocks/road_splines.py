"""Endpoint-preserving Hermite centreline and monotone grade interpolation."""
import numpy as np

def hermite(t,a,b,ma,mb):
 return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*ma+(-2*t**3+3*t*t)*b+(t**3-t*t)*mb

def smooth_grade(x,knots):
 for (a,ya),(b,yb) in zip(knots,knots[1:]):
  if x<=b:
   t=np.clip((x-a)/(b-a),0,1)
   return float(hermite(t,ya,yb,0,0))
 return knots[-1][1]

def sample_road(points,spacing=.8):
 p=np.array(points,float);keep=np.r_[True,np.linalg.norm(np.diff(p[:,[0,2]],axis=0),axis=1)>1e-5];p=p[keep]
 if len(p)<2:return p.tolist()
 d=np.linalg.norm(np.diff(p[:,[0,2]],axis=0),axis=1);s=np.r_[0,np.cumsum(d)];m=np.zeros_like(p)
 slopes=np.diff(p,axis=0)/d[:,None];m[0]=slopes[0];m[-1]=slopes[-1]
 for i in range(1,len(p)-1):
  m[i]=(p[i+1]-p[i-1])/(s[i+1]-s[i-1])
  left,right=slopes[i-1,1],slopes[i,1]
  m[i,1]=0 if left*right<=0 else 2*left*right/(left+right)
 # Flat tangency at road ends eases onto common junction/bridge landings.
 m[0,1]=m[-1,1]=0
 out=[]
 for i,length in enumerate(d):
  for t in np.linspace(0,1,max(2,int(np.ceil(length/spacing))+1))[:-1]:out.append(hermite(t,p[i],p[i+1],m[i]*length,m[i+1]*length).tolist())
 out.append(p[-1].tolist());return out
