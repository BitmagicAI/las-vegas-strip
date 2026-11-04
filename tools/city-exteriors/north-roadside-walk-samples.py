"""Reproducible approach/courtyard grids for existing support tests, in metres."""
import math,json
from pathlib import Path
out=Path('build/city-exteriors');out.mkdir(exist_ok=True)
def write(name,origin,yaw,xs,zs):
 c,s=math.cos(yaw),math.sin(yaw)
 points=[[origin[0]+c*x+s*z,.04,origin[1]-s*x+c*z] for x in xs for z in zs]
 (out/(name+'-samples.json')).write_text(json.dumps(points,separators=(',',':')))
write('ihop',(1777.5765,-3746.975),math.atan2(18.424,9.181),[-4,-2,0,2,4,6,8],[-3,-2.5,-2,-1.5])
write('oasis',(1799.532,-3798.11),math.atan2(10.809,5.674),[1.2,2.4,3.6,4.8,6],[-2+i*1.25 for i in range(65)])
