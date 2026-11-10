"""Scoped four-lift detail build; collision must remain byte-identical."""
from common import *
import pedestrian_lifts, harmon_east_lift
for site in pedestrian_lifts.SITES+[None]:
 key=site['key'] if site else harmon_east_lift.KEY
 collision=OUT/(key+'-exterior-collision.json');before=collision.read_bytes()
 B=Meshes()
 if site:pedestrian_lifts.exterior(B,site)
 else:harmon_east_lift.exterior(B)
 for label in B.labels:label['detail']=0
 B.save_all()
 changed=collision.read_bytes()!=before
 if changed:collision.write_bytes(before)
 assert not changed,'Collision changed; original restored: '+key
 print(key,sum(len(g['faces']) for g in B.groups.values()),'faces; collision byte-identical')
