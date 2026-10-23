import sys,json
sys.path.insert(0,'build/south-strip/python')
from shapely.geometry import Polygon
from PIL import Image,ImageDraw
im=Image.new('RGB',(1000,1580),'white');d=ImageDraw.Draw(im)
for f in json.load(open('build/strip-survey/survey.json'))['buildings']:
 for rings in f['polygons']:
  p=Polygon([(x,-z) for x,z in rings[0]]);x,z=p.centroid.coords[0]
  if -400<x<0 and 1390<z<2050:
   pts=[((xx+405)*2.4,(zz-1380)*2.3) for xx,zz in p.exterior.coords];d.polygon(pts,outline='gray');d.text(((x+405)*2.4,(z-1380)*2.3),f['id'].split('/')[-1][-4:]+' / '+str(f['height']),fill='black')
im.save('build/south-strip/map.png')
