"""Photo-led glass-and-bronze Bellagio arrival canopies, authored in Blender.

The main-entrance architectural language is fitted to the existing lake/gallery
portal without moving the lake or door. The south portico under the wing remains.
Dimensions adapt the reference architecture to the prototype's compressed plan.
"""
import math
import bpy
import bmesh
from mathutils import Vector

PREFIX = 'Bellagio Arrival / '


class Builder:
    def __init__(self, name, origin, scale=(1, 1, 1), yaw=0):
        self.name=name; self.origin=origin; self.scale=scale; self.yaw=yaw
        self.groups={}; self.colliders=[]; self.lights=[]

    def world(self, p):
        u,y,v=[a*b for a,b in zip(p,self.scale)]
        c,s=math.cos(self.yaw),math.sin(self.yaw)
        return (self.origin[0]+c*u-s*v,self.origin[1]+y,self.origin[2]-s*u-c*v)

    def mesh(self, verts, faces, material, smooth=False):
        g=self.groups.setdefault(material, [[],[],[]]); start=len(g[0])
        g[0].extend(self.world(p) for p in verts)
        g[1].extend(tuple(start+i for i in f) for f in faces)
        g[2].extend([smooth]*len(faces))

    def box(self,p,s,m):
        x,y,z=p; a,b,c=[v/2 for v in s]
        self.mesh([(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],
            [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)],m)

    def proxy(self,n,p,s):
        self.colliders.append(dict(name=PREFIX+self.name+' '+n,shape='box',position=self.world(p),size=[a*b for a,b in zip(s,self.scale)],yaw=self.yaw,group='environment'))

    def tube(self,points,r,m,closed=False,sides=6):
        points=[Vector(p) for p in points]; verts=[]
        for i,p in enumerate(points):
            tangent=(points[(i+1)%len(points)]-points[i-1]).normalized() if closed or 0<i<len(points)-1 else (points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
            axis=Vector((0,1,0)) if abs(tangent.y)<.9 else Vector((1,0,0))
            a=tangent.cross(axis).normalized(); b=tangent.cross(a).normalized()
            verts.extend(tuple(p+r*(a*math.cos(j*math.tau/sides)+b*math.sin(j*math.tau/sides))) for j in range(sides))
        faces=[(i*sides+j,i*sides+(j+1)%sides,((i+1)%len(points))*sides+(j+1)%sides,((i+1)%len(points))*sides+j) for i in range(len(points) if closed else len(points)-1) for j in range(sides)]
        if not closed:faces += [tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))]
        self.mesh(verts,faces,m,True)

    def lathe(self,p,profile,m,n=32):
        x,y,z=p
        verts=[(x+r*math.cos(j*math.tau/n),y+h,z+r*math.sin(j*math.tau/n)) for h,r in profile for j in range(n)]
        faces=[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j) for i in range(len(profile)-1) for j in range(n)]
        faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+j for j in range(n))]
        self.mesh(verts,faces,m,True)

    def lettering(self,label,p,size):
        curve=bpy.data.curves.new('Arrival lettering','FONT');curve.body=label;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=size;curve.extrude=.008
        ob=bpy.data.objects.new('Arrival lettering',curve);bpy.context.scene.collection.objects.link(ob)
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        # Local +V points out of the facade; reverse U so the outward-facing
        # text reads left-to-right after the game-coordinate axis conversion.
        self.mesh([(p[0]-v.co.x,p[1]+v.co.y,p[2]+v.co.z) for v in me.vertices],[tuple(f.vertices) for f in me.polygons],'ba_gold')
        bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(me);bpy.data.curves.remove(curve)

    def finish(self):
        for material,(verts,faces,smooth) in self.groups.items():
            name=PREFIX+self.name+' / '+material
            me=bpy.data.meshes.new(name); me.from_pydata([(x,-z,y) for x,y,z in verts],[],faces); me.update()
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
            ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.materials[material])
            ob['visibilityRole']='shell';ob['visibilityTower']='';ob['bellagioArrival']=True
            for p,s in zip(me.polygons,smooth):p.use_smooth=s
        return dict(colliders=self.colliders,lights=self.lights)


def materials():
    for name,color,metal,rough,emission,alpha in [
        ('ba_limestone',(.59,.48,.33),0,.77,0,1),
        ('ba_cream',(.80,.72,.56),0,.64,0,1),
        ('ba_coffer',(.46,.36,.235),0,.82,0,1),
        ('ba_bronze',(.19,.135,.066),.68,.37,0,1),
        ('ba_verdigris',(.095,.16,.145),.63,.43,0,1),
        ('ba_gold',(.51,.34,.12),.72,.35,0,1),
        ('ba_paver',(.28,.255,.215),0,.88,0,1),
        ('ba_paver_light',(.45,.40,.31),0,.87,0,1),
        ('ba_foliage',(.075,.105,.045),0,.91,0,1),
        ('ba_water',(.08,.19,.17),.45,.20,0,1),
        ('ba_lamp',(.95,.79,.50),.0,.32,.8,1),
        ('glass_ba_canopy',(.51,.69,.67),.20,.16,0,.26)]:
        mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.use_nodes=True
        bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,alpha)
        bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
        bs.inputs['Alpha'].default_value=alpha
        bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
        mat.diffuse_color=(*color,alpha);mat.use_backface_culling=False
        if alpha<1:mat.surface_render_method='DITHERED'


def canopy(b,full=True,column_filter=None):
    # Vault: real curved panes, longitudinal bars, and thick transverse ribs.
    def vault(t,v):return (8*math.cos(t),7.12+3.0*math.sin(t),v)
    for j in range(24):
        t0=j*math.pi/24;t1=(j+1)*math.pi/24
        for v in range(0,16,2):b.mesh([vault(t0,v),vault(t1,v),vault(t1,v+2),vault(t0,v+2)],[(0,1,2,3)],'glass_ba_canopy')
        b.tube([vault(t0,v) for v in [0,16]],.034,'ba_verdigris')
    for v in range(0,17,2):
        major=v%4==0
        b.tube([vault(i*math.pi/48,v) for i in range(49)],.13 if major else .045,'ba_verdigris',sides=8)
        if major:
            b.tube([(x,y-.40,z) for x,y,z in [vault(i*math.pi/48,v) for i in range(49)]],.060,'ba_bronze')
            # Paired scrolls in the curved web of every structural rib.
            for j in range(1,24):
                t=j*math.pi/24;x,y,_=vault(t,v)
                for direction in [-1,1]:
                    points=[]
                    for k in range(25):
                        a=k*math.tau/24*1.25;r=.18*(1-k/29)
                        points.append((x+direction*(.14+r*math.cos(a)),y-.20+r*math.sin(a),v))
                    b.tube(points,.024,'ba_gold',sides=5)
    # Rounded skylight termination, matched to the curved front colonnade.
    for j in range(16):
        a0=j*math.pi/16;a1=(j+1)*math.pi/16
        for k in range(8):
            def dome(a,t):return (8*math.cos(a)*math.cos(t),7.12+3*math.sin(t),16+4.5*math.sin(a)*math.cos(t))
            t0=k*math.pi/16;t1=(k+1)*math.pi/16
            b.mesh([dome(a0,t0),dome(a1,t0),dome(a1,t1),dome(a0,t1)],[(0,1,2,3)],'glass_ba_canopy')
        b.tube([dome(a0,k*math.pi/32) for k in range(17)],.06,'ba_verdigris')
    # Solid curved soffits with recessed coffers, four profile rails per panel.
    def sidepoint(side,u,v):
        return (side*u,5.9+1.2*math.sin((17-u)/9*math.pi/2),v)
    for side in [-1,1]:
        for i in range(6):
            u0=8+i*1.5;u1=u0+1.5
            for j in range(8):
                v0=j*2;v1=v0+2
                q=[sidepoint(side,u0,v0),sidepoint(side,u1,v0),sidepoint(side,u1,v1),sidepoint(side,u0,v1)]
                b.mesh(q+[(x,y+.35,z) for x,y,z in q],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'ba_cream')
                for inset,radius,mat in [(.10,.045,'ba_limestone'),(.24,.038,'ba_gold')]:
                    points=[sidepoint(side,u,v) for u,v in [(u0+inset,v0+inset),(u1-inset,v0+inset),(u1-inset,v1-inset),(u0+inset,v1-inset)]]
                    b.tube([(x,y-.04,z) for x,y,z in points],radius,mat,True)
                x,y,z=sidepoint(side,(u0+u1)/2,(v0+v1)/2)
                b.box((x,y-.03,z),(.35,.07,.35),'ba_coffer');b.box((x,y-.075,z),(.14,.035,.14),'ba_lamp')
        for u in [8,8.22,16.8,17]:
            x,y,_=sidepoint(side,u,0);b.box((x,y-.12,8),(.12,.2,16.2),'ba_limestone')
    # Front annular soffit and its radial coffers; open beneath it.
    for j in range(32):
        a0=j*math.pi/32;a1=(j+1)*math.pi/32
        def ring(a,k,yoffset=0):return ((8+9*k)*math.cos(a),7.1-1.2*k+yoffset,16+(4.5+5*k)*math.sin(a))
        q=[ring(a0,0),ring(a1,0),ring(a1,1),ring(a0,1)]
        b.mesh(q+[(x,y+.35,z) for x,y,z in q],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'ba_cream')
        if j%2==0:
            b.tube([ring(a0,k/8,-.04) for k in range(9)],.07,'ba_limestone')
        for k in [.20,.52,.82]:
            b.tube([ring(a,k,-.04) for a in [a0,a1]],.055,'ba_limestone')
    # Perimeter frieze and moulded cornices follow a single continuous horseshoe.
    perimeter=[(-17,0),(-17,8),(-17,16)]+[(17*math.cos(a),16+9.5*math.sin(a)) for a in [math.pi-j*math.pi/32 for j in range(1,33)]]+[(17,8),(17,0)]
    for (x0,v0),(x1,v1) in zip(perimeter,perimeter[1:]):
        b.mesh([(x0,y,v0) for y in [5.25,5.95]]+[(x1,y,v1) for y in [5.25,5.95]],[(0,1,3,2)],'ba_limestone')
    for y,r,mat in [(5.2,.11,'ba_bronze'),(5.35,.06,'ba_gold'),(5.92,.12,'ba_cream'),(6.12,.15,'ba_limestone')]:
        b.tube([(x,y,v) for x,v in perimeter],r,mat,sides=8)
    # Medallion frieze along straight sides, inset bronze disks and concentric rims.
    for side in [-1,1]:
        for v in [1+i*1.4 for i in range(11)]:
            for r in [.24,.30]:b.tube([(side*17.02,5.62+r*math.sin(a),v+r*math.cos(a)) for a in [j*math.tau/32 for j in range(32)]],.035,'ba_gold',True)
    for j in range(1,24):
        a=j*math.pi/24;x=17.025*math.cos(a);v=16+9.525*math.sin(a)
        tx,tz=-17*math.sin(a),9.5*math.cos(a);length=math.hypot(tx,tz);tx/=length;tz/=length
        for r in [.22,.29]:
            b.tube([(x+r*math.cos(t)*tx,5.62+r*math.sin(t),v+r*math.cos(t)*tz) for t in [k*math.tau/32 for k in range(32)]],.032,'ba_gold',True)
    columns=[(s*16.7,v) for s in [-1,1] for v in [1.2,8,15.7]]
    columns += [(16.7*math.cos(a),16+9.3*math.sin(a)) for a in [math.pi/6,math.pi/3,2*math.pi/3,5*math.pi/6]]
    for n,(x,v) in enumerate(columns):
        if column_filter is not None and not column_filter(b.world((x,0,v))):continue
        b.lathe((x,0,v),[(0,.78),(.16,.78),(.24,.65),(.45,.62),(.57,.46),(4.7,.42),(4.86,.61),(5.08,.7),(5.25,.7)],'ba_bronze',32)
        for h in [.26,.50,1.15,4.55,4.83,5.04]:b.lathe((x,h,v),[(0,.64),(.06,.64)],'ba_gold')
        for j in range(16):
            a=j*math.tau/16;b.tube([(x+.455*math.cos(a),y,v+.455*math.sin(a)) for y in [.65,4.55]],.025,'ba_gold')
        b.proxy('column '+str(n),(x,2.63,v),(1.12,5.26,1.12))
        if n<6:tx,tv=0,1
        else:
            a=math.atan2((v-16)/9.3,x/16.7);tx,tv=-16.7*math.sin(a),9.3*math.cos(a);length=math.hypot(tx,tv);tx/=length;tv/=length
        for sign in [-1,1]:
            b.tube([(x+sign*d*tx,y,max(.1,v+sign*d*tv)) for d,y in [(0,4.45),(.4,4.7),(1.3,5.12),(2.2,5.18)]],.075,'ba_bronze')
    # Suspended opaline bowls with bronze cage ribs and beaded gold rims.
    for x in [-10.3,10.3]:
        for v in [3.2,9.2,15.2,20]:
            top=6.7;rim=4.65
            b.tube([(x,rim+.15,v),(x,top,v)],.07,'ba_verdigris',sides=10)
            for h in [5.0,5.8,6.5]:b.lathe((x,h,v),[(0,.12),(.08,.12)],'ba_gold')
            b.lathe((x,rim,v),[(-.65,.10),(-.56,.48),(-.36,.83),(0,1.02)],'ba_lamp',40)
            b.lathe((x,rim,v),[(-.07,1.05),(.05,1.10),(.16,1.0)],'ba_verdigris',40)
            for j in range(8):
                a=j*math.tau/8
                b.tube([(x+r*math.cos(a),rim+h,v+r*math.sin(a)) for h,r in [(-.65,.1),(-.56,.50),(-.36,.85),(0,1.04)]],.038,'ba_bronze')
            for j in range(32):
                a=j*math.tau/32;b.lathe((x+1.06*math.cos(a),rim+.02,v+1.06*math.sin(a)),[(0,.035),(.045,.035)],'ba_gold',8)
    # Entry pilasters and header are outside the existing clear door opening.
    door_half=3.05 if full else 5/(2*b.scale[0])+.08
    for side in [-1,1]:
        x=side*(door_half+.48)
        b.box((x,2.65,.12),(.66,5.3,.6),'ba_limestone')
        b.box((x,.26,.27),(.95,.50,.85),'ba_cream')
        b.box((x,5.20,.27),(1.03,.3,.85),'ba_cream')
        for u in [-.2,0,.2]:b.box((x+u,2.9,.44),(.065,3.8,.08),'ba_gold')
    # Match header to each live leaf rather than scaling it into the portal.
    header_y=4.5/b.scale[1]+.42
    b.box((0,header_y,.1),(door_half*2+.35,.54,.52),'ba_bronze')
    for h in [-.31,.31]:b.box((0,header_y+h,.23),(door_half*2+1,.11,.74),'ba_cream')
    b.lettering('B E L L A G I O',(0,header_y,.38),.32)
    for x in [-8,8]:
        b.lights.append(dict(name=PREFIX+b.name+' warm canopy '+str(x),type='point',position=b.world((x,4.35,10)),color='#ffe1ae',intensity=45,distance=12,decay=2))
    # Paving and pale inlay ribbons establish the arrival court without steps.
    b.box((0,.018,12),(33,.03,24),'ba_paver')
    for x in range(-16,17):
        for v in range(24):
            if (x+v)%3==0:b.box((x+.23,.038,v+.45),(.92,.008,.91),'ba_paver_light')
    for x in [-13,-4,4,13]:b.box((x,.05,12),(.20,.025,24),'ba_cream')
    for v in [1,7,13,19,23.5]:b.box((0,.05,v),(33,.025,.16),'ba_cream')
    # Paired stone urns and topiary leave generous central and side walk routes.
    for x in [-14.2,14.2]:
        for v in [2.8,18.4]:
            b.lathe((x,0,v),[(0,.57),(.15,.62),(.25,.45),(.70,.63),(.88,.80),(1.0,.81)],'ba_cream')
            b.lathe((x,1,v),[(0,.65),(.3,.69),(.8,.50),(1.5,.26),(2.2,.02)],'ba_foliage',24)
            b.proxy('urn '+str(x)+' '+str(v),(x,.55,v),(1.6,1.1,1.6))
    if full:
        # Fountain sits beyond the court and away from the central through route.
        for x in [-10.5,10.5]:
            v=29
            b.lathe((x,0,v),[(0,2.15),(.18,2.2),(.35,2.1),(.45,1.9)],'ba_limestone',64)
            b.lathe((x,.39,v),[(0,1.83),(.035,1.83)],'ba_water',64)
            b.lathe((x,0,v),[(.42,.44),(1.4,.28),(1.55,1.05),(1.72,1.1),(1.85,.23),(2.8,.12),(2.9,.53),(3.05,.57),(3.18,.09)],'ba_cream',48)
            b.proxy('fountain '+str(x),(x,.3,v),(4.4,.6,4.4))
    return b.finish()


def build_arrival():
    materials()
    parts=[canopy(Builder('lake arrival pavilion',(-130.55,0,34),(.88,1,.48),-math.pi/2),False)]
    return {k:[v for p in parts for v in p[k]] for k in ['colliders','lights']}
