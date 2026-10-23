"""Guard against guest-room recipes escaping a mapped exterior replacement."""
import sys
sys.path.insert(0,'tools/strip-landmarks')
from common import *
t=next(t for t in json.load(open('src/work/hotels/towers.json')) if t['id']=='horseshoe-resort')
p=footprint('way/27897921');a,b,c,d=t['linear'];ox,_,oz=t['origin']
for x,z in [(-8.4,-17.1),(8.4,-17.1),(-8.4,-5.1),(8.4,-5.1),(-3.7,5.15),(3.7,5.15)]:
 assert p.contains(Point(ox+a*x+b*z,oz+c*x+d*z)),(x,z)
assert t['floors']==20 and t['bays']==2 and t['firstGuestFloor']==4 and t['set']=='horseshoe'
print('Horseshoe room/stair envelopes contained; existing guest schedule preserved: PASS')
