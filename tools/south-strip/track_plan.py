import json,math,xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image,ImageDraw
r=ET.parse('build/south-strip/nyny-map.osm').getroot();nodes={n.get('id'):n for n in r.findall('node')};ways={w.get('id'):w for w in r.findall('way')}
def point(n):return [6378137*math.radians(float(n.get('lon'))+115.173)*math.cos(math.radians(36.116)),-6378137*math.radians(float(n.get('lat'))-36.116)]
rel=next(e for e in r.findall('relation') if e.get('id')=='19531865');print('members',[(m.get('ref'),m.get('role')) for m in rel.findall('member')])
tracks=[]
for w in r.findall('way'):
 t={k.get('k'):k.get('v') for k in w.findall('tag')}
 if t.get('roller_coaster')=='track':tracks.append(dict(id=w.get('id'),tags=t,nodes=[n.get('ref') for n in w.findall('nd')],points=[point(nodes[n.get('ref')]) for n in w.findall('nd')]))
im=Image.new('RGB',(1300,1300),'#fafafa');d=ImageDraw.Draw(im)
def uv(p):return ((p[0]+300)*4,(p[1]-1400)*4)
for f in json.load(open('build/strip-survey/survey.json'))['buildings']:
 if f['id'].startswith('way/115661'):
  for rings in f['polygons']:
   pts=[uv((x,-z)) for x,z in rings[0]];d.polygon(pts,outline='#bbbbbb');d.text(pts[0],f['id'][-4:],fill='gray')
for j,t in enumerate(tracks):
 d.line([uv(p) for p in t['points']],fill=['red','blue','green','purple','orange'][j%5],width=3)
 for i,p in enumerate(t['points']):d.text(uv(p),f'{j}.{i}',fill='black')
 print(j,t['id'],t['tags'],t['points'])
station=point(nodes['9536189989']);print('station',station);d.ellipse([*[(x+v,y+v) for v in []]],fill='red') if False else None
lib=ways['115663314'];lp=[point(nodes[n.get('ref')]) for n in lib.findall('nd')];print('liberty',lp)
Path('build/south-strip/track-plan.json').write_text(json.dumps(dict(tracks=tracks,station=station,liberty=lp),indent=2));im.save('build/south-strip/track-plan.png')
