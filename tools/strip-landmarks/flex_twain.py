"""Original FLEX public shell and inferred room arrangement; references in block record."""
from common import *
KEY='flex-twain';ID='way/390003972';YAW=math.pi

def build(B):
 p=footprint(ID);F=Frame(B,1889.0,-555.15,YAW,y=0);E=Frame(B,1894.82,-550.3,math.pi/2,y=0)
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 entry=dict(p=E.p(0,.16,0),yaw=math.pi/2,width=1.65,height=2.55,name='Public lounge entrance',venue=KEY)
 B.shell(p,.05,5.7,'fx-stucco',roof=False,openings=[entry]);B.planar('fx-roof',p,5.55);B.planar('fx-foundation',p,.16,True)
 # Broad dark north and east parapets with two-sided raised identity.
 F.box('fx-fascia',(0,4.55,.12),(11.5,2.3,.24));F.text('FLEX',(0,4.72,.27),1.1,'fx-letter',back=True);F.text('COCKTAIL LOUNGE',(0,3.92,.28),.24,'fx-letter',back=True)
 E.box('fx-fascia',(-1,4.55,.13),(8.0,2.3,.25));E.text('FLEX',(-1,4.72,.29),1.0,'fx-letter',back=True)
 F.box('fx-awning',(0,3.22,.9),(11.8,.20,1.8));E.box('fx-awning',(-.8,3.22,.9),(7.7,.20,1.8))
 # RGB trim is surface emission only; fixtures use the existing shared light pool.
 for k,c in enumerate(['fx-red','fx-gold','fx-green','fx-blue','fx-violet']):F.box(c,(-4.7+k*2.35,3.24,1.83),(2.35,.055,.055))
 for u in [-5.5,-2.7,0,2.7,5.5]:F.tube('fx-metal',(u,.2,1.6),(u,3.1,1.6),.04,10)
 F.box('fx-planter',(0,.45,2.3),(11.7,.72,.6),True)
 for u in np.arange(-5.3,5.4,.65):F.lathe('fx-leaf',float(u),2.3,[(.78,.05),(.9,.23),(1.4,.20),(1.65,0)],9)
 F.box('fx-paving',(0,.08,.9),(11.9,.16,1.9),True);E.box('fx-paving',(0,.08,1.0),(2.7,.16,2.2),True)
 for u in [-.90,.90]:E.box('fx-metal',(u,1.5,.10),(.12,2.8,.2))
 E.box('fx-metal',(0,2.88,.12),(1.9,.12,.22));E.text('501',(0,3.02,.26),.23,'fx-letter',back=True)
 E.box('fx-sign',(3.0,1.7,.12),(3.4,1.5,.12));E.text('FLEX',(3,1.9,.21),.6,'fx-letter',back=True);E.text('COCKTAIL LOUNGE',(3,1.3,.21),.16,'fx-letter',back=True)
 F.tube('fx-metal',(-7.4,.1,4.7),(-7.4,7.3,4.7),.14,12);F.box('fx-fascia',(-7.4,7,4.7),(3.0,1.55,.5));F.text('FLEX',(-7.4,7,4.98),.75,'fx-letter',back=True)
 for u,v in [(-2,-12),(2,-15)]:F.box('fx-metal',(u,5.95,v),(1.4,.7,1.2))
 # Public room within mapped footprint. Rear service zone is sealed.
 B.property=KEY+'-interior';B.source='public/'+KEY
 F.box('fx-floor',(0,.18,-8.5),(10.4,.04,16.6));F.box('fx-ceiling',(0,3.35,-8.5),(10.4,.15,16.6))
 F.box('fx-wall',(5.15,1.76,-8.5),(.15,3.14,16.6),True)
 # East wall splits around the real side entrance; no trim spans the opening.
 for a,b in [(-.2,-3.9),(-5.85,-16.8)]:F.box('fx-wall',(-5.15,1.76,(a+b)/2),(.15,3.14,abs(b-a)),True)
 for v in [-.23,-16.75]:F.box('fx-wall',(0,1.76,v),(10.35,3.14,.15),True)
 rng=random.Random(330)
 for row in range(22):
  v=-.35-row*.74
  for k in range(9):
   u=-5.05+k*1.18+(row%2)*.59;a=max(-5.05,u);b=min(5.05,u+1.16)
   if b>a:F.box('fx-tile-'+str(rng.randrange(4)),((a+b)/2,.207,v-.35),(b-a,.009,.72))
 # Bar with stainless service aisle and fifteen original, nonfunctional gaming panels.
 F.box('fx-bar',(-2.7,.69,-9.4),(1.0,1.0,7.4),True);F.box('fx-metal',(-2.7,1.23,-9.4),(1.2,.10,7.6))
 for v in np.linspace(-6.05,-12.65,15):
  F.box('fx-frame',(-2.43,1.30,float(v)),(.40,.09,.34));F.box('fx-screen',(-2.43,1.352,float(v)),(.32,.012,.26))
  F.box('fx-blue',(-2.18,1.31,float(v)),(.04,.04,.09))
 for v in np.arange(-6.1,-12.7,-.88):
  F.lathe('fx-metal',-1.55,float(v),[(.21,.23),(.27,.23),(.30,.045),(.83,.045),(.87,.27)],16);F.lathe('fx-leather',-1.55,float(v),[(.87,0),(.87,.27),(.97,.27),(.97,0)],18)
 F.box('fx-metal',(-4.65,.7,-9.4),(.55,1,7.4),True)
 for h in [1.25,2.0,2.65]:F.box('fx-metal',(-4.65,h,-9.4),(.65,.055,7.4))
 for v in np.arange(-6,-12.8,-.28):
  for h in [1.30,2.05]:F.lathe('fx-bottle-'+str(rng.randrange(3)),-4.65,float(v),[(h,.055),(h+.20,.055),(h+.25,.023),(h+.32,.023)],9)
 for v in [-7,-10,-12]:
  F.box('fx-sink',(-4.62,1.3,v),(.38,.07,.55));F.path('fx-metal',[(-4.4,1.3,v),(-4.4,1.62,v),(-4.58,1.62,v)],.02,8)
 # Lounge reference: round tables, curved quilted chairs and stone fireplace.
 def chair(u,v,yaw):
  C=Frame(B,F.p(u,0,v)[0],F.p(u,0,v)[2],YAW+yaw,y=0)
  C.lathe('fx-leather',0,0,[(.35,0),(.35,.34),(.53,.37),(.60,.36),(.60,0)],20)
  # Continuous curved upholstery, including top and end caps; no slatted gaps.
  for a,b in zip(np.linspace(0,math.pi,33),np.linspace(0,math.pi,33)[1:]):
   for r in [.34,.46]:B.face('fx-leather',[C.p(r*math.cos(a),.53,r*math.sin(a)),C.p(r*math.cos(b),.53,r*math.sin(b)),C.p(r*math.cos(b),1.14,r*math.sin(b)),C.p(r*math.cos(a),1.14,r*math.sin(a))])
   B.face('fx-leather',[C.p(.34*math.cos(a),1.14,.34*math.sin(a)),C.p(.34*math.cos(b),1.14,.34*math.sin(b)),C.p(.46*math.cos(b),1.14,.46*math.sin(b)),C.p(.46*math.cos(a),1.14,.46*math.sin(a))])
  for a in [0,math.pi]:B.face('fx-leather',[C.p(.34*math.cos(a),.53,.34*math.sin(a)),C.p(.46*math.cos(a),.53,.46*math.sin(a)),C.p(.46*math.cos(a),1.14,.46*math.sin(a)),C.p(.34*math.cos(a),1.14,.34*math.sin(a))])
  for a in np.linspace(.1,math.pi-.1,10):C.tube('fx-stitch',(.38*math.cos(a),.63,.38*math.sin(a)),(.38*math.cos(a),1.09,.38*math.sin(a)),.008,5)
 for u,v in [(2.4,-2.7),(2.4,-5.4)]:
  F.lathe('fx-metal',u,v,[(.21,.34),(.25,.34),(.28,.06),(.88,.06)],18);F.lathe('fx-table',u,v,[(.88,0),(.88,.72),(.95,.72),(.95,0)],32)
  chair(u-1.15,v,math.pi/2);chair(u+1.15,v,-math.pi/2)
 F.box('fx-stone',(2.5,1.6,-.43),(4.6,2.7,.2));F.box('fx-dark',(2.5,.9,-.56),(3.5,.63,.08));F.box('fx-table',(2.5,1.4,-.65),(4.1,.09,.32))
 for row in range(8):
  for k in range(9):
   u=.28+k*.50
   if row<3 and .75<u<4.25:continue
   F.box('fx-stone-'+str((row+k)%3),(u,.37+row*.32,-.56),(.48,.29,.05))
 F.box('fx-dark',(2.5,2.42,-.57),(3.5,1.0,.06));F.text('FLEX',(2.5,2.43,-.62),.7,'fx-blue',back=False)
 # Rear stage and short physical stairs, with original screen graphics.
 F.box('fx-stage',(1.1,.47,-15.5),(7.0,.54,2.3),True)
 for i in range(3):F.box('fx-stage',(1.1,.20+(i+1)*.09,-13.55-i*.30),(2.6,(i+1)*.18,.32),True)
 F.box('fx-screen',(1.1,2.05,-16.55),(7,2.25,.1));F.text('FLEX',(1.1,2.15,-16.47),1.25,'fx-blue',back=True);F.text('COCKTAIL LOUNGE',(1.1,1.3,-16.46),.26,'fx-letter',back=True)
 for u in [-2.7,4.9]:F.box('fx-dark',(u,.65,-14.8),(.6,.9,.6),True)
 for u in [-3.5,0,3.5]:
  F.box('fx-blue',(u,3.22,-8),(.06,.06,14.5))
 for v in [-4,-9,-14]:
  F.tube('fx-metal',(0,3.25,v),(0,2.85,v),.02,8);F.lathe('fx-metal',0,v,[(2.48,0),(2.52,.16),(2.65,.24),(2.78,.16),(2.82,0)],16)
 for v in [-3,-9,-14]:F.light(0,2.8,v,power=45,range=9)
 # Routes deliberately avoid seating, bar furniture and private areas.
 route=[E.p(0,.16,2.2),E.p(0,.16,.4),F.p(-3.5,.20,-4.85),F.p(0,.20,-4.85),F.p(0,.20,-9.5),F.p(2.8,.20,-11.5)]
 views={n:dict(eye=F.p(*e),target=F.p(*t)) for n,e,t in [('entrance',(-3.5,1.8,-4.85),(2,1.3,-3)),('lounge',(0,1.8,-5),(2.5,1.6,-1)),('bar',(0,1.8,-9),(-3.7,1.3,-10)),('stage',(2.8,1.8,-11.5),(1,1.7,-16))]}
 return dict(key=KEY,name='FLEX Twain',center=[p.centroid.x,0,p.centroid.y],bounds=[p.bounds[0]-2,p.bounds[1]-6,p.bounds[2]+4,p.bounds[3]+1],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(0,.16,-.2),yaw=YAW+math.pi,width=10.4,depth=16.6,height=3.1)],lights=B.lights,hotelSources=[],routes=[dict(name='Side entry, lounge, bar and stage approach',points=route)],views=views)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
