"""Individually styled LINQ and Vanderpump streamed guest modules, local export."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,'tools/highrises');sys.path.insert(0,'tools/level')
import interiors as h
import resort_guest_templates as g
import bpy,numpy as np
T=json.loads(Path('build/strip-landmarks/guest-towers.json').read_text())
styles={'linq':dict(wall=(.75,.75,.70),wood=(.53,.39,.24),accent=(.24,.38,.53),door=(.29,.24,.20),carpet=(.26,.27,.29),pattern='bubbles',depth=7.6),'vanderpump':dict(wall=(.66,.62,.57),wood=(.17,.13,.12),accent=(.51,.32,.37),door=(.15,.17,.16),carpet=(.34,.32,.30),pattern='floral',depth=7.6)}
styles['polo']=dict(wall=(.78,.75,.68),wood=(.66,.48,.27),accent=(.39,.37,.32),door=(.42,.29,.18),carpet=(.58,.55,.47),pattern='waves',depth=7.6)
for t in T:
 key=t['set'];g.SETS[key]=styles[key];g.RECIPES.append(t);h.bykey[key]=dict(key=key,name=t['name'],family='modern' if key=='linq' else 'classical',kind='apartment' if key=='polo' else 'hotel',towers=[t])
prior=g.finish
def finish(kind):
 key=g.KEY
 if kind=='room':
  for o in list(bpy.data.objects):
   if any(n in o.name for n in ['headboard surround','upholstered headboard','headboard button']):bpy.data.objects.remove(o,do_unlink=True)
  if key=='linq':
   v,u=np.mgrid[0:512,0:512]/512;d=np.sqrt(((u*4)%1-.5)**2+((v*4)%1-.5)**2);pix=np.ones((512,512,3))*[.30,.40,.52];pix[d<.32]=[.66,.71,.73];pix+=(np.sin(u*1900)*np.sin(v*1400))[:,:,None]*.035
   h.textured('linq blue discs',pix);g.D('blue circle wallpaper',(4.8,1.8,-2.906),(5.1,3.3,.02),'linq blue discs')
   g.D('continuous floating oak headboard',(4.7,.83,-2.85),(4.7,1.34,.11),'wood')
   for x in [2.78,5.62]:
    g.D('rectangular bedside lamp frame',(x,1.12,-2.47),(.46,.39,.08),'nickel');g.D('rectangular bedside lamp diffuser',(x,1.12,-2.41),(.43,.24,.06),'shade')
   g.pipe('round hanging mirror rim',[(6.3+.6*math.cos(a),2.2+.6*math.sin(a),2.885) for a in np.linspace(0,math.tau,65)],.025,'black',True)
   g.pipe('mirror hanging strap',[(5.71,2.65,2.885),(6.3,3.2,2.885),(6.89,2.65,2.885)],.018,'leather')
   # Mirror is a separate circular surface, not a square on the wall.
   from bellagio_premier import mesh
   pts=[(6.3,2.2,2.89)]+[(6.3+.585*math.cos(a),2.2+.585*math.sin(a),2.89) for a in np.linspace(0,math.tau,65)]
   mesh('round LINQ mirror',pts,[(0,i,i+1) for i in range(1,65)],g.M('mirror'))
  elif key=='vanderpump':
   # Original toile-style botanical wallpaper, inspired by the photographed
   # monochrome woodland mural, without embedding the reference photograph.
   rng=np.random.default_rng(29);canvas=np.ones((512,1024,3))*[.79,.78,.75]
   def stroke(x0,y0,x1,y1,width,shade):
    for t in np.linspace(0,1,max(2,int(math.hypot(x1-x0,y1-y0)))):
     x=int(x0+(x1-x0)*t);y=int(y0+(y1-y0)*t);r=max(1,int(width));xa,xb=max(0,x-r),min(1024,x+r+1);ya,yb=max(0,y-r),min(512,y+r+1)
     if xa<xb and ya<yb:canvas[ya:yb,xa:xb]=shade
   def branch(x,y,angle,length,width,depth):
    xx=x+math.cos(angle)*length;yy=y+math.sin(angle)*length;stroke(x,y,xx,yy,width,[.32,.33,.31])
    if depth:
     for delta in [-.55,.45]:branch(xx,yy,angle+delta+float(rng.uniform(-.1,.1)),length*.70,width*.69,depth-1)
    else:
     for j in range(14):
      u=xx+rng.normal(0,8);v=yy+rng.normal(0,7);stroke(u,v,u+2,v-2,.9,[.49,.50,.46])
   for xx in [75,335,620,910]:branch(xx,520,-1.55,126,3.5,6)
   h.textured('Vanderpump botanical toile',canvas);g.D('woodland mural',(4.8,1.7,-2.906),(5.7,3.35,.018),'Vanderpump botanical toile')
   g.D('dark full-height upholstered backdrop',(4.3,1.70,-2.90),(4.1,3.2,.035),'wood')
   for j in range(10):g.soft('scalloped charcoal headboard',(2.65+j*.35,1.22+(.28*math.sin(j*math.pi/9)),-2.77),(.33,1.6+(.56*math.sin(j*math.pi/9)),.13),'black')
   for x in [2.52,6.0]:g.pipe('gilded headboard border',[(x,.3,-2.73),(x,2.7,-2.73),(x+(.17 if x<4 else -.17),2.85,-2.73)],.015,'trim')
   g.soft('blush foot throw',(4.2,.86,-.68),(2.08,.06,.52),'accent')
   for x in [3.8,4.5]:g.soft('blush accent pillow',(x,.97,-2.0),(.45,.20,.35),'accent')
   g.soft('velvet window sofa',(6.68,.48,1.55),(.92,.26,1.65),'accent');g.soft('velvet sofa back',(7.08,.87,1.55),(.16,.77,1.75),'accent');g.proxy('sofa',(6.68,.54,1.55),(1.05,1.08,1.75))
   for x in [2.85,5.60]:
    g.D('mirrored bedside cabinet',(x,.45,-2.12),(.65,.65,.035),'mirror')
    for j in range(8):g.D('fluted bronze bedside table',(x-.25+j*.07,.42,-2.11),(.025,.61,.023),'trim')
   g.trim_panel(3.7,2.45,2.875,1.75,1.02);g.frame(3.7,2.45,2.86,1.5,.78)
  elif key=='polo':
   # The kitchenette occupies the generic media-console bay; remove that
   # furniture and its collision, rather than hiding overlapping cabinetry.
   remove=['media console','stone console top','console door seam','remote control','remote key']
   for o in list(bpy.data.objects):
    if any(n in o.name for n in remove):bpy.data.objects.remove(o,do_unlink=True)
   g.b.level.colliders[:]=[c for c in g.b.level.colliders if not any(n in c.name for n in remove)]
   for o in bpy.data.objects:
    if 'television' in o.name:o.location.x-=1
   v,u=np.mgrid[0:512,0:512]/512;pix=np.ones((512,512,3))*[.51,.48,.41];pix+=(np.sin(u*37+np.sin(v*21))*.022+np.sin(u*1510)*np.sin(v*1370)*.012)[:,:,None]
   h.textured('roomcarpet',pix)
   g.D('Polo timber headboard',(4.2,1.20,-2.86),(3.9,1.8,.16),'wood')
   for x in [2.7,3.7,4.7,5.7]:g.frame(x,2.6,-2.76,.75,.58)
   for x in [2.7,5.7]:
    g.D('granite bedside cabinet',(x,.48,-2.2),(.72,.83,.65),'wood');g.D('granite bedside top',(x,.92,-2.2),(.78,.08,.70),'stone')
   # Photographed self-catering character: honey-colored cabinets, granite,
   # inset sink, compact appliances and a small dining/work table.
   g.B('Polo kitchenette',(6.0,.46,2.52),(2.9,.92,.67),'wood');g.D('granite worktop',(6.0,.95,2.52),(2.98,.06,.71),'stone')
   for x in [4.9,5.6,6.3,7.0]:
    g.D('cabinet recessed panel',(x,.45,2.168),(.58,.70,.035),'linen');g.D('brushed cabinet pull',(x+.20,.73,2.14),(.025,.15,.025),'nickel')
   g.D('sink steel rim',(5.3,.993,2.5),(.61,.014,.45),'nickel');g.D('sink basin',(5.3,1.002,2.5),(.51,.014,.35),'black')
   g.pipe('arched kitchen faucet',[(5.3,1.0,2.72),(5.3,1.27,2.72),(5.3,1.32,2.59),(5.3,1.18,2.54)],.015,'nickel')
   g.B('upper kitchen cabinet',(6.3,2.18,2.66),(2.30,.80,.44),'wood');g.D('microwave appliance',(6.3,1.62,2.59),(.73,.45,.45),'black');g.D('microwave window',(6.22,1.62,2.35),(.47,.27,.025),'mirror')
   g.D('coffee machine',(6.85,1.17,2.5),(.29,.39,.29),'black');g.D('coffee carafe',(6.85,1.14,2.34),(.19,.23,.16),'mirror')
   g.D('suite writing desk',(3.0,.76,2.40),(1.1,.12,.7),'wood');g.chair(3,1.5,'linen')
 if kind=='corridor':
  for side in [-1,1]:
   # Either side of the room door (1.3 m opening at z 0, architraves at +-0.72): one panel across the doorway read as the
   # lower half of the door, and stayed shut when the door swung open (2026-10-08 film review).
   for z in [-1.82,1.82]:
    g.D('corridor lower wall panel',(side*1.70,.65,z),(.035,1.25,2.24),'wood')
    g.D('corridor dado',(side*1.67,1.30,z),(.06,.08,2.26),'trim')
   if key=='vanderpump':
    for z in [-2.2,2.2]:g.D('fluted door pier',(side*1.64,1.65,z),(.10,3.15,.12),'trim')
   elif key=='linq':
    for z in [-2.5,2.5]:g.D('blue wayfinding door reveal',(side*1.65,1.65,z),(.10,3.15,.15),'accent')
 prior(kind)
g.finish=finish
wanted=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
# --corridors-only: re-export just the corridor modules (the lobbies get their doorways cut afterwards by
# export_guest_lobbies.py, so a full run would undo that)
corridors_only='--corridors-only' in wanted;structure_only='--structure-only' in wanted
wanted=[w for w in wanted if w not in ('--corridors-only','--structure-only')]
for t in T:
 k=t['set']
 if wanted and k not in wanted:continue
 if corridors_only:g.start(k);g.corridor();print('LANDMARK GUEST CORRIDOR',k,flush=True);continue
 if structure_only:g.structure(k);print('LANDMARK GUEST STRUCTURE',k,flush=True);continue
 g.structure(k)
 for fn in [g.corridor,g.room,g.door]:g.start(k);fn()
 h.lobby(h.bykey[k],t);print('LANDMARK GUEST SET',k,flush=True)
