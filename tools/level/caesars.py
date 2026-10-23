"""Reference-led Caesars Palace complex, with a walkable casino and service suite."""
import math
import bpy
from placement import checkpoint,relocate
from bmlevel import mat,context,prism,slab,door,volume,link,landmark,lamp,level,scene


def curved_crown_geometry():
    vs=[];fs=[]
    for i in range(40):
        a=math.radians(-66.4+i*132/40);b=math.radians(-66.4+(i+1)*132/40);base=len(vs)
        vs.extend((-158+r*math.cos(t),y,243+r*math.sin(t)) for y in [48.8,49.15] for r,t in [(24.3,a),(37.7,a),(37.7,b),(24.3,b)])
        fs.extend(tuple(base+j for j in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    return vs,fs

def build_caesars(api):
    serial=0; batches={}
    def uid(n):
        nonlocal serial
        serial+=1;return f'Caesars {serial:05d} {n}'
    def mesh(n,vs,fs,m):
        me=bpy.data.meshes.new(uid(n));me.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);me.update()
        ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob);me.materials.append(bpy.data.materials[m])
        level.visual_points.extend(vs)
        return ob
    def flush():
        for m,(vs,fs) in batches.items():mesh('batched '+m,vs,fs,m)
        batches.clear()
    def D(n,p,size,m='c_stone',yaw=0):
        # Batch architectural trim by material to keep the editable build responsive.
        vs,fs=batches.setdefault(m,([],[]));base=len(vs);c,s=math.cos(yaw),math.sin(yaw)
        for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
            x,y,z=sx*size[0]/2,sy*size[1]/2,sz*size[2]/2
            vs.append((p[0]+c*x+s*z,p[1]+y,p[2]-s*x+c*z))
        fs.extend(tuple(base+i for i in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    def B(n,p,size,m='c_stone',**kw):return api['box'](uid(n),p,size,m,**kw)
    def lathe(n,x,z,profile,m='c_stone',count=32):
        vs=[(x+r*math.cos(i*math.tau/count),y,z+r*math.sin(i*math.tau/count)) for r,y in profile for i in range(count)]
        fs=[(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(len(profile)-1) for i in range(count)]
        fs.extend([tuple(reversed(range(count))),tuple(range((len(profile)-1)*count,len(profile)*count))]);return mesh(n,vs,fs,m)
    def column(x,z,y=0,h=9,r=.5):
        lathe('Roman column',x,z,[(r*1.45,y),(r*1.45,y+.3),(r,y+.65),(r*.88,y+h-.8),(r*1.45,y+h-.6),(r*1.45,y+h)],'c_stone',20)
        D('Corinthian capital',(x,y+h-.35,z),(r*3,.7,r*3))
        for i in range(12):
            a=i*math.tau/12;D('column flute',(x+r*.93*math.cos(a),y+h/2,z+r*.93*math.sin(a)),(.045,h-1.8,.045),'c_shadow')
    def roof(x,z,w,d,y,h):
        vs=[(x+sx*ww/2,yy,z+sz*dd/2) for ww,dd,yy in [(w,d,y),(w*.73,d*.90,y+h)] for sx,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        mesh('red pitched crown',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'c_red')
        D('roof ridge',(x,y+h+.2,z),(w*.75,.4,d*.92))
        for side in [-1,1]:D('roof edge',(x+side*w/2,y+.12,z),(.6,.5,d+.4))
    def arch(x,y,z,w,h,yaw=0):
        c,s=math.cos(yaw),math.sin(yaw);r=w/2;spring=h-r
        def P(u,v,o):return(x+c*u+s*o,y+v,z-s*u+c*o)
        D('arched recess',P(0,spring/2,-.03),(w,spring,.12),'c_glass',yaw)
        vs=[P(0,spring,-.09)]+[P(r*math.cos(i*math.pi/16),spring+r*math.sin(i*math.pi/16),-.09) for i in range(17)]
        mesh('arched window fan',vs,[tuple(range(len(vs)))],'c_glass')
        for side in [-1,1]:D('arch jamb',P(side*(r+.1),spring/2,.10),(.2,spring,.3),'c_stone',yaw)
        vs=[];fs=[]
        for i in range(16):
            a,b=i*math.pi/16,(i+1)*math.pi/16;base=len(vs)
            vs.extend(P(rr*math.cos(t),spring+rr*math.sin(t),o) for o in [-.03,.25] for rr,t in [(r,a),(r,b),(r+.22,b),(r+.22,a)])
            fs.extend(tuple(base+j for j in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        mesh('arch surround',vs,fs,'c_stone')
    def pediment(x,z,w,y,yaw=math.pi/2):
        c,s=math.cos(yaw),math.sin(yaw)
        def P(u,v,o):return(x+c*u+s*o,y+v,z-s*u+c*o)
        vs=[P(u,v,o) for o in [-.3,.3] for u,v in [(-w/2,0),(w/2,0),(0,w*.2)]]
        mesh('Roman triangular pediment',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'c_stone')
        D('pediment base',P(0,-.25,0),(w+.7,.55,1),'c_stone',yaw)
    for n,c,metal,rough in [('c_stone',(.78,.74,.64),0,.8),('c_shadow',(.42,.39,.33),0,.85),('c_red',(.40,.035,.025),.12,.7),('c_glass',(.055,.085,.105),.5,.28),('c_gold',(.55,.35,.09),.72,.35),('c_water',(.025,.34,.34),.3,.18),('c_carpet',(.19,.09,.07),0,1)]:mat(n,c,metal=metal,roughness=rough)
    with context('Caesars / high-rise towers'):
        def tower(x,z,w,d,h):
            B('ivory tower body',(x,h/2,z),(w,h,d))
            for y in [3,10,17,h-12,h-4,h]:D('tower layered belt',(x,y,z),(w+.7,.45,d+.7))
            for side in [-1,1]:
                xx=x+side*(w/2+.13)
                for zz in range(int(z-d/2+3),int(z+d/2-1),3):
                    for yy in range(19,int(h-13),3):D('vertical window grid',(xx,yy,zz),(.16,2.5,1.6),'c_glass')
                    D('engaged tower pier',(xx+side*.12,(h+5)/2,zz-1.2),(.5,h-16,.35))
                    arch(xx+side*.14,h-11,zz,1.8,5.8,side*math.pi/2)
                for zz in [z-d/2+1.2,z+d/2-1.2]:D('giant tower corner pier',(xx+side*.25,h/2,zz),(1,h,1.5))
            for side in [-1,1]:
                zz=z+side*(d/2+.13)
                for xx in range(int(x-w/2+3),int(x+w/2-1),3):
                    for yy in range(18,int(h-12),3):D('tower end window',(xx,yy,zz),(1.7,2.5,.16),'c_glass')
                for xx in [x-w/2+1,x+w/2-1]:D('end corner pier',(xx,h/2,zz),(.8,h,.8))
            roof(x,z,w+1,d+1,h+.2,5)
        mark=checkpoint()
        tower(-198,225,25,108,96)
        for z in [179,225,271]:
            # Crown pavilions project slightly from the long red-roofed Augustus wing.
            B('Augustus projecting pavilion',(-197,50,z),(28,100,13))
            for zz in [z-4,z,z+4]:
                D('pavilion tall window',(-182.85,48,zz),(.16,73,2.3),'c_glass')
                D('pavilion pilaster',(-182.5,48,zz-1.6),(.8,77,.5))
            for yy in [10,86,91,99]:D('pavilion cornice',(-195.4,yy,z),(32,.65,15))
            for zz in [z-4, z, z+4]:arch(-182.2,87,zz,2.5,5.6,math.pi/2)
            roof(-196,z,32,16,100,5);pediment(-181.7,z,13,99)
        flush();relocate(mark,(-198,0,225),(-149,0,-196),math.pi/2)
        mark=checkpoint()
        tower(-151,277,62,22,89)
        for x in [-176,-126]:
            B('Palace end pavilion',(x,46.5,277),(13,93,26))
            roof(x,277,15,28,93,5)
            pediment(x,290.2,12,91,0)
        flush();relocate(mark,(-151,0,277),(-199,0,-250),math.pi/2)
        mark=checkpoint()
        # Curved central hotel wing assembled from tangent bays with continuous balcony bands.
        for i in range(15):
            a=math.radians(-62+i*8.8);x=-158+31*math.cos(a);z=243+31*math.sin(a);yaw=-a
            B('curved central hotel bay',(x,24,z),(12,48,6.2),yaw=yaw)
            for yy in range(5,47,3):
                D('curved dark glazing',(x+6.1*math.cos(a),yy,z+6.1*math.sin(a)),(.15,2.3,4.8),'c_glass',yaw)
                D('curved balcony ribbon',(x,yy-1.35,z),(12.7,.2,5.35),'c_stone',yaw)
            D('curved wing roof cornice',(x,48.4,z),(13,.8,5.6),'c_stone',yaw)
        vs,fs=curved_crown_geometry();mesh('continuous curved roof crown',vs,fs,'c_stone')
        roof(-139,218,22,17,49,4)
        flush();relocate(mark,(0,0,0),(-20,8.5,-503))
    mark=checkpoint()
    with context('Caesars / public casino'):
        slab('Caesars casino floor',(-141,197),(82.6,38.6),'b_marble',y=.015,thickness=.4)
        slab('Caesars casino roof',(-141,197),(82.6,38.6),'c_stone',y=8.5,thickness=.5)
        B('west casino wall',(-182,4,197),(.6,8,38))
        B('south casino wall',(-141,4,178),(82,8,.6))
        for a,b in [(178,190),(196,216)]:B('east casino wall',(-100,4,(a+b)/2),(.6,8,b-a+.05))
        B('east entrance header',(-100,6.4,193),(.65,3.2,6.05))
        for a,b in [(-182,-119),(-115,-100)]:B('north casino wall',((a+b)/2,4,216),(b-a+.05,8,.6))
        B('north entrance header',(-117,6.4,216),(4.05,3.2,.65))
        door('caesars_main',(-100,0,193),yaw=math.pi/2,width=6,height=4.8,animation='slide',auto_open_radius=7)
        door('caesars_garden',(-117,0,216),width=4,height=4.8,animation='slide',auto_open_radius=6)
        volume('caesars_casino_envelope',(-141,4,197),(82,8,38),tags=['casino','indoors'])
        D('casino carpet',(-135,.065,197),(62,.05,34),'c_carpet')
        D('casino entry avenue',(-128,.10,193),(55,.04,5),'b_marble')
        D('casino garden avenue',(-117,.11,204),(5,.04,24),'b_marble')
        for x in [-151,-134,-110]:
            for z in [183,207]:
                column(x,z,0,7.8,.35)
                D('ceiling coffer',(x,7.8,z),(12,.3,9))
        for x in [-144,-130]:
            for z in [184,207]:
                B('gaming table plinth',(x,.55,z),(2.7,1.1,1.7),'b_walnut')
                D('green gaming table',(x,1.15,z),(4.2,.18,2.5),'b_felt')
                for dx in [-1.4,0,1.4]:lathe('casino stool',x+dx,z+2,[(.25,0),(.1,.5),(.38,.65)],'c_red',16)
        for x in [-157,-153,-149,-145]:
            B('slot cabinet',(x,1,212),(1.3,2,.9),'c_shadow')
            D('slot screen',(x,1.4,211.5),(1,.9,.08),'c_glass')
            D('slot button shelf',(x,.85,211.35),(1.2,.15,.6),'c_gold')
        for x,z in [(-128,193),(-148,193),(-114,205)]:
            lathe('casino chandelier',x,z,[(1.6,6.4),(1.8,6.7),(1.3,7)],'c_gold')
            lamp(uid('casino warm light'),(x,6,z),'#ffdbad',130,25)
        lamp('Caesars service emergency',(-166,3.5,195),'#c88548',35,18)
        lamp('Caesars supply room light',(-176,4,185),'#d4b584',25,12)
        # Corridor and two sealed side rooms, each with a real sliding door.
        for a,b in [(178,190),(196,216)]:B('service corridor partition',(-161,4,(a+b)/2),(.5,8,b-a+.03))
        B('service opening header',(-161,6.1,193),(.55,3.8,6.05))
        for z in [185,205]:
            for zz in [z-6,z+6]:B('service room return',(-176,4,zz),(12,8,.5))
            for a,b in [(z-6,z-1.5),(z+1.5,z+6)]:B('service room doorway',(-170,4,(a+b)/2),(.5,8,b-a+.03))
            B('service door header',(-170,5.6,z),(.55,4.8,3.05))
            door('caesars_service_'+str(z),(-170,0,z),yaw=math.pi/2,width=3,height=3.2,animation='slide',auto_open_radius=4)
            volume('caesars_room_'+str(z),(-176,4,z),(12,8,12),tags=['indoors','service'])
            B('service storage crate',(-180,.55,z+3),(2,1.1,2),'b_walnut')
            landmark('caesars_'+('supplies' if z==185 else 'hide'),(-176,.1,z),tags=['supply-staging'] if z==185 else ['horde-hide'])
            volume('caesars_corridor_'+str(z),(-166,1.5,z),(3,3,3),roofed=False,tags=['route'])
            volume('caesars_room_entry_'+str(z),(-176,1.5,z),(3,3,3),roofed=False,tags=['route'])
            link('caesars_corridor_'+str(z),'caesars_room_entry_'+str(z),door='caesars_service_'+str(z))
        for n,p in [('street',(-58,1.5,185)),('portico',(-94,1.5,193)),('entry',(-105,1.5,193)),('hall',(-151,1.5,193)),('corridor',(-166,1.5,193)),('garden_aisle',(-117,1.5,207)),('garden_exit',(-117,1.5,223))]:volume('caesars_'+n,p,(3,3,3),roofed=False,tags=['route'])
        link('south_west','caesars_street');link('caesars_street','caesars_portico');link('caesars_portico','caesars_entry',door='caesars_main');link('caesars_entry','caesars_hall');link('caesars_hall','caesars_corridor')
        for z in [185,205]:link('caesars_corridor','caesars_corridor_'+str(z))
        link('caesars_entry','caesars_garden_aisle');link('caesars_garden_aisle','caesars_garden_exit',door='caesars_garden')
    with context('Caesars / Roman forecourt'):
        # Main temple portico faces the Strip; columns stay clear of its 6 m central entry.
        for z in [183,187,199,203]:column(-94,z,0,10,.6)
        D('portico entablature',(-95,10.5,193),(10,1.1,25))
        pediment(-89.8,193,26,11)
        roof(-96,193,12,26,11,3)
        api['text']('Caesars portico name','CAESARS PALACE',(-89.1,10.1,193),'c_gold',yaw=math.pi/2,size=.7)
        # Decorative arcades unify the casino podium with the temple entrance.
        for z in [180,207,212]:arch(-99.6,.6,z,3,5.8,math.pi/2)
        for x in range(-177,-100,6):arch(x,.6,177.55,3.6,5.8,math.pi)
        for y in [7.5,8.5]:D('podium continuous cornice',(-141,y,197),(84,.5,40))
        # Shallow ornamental pools, curbed to preserve dry pedestrian circulation.
        for x,z,r in [(-78,216,9),(-87,241,7)]:
            lathe('pool basin',x,z,[(r,0),(r,.35),(r-.65,.35),(r-.65,.05)],'c_stone',64)
            lathe('turquoise pool',x,z,[(r-.7,.12),(r-.7,.16)],'c_water',64)
            lathe('tiered fountain',x,z,[(1.8,.2),(1.8,.65),(.65,.9),(.5,2.7),(2.3,2.8),(2.4,3.1),(.6,3.2),(.4,4.7),(1.3,4.8),(1.4,5),(.25,5.1),(.15,6)],'c_stone')
            for i in range(20):
                a=i*math.tau/20;D('pool coping',(x+r*math.cos(a),.3,z+r*math.sin(a)),(1.0,.6,3),'c_stone',-a)
        for z in [227,233,239]:column(-62,z,0,6,.38)
        D('garden pergola',(-62,6.3,233),(5,.5,19));roof(-63,233,7,19,6.6,2)
        # Paired ornamental temple gazebos at the garden edge.
        for x,z in [(-108,250),(-69,251)]:
            for dx in [-2.5,2.5]:
                for dz in [-2.5,2.5]:column(x+dx,z+dz,0,5,.27)
            roof(x,z,7,7,5.4,2)
        landmark('caesars_fountain',(-78,0,216),tags=['landmark'])
    flush();relocate(mark,(0,0,0),(8,0,-435))
    mark=checkpoint()
    with context('Caesars / Colosseum'):
        cx,cz,r=-83,273,21
        outline=[(cx+r*math.cos(i*math.tau/64),cz+r*math.sin(i*math.tau/64)) for i in range(64)]
        prism('Colosseum cylindrical auditorium',outline,0,25,'c_stone')
        for y in [1,8.2,16.2,24.5]:lathe('Colosseum ring cornice',cx,cz,[(r+.6,y),(r+.6,y+.45)],'c_stone',96)
        for i in range(32):
            a=i*math.tau/32;x=cx+(r+.17)*math.cos(a);z=cz+(r+.17)*math.sin(a);yaw=math.pi/2-a
            for y in [1.2,9,17]:arch(x,y,z,2.5,5.4,yaw)
            D('Colosseum pilaster',(cx+(r+.3)*math.cos(a+.098),12.5,cz+(r+.3)*math.sin(a+.098)),(.5,24,.5))
        lathe('Colosseum roof drum',cx,cz,[(r-1,25),(r-1,25.5)],'c_shadow',96)
        for i in range(8):
            a=i*math.tau/8;D('Colosseum roof vent',(cx+12*math.cos(a),25.8,cz+12*math.sin(a)),(2,.7,2),'c_shadow')
        landmark('caesars_colosseum',(-59,0,273),tags=['landmark'])
        for n,p in [('garden_walk',(-53,1.5,317)),('colosseum_walk',(-53,1.5,273))]:volume('caesars_'+n,p,(3,3,3),roofed=False,tags=['route'])
        link('caesars_street','caesars_garden_walk');link('caesars_garden_walk','caesars_colosseum_walk')
    flush();relocate(mark,(0,0,0),(18,0,-546))
    print('Caesars towers, casino, gardens and Colosseum complete',flush=True)
    return {'entrance':[-92,0,-242],'casinoCenter':[-133,0,-238],'supplies':[-168,.1,-250],'hordeHide':[-168,.1,-230],'colosseum':[-65,0,-273],'mapNorth':[0,0,-1]}
