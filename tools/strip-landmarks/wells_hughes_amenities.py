"""Original southwest garden paths and west pergola study; tower preserved.
Palm species/source remains unresolved: no substitute broadleaf trees installed.
"""
from common import *
from rio_amenities import AmenityMeshes
RECORD=Path('docs/project-records/hughes-center-amenities');Y=.14

def build(B):
 B.property='wellsHughesAmenities-exterior';B.source='wells-hughes-amenities';B.detail=0
 tower=footprint('way/156624462')
 site=Polygon([(1440,-349),(1453,-355),(1455,-338),(1460,-326),(1478,-306),(1490,-305),(1490,-296),(1449,-296),(1443,-315)]).difference(tower.buffer(.4))
 lines=[LineString([(1447,-343),(1454,-321),(1468,-305),(1487,-300)]),LineString([(1446,-310),(1473,-310)]),LineString([(1455,-298),(1455,-326)])]
 paths=unary_union([l.buffer(.95,cap_style=2,join_style=2) for l in lines]).intersection(site)
 B.planar('wha-lawn',site.difference(paths),Y)
 B.planar('wha-path',paths,Y+.025,True)
 # Two flat slatted shade structures visible along the western tower apron.
 pergolas=[]
 for x,z in [(1449,-341),(1452,-329)]:
  F=Frame(B,x,z,math.radians(-18),y=Y);p=F.poly([(-2.7,-3.6),(2.7,-3.6),(2.7,3.6),(-2.7,3.6)])
  if p.intersects(tower.buffer(.4)):continue
  B.planar('wha-paving',p,Y+.04,True)
  for u in [-2.5,2.5]:
   for v in [-3.4,3.4]:F.box('wha-metal',(u,1.65,v),(.15,3.3,.15),True)
   F.box('wha-metal',(u,3.25,0),(.18,.2,7.2))
  for v in np.arange(-3.5,3.51,.32):F.box('wha-slat',(0,3.4,float(v)),(5.5,.09,.12))
  for u in [-1.8,1.8]:
   F.box('wha-seat',(u,.48,0),(.65,.14,2.2),True)
   for v in [-.8,.8]:F.box('wha-metal',(u,.21,v),(.42,.42,.08))
  pergolas.append([x,z])
 # Low clipped hedge near the building edge; interrupted by the crossing path.
 hedge=tower.buffer(1.9).difference(tower.buffer(1.15)).intersection(site).difference(paths.buffer(.45))
 B.shell(hedge,Y,Y+.7,'wha-hedge',solid=True)
 routes=[]
 for i,l in enumerate(lines):
  clipped=l.intersection(site.buffer(-.05))
  for k,s in enumerate([clipped] if clipped.geom_type=='LineString' else clipped.geoms):
   if s.length>1:routes.append({'name':f'wells-garden-path-{i}-{k}','points':[[x,Y+.025,z] for x,z in s.coords]})
 audit={'gardenAreaM2':site.area,'pathAreaM2':paths.area,'pergolas':pergolas,'limitations':['Uninstalled study, approximate aerial and Dec2024StreetView layout.','Road and neighboring parcel clearance requires installed review.','Palm trees with white lower trunks not substituted by available broadleaf sources; remain unfinished.','Public lobby, exact crown proportions and east patio remain unchanged.','No terrain/road regeneration.']}
 (RECORD/'wells-geometry.json').write_text(json.dumps(audit,indent=2)+'\n');(RECORD/'wells-routes.json').write_text(json.dumps(routes,indent=2)+'\n');return audit
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
