"""Bellagio's north lakefront village, authored in geographic metres.

Plan geometry: OSM podium, rotundas and lake way/22971030. Roof profiles,
facade sections and planting are fitted to the creator's aerial and JERDE's
photograph/rotunda drawing, not claimed to be a measured architectural survey.
All decorative geometry is material-batched and has no physics bodies.
"""
from common import *

NORTH = box(-211, 170, -22, 257)
ROOF_IDS = ['way/'+i for i in ['114714407','114714408','114714409',
    '114714410','114714411','114714412','114716303']]
LAKE = Polygon(json.loads(Path('tools/resort-blocks/references/bellagio/lake-outline.json').read_text())['coordinates'])
WATER_Y=-1.1
# A small upper-level exit pavilion, not the former two-storey U around a path.
PAVILIONS=[(-146,245,23,17,.49,12.9,'lake-ochre','LOUIS VUITTON'),
    (-119,237,19,15,.32,12.0,'lake-cream',''),
    (-90,230,18,15,.30,13.6,'lake-ochre','LOUIS VUITTON'),
    (-52,201,16,15,.30,13.0,'lake-cream',''),
    (-39,190,13,15,.30,12.0,'lake-ochre','VIA BELLAGIO')]

def pavilion_polys(b):
    return [Frame(b,x,z,yaw,0).poly([(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]) for x,z,w,d,yaw,*_ in PAVILIONS]

def build(b,site,via,slab,routes,portals):
    b.property='bellagioBlock-exterior';b.detail=0
    def source(s,detail=0):b.source='lakefront-'+s;b.detail=detail
    def fr(x,z,y=0,yaw=0):return Frame(b,x,z,yaw,y)
    def path(mat,pts,r=.05,n=8):b.path(mat,pts,r,n)

    def balustrade(points,y,h=1.05,solid=False):
        """Turned stone balusters; one simple hidden rail collision per span."""
        for a,c in zip(points,points[1:]):
            length=math.dist(a,c)
            if length<.05:continue
            f=fr((a[0]+c[0])/2,(a[1]+c[1])/2,y,-math.atan2(c[1]-a[1],c[0]-a[0]))
            f.box('lake-stone',(0,.09,0),(length,.18,.42))
            f.box('lake-stone',(0,h,0),(length,.17,.47))
            if solid:
                collision=b.solids[b.property];offset=len(collision['vertices'])//3
                collision['vertices'].extend(v for pt in [f.p(-length/2,.1,0),f.p(length/2,.1,0),f.p(length/2,h,0),f.p(-length/2,h,0)] for v in pt)
                collision['indices'].extend(offset+i for i in [0,1,2,0,2,3])
            for x in np.linspace(-length/2,length/2,max(2,math.ceil(length/.62)+1)):
                f.lathe('lake-stone',x,0,[(.18,.105),(.24,.13),(.32,.11),(.48,.16),(.62,.15),(.78,.07),(.89,.11),(.93,.11)],8)
            for x in [-length/2,length/2]:
                f.box('lake-cream',(x,h/2,0),(.34,h,.38));f.box('lake-stone',(x,h+.12,0),(.45,.12,.49))

    def arched_window(f,x,w,base,h,depth=.13,balcony=False):
        r=w/2;spring=base+h-r
        outline=[(x-r,base,depth),(x+r,base,depth)]+[(x+r*math.cos(a),spring+r*math.sin(a),depth) for a in np.linspace(0,math.pi,25)]
        b.face('lake-glazing',[f.p(*p) for p in outline])
        f.arch(x,depth+.17,w,h+base,'lake-stone',.16,base=base)
        f.arch(x,depth+.20,w+.5,h+base+.25,'lake-stone',.075,base=base)
        for dx in np.arange(-w/2+.65,w/2,.65):
            top=spring+math.sqrt(max(0,r*r-dx*dx))-.1
            f.box('lake-bronze',(x+dx,(base+top)/2,depth+.04),(.055,top-base,.065))
        for yy in np.arange(base+1,spring+.1,1.15):f.box('lake-bronze',(x,yy,depth+.06),(w,.065,.085))
        f.box('lake-bronze',(x,spring,depth+.05),(w,.1,.1))
        for a in np.linspace(.18,math.pi-.18,7):
            f.tube('lake-bronze',(x,spring,depth+.06),(x+(r-.12)*math.cos(a),spring+(r-.12)*math.sin(a),depth+.06),.026,6)
        # Fanlight keystone, sill and recessed spandrel plaque.
        f.box('lake-stone',(x,base+h+.13,depth+.21),(.42,.5,.28))
        f.box('lake-stone',(x,base-.12,depth+.22),(w+.5,.24,.55))
        if balcony:
            center=f.p(x,0,0);poly=Point(center[0],center[2]).buffer(w*.58,quad_segs=16)
            front=f.poly([(x-w*.75,0),(x+w*.75,0),(x+w*.75,w),(x-w*.75,w)])
            poly=poly.intersection(front)
            slab(poly,base-.05,'lake-stone',False)
            arcpts=[f.p(x+math.cos(a)*w*.58,0,math.sin(a)*w*.58) for a in np.linspace(0,math.pi,13)]
            balustrade([(p[0],p[2]) for p in arcpts],base)
            for yy,rr in [(base-.3,w*.55),(base-.65,w*.44),(base-1,w*.3)]:
                pts=[f.p(x+math.cos(a)*rr,yy,math.sin(a)*rr) for a in np.linspace(0,math.pi,25)]
                path('lake-stone',pts,.12)

    def hip_roof(f,w,d,y,rise):
        """Low terracotta hipped roof with real ridges and individually rolled tiles."""
        w+=1;d+=1;ridge=max(0,w/2-d/2)
        a=(-w/2,y,-d/2);c=(w/2,y,-d/2);e=(w/2,y,d/2);g=(-w/2,y,d/2);q=(-ridge,y+rise,0);r=(ridge,y+rise,0)
        for face in [(a,c,r,q),(c,e,r),(e,g,q,r),(g,a,q)]:b.face('lake-terracotta',[f.p(*p) for p in face])
        for aa,cc in [(a,q),(c,r),(e,r),(g,q),(q,r)]:
            if math.dist(aa,cc)>.001:f.tube('lake-tile-light',aa,cc,.13,8)
        # Tile rolls change silhouette and cast shallow shadows. Cross seams use texture.
        for sign in [-1,1]:
            for x in np.arange(-w/2+.2,w/2,.36):
                topx=max(-ridge,min(ridge,x));f.tube('lake-tile-light',(x,y+.05,sign*d/2),(topx,y+rise+.04,0),.06,6)
        for sign in [-1,1]:
            for z in np.arange(-d/2+.2,d/2,.38):f.tube('lake-terracotta',(sign*w/2,y+.05,z),(sign*ridge,y+rise+.04,0),.055,6)
        for yy,ss in [(y-.35,.3),(y-.13,.16)]:f.box('lake-stone',(0,yy,0),(w,ss,d))
        f.box('lake-bronze',(0,y-.02,-d/2),(w,.12,.10));f.box('lake-bronze',(0,y-.02,d/2),(w,.12,.10))

    def lantern(f,x,y,z):
        f.box('lake-bronze',(x,y,z),(.17,.55,.18));f.tube('lake-bronze',(x,y,z),(x,y,z+.4),.035)
        f.box('warm',(x,y+.05,z+.42),(.16,.35,.16))
        f.lathe('lake-bronze',x,z+.42,[(y-.2,.15),(y-.15,.15),(y+.25,.15),(y+.42,0)],8)

    source('village-shell')
    ppolys=pavilion_polys(b)
    rotundas=[(-68.15,206.5,7.55,17.2,6.4,'lake-glazing'),
        (-103.65,216.95,7.35,14.3,5.5,'lake-stone'),
        (-140.25,216.7,7.6,14.4,5.5,'lake-gold'),
        (-175.7,236.45,8.4,14.5,5.7,'lake-gold')]
    rpolys=[Point(x,z).buffer(r,quad_segs=24) for x,z,r,*_ in rotundas]
    masses=unary_union(ppolys+rpolys)
    north=site.intersection(NORTH)
    # Roof support is cut beneath the glazed arcade, rather than opaque under glass.
    vaultline=LineString([(-184,212),(-175.7,236.45),(-140.25,216.7),(-103.65,216.95),(-68.15,206.5)])
    vaultmask=vaultline.buffer(4.15).union(unary_union(rpolys))
    b.shell(site,.24,11.35,'lake-cream',openings=portals,roof=False,
        interior=(via.union(masses.buffer(.3)).union(site.difference(NORTH).buffer(.001)),26))
    slab(north.difference(masses.union(vaultmask)),11.45,'lake-roof',False)
    # Model the remaining connecting facade too: the OSM plan has narrow returns
    # between the projecting shops, not featureless twelve-metre retaining walls.
    for aa,cc in zip(site.exterior.coords,list(site.exterior.coords)[1:]):
        edge=LineString([aa,cc])
        if edge.length<3 or not NORTH.covers(edge) or max(aa[1],cc[1])<208:continue
        remainder=edge.difference(masses.buffer(.5)).difference(via.buffer(.5))
        segments=list(remainder.geoms) if hasattr(remainder,'geoms') else [remainder]
        for segment in segments:
            if segment.is_empty or segment.geom_type!='LineString' or segment.length<3:continue
            a,c=list(segment.coords)[0],list(segment.coords)[-1];dx,dz=c[0]-a[0],c[1]-a[1];le=segment.length;dx/=le;dz/=le
            nx,nz=dz,-dx
            if site.contains(Point((a[0]+c[0])/2+nx,(a[1]+c[1])/2+nz)):nx,nz=-nx,-nz
            yaw=math.atan2(nx,nz);f=fr((a[0]+c[0])/2+nx*.07,(a[1]+c[1])/2+nz*.07,0,yaw)
            for yy,hh,depth in [(1,.36,.18),(5.6,.36,.35),(10.8,.35,.5),(11.25,.22,.7)]:f.box('lake-stone',(0,yy,depth),(le,hh,.4))
            count=max(1,round(le/5.2));pitch=le/count
            for k in range(count):
                x=(k+.5)*pitch-le/2
                arched_window(f,x,min(3.1,pitch-.9),5.95,4.5,balcony=le>5)
                arched_window(f,x,min(2.7,pitch-1.1),.6,4.3)
                f.box('lake-stone',(x-pitch/2+.2,5.5,.22),(.32,10.1,.45))
                lantern(f,x+pitch*.43,7.1,.33)
    for idx,((x,z,w,d,yaw,h,mat,name),p) in enumerate(zip(PAVILIONS,ppolys)):
        source('pavilions');f=fr(x,z,0,yaw)
        b.shell(p,.24,h,mat,roof=False,interior=(via,11.7))
        # Restore the solid head above bridge openings; circulation voids need
        # 3.7 m of clear height, not a missing wall all the way up to the eaves.
        upperhead=p.boundary.intersection(via)
        lines=list(upperhead.geoms) if hasattr(upperhead,'geoms') else [upperhead]
        for line in lines:
            if line.geom_type!='LineString' or line.is_empty:continue
            for a,c in zip(line.coords,list(line.coords)[1:]):
                b.face(mat,[(a[0],9.85,a[1]),(c[0],9.85,c[1]),(c[0],h,c[1]),(a[0],h,a[1])],True)
        hip_roof(f,w,d,h+.3,2.7 if idx<3 else 2.3)
        for yy,hh,offset in [(1.1,.35,.1),(5.8,.28,.2),(h-.8,.23,.26),(h-.3,.28,.42)]:
            b.shell(p.buffer(offset,join_style=2),yy,yy+hh,'lake-stone',roof=False,solid=False,interior=(via,11.7))
        # All faces use their own outward frames; visible doors are genuinely arched.
        for side in [-1,1]:
            fac=fr(*[f.p(0,0,side*d/2)[i] for i in [0,2]],0,yaw+(math.pi if side<0 else 0))
            for xx in np.arange(-w/2+3,w/2-1,5.8):
                wp=fac.p(xx,0,0)
                if via.buffer(.2).covers(Point(wp[0],wp[2])):continue
                arched_window(fac,xx,3.2,6.2,h-7.0,balcony=True)
                arched_window(fac,xx,3.0,1.0,4.0)
            for xx in [-w/2+.35,w/2-.35]:fac.box('lake-stone',(xx,h/2,.2),(.55,h,.4))
            if name:fac.text(name,(0,h-1.65,.3),min(.4,w/(len(name)*.9)),'lake-bronze')
        for side in [-1,1]:
            end=fr(*[f.p(side*w/2,0,0)[i] for i in [0,2]],0,yaw+side*math.pi/2)
            for xx in [-d*.26,d*.26]:
                wp=end.p(xx,0,0)
                if via.buffer(.5).covers(Point(wp[0],wp[2])):continue
                arched_window(end,xx,3.1,6.15,h-7,balcony=False)
        for xx in [-w*.35,w*.35]:lantern(f,xx,7,d/2+.35)
        # Stone finial / little rooftop lantern.
        f.lathe('lake-stone',0,0,[(h+3,.7),(h+3.4,.7),(h+3.55,.42),(h+4.4,.42),(h+4.8,0)],16)
        if idx==1:
            # Distinct dark curved shop bay visible in the supplied aerial.
            # Dimensions are fitted to the photograph, not an as-built survey.
            center=f.p(0,0,d/2-.3);r=3.7
            bay=Point(center[0],center[2]).buffer(r,quad_segs=24).intersection(f.poly([(-r, d/2-.3),(r,d/2-.3),(r,d/2+r),(-r,d/2+r)]))
            slab(bay,6.12,'lake-stone',False)
            for a,c in zip(np.linspace(0,math.pi,25),np.linspace(0,math.pi,25)[1:]):
                aa=(r*math.cos(a),d/2-.3+r*math.sin(a));cc=(r*math.cos(c),d/2-.3+r*math.sin(c))
                b.face('lake-glazing',[f.p(aa[0],6.2,aa[1]),f.p(cc[0],6.2,cc[1]),f.p(cc[0],10.8,cc[1]),f.p(aa[0],10.8,aa[1])])
                f.tube('blackiron',(aa[0],6.2,aa[1]),(aa[0],10.8,aa[1]),.045,6)
                b.face('blackiron',[f.p(aa[0],10.8,aa[1]),f.p(cc[0],10.8,cc[1]),f.p(cc[0],11.9,cc[1]),f.p(aa[0],11.9,aa[1])])
            slab(bay.buffer(.25),12,'blackiron',False)

    source('rotundas')
    for x,z,r,h,rise,mat in rotundas:
        p=Point(x,z).buffer(r,quad_segs=24)
        b.shell(p,.24,h,'lake-cream',roof=False,interior=(via,12))
        for yy,rr,hh in [(1,r+.16,.45),(5.8,r+.35,.38),(h-.65,r+.4,.3),(h-.2,r+.6,.45),(h+.28,r+.35,.17)]:
            b.lathe('lake-stone',(x,z),[(yy,rr),(yy+hh,rr)],64)
        for a in np.linspace(0,math.tau,12,endpoint=False):
            xx,zz=x+(r+.035)*math.cos(a),z+(r+.035)*math.sin(a)
            if via.buffer(.1).covers(Point(xx,zz)):continue
            f=fr(xx,zz,0,math.pi/2-a)
            arched_window(f,0,3.0,6.2,h-7.1,balcony=math.sin(a)>.25)
            for dx in [-1.8,1.8]:f.box('lake-stone',(dx,(h+6)/2,0),(.32,h-6,.27))
        # Ribbed semi-ellipsoid dome with two opaque colored types and glazed type.
        for j in range(14):
            a0=j*math.pi/28;a1=(j+1)*math.pi/28
            for k in range(64):
                u=k*math.tau/64;v=(k+1)*math.tau/64
                def dp(a,t):return (x+r*math.cos(a)*math.cos(t),h+.5+rise*math.sin(a),z+r*math.cos(a)*math.sin(t))
                mm=mat if mat!='lake-gold' else ('lake-gold' if (j+k)%2 else 'lake-stone')
                b.face(mm,[dp(a0,u),dp(a0,v),dp(a1,v),dp(a1,u)])
        for a in np.linspace(0,math.tau,32,endpoint=False):
            path('lake-stone',[(x+(r+.045)*math.cos(t)*math.cos(a),h+.53+rise*math.sin(t),z+(r+.045)*math.cos(t)*math.sin(a)) for t in np.linspace(0,math.pi/2,23)],.065)
        for t in [.0,.18,.4,.65,1.0]:
            b.lathe('lake-stone',(x,z),[(h+.53+rise*math.sin(t),r*math.cos(t)+.06),(h+.61+rise*math.sin(t),r*math.cos(t)+.06)],64)
        b.lathe('lake-gold',(x,z),[(h+rise+.45,.25),(h+rise+.9,.48),(h+rise+1.3,.22),(h+rise+2.2,.08),(h+rise+2.65,0)],24)

    source('glazed-arcade')
    # The centerline follows the four mapped skylights, with each vault stopping at its rotunda.
    centers=[(-184,212,6.2),(-175.7,236.45,8.6),(-140.25,216.7,7.8),(-103.65,216.95,7.6),(-68.15,206.5,7.8)]
    for aa,cc in zip(centers,centers[1:]):
        x,z,r0=aa;xx,zz,r1=cc;dx,dz=xx-x,zz-z;length=math.hypot(dx,dz);dx/=length;dz/=length
        a=(x+dx*r0,z+dz*r0);c=(xx-dx*r1,zz-dz*r1);le=math.dist(a,c)
        f=fr((a[0]+c[0])/2,(a[1]+c[1])/2,0,-math.atan2(dz,dx));rad=4.0;base=11.65
        for j in range(16):
            u=j*math.pi/16;v=(j+1)*math.pi/16
            b.face('lake-glazing',[f.p(-le/2,base+rad*math.sin(u),rad*math.cos(u)),f.p(le/2,base+rad*math.sin(u),rad*math.cos(u)),f.p(le/2,base+rad*math.sin(v),rad*math.cos(v)),f.p(-le/2,base+rad*math.sin(v),rad*math.cos(v))])
        for t in np.linspace(-le/2,le/2,max(2,math.ceil(le/1.6)+1)):
            f.path('lake-stone',[(t,base+rad*math.sin(a)+.04,rad*math.cos(a)) for a in np.linspace(0,math.pi,25)],.06)
        for a in np.linspace(0,math.pi,9):f.tube('lake-stone',(-le/2,base+rad*math.sin(a)+.04,rad*math.cos(a)),(le/2,base+rad*math.sin(a)+.04,rad*math.cos(a)),.045)

    source('corner-campanile')
    f=fr(-37.2,188,0,.3)
    f.box('lake-cream',(0,15,0),(4.6,6,4.6))
    for side in range(4):
        ff=fr(*[f.p(2.33*math.sin(side*math.pi/2),0,2.33*math.cos(side*math.pi/2))[i] for i in [0,2]],0,.3+side*math.pi/2)
        arched_window(ff,0,2.4,14.2,3.1)
    for y in [12.4,13,18]:f.box('lake-stone',(0,y,0),(5,.27,5))
    f.lathe('lake-stone',0,0,[(18.2,2.7),(18.6,2.7),(18.8,2.05)],32)
    f.lathe('lake-glazing',0,0,[(18.8,2.05),(19.5,1.9),(20.2,1.3),(20.8,.4),(21,0)],32)
    for a in np.linspace(0,math.tau,12,endpoint=False):
        f.path('lake-stone',[(r*math.cos(a),y,r*math.sin(a)) for y,r in [(18.8,2.07),(19.5,1.92),(20.2,1.32),(20.8,.42)]],.07)

    source('shore-gardens')
    rng=random.Random(119)
    def rock(x,y,z,r):
        # Unequal strata and a skewed crown avoid the old uniform bead border.
        n=11;sectors=[rng.uniform(.8,1.22) for _ in range(n)]
        rings=[]
        for j in range(7):
            lat=-math.pi/2+j*math.pi/6
            rings.append([(x+r*math.cos(lat)*sectors[k]*math.cos(k*math.tau/n)+.16*r*math.sin(lat),
                y+r*.64*math.sin(lat)+rng.uniform(-.07,.07)*r,
                z+r*.85*math.cos(lat)*sectors[k]*math.sin(k*math.tau/n)) for k in range(n)])
        for j in range(6):
            for k in range(n):b.face('lake-rock',[rings[j][k],rings[j][(k+1)%n],rings[j+1][(k+1)%n],rings[j+1][k]])
    # Rocks follow the surveyed shoreline. Public passage and building floors remain clear.
    shore=LAKE.exterior
    for distance in np.arange(0,shore.length,2.2):
        q=shore.interpolate(distance)
        if q.x>-60 or q.y>280:continue
        if via.buffer(1).contains(q):continue
        rock(q.x+rng.uniform(-.6,.6),WATER_Y+rng.uniform(.05,.7),q.y+rng.uniform(-.7,.7),rng.uniform(1.05,2.1))
        if rng.random()<.35:rock(q.x+rng.uniform(-.8,.8),WATER_Y+1.1,q.y-.55,rng.uniform(.65,1.15))
    def tree(x,z,h=6,r=3.1):
        b.tube('bark',(x,.1,z),(x+.25,h*.68,z),.20,9,.10)
        for k in range(9):
            a=k*2.399;rr=r*(.28+.15*(k%4));xx=x+math.cos(a)*rr;zz=z+math.sin(a)*rr;yy=h*(.68+.065*(k%4))
            b.tube('bark',(x,h*.4,z),(xx,yy-.4,zz),.09,7,.025)
            rad=r*.4
            b.sphere('lake-leaf',(xx,yy,zz),rad*.75,10,6,scale=(1,.85,1))
            for j in range(150):
                az=rng.random()*math.tau;v=rng.uniform(-1,1);q=math.sqrt(1-v*v)*rng.uniform(.68,1.05)
                center=np.array([xx+math.cos(az)*q*rad,yy+v*rad*.9,zz+math.sin(az)*q*rad])
                tilt=rng.uniform(.15,.9);angle=rng.random()*math.tau;length=rng.uniform(.17,.35)
                axis=np.array([math.cos(angle)*length,tilt*length,math.sin(angle)*length]);side=np.array([-math.sin(angle),.12,math.cos(angle)])*length*.44
                ridge=center+np.array([0,.045,0])
                outline=[center-axis,center+side,center+axis,center-side]
                mat=['lake-leaf','foliage','sage'][rng.randrange(3)]
                for m in range(4):b.face(mat,[outline[m],outline[(m+1)%4],ridge])
    for x,z,h,r in [(-160,263,8.6,4.2),(-134,255,8.3,4),(-106,245,8.8,4.1),(-80,239,8.6,4.3),(-63,220,8,3.6),(-175,266,7.8,3.4),(-159,223,6.6,3.5),(-128,217,5.5,2.5)]:
        if via.buffer(2).covers(Point(x,z)):continue
        patch=Point(x,z).buffer(r*.9,quad_segs=10).difference(via.buffer(1.0)).difference(masses.buffer(.2))
        if patch.area<5:continue
        c=patch.representative_point();x,z=c.x,c.y
        b.extrude('lake-earth',patch,WATER_Y,.6,False)
        tree(x,z,h,r)
        for j in range(7):rock(x+rng.uniform(-r,r),.25,z+rng.uniform(-r,r),rng.uniform(.55,1.25))
        for j in range(7):
            a=j*2.399;xx=x+math.cos(a)*r*.8;zz=z+math.sin(a)*r*.8
            b.sphere('lake-leaf',(xx,.8,zz),.6,9,6,scale=(1,.65,1))

    source('lake')
    # The city terrain is separately cut to this polygon, so no coplanar surface remains.
    b.planar('lake-water',LAKE,WATER_Y)
    b.planar('lake-deep',LAKE,-3.0,True)
    b.shell(LAKE,-3.0,.15,'lake-rock',roof=False,solid=True)
    # Hardware is submerged, not a second drawing on the water surface. The
    # opaque water shader owns the top; a later fountain show can use these origins.
    # Layout is an interpreted visual feature, not an as-built nozzle survey.
    source('fountain-array')
    hardware_y=WATER_Y-.63
    for x,z,r in [(-96,311,15),(-103,369,16),(-87,429,14)]:
        for rr in [r-.65,r,r+.65]:path('lake-underwater',[(x+rr*math.cos(a),hardware_y+.024,z+rr*math.sin(a)) for a in np.linspace(0,math.tau,97)],.075)
        for a in np.linspace(0,math.tau,42,endpoint=False):b.box('lake-underwater',(x+r*math.cos(a),hardware_y+.07,z+r*math.sin(a)),(.16,.12,.16))
    for off in [-.6,0,.6]:
        path('lake-underwater',[(-54+off+7*math.sin(t*math.pi),hardware_y+.025,250+t*225) for t in np.linspace(0,1,160)],.09)
    for z in [285,342,399,452]:path('lake-underwater',[(-142,hardware_y+.025,z),(-53,hardware_y+.025,z+10)],.07)

    source('strip-promenade')
    # East shore is a scalloped continuous promenade; model its actual lake edge.
    rim=LAKE.buffer(5,join_style=1).difference(LAKE).intersection(box(-42,208,-14,505))
    slab(rim,.24,'lake-paving')
    # Resample before generating balusters to avoid tiny OSM segments producing thousands of posts.
    coords=list(shore.coords)
    for a,c in zip(coords,coords[1:]):
        if max(a[0],c[0])< -42 or min(a[1],c[1])<210 or max(a[1],c[1])>503:continue
        balustrade([a,c],.24,solid=True)
    for z in np.arange(238,495,24):
        q=shore.interpolate(shore.project(Point(-20,z)));x=q.x+3.4
        tree(x,z,5.7,2.4)
        f=fr(x,z+.0,.24);f.lathe('lake-stone',0,0,[(0,.95),(.35,.95),(.45,1.05)],20)
        f.bench(0,4,'lake-bronze')
        for dz in [-6,6]:
            f.lathe('lake-bronze',0,dz,[(0,.15),(.15,.2),(.28,.09),(3.2,.065)],10)
            f.lathe('warm',0,dz,[(3.2,.21),(3.55,.21),(3.72,0)],8)
    routes.append(dict(name='Lake promenade',points=[[-14,.24,240],[-14,.24,280],[-14,.24,320],[-14,.24,360],[-14,.24,400],[-14,.24,440],[-14,.24,480]]))
    return dict(lakeAreaM2=round(LAKE.area),lakeSource='way/22971030',waterElevationEstimateM=WATER_Y,
        pavilionCount=len(PAVILIONS),rotundas=len(rotundas),sources=['Creator Google Earth aerial','JERDE Bellagio project photograph','JERDE rotunda drawing'],
        estimates=['Facade heights and roof pitches','Window/balcony bay dimensions','Shore planting species and placement','Fountain hardware layout'])
