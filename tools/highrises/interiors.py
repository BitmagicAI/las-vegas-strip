"""Distinct photographed design cues on reusable, streamed property modules.
Layouts are fitted adaptations, not claims of surveyed interior floor plans.
"""
import sys,json,math,random
from pathlib import Path
sys.path.insert(0,'tools/level');sys.path.insert(0,'tools/highrises')
import bpy,numpy as np
import resort_guest_templates as g
from bellagio_premier import mesh
from catalog import records
plans=json.loads(Path('build/highrises/plan.json').read_text());bykey={p['key']:p for p in plans}
def rgb(s):return tuple(int(s[i:i+2],16)/255 for i in (1,3,5))
# Corridor colors/patterns observed in the archived contact sheets. Avoid treating
# mismatched search-result photographs as evidence of an exact room design.
styles={
'wynn':('#17191b','#b6a484','#511d1b','floral'),'encore':('#17171b','#b9a389','#65132a','floral'),
'venetian':('#756952','#cdc6b8','#253d5d','loops'),'palazzo':('#333537','#b7b0a4','#33465a','floral'),
'fontainebleau':('#354657','#d1cec4','#174475','waves'),'resorts-world':('#293d50','#cec7ba','#466b80','ribbon'),
'park-mgm':('#344832','#c5c2b6','#2e492e','branch'),'mandalay-bay':('#2c3637','#a89d8b','#142840','floral'),
'mgm-grand':('#323039','#b8ae9e','#42284a','floral'),'mirage':('#413637','#b0a394','#793d47','floral'),
'treasure-island':('#5b452a','#c0af8c','#876344','scroll'),'w-las-vegas':('#282824','#77776d','#b2ada4','branch'),
'harrahs':('#402e31','#bab4a8','#922533','bubbles'),'rio':('#53432d','#c3ad88','#934438','waves'),
'new-york':('#565454','#b9b7b1','#bc852b','maze'),'sahara':('#493d31','#b49b78','#b19454','branch'),
'panorama':('#323839','#c3bda9','#466579','waves'),'martin':('#343630','#bab7a8','#a33027','maze'),
'allure':('#5a4729','#bbb198','#896324','waves'),'sky':('#565248','#c7c3b4','#40677a','maze'),
}
for p in plans:
 key=p['key'];carpet,wall,accent,pattern=styles.get(key,('#4c4940',p['stone'],p['accent'],'scroll' if p['family']=='classical' else 'maze'))
 g.SETS[key]=dict(wall=rgb(wall),wood=(.11,.075,.043),accent=rgb(accent),door=(.14,.11,.075) if key not in ['palazzo','venetian','trump'] else (.67,.64,.57),carpet=rgb(carpet),pattern=pattern,depth=7.6)
g.RECIPES+= [t for p in plans for t in p['towers']]
original_export=g.b.export
def unique_export(*args,**kwargs):
 for field in ['colliders','lights','volumes','landmarks','stairs']:
  seen={}
  for obj in getattr(g.b.level,field,[]):
   name=obj.get('name') if isinstance(obj,dict) else getattr(obj,'name',None)
   if name is None:continue
   n=seen.get(name,0);seen[name]=n+1
   if n:
    if isinstance(obj,dict):obj['name']=name+' '+str(n)
    else:obj.name=name+' '+str(n)
 return original_export(*args,**kwargs)
g.b.export=unique_export
original_finish=g.finish

def chandelier(x,z,y=5.9,classic=False):
 g.pipe('chandelier suspension',[(x,6.6,z),(x,y,z)],.018)
 for r,h in [(1.0,y),(.75,y-.32),(.45,y-.58)]:
  g.pipe('chandelier tier',[(x+r*math.cos(a),h,z+r*math.sin(a)) for a in np.linspace(0,math.tau,33)],.025,closed=True)
  for j in range(12):
   a=j*math.tau/12;g.L('crystal pendant',(x+r*math.cos(a),h-.25,z+r*math.sin(a)),[(0,.025),(.12,.07),(.26,.03)],'shade',8)

def greenery(x,z,blue=False):
 g.L('planter',(x,0,z),[(0,.35),(.1,.52),(.7,.43)],'accent' if blue else 'stone',24)
 for j in range(7):
  a=j*math.tau/7
  g.pipe('plant stem',[(x,.6,z),(x+.2*math.cos(a),1.4,z+.2*math.sin(a)),(x+.7*math.cos(a),1.65,z+.7*math.sin(a))],.018,'wood')
  pts=[(x,1.7,z),(x+.75*math.cos(a),1.5,z+.75*math.sin(a)),(x+.45*math.cos(a+.25),1.35,z+.45*math.sin(a+.25))]
  mesh('lance leaf',pts,[(0,1,2),(2,1,0)],g.M('plant'))

def finish(kind):
 p=bykey[g.KEY];key=g.KEY
 if kind=='room':
  if key in ['rio','springhill','westgate','elara','signature','venetian','palazzo']:
   for obj in list(bpy.data.objects):
    if any(n in obj.name for n in ['armchair','chair leg']):bpy.data.objects.remove(obj,do_unlink=True)
   g.b.level.colliders[:]=[c for c in g.b.level.colliders if 'armchair' not in c.name]
  for o in bpy.data.objects:
   if o.type=='MESH' and 'upholstered headboard' in o.name:
    o.data.materials.clear();o.data.materials.append(g.b.scene.materials[g.M('accent' if key in ['park-mgm','encore','new-york'] else 'linen')])
  # Property-specific headwall assemblies and furnishings, beyond color changes.
  if key=='park-mgm':
   g.D('green upholstered full headwall',(4.2,1.6,-2.89),(4.0,3.05,.05),'accent')
   for i,(x,y,w,h) in enumerate([(2.55,2.7,.5,.7),(3.1,2.45,.55,.6),(3.8,2.7,.6,.55),(4.6,2.4,.55,.7),(5.3,2.7,.7,.6)]):g.frame(x,y,-2.83,w,h)
  elif key=='fontainebleau':
   for row in range(5):
    for col in range(7):
     x=3.1+col*.34;y=.65+row*.36
     g.pipe('diamond headboard quilting',[(x,y,-2.79),(x+.17,y+.18,-2.79),(x+.34,y,-2.79)],.009,'trim')
  elif key in ['wynn','encore']:
   if key=='wynn':
    for x in np.arange(2.35,6.25,.28):g.D('Wynn walnut headwall panel',(x,1.73,-2.895),(.264,3.2,.035),'wood')
   else:g.D('Encore crimson headwall',(4.2,1.73,-2.90),(4.0,3.25,.03),'accent')
   for x in [2.75,5.65]:g.D('champagne bedside mirror',(x,1.75,-2.86),(.53,2.2,.045),'mirror')
   g.soft('padded foot bench',(4.2,.46,-.48),(1.9,.24,.42),'accent')
  elif key=='new-york':
   for i in range(15):g.D('Manhattan skyline artwork',(2.55+i*.21,2.47,-2.86),(.16,.2+(i*7%8)*.06,.03),'wood')
  elif key in ['venetian','palazzo']:
   for x in [2.6,5.7]:g.trim_panel(x,2.0,-2.86,.6,2.2)
   g.soft('suite sofa',(6.6,.48,1.65),(1.0,.23,1.7),'accent');g.soft('suite sofa back',(7.05,.85,1.65),(.2,.88,1.8),'accent');g.table(5.65,1.6,.40);g.proxy('suite sofa collision',(6.6,.55,1.65),(1.1,1.1,1.8))
  elif key=='luxor':
   g.D('Tower Premier mirrored headwall',(4.2,2.53,-2.895),(3.7,1.1,.025),'mirror');g.frame(2.7,2.0,2.88,.95,.7)
  if (p['kind']=='apartment' and key!='polo') or key in ['signature','trump','elara','grand-chateau','hgv-boulevard']:
   # A compact kitchen/dining zone beside the window; the central entry lane stays clear.
   g.B('suite kitchen cabinet',(6.35,.46,2.54),(2.0,.92,.60),'wood');g.D('stone kitchen counter',(6.35,.94,2.54),(2.08,.06,.64),'stone')
   g.D('induction cooktop',(6.8,.98,2.5),(.50,.016,.43),'black')
   for x in [6.69,6.91]:g.pipe('hob ring',[(x+.065*math.cos(a),.992,2.48+.065*math.sin(a)) for a in np.linspace(0,math.tau,17)],.004,'nickel',True)
   g.D('kitchen backsplash',(6.3,1.2,2.89),(2.1,.45,.025),'mirror');g.D('microwave',(5.5,1.18,2.5),(.45,.34,.38),'black')
  if key=='mandalay-bay':
   # Original blue/gold marble interpretation of the photographed headwall.
   v,u=np.mgrid[0:512,0:768]/512;vein=np.sin(u*11+2*np.sin(v*7)+1.5*np.sin(u*3+v*5));pix=np.ones((512,768,3))*[.75,.77,.69];pix[vein>.65]=[.24,.46,.53];pix[abs(vein)<.12]=[.64,.44,.15]
   textured('mandalay mural',pix);g.D('blue and gold marble headwall',(4.2,1.73,-2.90),(4.0,3.2,.025),'mandalay mural')
  if key=='mgm-grand':
   for x in np.arange(2.4,6.15,.09):g.D('renovated MGM headwall slat',(x,1.75,-2.89),(.056,3.2,.03),'wood')
   g.soft('black foot bench',(4.2,.45,-.48),(1.8,.26,.40),'black')
  if key=='treasure-island':
   for j in range(4):g.D('TI horizontal padded headboard',(4.2,1.1+j*.29,-2.76),(2.65,.26,.06),'linen' if j%2 else 'leather')
  if key=='w-las-vegas':
   for x in np.arange(2.45,6.1,.42):g.soft('W white padded headwall',(x,1.74,-2.84),(.40,3.12,.06),'linen')
  if key=='new-york':
   for j in range(10):
    for i in range(12):g.D('Soho white brick',(2.45+i*.31+(j%2)*.15,1.75+j*.15,-2.89),(.29,.135,.025),'linen')
  if key in ['rio','springhill','westgate','elara','signature']:
   g.soft('suite lounge chaise',(6.35,.45,1.68),(.82,.24,1.75),'accent');g.soft('chaise raised back',(6.73,.83,1.68),(.16,.74,1.82),'accent');g.proxy('suite chaise collision',(6.35,.53,1.68),(.95,1.06,1.85))
  if key in ['sahara','grand-chateau','palms','strat','westgate','resorts-world','elara']:
   for j in range(7):g.soft('channelled upholstered headboard',(3.0+j*.4,1.8,-2.78),(.37,2.3,.05),'linen')
   if key=='elara':
    for j in range(5):g.D('Elara dark timber crown',(4.2,2.65+j*.12,-2.85),(3.25,.10,.03),'wood')
   if key=='sahara':
    for x in [2.6,5.75]:g.D('Sahara headwall mirror',(x,1.84,-2.85),(.6,2.85,.04),'mirror')
  if key=='circus-circus':
   for i in range(4):g.frame(3.05+i*.75,2.72,-2.84,.45,.55)
  if p['kind']=='apartment' and key!='polo':
   for x in np.arange(2.3,7.5,.18):g.D('apartment timber flooring',(x,.019,0),(.172,.016,5.78),'wood',0)
   for yy in [.3,.72]:g.D('island drawer pull',(6.4,yy,2.19),(.4,.025,.018),'nickel')
  if key in ['trump','signature','grand-chateau']:g.trim_panel(3.6,2.65,2.85,1.65,.50)
 if kind=='corridor':
  if key in ['wynn','encore','mandalay-bay','palazzo','venetian']:
   # either side of the room door (a rail across the doorway stayed put when the door swung open)
   for s in [-1,1]:
    for z in [-1.84,1.84]:g.D('corridor dado',(s*1.706,.91,z),(.065,.085,2.32),'ceiling')
  if key in ['venetian','palazzo']:
   for side in [-1,1]:
    g.D('cream raised door frame',(side*1.69,2.89,0),(.12,.17,1.66),'ceiling')
  if key in ['martin','strat','resorts-world']:
   for s in [-1,1]:g.D('linear corridor ceiling cove',(s*1.46,3.26,0),(.025,.045,6),'shade')
 if kind=='door' and key=='palazzo':
  for z in [-.09,.09]:g.pipe('oval Palazzo door moulding',[(.45*math.cos(a),.75*math.sin(a),z) for a in np.linspace(0,math.tau,49)],.018,'ceiling',True)
 original_finish(kind)
g.finish=finish

def textured(name,pix):
 g.b.mat(g.M(name),(.8,.8,.8),roughness=.32)
 im=g.image(g.M(name),pix);nt=g.b.scene.materials[g.M(name)].node_tree
 tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;nt.links.new(tx.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])

def flower_arrangement(x,z):
 g.L('floral stone vase',(x,0,z),[(0,.30),(.2,.38),(.7,.27),(.9,.32)],'stone',24)
 rng=random.Random(46)
 for j in range(50):
  a=rng.random()*math.tau;r=.62*math.sqrt(rng.random());y=1.3+.65*(1-r/.8)
  xx=x+r*math.cos(a);zz=z+r*math.sin(a)
  g.pipe('flower stem',[(x,.7,z),(xx,y,zz)],.008,'wood')
  g.L('rose petals',(xx,y,zz),[(0,.05),(.055,.105),(.12,.08),(.14,.028)],'accent' if j%3 else 'linen',8)

def lobby(p,t):
 key=p['key'];g.start(key);g.b.mat(g.M('plant'),(.07,.17,.045));g.b.mat(g.M('water'),(.07,.23,.27),metal=.25,roughness=.18)
 front=-5.25-6*t['bays'];entry=t['lobbyFront'];end=-5.6;length=end-front;mid=(front+end)/2
 classic=key in ['wynn','encore','venetian','palazzo','trump','treasure-island','bellagio-spa','grand-chateau','harrahs','mirage']
 v,u=np.mgrid[0:512,0:512]/512;vein=np.sin(u*15+np.sin(v*5)*2+np.sin(u*37+v*19)*.25);pix=np.ones((512,512,3))*[.72,.70,.65];pix-=np.exp(-abs(vein)*17)[:,:,None]*.12
 textured('lobby marble',pix)
 # Main fitted lobby. A smaller glazed vestibule connects its centre to the facade.
 g.B('lobby stone slab',(0,-.12,mid),(19,.24,length),'lobby marble');g.B('lobby coffer ceiling',(0,6.88,mid),(19,.24,length),'ceiling')
 g.B('continuous stair threshold',(0,-.12,-5.35),(2.12,.24,.60),'stone')
 for s in [-1,1]:
  connection=t.get('publicConnection')
  if connection and connection['side']==s:
   at,width=connection['at'],connection['width']
   for za,zb in [(front,at-width/2),(at+width/2,end)]:
    if zb>za:g.B('lobby perimeter',(s*9.4,3.35,(za+zb)/2),(.2,6.7,zb-za),'wall')
   g.B('public gallery lintel',(s*9.4,5.65,at),(.2,2.1,width),'wall')
  else:g.B('lobby perimeter',(s*9.4,3.35,mid),(.2,6.7,length),'wall')
  for z in np.arange(front+2,end-1,4.8):
   if connection and connection['side']==s and abs(z-connection['at'])<connection['width']/2+2.4:continue
   g.D('wall panel pilaster',(s*9.23,3.2,z),(.12,6.4,.18),'wood');g.D('reception wall sconce',(s*9.08,2.6,z),(.2,.65,.25),'shade')
   g.D('wall dado',(s*9.21,.7,z),(.10,1.4,4.6),'wood')
 for z in np.arange(front+3,end,6):
  for x in ([-5.6,5.6] if classic else [-8.8,8.8]):
   g.L('stone column',(x,0,z),[(0,.36),(.16,.4),(.22,.29),(6.1,.29),(6.3,.45),(6.6,.45)],'stone',24)
   g.D('coffer perimeter',(x,6.65,z),(6.5,.16,.14),'trim')
  for x in [-5.8,0,5.8]:
   for dz in [-2.6,2.6]:g.D('coffer cross beam',(x,6.59,z+dz),(5.45,.20,.16),'ceiling')
   for xx in [x-2.65,x+2.65]:g.D('coffer longitudinal beam',(xx,6.59,z),(.16,.20,5.35),'ceiling')
   g.D('recessed ceiling panel',(x,6.72,z),(5.1,.035,4.97),'wood' if not classic else 'stone')
   for xx in [x-2.4,x+2.4]:g.D('cove glow',(xx,6.54,z),(.025,.018,4.6),'shade')
  g.D('marble floor inset',(0,.007,z),(3.5,.014,.10),'wood');g.b.lamp('lobby pool',(0,5.6,z),'#ffe8cf',intensity=65,distance=13)
  if z<front+22:chandelier(0,z,5.75,p['family']=='classical')
 # Rear wall connects seamlessly to the resident stair enclosure, leaving a 2 m opening.
 for s in [-1,1]:g.B('stair lobby return',(s*5.23,3.35,-5.45),(8.35,6.7,.20),'wall')
 g.B('stair portal lintel',(0,4.82,-5.45),(2.12,4.0,.20),'wall')
 for s in [-1,1]:g.B('arrival front pier',(s*5.70,3.35,front),(7.45,6.7,.20),'wall')
 g.B('arrival lintel',(0,5.7,front),(3.95,2.0,.20),'wall')
 if entry<front-.1:
  l=front-entry;z=(front+entry)/2
  g.B('entrance gallery floor',(0,-.12,z),(4.0,.24,l),'stone');g.B('entrance gallery ceiling',(0,4.7,z),(4.0,.20,l),'ceiling')
  for s in [-1,1]:g.B('entrance gallery side',(s*2.0,2.3,z),(.18,4.6,l),'wall')
  for z in np.arange(entry+1,front,3):g.D('gallery light',(0,4.54,z),(.9,.045,.5),'shade')
 # Entrance outside cover and glazed sidelight frames, not a blank doorway.
 # The permanent exterior owns the canopy, supports and arrival apron.
 for s in [-1,1]:
  greenery(s*2.7,entry-1.4,key=='sky')
  g.D('glazed entrance sidelight',(s*1.65,2.15,entry),(.65,4.3,.05),'glass_window')
  g.D('portal frame',(s*1.28,2.15,entry),(.08,4.3,.18),'nickel')
 g.D('portal transom',(0,4.35,entry),(4,.10,.18),'nickel');g.b.text('property entrance',p['name'].upper(),(0,4.03,entry-.14),g.M('trim'),size=min(.5,7/max(1,len(p['name']))),both_faces=False)
 # Marble tile joints, perimeter borders, and a flush arrival medallion.
 verts=[];faces=[]
 for x in np.arange(-9,9,1.5):
  for zz in np.arange(front+.15,end-1.5,1.5):
   n=len(verts);verts.extend([(x,.014,zz),(x+1.47,.014,zz),(x+1.47,.014,zz+1.47),(x,.014,zz+1.47)]);faces.append((n,n+1,n+2,n+3))
 mesh('marble tile field',verts,faces,g.M('lobby marble'))
 for x in [-8.95,-4.2,4.2,8.95]:g.D('floor brass border',(x,.024,mid),(.055,.009,length-.25),'trim',0)
 for r in [1.1,1.5,1.58,1.78]:g.pipe('arrival stone medallion',[(r*math.cos(a),.032,front+3.3+r*math.sin(a)) for a in np.linspace(0,math.tau,65)],.018,'wood' if r<1.6 else 'trim',True)
 z=front+min(7,length*.52)
 # Concierge/check-in to the left, lounge to the right, clear 3.5 m axial route.
 g.B('reception desk',(-5.9,.65,z),(4.8,1.3,1.05),'wood');g.D('stone reception counter',(-5.9,1.32,z),(5,.1,1.2),'stone')
 for x in [-7.2,-5.4]:g.D('check-in monitor',(x,1.57,z+.12),(.46,.3,.045),'black')
 g.D('reception feature wall',(-6.0,2.7,z+1.4),(5.6,4.4,.2),'accent');g.b.text('reception identity',p['name'].upper(),(-6,3.55,z+1.26),g.M('shade'),size=.24,both_faces=False)
 for zz in [z-1.4,z+1.5]:g.chair(5.2,zz,'accent');g.chair(7.1,zz,'linen')
 g.table(6.2,z,.5);greenery(8.1,z+3)
 for zz in np.arange(z+9,end-2,9):
  g.chair(-7,zz);g.chair(7,zz);g.table(-5.7,zz,.4);greenery(8,zz+2)
 # Signature installations from the photographs.
 if key=='fontainebleau':
  for x in np.arange(-3.5,3.6,.36):g.pipe('blue-lit entrance fin',[(x,4.9,entry-3.4),(x,5.4,entry-2),(x,5.0,entry+.1)],.055,'accent')
 elif key=='park-mgm':
  for i in range(18):
   a=i*math.tau/18;g.pipe('tree root ceiling sculpture',[(0,6.6,z),(2*math.cos(a),6.1,z+2*math.sin(a)),(4*math.cos(a+.2),6.0,z+4*math.sin(a+.2))],.08,'wood')
 elif key=='mirage':
  g.D('reception aquarium',(-6,2.55,z+1.20),(5.0,1.55,.09),'water')
  for i in range(23):g.L('aquarium coral',(-8.2+i*.2,1.82,z+1.08),[(0,.07),(.2+(i%4)*.13,.03)],'accent',8)
 elif key=='panorama':
  for i in range(8):g.L('sculpted metallic lobby column',(4.2,i*.8,z+6),[(0,.47),(.3,.65),(.8,.40)],'nickel',7)
 elif key=='luxor':
  for s in [-1,1]:
   g.B('pharaoh throne',(s*3.5,1.0,z+4),(1.6,2,1.5),'stone');g.L('pharaoh torso',(s*3.5,1.6,z+4),[(0,.62),(1.8,.42)],'stone',12);g.L('pharaoh head',(s*3.5,3.5,z+4),[(0,.25),(.55,.43),(.9,.16)],'stone',12)
 elif key in ['wynn','encore']:
  for x in [-4.4,4.4]:flower_arrangement(x,min(end-1.2,z+4))
 elif key=='circus-circus':
  for x in np.arange(-3.5,3.6,.4):g.L('marquee bulb',(x,4.53,entry-3.3),[(0,.05),(.12,.10),(.2,.03)],'shade',8)
 elif key=='martin':
  for yy in np.arange(.6,4.3,.17):
   for s in [-1,1]:g.D('entrance horizontal slat',(s*2.6,yy,entry-.15),(2.4,.06,.1),'nickel')
 elif key=='sahara':
  for x in [-2.5,0,2.5]:g.pipe('angular bronze canopy rib',[(x,4.6,entry+.3),(x+1,4.35,entry-1.3),(x,4.6,entry-3.2)],.05,'trim')
 elif key=='signature':
  for r in [.6,1.1,1.6]:g.pipe('circular marble floor inlay',[(r*math.cos(a),.016,z+4+r*math.sin(a)) for a in np.linspace(0,math.tau,49)],.015,'wood',True)
 # Authoring audit metadata for the continuous route, before export.
 g.b.volume('arrival lobby',(0,3.2,mid),(18.5,6.4,length-.2),tags=['indoors','public'])
 g.b.landmark('entrance',(0,.02,entry),tags=['entry']);g.b.landmark('guest stairs',(0,.02,-5.5),tags=['stairs']);g.b.spawn((0,.03,front+2))
 # World-space UVs on lobby marble and timber, matching reusable guest modules.
 bpy.context.view_layer.update()
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='LobbyUV')
  for poly in o.data.polygons:
   for li in poly.loop_indices:
    w=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
    uv.data[li].uv=(w.x/2,-w.y/2) if abs(poly.normal.z)>.5 else ((-w.y/2,w.z/2) if abs(poly.normal.x)>.5 else (w.x/2,w.z/2))
 name=t['id']+'-lobby';g.b.export('build/hotels',name)

def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 rooms_only='--rooms-only' in args;corridors_only='--corridors-only' in args;structure_only='--structure-only' in args
 wanted=[a for a in args if a not in ('--rooms-only','--corridors-only','--structure-only')] or list(bykey)
 for key in wanted:
  p=bykey[key]
  if not p['towers']:continue
  if rooms_only:
   g.start(key);g.room();continue
  if corridors_only:
   g.start(key);g.corridor();continue
  if structure_only:
   g.structure(key);continue
  g.structure(key)
  for fn in [g.corridor,g.room,g.door]:g.start(key);fn()
  for t in p['towers']:lobby(p,t)
  print('HIGHRISE PROPERTY COMPLETE',key,flush=True)
if __name__=='__main__':main()
