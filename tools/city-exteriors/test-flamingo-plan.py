"""Guard against guest-room recipes escaping a mapped exterior replacement."""
import sys
sys.path.insert(0,'tools/strip-landmarks')
from common import *
t=next(t for t in json.load(open('src/work/hotels/towers.json')) if t['id']=='flamingo-north')
p=footprint('way/115766962');a,b,c,d=t['linear'];ox,_,oz=t['origin']
for x,z in [(-7.0,-77.1),(7.0,-77.1),(-7.0,-5.1),(7.0,-5.1),(-3.7,5.15),(3.7,5.15)]:
 assert p.contains(Point(ox+a*x+b*z,oz+c*x+d*z)),(x,z)
assert t['floors']==18 and t['bays']==12 and t['firstGuestFloor']==4 and t['set']=='flamingo'
print('Flamingo room/stair envelopes contained; existing guest schedule preserved: PASS')
