"""Cosmopolitan: reference-led twin towers and a limited walkable casino podium."""
import bpy, math, random
from bmlevel import mat,box,slab,door,volume,link,landmark,lamp,level,scene

def build_cosmopolitan():
    batches={};labels=[];serial=0;rng=random.Random(3708)
    palette=[('co_metal',(.35,.4,.43),.72,.32,0),('co_dark',(.035,.053,.068),.35,.42,0),('co_glass',(.095,.19,.25),.72,.2,0),('co_glass2',(.13,.24,.29),.7,.23,0),('co_glass3',(.085,.155,.195),.68,.22,0),('co_rail',(.14,.25,.29),.62,.26,0),('co_stone',(.46,.43,.38),.05,.65,0),('co_white',(.72,.7,.62),.06,.55,0),('co_floor',(.095,.083,.072),.12,.38,0),('co_carpet',(.10,.027,.045),0,.95,0),('co_bronze',(.36,.22,.085),.7,.32,0),('co_blue',(.07,.3,.75),.1,.3,1.6),('co_gold',(1,.62,.25),.1,.32,1.3),('co_crystal',(.65,.49,.7),.5,.18,.25),('co_pool',(.035,.24,.27),.4,.15,0)]
    for n,c,m,r,e in palette:mat(n,c,metal=m,roughness=r,glow=e)
    def uid(n):
        nonlocal serial
        serial+=1;return f'Cosmopolitan {serial:05d} {n}'
    def mesh(n,vs,fs,m):
        me=bpy.data.meshes.new(uid(n));me.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);me.update();o=bpy.data.objects.new(me.name,me);scene.collection.objects.link(o);me.materials.append(bpy.data.materials[m]);level.visual_points.extend(vs);return o
    def D(n,p,s,m='co_metal',yaw=0):
        vs,fs=batches.setdefault(m,([],[]));base=len(vs);c,t=math.cos(yaw),math.sin(yaw)
        for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            x,y,z=a*s[0]/2,b*s[1]/2,d*s[2]/2;vs.append((p[0]+c*x+t*z,p[1]+y,p[2]-t*x+c*z))
        fs.extend(tuple(base+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    def B(n,p,s,m='co_dark'):box(uid(n),p,s,m)
    def label(n,string,p,size=1,yaw=0):
        cr=bpy.data.curves.new(uid(n),'FONT');cr.body=string;cr.align_x='CENTER';cr.size=size;cr.extrude=.018
        o=bpy.data.objects.new(cr.name,cr);scene.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.rotation_euler=(math.pi/2,0,yaw);cr.materials.append(bpy.data.materials['co_white']);labels.append(o)
    def tower(n,x,z,w,d,h,floors,slope=False):
        base=16;step=(h-base-6)/floors
        B(n+' structural silhouette',(x,(h+base-6)/2,z),(w-2.8,h-base-6,d-2.8))
        # Each floor has an actual projecting slab, recessed glazing, balcony
        # balustrade, privacy screens and mullions, on all four elevations.
        for f in range(floors):
            y=base+f*step
            D(n+' floor slab',(x,y,z),(w,.22,d),'co_metal')
            for side in [-1,1]:
                for j in range(round(w/3.6)):
                    pitch=w/round(w/3.6);xx=x-w/2+(j+.5)*pitch
                    m=['co_glass','co_glass2','co_glass3'][(j+f//6)%3]
                    D('north south recessed pane',(xx,y+step/2,z+side*(d/2-1.38)),(pitch-.1,step-.24,.1),m)
                    D('north south balcony glass',(xx,y+.66,z+side*(d/2-.12)),(pitch-.12,1,.08),'co_rail')
                    D('balcony handrail',(xx,y+1.18,z+side*(d/2-.12)),(pitch,.055,.09))
                    D('balcony dividing screen',(xx-pitch/2,y+step*.47,z+side*(d/2-.72)),(.11,step*.88,1.3),'co_dark')
                for j in range(round(d/3.6)):
                    pitch=d/round(d/3.6);zz=z-d/2+(j+.5)*pitch
                    # Curtain-wall core at the south end contrasts with terraces.
                    balcony=j<round(d/3.6)*.78
                    xx=x+side*(w/2-(1.38 if balcony else .18))
                    D('east west pane',(xx,y+step/2,zz),(.1,step-.24,pitch-.1),['co_glass','co_glass2','co_glass3'][(j+f//8)%3])
                    D('vertical mullion',(xx+side*.08,y+step/2,zz-pitch/2),(.1,step,.075))
                    if balcony:
                        D('side balcony glass',(x+side*(w/2-.12),y+.66,zz),(.08,1,pitch-.1),'co_rail')
                        D('side handrail',(x+side*(w/2-.12),y+1.18,zz),(.09,.055,pitch))
                        D('side privacy',(x+side*(w/2-.72),y+step*.47,zz-pitch/2),(1.3,step*.88,.11),'co_dark')
            if f%10==0:
                for side in [-1,1]:D('blue architectural band',(x,y+.23,z+side*(d/2+.02)),(w,.06,.055),'co_blue')
        roof=h-6
        B(n+' crown base',(x,roof+1,z),(w,2,d),'co_glass')
        vs=[(x+a*w/2,roof+2,z+b*d/2) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        vs += [(xx,h-(0 if zz<z else 4) if slope else h,zz) for xx,yy,zz in vs]
        mesh(n+' sculpted crown',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'co_glass3')
        for side in [-1,1]:
            D('corner vertical edge',(x+side*w/2,base+(h-base-6)/2,z-d/2),(.2,h-base-6,.22))
        label(n+' north crown','THE COSMOPOLITAN',(x,h-3.1,z-d/2-.15),min(2.0,w/14),math.pi)
        label(n+' east crown','COSMOPOLITAN',(x+w/2+.15,h-4,z),min(2.6,d/12),math.pi/2)
    tower('Boulevard Tower',-66,218,40,76,180,49,True)
    tower('Chelsea Tower',-165,231,70,34,184,51)
    # Podium: solid upper decks above a genuinely hollow, traversable casino.
    slab(uid('casino floor'),(-119,234.5),(180,79),'co_floor',y=.06)
    B('podium ceiling',(-119,8.75,234.5),(180, .5,79),'co_stone')
    B('upper podium mass',(-119,12.5,234.5),(180,7,79),'co_dark')
    B('Boulevard pool support',(-40,8,182),(22,16,26),'co_dark')
    def wall(n,axis,at,start,end,opening=None,m='co_stone'):
        spans=[(start,end,0,8.5)]
        if opening:
            mid,width=opening;spans=[(start,mid-width/2,0,8.5),(mid+width/2,end,0,8.5),(mid-width/2,mid+width/2,4.3,8.5)]
        for a,b,lo,hi in spans:
            p=(at,(lo+hi)/2,(a+b)/2) if axis=='x' else ((a+b)/2,(lo+hi)/2,at)
            s=(.55,hi-lo,b-a+.05) if axis=='x' else (b-a+.05,hi-lo,.55)
            B(n,p,s,m)
    wall('east entrance wall','x',-29,195,274,(242,6),'co_glass3')
    wall('north exit wall','z',195,-209,-29,(-135,4),'co_glass3')
    wall('south wall','z',274,-209,-29)
    wall('west loading wall','x',-209,195,274,(242,4))
    wall('service partition','x',-177,195,274,(242,4))
    wall('stock room partition','z',238,-209,-177,(-191,3))
    wall('staff room partition','z',246,-209,-177,(-191,3))
    for n,p,yaw,w in [('Strip entrance',(-29,0,242),math.pi/2,6),('Bellagio-side entrance',(-135,0,195),0,4),('service entrance',(-177,0,242),math.pi/2,4),('west escape',(-209,0,242),math.pi/2,4),('stock door',(-191,0,238),0,3),('staff door',(-191,0,246),0,3)]:
        door('Cosmopolitan '+n,p,yaw=yaw,width=w,height=4.3)
    # Readable street facade, layered black/bronze frames and deep overhang.
    for yy in [3.9,8.6,12,16.1]:
        D('Strip fascia',(-28.6,yy,234.5),(.35,.45,79),'co_bronze')
        D('north fascia',(-119,yy,194.6),(180,.4,.35),'co_metal')
    for zz in range(198,273,4):
        if abs(zz-242)>4:D('Strip vertical mullion',(-28.5,7.8,zz),(.3,15.6,.23),'co_bronze')
    B('entrance overhang',(-25.8,5,242),(7,.45,12),'co_metal')
    label('entry sign','THE COSMOPOLITAN',(-22.15,5.5,242),.72,math.pi/2)
    D('front digital screen',(-28.15,11.5,263),(.12,7,15),'co_dark')
    label('digital artwork','AFTER THE LIGHT',(-28,11.5,263),.55,math.pi/2)
    for zz in range(257,270):D('screen damaged lines',(-27.96,9+(zz%3),zz),(.04,.08,.65),'co_blue')
    # Northern low-rise neighbors preserve the characteristic uneven base line.
    for x,w in [(-111,35),(-169,34)]:
        B('Jockey Club contextual low rise',(x,11,180),(w,22,20),'co_white')
        for y in range(3,22,3):
            for xx in range(int(x-w/2+2),int(x+w/2),3):D('low rise window',(xx,y,169.9),(1.5,1.8,.1),'co_dark')
        D('low rise cornice',(x,22.1,180),(w+1,.3,21),'co_white')
    # Pool terrace along the Strip: recessed water, coping, lounge furniture.
    D('pool deck',(-40,16.18,198),(22,.3,58),'co_stone')
    D('Boulevard Pool',(-39,16.36,190),(12,.08,23),'co_pool')
    for x in [-45.3,-32.7]:D('pool coping',(x,16.4,190),(.6,.3,24),'co_white')
    for z in [178.2,201.8]:D('pool coping',(-39,16.4,z),(13,.3,.6),'co_white')
    for zz in range(206,226,3):
        for xx in [-46,-34]:
            D('sun lounger',(xx,16.65,zz),(1,.35,2.2),'co_white');D('lounger cushion',(xx,16.86,zz),( .85,.08,1.9),'co_dark')
    for zz in range(171,227,3):D('pool balustrade',(-28.8,16.9,zz),(.08,1.4,2.9),'co_rail')
    # Clear 6 m axial aisle: props are set back from x axis z242.
    D('central carpet',(-104, .115,242),(142,.08,5),'co_carpet')
    for x in [-155,-135,-115,-95,-75,-55]:
        for z in [208,228,260]:
            if x==-135 and z<=242:continue
            B('casino column',(x,4.25,z),(1.2,8.5,1.2),'co_dark')
            for a in [-.64,.64]:D('column brass inlay',(x+a,4.2,z),(.04,8,.95),'co_bronze')
    for x in [-151,-119,-87,-55]:
        for z in [218,260]:
            B('gaming table base',(x,.55,z),(2,.9,1.5))
            D('gaming table top',(x,1.05,z),(3.6,.22,2.1),'co_carpet')
            for dx in [-1.3,0,1.3]:
                D('chair seat',(x+dx,.55,z-1.8),(.65,.18,.65),'co_dark');D('chair back',(x+dx,.95,z-2.1),(.65,.8,.15),'co_carpet')
    for x in [-163,-145,-111,-93]:
        for z in [203,207,255,259,263,267]:
            B('slot cabinet',(x,.85,z),(1.1,1.7,.9))
            D('slot chrome frame',(x,1.2,z-.48),(.94,.85,.09),'co_bronze')
            D('slot dark display',(x,1.2,z-.54),(.8,.65,.06),'co_glass')
            if rng.random()<.2:D('slot surviving screen',(x,1.2,z-.58),(.65,.5,.02),'co_blue')
            D('slot console',(x,.77,z-.65),(1,.14,.4),'co_metal')
    # Suspended crystal strands form the hourglass silhouette of The Chandelier.
    cx,cz=-59,218
    for i in range(96):
        a=i*math.tau/96
        for j in range(16):
            y=2.5+j*.36;r=3.2+1.6*((y-5.2)/3)**2
            D('crystal pendant',(cx+r*math.cos(a),y,cz+r*math.sin(a)),(.075,.22,.075),'co_crystal')
    B('Chandelier bar island',(cx, .65,cz),(4,1.3,3),'co_dark')
    D('Chandelier bar counter',(cx,1.35,cz),(5,.2,4),'co_bronze')
    label('bar name','THE CHANDELIER',(-59,2,213),.42,math.pi)
    # Ceiling coffers and warm cove lighting.
    for x in range(-167,-35,12):
        for z in [204,222,260]:
            D('ceiling coffer',(x,8.42,z),(8,.13,7),'co_dark');D('ceiling glowing strip',(x,8.31,z-3.45),(7.7,.05,.05),'co_gold')
    for x in [-155,-115,-75,-40]:
        for z in [213,243,264]:lamp(uid('casino warm light'),(x,6.8,z),'#eec69d',80,26)
    lamp(uid('crystal light'),(-59,5.8,218),'#d7b3df',100,18)
    for z in [216,261]:
        for x in [-204,-181]:
            B('supply shelving',(x,1.2,z),(1.2,2.4,14),'co_metal')
            for yy in [.4,1.2,2]:
                for zz in range(z-6,z+7,3):D('stored cartons',(x,yy,zz),(.85,.6,1.8),'co_stone')
        lamp(uid('service light'),(-192,5,z),'#b4c6d4',65,22)
    # Restrained decay without obscuring the architecture or blocking the route.
    for i in range(45):
        x=rng.uniform(-171,-33);z=rng.choice([rng.uniform(196,201),rng.uniform(270,273)])
        D('fallen facade fragment',(x,.1,z),(rng.uniform(.1,.7),.15,rng.uniform(.2,.9)),'co_stone',rng.random()*6)
    for name,p,size,roof in [('casino',(-103,4.25,234.5),(147.4,8.5,78.4),True),('service corridor',(-193,4.25,242),(31.4,8.5,7.4),True),('stock room',(-193,4.25,216.5),(31.4,8.5,42.4),True),('staff room',(-193,4.25,260),(31.4,8.5,27.4),True),('Strip approach',(-23,2,242),(3,4,4),False),('north approach',(-135,2,190),(3,4,4),False),('west approach',(-213,2,242),(3,4,4),False)]:
        volume('Cosmopolitan '+name,p,size,roofed=roof,tags=['cosmopolitan','interior' if roof else 'route'])
    # Separate narrow route volumes keep audit rays clear of the gaming banks.
    for name,p in [('east aisle',(-35,2,242)),('central aisle',(-103,2,242)),('service aisle',(-170,2,242)),('north aisle',(-135,2,202)),('north junction',(-135,2,242)),('service junction',(-191,2,242)),('stock aisle',(-191,2,216)),('staff aisle',(-191,2,260))]:volume('Cosmopolitan '+name,p,(2,4,2),roofed=False,tags=['route'])
    for a,b,d in [('Strip approach','east aisle','Strip entrance'),('east aisle','central aisle',None),('central aisle','service aisle',None),('service aisle','service junction','service entrance'),('service junction','west approach','west escape'),('service junction','stock aisle','stock door'),('service junction','staff aisle','staff door'),('north approach','north aisle','Bellagio-side entrance'),('north aisle','north junction',None),('north junction','central aisle',None)]:link('Cosmopolitan '+a,'Cosmopolitan '+b,door='Cosmopolitan '+d if d else None)
    landmark('Cosmopolitan supply staging',(-192,.1,218),tags=['supply-reserve'])
    landmark('Cosmopolitan staff hide',(-192,.1,262),tags=['horde-hide-reserve'])
    landmark('Cosmopolitan entrance',(-23,.1,242),tags=['entrance'])
    print('Cosmopolitan geometry assembled; converting labels',flush=True)
    for m,(vs,fs) in batches.items():mesh('batched '+m,vs,fs,m)
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    for o in labels:
        me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));ob=bpy.data.objects.new(o.name+' glyphs',me);scene.collection.objects.link(ob);ob.matrix_world=o.matrix_world.copy();bpy.data.objects.remove(o,do_unlink=True)
    return {'boulevardTower':[-66,180,218],'chelseaTower':[-165,184,231],'entry':[-23,.1,242],'supplyReserve':[-192,.1,218],'hideReserve':[-192,.1,262]}
