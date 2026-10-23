"""Property-specific photo-referenced modular guest accommodation.

Research photographs remain in build/hotels/resort-expansion; all shipped
textures and meshes below are authored, not copied photographs. Rooms use
the established centre-door six-metre bay, adapted to our compressed towers.
"""
import sys,math,json,os
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,'tools/level')
from bellagio_premier import b,box,tube,lathe,cushion,coord,proxy
OUT=Path('build/hotels');TEX=OUT/'resort-expansion/textures';TEX.mkdir(parents=True,exist_ok=True)
RECIPES=json.loads(Path('src/work/hotels/towers.json').read_text())
SETS={
 'paris':dict(wall=(.72,.69,.60),wood=(.065,.054,.041),accent=(.40,.035,.055),door=(.31,.32,.30),carpet=(.21,.22,.17),pattern='scroll',depth=6.1),
 'caesars':dict(wall=(.60,.56,.50),wood=(.14,.09,.045),accent=(.055,.13,.32),door=(.27,.21,.15),carpet=(.24,.22,.21),pattern='hex',depth=7.8),
 'cosmopolitan':dict(wall=(.34,.36,.38),wood=(.10,.07,.09),accent=(.12,.22,.34),door=(.44,.45,.40),carpet=(.06,.14,.26),pattern='waves',depth=8.1),
 'flamingo':dict(wall=(.49,.49,.48),wood=(.09,.075,.07),accent=(.63,.15,.29),door=(.43,.44,.43),carpet=(.12,.17,.16),pattern='loops',depth=5.1),
 'horseshoe':dict(wall=(.53,.51,.49),wood=(.18,.105,.061),accent=(.53,.055,.032),door=(.41,.025,.047),carpet=(.12,.115,.11),pattern='bubbles',depth=6.5),
 'planet-hollywood':dict(wall=(.22,.23,.23),wood=(.038,.03,.028),accent=(.20,.44,.44),door=(.055,.32,.31),carpet=(.23,.21,.20),pattern='maze',depth=6.1),
 'aria':dict(wall=(.58,.55,.42),wood=(.13,.065,.028),accent=(.045,.11,.23),door=(.07,.04,.025),carpet=(.18,.16,.13),pattern='ribbon',depth=8.1),
 'vdara':dict(wall=(.58,.53,.36),wood=(.13,.075,.035),accent=(.42,.49,.22),door=(.075,.055,.035),carpet=(.12,.16,.16),pattern='branch',depth=7.2),
 'waldorf':dict(wall=(.67,.63,.57),wood=(.055,.038,.029),accent=(.36,.32,.29),door=(.07,.045,.034),carpet=(.055,.047,.042),pattern='floral',depth=8.1)
}
KEY='';CFG={}
def M(n):return KEY+'_'+n
def D(n,p,s,m='wall',bevel=.012):return box(n,p,s,M(m),bevel,False)
def B(n,p,s,m='wall'):return box(n,p,s,M(m),0,True)
def soft(n,p,s,m='linen'):return cushion(n,p,s,M(m))
def L(n,p,profile,m='trim',segments=24,scale=(1,1,1)):return lathe(n,p,profile,M(m),segments,scale)
def pipe(n,pts,r=.012,m='trim',closed=False):return tube(n,pts,r,M(m),closed)
def image(name,pix):
 h,w=pix.shape[:2];im=bpy.data.images.new(name,w,h,alpha=True);rgba=np.ones((h,w,4),dtype=np.float32);rgba[:,:,:3]=np.clip(pix,0,1);im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str((TEX/(name+'.png')).resolve());im.file_format='PNG';im.save();im.pack();return im
IMAGES={}
def pattern(c):
 n=768;v,u=np.mgrid[0:n,0:n]/n;x=(u-.5)*3.8;z=(v-.5)*6;kind=c['pattern'];base=np.array(c['carpet']);rgb=np.ones((n,n,3))*base
 light=np.array([.65,.59,.46]);accent=np.array(c['accent'])
 if kind=='scroll':f=np.sin(13*x+2*np.cos(z*math.pi))+np.cos(8*z+2*np.sin(4*x));mask=np.abs(f)<.22
 elif kind=='hex':
  xx=(x*1.7+np.round(z*1.8)%2*.5)%1-.5;zz=(z*1.8)%1-.5;r=np.maximum(abs(xx)*.866+abs(zz)*.5,abs(zz));mask=(r>.28)&(r<.39);rgb[r<.2]=(.10,.10,.10);rgb[(r>.39)&(r<.44)]=(.40,.045,.045)
 elif kind=='waves':
  r=np.sqrt((x+.5*np.sin(z*1.05))**2+(.6*np.sin(z*math.pi/6))**2);mask=np.sin(r*34+z*2)> .50;rgb[(np.sin(z*1.05+x*2)>.2)&(~mask)]=(.12,.10,.23)
 elif kind=='loops':r=np.sqrt(((x*2)%1-.5)**2+((z*2)%1-.5)**2);mask=(r>.29)&(r<.36);light=np.array([.56,.28,.34])
 elif kind=='bubbles':
  r=np.sqrt(((x*2+.17*np.sin(z*4))%1-.5)**2+((z*1.5)%1-.5)**2);mask=r<.19;light=np.array([.56,.28,.30]);rgb[(r>.22)&(r<.27)]=(.53,.49,.43)
 elif kind=='maze':f=np.cos(x*10+np.sin(z*9))+np.sin(z*10+np.sin(x*9));mask=np.abs(f)<.25
 elif kind=='ribbon':
  w=x+.25*np.sin(z*math.pi/3);mask=(abs(w)<.87)&(abs(np.sin(w*8))>.48);light=np.array([.59,.57,.25]);rgb[(abs(w)<.87)&(~mask)]=(.20,.33,.50)
 elif kind=='branch':f=x-.5*np.sin(z*math.pi/3);mask=np.abs(np.sin(f*13+np.cos(z*math.pi)))>.91
 else:
  r=np.sqrt(x*x+(1.9*np.sin(z*math.pi/6))**2);a=np.arctan2(z,x);mask=(r<1.1+.5*np.cos(a*7))|(np.abs(np.sin(15*x+4*np.cos(z*math.pi/3)))>.987);light=np.array([.77,.72,.61])
 rgb[mask]=light
 rng=np.random.default_rng(500+list(SETS).index(KEY));rgb+=(rng.random((n,n,1))-.5)*.055
 return rgb
def start(key):
 global KEY,CFG
 KEY=key;CFG=SETS[key];b.reset()
 palette={**{n:CFG[n] for n in ['wall','wood','accent','door','carpet']},'ceiling':(.76,.74,.68),'linen':(.88,.86,.80),'shade':(.86,.78,.63),'trim':(.48,.38,.23),'nickel':(.54,.57,.58),'stone':(.74,.71,.64),'black':(.009,.014,.019),'mirror':(.52,.62,.63),'glass_window':(.47,.67,.76),'leather':(.50,.31,.14),'art':(.73,.67,.57)}
 palette['roomcarpet']=(.31,.30,.27)
 for n,c in palette.items():b.mat(M(n),c,roughness=.92 if n in ['wall','linen','carpet'] else .4,metal=.8 if n in ['trim','nickel','mirror'] else 0,alpha=.1 if n=='glass_window' else 1,glow=.38 if n=='shade' else 0)
 for n in ['carpet','roomcarpet','wall','wood','art']:
  tag=M(n)
  if tag not in IMAGES:
   if n=='carpet':pix=pattern(CFG)
   elif n=='roomcarpet':
    v,u=np.mgrid[0:768,0:768]/768
    if KEY=='paris':f=np.sin(u*math.tau*7)+np.cos(v*math.tau*9)
    elif KEY=='flamingo':f=np.sin(u*math.tau*43)*np.cos(v*math.tau*51)
    elif KEY in ['cosmopolitan','aria','vdara']:f=np.sin(u*math.tau*23+.7*np.sin(v*math.tau*3))
    else:f=np.sin(u*math.tau*17+np.sin(v*math.tau*19))+np.sin(v*math.tau*17)
    base=np.array([.23,.23,.215] if KEY in ['flamingo','aria'] else [.31,.30,.27]);pix=np.ones((768,768,3))*base+(np.abs(f)<.18)[:,:,None]*.085+(.012*np.sin(u*1780)*np.cos(v*1990))[:,:,None]
   else:
    v,u=np.mgrid[0:512,0:512]/512;base=np.array(palette[n]);grain=np.sin(u*1930)*.013+np.sin(v*2120)*.012
    if n=='wood':grain+=.012*np.sin(u*790+1.5*np.sin(v*13))
    if n=='wall':grain+=.025*np.sin(u*56)
    pix=np.ones((512,512,3))*base+grain[:,:,None]
    if n=='art':
     for k in range(7):pix[np.abs(u-(.16+.1*k+.085*np.sin(v*9+k)))<.011]=CFG['accent']
   im=image(tag,pix);IMAGES[tag]=im.name
  im=bpy.data.images.get(IMAGES[tag])
  if not im:im=bpy.data.images.load(str((TEX/(tag+'.png')).resolve()));im.pack();IMAGES[tag]=im.name
  nt=b.scene.materials[tag].node_tree;tx=nt.nodes.new('ShaderNodeTexImage');tx.image=im;nt.links.new(tx.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
# GUEST_ONLY=entry,stair,...: export only these module kinds (the others are built and dropped), so one kind can be
# re-exported without touching modules a later step patched (the lobbies' doorway cuts)
ONLY={k for k in os.environ.get('GUEST_ONLY','').split(',') if k}
def finish(kind):
 if ONLY and kind not in ONLY:print('SKIPPED (GUEST_ONLY)',KEY+'-'+kind,flush=True);return
 bpy.context.view_layer.update()
 for o in list(bpy.data.objects):
  if o.type!='MESH':continue
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='ResortUV')
  for poly in o.data.polygons:
   mat=o.data.materials[poly.material_index].name
   for li in poly.loop_indices:
    w=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;x,y,z=w.x,w.z,-w.y
    if mat in [M('carpet'),M('roomcarpet')]:q=((x+1.9)/3.8,(z+3)/6)
    elif abs(poly.normal.z)>.5:q=(x/2,z/2)
    elif abs(poly.normal.x)>.5:q=(z/2,y/2)
    else:q=(x/2,y/2)
    uv.data[li].uv=q
 b.spawn((0,.03,0));name=KEY+'-'+kind;b.export(str(OUT),name)
 Path('src/work/hotels/'+name+'.json').write_text((OUT/(name+'.mesh-level.json')).read_text())
 print('RESORT TEMPLATE',name,len(b.level.colliders),flush=True)
def lamp(x,z,y=.85,style=None):
 style=style or KEY
 if style in ['paris','caesars','horseshoe']:
  L('ceramic lamp',(x,y,z),[(0,.13),(.035,.16),(.13,.09),(.25,.15),(.32,.07),(.4,.04)],'accent')
 else:L('lamp stem',(x,y,z),[(0,.12),(.035,.12),(.045,.018),(.39,.018)],'nickel')
 L('linen lamp shade',(x,y+.37,z),[(0,.21),(.28,.18)],'shade',32)
 for h in [y+.37,y+.65]:L('shade binding',(x,h,z),[(0,.212),(.009,.212)],'trim')
def frame(x,y,z,w=1.1,h=.8):
 D('picture frame',(x,y,z),(w+.09,h+.09,.065),'wood');D('original abstract artwork',(x,y,z+(.041 if z<0 else -.041)),(w,h,.015),'art')
def trim_panel(x,y,z,w,h):
 for xx in [x-w/2,x+w/2]:D('panel vertical moulding',(xx,y,z),(.032,h,.04),'trim')
 for yy in [y-h/2,y+h/2]:D('panel horizontal moulding',(x,yy,z),(w,.032,.04),'trim')
def chair(x,z,material='accent',scale=1):
 soft('armchair seat',(x,.48,z),(.72*scale,.16,.72),material);soft('armchair back',(x,.81,z+.30),(.74*scale,.70,.17),material)
 for s in [-1,1]:soft('armchair arm',(x+s*.38*scale,.65,z),(.13,.32,.77),material)
 for xx in [-.27,.27]:
  for zz in [-.27,.27]:D('chair leg',(x+xx*scale,.22,z+zz),(.04,.42,.04),'wood')
 proxy('armchair collision',(x,.47,z),(.88*scale,.94,.82))
def table(x,z,r=.4):
 L('table pedestal',(x,.03,z),[(0,.30),(.03,.30),(.055,.045),(.53,.045)],'trim')
 L('stone tabletop',(x,.56,z),[(0,r),(.045,r)],'stone',40);proxy('table collision',(x,.32,z),(r*1.8,.64,r*1.8))
def bed(x,z,width=1.95,style='king'):
 B('upholstered bed base',(x,.25,z),(width+.06,.5,2.15),'wood')
 soft('thick mattress',(x,.56,z),(width,.27,2.1));soft('tucked duvet',(x,.735,z+.11),(width+.04,.18,1.88))
 for offset in [-width*.235,width*.235]:
  soft('rear pillow',(x+offset,.83,z-.72),(.77,.22,.48));soft('front pillow',(x+offset,.84,z-.50),(.67,.18,.43))
 D('duvet foot fold',(x,.839,z+.65),(width+.06,.045,.42),'accent' if KEY in ['aria','horseshoe','cosmopolitan'] else 'linen',.018)
 # Headboards echo each photographed property rather than a common recolor.
 headmat='leather' if KEY=='horseshoe' else 'linen' if KEY in ['paris','waldorf'] else 'accent' if KEY=='aria' else 'wood'
 D('headboard surround',(x,1.20,z-1.19),(width+.32,1.70,.16),'wood')
 soft('upholstered headboard',(x,1.24,z-1.075),(width+.15,1.55,.10),headmat)
 for i in range(7):
  xx=x-width/2+i*width/6
  if KEY in ['flamingo','aria']:D('headboard vertical piping',(xx,1.22,z-1.01),(.012,1.45,.015),'trim')
  else:
   for yy in [1.0,1.48]:L('headboard button',(xx,yy,z-1.008),[(0,.014),(.012,.014)],'trim',12)
 if KEY in ['paris','caesars','waldorf']:
  for sx in [-1,1]:D('headboard mirror',(x+sx*(width/2+.36),1.47,z-1.18),(.38,2.15,.035),'mirror')
 for sx in ([] if KEY=='planet-hollywood' else [-1,1]):
  xx=x+sx*(width/2+.37)
  B('bedside chest',(xx,.36,z-.73),(.60,.72,.48),'stone' if KEY=='paris' else 'wood')
  for y in [.24,.50]:D('drawer edge',(xx,y,z-.478),(.54,.014,.02),'trim')
  D('drawer pull',(xx,.52,z-.45),(.15,.018,.028),'nickel');lamp(xx,z-.73,.75)
  D('wall power outlet',(xx,.99,z-1.2),(.11,.09,.025),'black')
 D('bedside tablet',(x+width/2+.35,.77,z-.68),(.20,.035,.15),'black')
def bath(depth):
 # 2.1 x 2.0 m wet room, clear 1.05 m entry. Entry route stays at z=0.
 B('bathroom partition',(2.15,1.7,-1.94),(.13,3.4,2.0),'wall')
 B('bathroom entry return',(.50,1.7,-.9),(1.,3.4,.13),'wall')
 B('bathroom door header',(1.59,3.02,-.9),(1.05,.76,.13),'wall')
 D('bathroom stone floor',(1.05,.012,-1.94),(2.08,.024,1.98),'stone')
 for i in range(8):D('bath tile joint',(1.05,.027,-2.9+i*.25),(2.05,.002,.006),'wall',0)
 B('vanity cabinet',(.48,.42,-1.83),(.62,.84,1.30),'wood');D('quartz vanity',(.48,.9,-1.83),(.70,.08,1.39),'stone')
 L('porcelain basin',(.50,.95,-1.83),[(0,.20),(.06,.24),(.095,.23),(.08,.15)],'linen',32,scale=(1,1,1.35))
 pipe('basin faucet',[(.25,.96,-1.83),(.25,1.19,-1.83),(.46,1.19,-1.83)],.016,'nickel')
 D('backlit mirror',(.095,1.75,-1.84),(.018,1.22,1.37),'shade');D('vanity mirror',(.114,1.75,-1.84),(.018,1.13,1.27),'mirror')
 B('shower tray',(1.53,.07,-2.48),(1.0,.14,.84),'stone')
 D('shower glass',(1.51,1.12,-2.02),(.98,2.08,.023),'glass_window');pipe('shower riser',[(2.05,.9,-2.62),(2.05,2.35,-2.62),(1.8,2.35,-2.62)],.016,'nickel')
 L('rain head',(1.8,2.31,-2.62),[(0,.13),(.035,.13)],'nickel',24)
 L('toilet pedestal',(1.56,.025,-1.34),[(0,.19),(.28,.16),(.36,.24)],'linen',24,scale=(1,1,1.25));L('toilet seat',(1.56,.4,-1.34),[(0,.24),(.06,.24)],'linen',24,scale=(1,1,1.3))
 D('toilet cistern',(1.93,.57,-1.34),(.18,.52,.40),'linen')
 for z in [-1.42,-1.63]:soft('folded hand towel',(.57,1.00,z),(.30,.045,.15))
 for z in [-2.25,-2.35]:L('toiletry bottle',(.28,.94,z),[(0,.027),(.16,.027),(.18,.012)],'accent',12)
 pipe('towel rail',[(.25,1.12,-.94),(.72,1.12,-.94)],.015,'nickel');D('hanging towel',(.48,.90,-.92),(.35,.43,.04),'linen')
def room():
 depth=CFG['depth'];terrace=KEY=='cosmopolitan';end=depth-1.22 if terrace else depth;bedx=min(end-1.55,4.20)
 B('room floor',(depth/2-.02,-.10,0),(depth-.04,.2,5.89),'roomcarpet')
 B('room ceiling',(depth/2,3.5,0),(depth,.2,6),'ceiling')
 for z in [-2.9625,2.9625]:B('party wall',(depth/2,1.75,z),(depth,3.5,.075),'wall')
 for z in [-2.64,2.64]:B('window pier',(end-.04,1.75,z),(.16,3.5,.58),'wall')
 B('window sill',(end-.04,.23,0),(.16,.46,4.74),'stone');B('window header',(end-.04,3.22,0),(.16,.56,4.74),'ceiling')
 # Cosmo terrace has an open central sliding door and a safety balustrade.
 glasswidth=1.56 if terrace else 4.73
 for z in [-1.55,1.55] if terrace else [0]:B('window glass',(end-.015,1.71,z),(.025,2.44,glasswidth),'glass_window')
 for z in [-2.36,-.79,.79,2.36]:D('slim window mullion',(end-.10,1.7,z),(.07,2.48,.045),'nickel')
 for y in [.48,2.95]:D('window track',(end-.10,y,0),(.10,.045,4.78),'wood')
 if terrace:
  B('terrace deck',(end+.61,-.085,0),(1.23,.20,5.9),'stone')
  B('terrace balustrade',(depth-.07,.60,0),(.06,1.2,5.8),'glass_window')
  for z in [-2.87,0,2.87]:D('terrace rail post',(depth-.08,.61,z),(.045,1.22,.045),'nickel')
  D('terrace handrail',(depth-.08,1.23,0),(.075,.045,5.9),'nickel');chair(end+.56,2.0,'wood',.65)
 for z in [-2.51,2.51]:
  for i in range(11):L('curtain pleat',(end-.25,.14,z+(i-5)*.067),[(0,.049),(2.86,.049)],'accent' if KEY in ['aria','cosmopolitan'] else 'linen',12,scale=(1.2,1,1))
 for z in [-2.90,2.90]:D('perimeter skirting',(depth/2,.09,z),(depth-.2,.16,.04),'wood');D('ceiling cornice',(depth/2,3.29,z),(depth-.2,.15,.14),'ceiling')
 bath(depth)
 # Clear the entry sightline. Major furniture lives to either side of z=0.
 if KEY=='planet-hollywood':
  for x in [3.15,4.83]:bed(x,-1.70,1.36,'queen');frame(x,2.55,-2.90,1.06,.57)
  B('shared queen nightstand',(3.99,.35,-2.35),(.29,.70,.55),'wood');lamp(3.99,-2.35,.72)
 elif KEY=='vdara':
  bed(4.05,-1.70,1.9)
  B('bedroom TV divider',(3.04,1.15,1.78),(.18,2.30,2.15),'wood');D('dual sided television',(3.16,1.47,1.78),(.04,.67,1.35),'black');D('living room television',(2.93,1.47,1.78),(.04,.67,1.35),'black')
 else:bed(bedx,-1.70,1.85 if depth<6 else 1.98)
 if KEY=='horseshoe':
  D('red patterned head wall',(bedx,1.81,-2.914),(3.40,2.95,.018),'accent')
  # Fine interlocking gold circles behind the leather headboard.
  for x in np.arange(bedx-1.6,bedx+1.65,.22):
   for y in np.arange(.35,3.25,.34):pipe('gold wallpaper circle',[(x+.12*math.cos(a),y+.19*math.sin(a),-2.897) for a in np.linspace(0,math.tau,19)],.005,'shade',True)
 if KEY in ['aria','waldorf']:
  for x in np.arange(2.3,depth-.3,.34):D('headwall timber batten',(x,2.93,-2.87),(.31,.23,.045),'wood')
 if KEY=='paris':
  for x in [3.0,4.1,5.2]:trim_panel(x,2.6,-2.88,.8,.67)
  frame(2.7,2.10,2.90,1.20,.95)
 if KEY=='caesars':
  for xx in [bedx-1.37,bedx+1.37]:D('full height bevelled mirror',(xx,2.20,-2.90),(.52,1.83,.04),'mirror')
  B('bench frame',(bedx,.27,-.68),(1.65,.5,.46),'trim');soft('blue upholstered bench',(bedx,.57,-.68),(1.68,.17,.5),'accent')
 if KEY=='waldorf':
  for x in [bedx-.70,bedx+.70]:D('clear bench support',(x,.27,-.68),(.055,.48,.46),'glass_window')
  soft('linen bed bench',(bedx,.53,-.68),(1.55,.15,.49),'linen')
 # Wall console / luggage storage; TV faces the beds across the walking lane.
 consolex=min(depth-1.3,4.0)
 B('media console',(consolex,.43,2.61),(2.10,.86,.58),'wood');D('stone console top',(consolex,.89,2.61),(2.18,.07,.65),'stone')
 for xx in [consolex-.77,consolex,consolex+.77]:D('console door seam',(xx,.46,2.306),(.012,.69,.018),'trim')
 D('television frame',(consolex,1.70,2.80),(1.48,.86,.075),'black');D('television screen',(consolex,1.70,2.75),(1.39,.77,.008),'mirror')
 D('remote control',(consolex+.6,.96,2.50),(.05,.025,.17),'black')
 for i in range(5):D('remote key',(consolex+.6,.976,2.45+i*.025),(.024,.003,.008),'nickel')
 if KEY=='vdara':
  B('kitchen lower cabinetry',(.51,.47,1.81),(.9,.94,2.05),'wood');D('kitchen quartz worktop',(.51,.98,1.81),(.99,.08,2.12),'stone')
  D('induction hob',(.55,1.026,2.30),(.69,.014,.58),'black')
  for z in [2.17,2.45]:L('induction ring',(.55,1.04,z),[(0,.10),(.002,.10)],'nickel',24)
  D('kitchen sink',(.55,1.031,1.18),(.61,.025,.48),'nickel');pipe('kitchen mixer',[(.23,1.02,1.18),(.23,1.31,1.18),(.5,1.31,1.18)],.017,'nickel')
  B('upper kitchen cabinets',(.36,2.22,1.85),(.65,.85,2.0),'wood');D('microwave',(.704,2.13,1.65),(.045,.38,.64),'black')
  for z in [1.1,1.7,2.3]:D('cabinet pull',(.98,.74,z),(.02,.25,.035),'nickel')
  chair(1.83,2.10,'accent');table(1.73,.97,.34)
 elif KEY=='flamingo':
  soft('pink chaise',(4.03,.44,1.43),(.93,.24,1.8),'accent');soft('chaise back',(4.41,.79,1.43),(.16,.62,1.85),'accent');proxy('chaise',(4.03,.43,1.43),(1.0,.86,1.85))
  frame(1.18,2.18,2.90,.95,.78)
  # Flamingo-shaped lamp uses a bent neck and two slender legs.
  pipe('flamingo lamp neck',[(2.76,1.10,-2.41),(2.69,1.30,-2.41),(2.77,1.43,-2.41),(2.87,1.39,-2.41)],.025,'accent')
 elif KEY in ['paris','cosmopolitan']:
  x=depth-1.7 if not terrace else 5.70
  soft('chaise cushion',(x,.50,1.44),(.88,.22,1.70),'accent');soft('chaise back',(x+.34,.82,1.44),(.18,.64,1.75),'accent');proxy('chaise',(x,.43,1.44),(1,.86,1.8));table(x-1.02,1.40,.32)
 else:
  chair(depth-1.13,1.63,'linen' if KEY in ['aria','waldorf'] else 'accent');table(depth-2.03,1.17,.33)
 # Entry wardrobe is opposite the bathroom, leaving 1.65 m through passage.
 B('wardrobe',(.45,1.25,2.15),(.83,2.5,1.51),'wood')
 for z in [1.78,2.47]:D('wardrobe handle',(.887,1.32,z),(.036,.40,.025),'nickel')
 D('closet reveal',(.879,1.3,2.12),(.008,2.32,.013),'black')
 for x,z in [(1.5,.9),(depth-1.2,.0)]:L('recessed ceiling light',(x,3.365,z),[(0,.11),(.024,.11)],'shade',24)
 b.lamp('ambient guest room',(depth*.55,2.85,.35),'#ffead0',intensity=23,distance=9)
 b.lamp('window daylight',(end-.4,2.6,0),'#c2d7e7',intensity=13,distance=6)
 b.volume('guest room',(depth/2,1.5,0),(depth-.1,3,5.8),tags=['indoors','hotel-room'])
 finish('room')
def corridor():
 B('patterned corridor floor',(0,-.09,0),(3.8,.18,6),'carpet');B('corridor ceiling',(0,3.5,0),(3.8,.2,6),'ceiling')
 for side in [-1,1]:
  for z in [-1.825,1.825]:
   B('wall beside room door',(side*1.85,1.7,z),(.2,3.4,2.35),'wall');D('wall skirting',(side*1.716,.095,z),(.065,.19,2.35),'wood')
   if KEY in ['paris','caesars','planet-hollywood']:D('dado rail',(side*1.705,.96,z),(.075,.075,2.35),'ceiling')
  B('door header',(side*1.85,3.04,0),(.2,.92,1.3),'wall')
  for z in [-.72,.72]:D('door architrave',(side*1.715,1.36,z),(.10,2.72,.13),'wood' if KEY in ['aria','vdara','waldorf','planet-hollywood'] else 'ceiling')
  D('door lintel casing',(side*1.715,2.74,0),(.10,.15,1.57),'wood' if KEY in ['aria','vdara','waldorf','planet-hollywood'] else 'ceiling')
  D('continuous crown',(side*1.64,3.27,0),(.22,.17,6),'ceiling')
  if KEY in ['cosmopolitan','flamingo']:D('ceiling light slot',(side*1.50,3.18,0),(.035,.032,6),'shade')
  for z in [1.55]:
   D('wall art surround',(side*1.704,1.85,z),(.05,1.30,.86),'wood');D('original corridor artwork',(side*1.668,1.85,z),(.019,1.17,.72),'art')
  D('sconce backplate',(side*1.706,2.13,-1.12),(.08,.40,.22),'trim')
  D('sconce diffuser',(side*1.56,2.16,-1.12),(.22,.34,.28),'shade')
 for z in [-1.5,1.5]:
  if KEY=='vdara':
   for y,r in [(3.13,.35),(3.20,.39),(3.27,.42)]:L('ringed brass pendant',(0,y,z),[(0,r),(.05,r)],'trim',40)
   L('pendant diffuser',(0,3.08,z),[(0,.31),(.07,.31)],'shade',32)
  elif KEY=='aria':
   for x in [-.35,0,.35]:L('clustered ceiling drum',(x,3.13,z),[(0,.19),(.17,.19)],'shade',24)
  else:
   L('ceiling drum',(0,3.08,z),[(0,.34),(.24,.34)],'shade',40)
   for y in [3.07,3.33]:L('drum metal band',(0,y,z),[(0,.351),(.025,.351)],'trim',40)
   if KEY in ['paris','waldorf']:
    for i in range(10):
     a=i*math.tau/10;pipe('lantern upright',[(.347*math.cos(a),3.10,z+.347*math.sin(a)),(.347*math.cos(a),3.31,z+.347*math.sin(a))],.008,'wood')
  b.lamp('corridor warm pool '+str(z),(0,2.85,z),'#ffead2',intensity=12,distance=6)
 b.volume('guest corridor',(0,1.5,0),(3.1,3,5.9),tags=['indoors','corridor']);finish('corridor')
def door():
 D('door leaf',(0,0,0),(1.285,2.63,.13),'door')
 for side in [-1,1]:
  z=side*.075
  if KEY in ['paris','caesars','cosmopolitan','planet-hollywood']:trim_panel(0,.30,z,.98,1.58);trim_panel(0,-.91,z,.98,.40)
  D('electronic lock',(.47,-.28,side*.091),(.095,.24,.035),'nickel');D('keycard reader',(.47,-.20,side*.113),(.064,.08,.012),'black');D('door lever',(.40,-.32,side*.135),(.18,.025,.035),'nickel')
  D('peephole',(0,.35,side*.081),(.025,.025,.012),'nickel')
 finish('door')
def _stairs(*a,**k):
 # bmlevel lost stairs(waist=) on 2026-10-05; the stair modules were exported before that. A run that only re-exports
 # other module kinds (GUEST_ONLY without 'stair') builds them without it; one that exports stairs must not.
 import inspect
 if 'waist' not in inspect.signature(b.stairs).parameters:
  if not ONLY or 'stair' in ONLY:raise RuntimeError('bmlevel.stairs() has no waist= any more: restore it before re-exporting stair modules')
  k.pop('waist',None)
 return b.stairs(*a,**k)
def structure(key):
 # Exact proven stair geometry, distinct local materials for each hotel.
 start(key)
 b.slab('lower landing',(0,-3.65),(6.8,2.4),M('stone'),thickness=.18)
 b.slab('hallway threshold',(0,-4.975),(1.8,.25),M('stone'),thickness=.18)
 b.slab('middle landing',(0,3.65),(6.8,2.35),M('stone'),y=1.8,thickness=.18)
 with b.context('outbound flight',origin=(-1.65,0,-2.5)):_stairs('outbound',(0,0,0),1.8,5,M('stone'),width=2.8,rail=M('trim'),waist=.22)
 with b.context('return flight',origin=(1.65,1.8,2.5),yaw=math.pi):_stairs('return',(0,0,0),1.8,5,M('stone'),width=2.8,rail=M('trim'),waist=.22)
 for side in [-1,1]:B('shaft sidewall',(side*3.55,1.8,0),(.3,3.6,9.9))
 B('shaft rear',(0,1.8,4.95),(7.4,3.6,.3))
 for x in [-2.25,2.25]:B('shaft front pier',(x,1.8,-4.95),(2.7,3.6,.3))
 B('shaft lintel',(0,3.14,-4.95),(1.8,.88,.3))
 D('landing diffuser',(0,3.35,-3.65),(1.1,.06,.55),'shade');b.lamp('landing light',(0,2.9,-3.65),'#ffe4bd',intensity=17,distance=8);finish('stair')
 start(key);height=next(t['firstGuestFloor'] for t in RECIPES if t['set']==key)*3.6
 for side in [-1,1]:B('podium side cladding',(side*3.83,height/2,0),(.24,height,10.65))
 B('podium rear',(0,height/2,5.23),(7.42,height,.24))
 for side in [-1,1]:B('entry pier',(side*2.305,1.325,-5.23),(2.79,2.65,.24))
 B('entry headwall',(0,(height+2.65)/2,-5.23),(7.42,height-2.65,.24))
 for side in [-1,1]:
  D('full height timber pilaster',(side*3.53,height/2,-5.42),(.30,height,.21),'wood')
  D('stone dado',(side*2.3,.50,-5.38),(2.6,1.,.09),'stone')
  D('entry wall sconce',(side*2.0,2.3,-5.52),(.28,.57,.24),'shade')
 for x in [-1.04,1.04]:D('recessed entry door surround',(x,1.38,-5.41),(.20,2.76,.22),'wood')
 D('entry overdoor',(0,2.91,-5.42),(2.28,.32,.22),'wood')
 # the lower moulding stops at the stair door's surrounds: run across it, it barred the doorway at 1 m (2026-10-08)
 for side in [-1,1]:D('continuous podium moulding',(side*2.43,1.05,-5.44),(2.78,.13,.24),'trim')
 D('continuous podium moulding',(0,height-.2,-5.44),(7.62,.13,.24),'trim')
 finish('entry')
 start(key);B('sealed panel',(0,1.7,-2.42),(6.8,3.4,.18));D('sealed stripe',(0,1.55,-2.30),(3,.05,.04),'trim');finish('cap')
 start(key);D('shaft streaming closure',(0,-.09,0),(7.4,.18,10.2));finish('closure')

if __name__=='__main__':
 wanted=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(SETS)
 structure_only='--structure-only' in wanted;wanted=[w for w in wanted if w!='--structure-only'] or list(SETS)
 for key in wanted:
  structure(key)
  if structure_only:continue
  for fn in [corridor,room,door]:start(key);fn()
 print('ALL RESORT GUEST SETS COMPLETE',flush=True)
