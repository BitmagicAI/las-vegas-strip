"""Guard against guest-room recipes escaping a mapped exterior replacement."""
import sys
sys.path.insert(0,'tools/strip-landmarks')
from common import *
t=next(t for t in json.load(open('src/work/hotels/towers.json')) if t['id']=='caesars-palace')
p=footprint('way/134944648');a,b,c,d=t['linear'];ox,_,oz=t['origin']
for x,z in [(-9.7,-53.1),(9.7,-53.1),(-9.7,-5.1),(9.7,-5.1),(-3.7,5.15),(3.7,5.15)]:
 assert p.contains(Point(ox+a*x+b*z,oz+c*x+d*z)),(x,z)
assert t['floors']==24 and t['bays']==8 and t['firstGuestFloor']==3 and t['set']=='caesars'
print('Palace room/stair envelopes contained; existing guest schedule preserved: PASS')
