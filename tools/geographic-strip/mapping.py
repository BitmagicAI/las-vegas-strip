"""Reproducible horizontal fitting; vertical storeys and source files are preserved."""
import json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'build/geographic-strip/before'
# source X/Z envelope, OSM target X/Z envelope, plan rotation, source features
RECIPES={
 'bellagio':([-179,-113,-140,77],[-321,204,-270,439],0,['way/25723909']),
 'paris':([41,-138,216,54],[35,327,291,523],0,['way/33974140','way/27831697']),
 'eiffel':([46.3,-85.7,139.7,7.7],[35,361,114,440],0,['way/27831699']),
 'caesars':([-213.2,-296.25,-43.4,-180.3],[-436,-249,-77,111],0,['way/115672893','way/34068416']),
 'cosmopolitan':([-209,169,-21,270],[-365,605,-68,732],0,['way/27897905','way/472669744','way/134795273']),
 'flamingo':([84,-259,200,-215],[29,-157,241,63],0,['way/116761428']),
 'horseshoe':([95.7,-147.12,127.62,-89.37],[85,273,212,299],math.pi/2,['way/27897921']),
 'planet-hollywood':([117.74,174.27,173.26,265.77],[120,561,187,758],0,['way/134921373','way/134921371','way/134921379']),
 'aria':([-453.35,338.5,-225,500.5],[-498,793,-235,1061],0,['way/52175576','way/134930088','way/134930089','way/134930090','way/134930091','way/134930092']),
 'vdara':([-356.35,187.01,-261.65,299.18],[-516,696,-382,768],math.pi/2,['relation/20214578']),
 'waldorf':([-140,534,-38.9,621.25],[-156,1050,-73,1126],0,['way/52194829']),
 'crystals':([-282.35,322.73,-21.79,480.55],[-237,824,-33,1014],0,['way/52134608']),
 'veer-east':([-143,439.4252,-107,467.4252],[-137,932,-107,982],0,['way/52134834']),
 'veer-west':([-207,408.5748,-171,436.5748],[-195,930,-165,982],0,['way/52134835']),
 # Dry south forecourt. The original (-51,290) center was inside Bellagio Lake.
 'sanctuary':([-58,-16,-26,16],[-76,524,-44,556],0,[]),
 # Small mission depots are placed off the through carriageways.
 'medicine':([44,-123,70,-103],[255,168,281,188],0,[]),
 'weapons':([55,81,81,103],[327,496,353,518],0,[]),
 'ammo':([-89,115,-63,137],[-378,576,-352,598],0,[]),
}

def recipe(key):
 old,new,yaw,ids=RECIPES[key];ox=(old[0]+old[2])/2;oz=(old[1]+old[3])/2;nx=(new[0]+new[2])/2;nz=(new[1]+new[3])/2;c=math.cos(yaw);s=math.sin(yaw)
 wx=abs(c)*(old[2]-old[0])+abs(s)*(old[3]-old[1]);wz=abs(s)*(old[2]-old[0])+abs(c)*(old[3]-old[1]);sx=(new[2]-new[0])/wx;sz=(new[3]-new[1])/wz
 a,b,c,d=sx*c,sx*s,-sz*s,sz*c
 return dict(key=key,source=old,target=new,osm=ids,linear=[a,b,c,d],translation=[nx-a*ox-b*oz,nz-c*ox-d*oz],heightScale=1)
TRANSFORMS={k:recipe(k) for k in RECIPES}

def point(p,key):
 t=TRANSFORMS[key];a,b,c,d=t['linear'];x,z=p[0],p[2]
 return [a*x+b*z+t['translation'][0],p[1],c*x+d*z+t['translation'][1]]
def vector(p,key):
 a,b,c,d=TRANSFORMS[key]['linear'];return [a*p[0]+b*p[2],p[1],c*p[0]+d*p[2]]
def yaw(angle,key):
 v=vector([math.sin(angle),0,math.cos(angle)],key);return math.atan2(v[0],v[2])
def owner(name,p=None,default=None):
 n=name.lower()
 if 'sanctuary' in n or n in ('spawn','haven'):return 'sanctuary'
 if 'medicine supply' in n or 'north_garage' in n:return 'medicine'
 if 'weapons supply' in n or 'south_casino' in n:return 'weapons'
 if 'ammo supply' in n or 'ammo_cache' in n:return 'ammo'
 if 'food supply' in n:return 'bellagio'
 if 'colosseum' in n or 'forum' in n:return 'caesars'
 if 'arc de triomphe' in n:return 'paris'
 if 'eiffel' in n or 'paris_lift' in n or 'paris_deck' in n:return 'eiffel'
 match=re.search(r'paris (\d{5})',n)
 if match and 21490<=int(match[1])<=27150:return 'eiffel'
 if 'crystals / veer access' in n:return 'crystals'
 if 'veer' in n:
  return 'veer-east' if 'east' in n else 'veer-west' if 'west' in n else ('veer-east' if p is not None and p[0]>-157 else 'veer-west')
 for token,key in [('planet hollywood','planet-hollywood'),('planet-hollywood','planet-hollywood'),('miracle mile','planet-hollywood'),('cosmo','cosmopolitan'),('bellagio','bellagio'),('horseshoe','horseshoe'),('flamingo','flamingo'),('paris','paris'),('caesars','caesars'),('crystals','crystals'),('vdara','vdara'),('waldorf','waldorf'),('aria','aria')]:
  if token in n:return key
 if default:return default
 if p is not None:
  x,z=p[0],p[2]
  if -58<=x<=-26 and -16<=z<=16:return 'sanctuary'
  # Public interior meshes carry old district positions even when their names
  # have only a generic furniture label. Use the existing property envelopes.
  boxes={'bellagio':[-220,-116,-60,80],'paris':[40,-140,220,60],'caesars':[-220,-310,-40,-170],'cosmopolitan':[-218,163,-18,315],'flamingo':[85,-264,211,-207],'horseshoe':[70,-156,141,-78],'planet-hollywood':[53,171,202,281],'crystals':[-287,317,-20,485],'aria':[-460,328,-224,506],'vdara':[-359,185,-260,301],'waldorf':[-143,530,-35,625]}
  hits=[k for k,(x0,z0,x1,z1) in boxes.items() if x0<=x<=x1 and z0<=z<=z1]
  if hits:return min(hits,key=lambda k:(boxes[k][2]-boxes[k][0])*(boxes[k][3]-boxes[k][1]))
 return None

def collider(c,key):
 c=dict(c)
 if c['shape']=='box':
  a=c.get('yaw',0);co=math.cos(a);si=math.sin(a);v=[]
  for x in [-c['size'][0]/2,c['size'][0]/2]:
   for y in [-c['size'][1]/2,c['size'][1]/2]:
    for z in [-c['size'][2]/2,c['size'][2]/2]:v.extend(point([c['position'][0]+co*x+si*z,c['position'][1]+y,c['position'][2]-si*x+co*z],key))
  return dict(name=c['name'],shape='convexHull',vertices=v,group=c.get('group','terrain'))
 c['vertices']=[v for i in range(0,len(c['vertices']),3) for v in point(c['vertices'][i:i+3],key)];return c

def center(c):
 if 'position'in c:return c['position']
 v=c['vertices'];return [(min(v[i::3])+max(v[i::3]))/2 for i in range(3)]

def veer_openings():
 boxes=[([t['target'][0]-.5,10.8,t['target'][1]-.5],[t['target'][2]+.5,210,t['target'][3]+.5]) for k,t in TRANSFORMS.items() if k.startswith('veer-')]
 specs=json.loads((ROOT/'build/arrival-reconstruction/report.json').read_text())['properties']
 for key in ['veer-east','veer-west']:
  t=specs[key];ox,y,oz=t['origin'];w,depth,h=t['dimensions'];co,si=math.cos(t['yaw']),math.sin(t['yaw'])
  ps=[point([ox+co*x+si*z,y,oz-si*x+co*z],key) for x in [-w/2,w/2] for z in [-1,depth+.5]]
  boxes.append(([min(p[0] for p in ps)-.4,.22,min(p[2] for p in ps)-.4],[max(p[0] for p in ps)+.4,h+.5,max(p[2] for p in ps)+.4]))
 return boxes
