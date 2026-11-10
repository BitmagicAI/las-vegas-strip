"""Original north-entry canopy study from Raiders2020 photo26 / Jan2025 Street View.
Dimensions are inferred. Existing mapped circulation is retained, including where it
conflicts with the reference terrace: this pass does not raise or replace that ground.
"""
from common import *
from shapely.geometry import shape

def build(B):
 B.source='allegiant-stadium/north-entry-canopy'
 features=json.loads(Path('build/geographic-strip/surface-layers.geojson').read_text())['features']
 region=box(-1020,2620,-838,2670)
 circulation=unary_union([shape(f['geometry']).intersection(region) for f in features if f['properties']['kind'] in ['road','sidewalk']]).buffer(.4)
 # Broad shallow curved roof, independently authored in world metres.
 cx=-929.09
 def z(x):return 2633+.0034*(x-cx)**2
 def roof(x,t):return (x,4.65+.42*math.sin(math.pi*t),z(x)+6*t)
 xs=np.linspace(cx-82,cx+82,83)
 for a,b in zip(xs,xs[1:]):
  for j in range(6):
   lo,hi=j/6,(j+1)/6
   B.upface('anc-roof',[roof(a,lo),roof(b,lo),roof(b,hi),roof(a,hi)],True)
   B.face('anc-soffit',[(x,y-.14,zz) for x,y,zz in [roof(a,hi),roof(b,hi),roof(b,lo),roof(a,lo)]])
  for t in [0,1]:
   B.face('anc-edge',[roof(a,t),roof(b,t),(b,4.37,z(b)+6*t),(a,4.37,z(a)+6*t)])
 # Thin roof ribs and a paired support rhythm. Omit supports that would obstruct
 # pre-existing roads or sidewalks rather than silently replacing circulation.
 supports=[];omitted=[]
 for x in np.linspace(cx-80,cx+80,21):
  B.path('anc-frame',[(xx,y+.025,zz) for xx,y,zz in [roof(x,j/8) for j in range(9)]],.035,5)
  for t in [.08,.92]:
   zz=z(x)+6*t;p=Point(x,zz).buffer(.28)
   if p.intersects(circulation):
    omitted.append([x,zz]);continue
   top=roof(x,t)[1]-.12
   B.box('anc-frame',(x,top/2,zz),(.18,top,.18),True);supports.append([x,zz])
 assert supports
 report={'scope':'Curved North Entry canopy only; no terrace or interior access claim','dimensionsInferred':{'widthM':164,'depthM':6,'edgeRoofM':4.65,'crownM':5.07},'supports':supports,'omittedSupportsAtMappedCirculation':omitted,'minimumRoofClearanceM':4.37,'remaining':['Exact canopy registration/section dimensions require further survey.','Raised terrace, paired stairs and Raider Image store remain absent: inferred terrace footprint conflicts with mapped circulation; roads retained.','Ground doors, broad north glazing/frame, signs and landscaping remain incomplete.']}
 p=Path('docs/project-records/allegiant-terrace-refinement/canopy-geometry.json');p.write_text(json.dumps(report,indent=2)+'\n')
 return report
