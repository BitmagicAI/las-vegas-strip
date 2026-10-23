import sys,numpy as np
sys.path.insert(0,'tools/resort-blocks')
from road_splines import sample_road,smooth_grade
p=[[0,.135,0],[10,2,2],[30,6,10],[50,6,15]]
s=np.array(sample_road(p));assert np.allclose(s[0],p[0]) and np.allclose(s[-1],p[-1]);assert np.min(s[:,1])>=.135-1e-9 and np.max(s[:,1])<=6+1e-9
assert np.max(np.linalg.norm(np.diff(s[:,[0,2]],axis=0),axis=1))<1
for a,b in [(-350,-310),(-349,-313),(-297,-266),(-250,-222)]:
 knots=[(a,0),(b,3.4)];epsilon=.001
 assert abs(smooth_grade(a+epsilon,knots)/epsilon)<.001
 assert abs((3.4-smooth_grade(b-epsilon,knots))/epsilon)<.001
print('Spline endpoints, sample spacing, bounded height and flat ramp tangency passed')
