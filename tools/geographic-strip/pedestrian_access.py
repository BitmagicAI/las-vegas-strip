from pathlib import Path
"""Pedestrian topology and small, streamed public bridge concourses.

OSM supplies horizontal alignments. Six metre bridge decks are an estimate;
indoor circulation without level tags is explicitly reconstructed, not surveyed.
"""
import json, math, collections, heapq
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, nearest_points, triangulate
from shapely.strtree import STRtree
from streets import StreetBuilder
WALK={'footway','path','pedestrian','steps'}


def correct_heights(roads,elev):
    """Keep pavements at grade; steps join level landings, never sagging ramps.
    A sidewalk meeting a bridge at an elevator remains a separate ground level.
    Explicit bridge nodes win at the shared landing, but each sidewalk uses its
    own grade in the mesh builder (one OSM node can describe two levels).
    """
    # Preserve the independently solved vehicle grades before pedestrian
    # landings update shared OSM nodes (e.g. the Venetian forecourt driveway).
    for r in roads:
        if r['highway'] not in WALK:r['heights']=[elev[n] for n in r['nodes']]
    walking=[r for r in roads if r['highway'] in WALK]
    ground={n for r in walking if r['tags'].get('footway') in ('sidewalk','crossing') for n in r['nodes']}
    links=collections.defaultdict(list);height={};seeds=set()
    for r in walking:
        if r['bridge']:
            for n in r['nodes']:height[n]=6*max(1,int(r['tags'].get('layer','1')));seeds.add(n)
        if r['highway']=='steps' or r['tags'].get('footway') in ('sidewalk','crossing'):continue
        for a,b in zip(r['nodes'],r['nodes'][1:]):links[a].append(b);links[b].append(a)
    queue=collections.deque(seeds)
    while queue:
        n=queue.popleft()
        for k in links[n]:
            if k in height or k in ground:continue
            height[k]=height[n];queue.append(k)
    for r in walking:
        # Sidewalks never become enormous wedge-shaped bridge approaches.
        if r['tags'].get('footway') in ('sidewalk','crossing') and not r['bridge']:
            r['heights']=[0.0]*len(r['nodes']);continue
        h=[height.get(n,0.0) for n in r['nodes']]
        if r['highway']=='steps':
            distances=[0]
            for a,b in zip(r['points'],r['points'][1:]):distances.append(distances[-1]+math.dist(a,b))
            h=[h[0]+(h[-1]-h[0])*d/distances[-1] for d in distances]
        r['heights']=h
        for n,v in zip(r['nodes'],h):elev[n]=v
    # Bellagio north-west corner has short flights on a raised forecourt.
    # Infer their intermediate terrace from the two connected stair flights,
    # instead of raising a 4 m long staircase by the full bridge height.
    byid={r['id']:r for r in walking}
    for ident in (115672898,346408992,1436726287,1436726288,1436726289,1436726290,1436726291):
        r=byid.get(ident)
        if not r:continue
        if ident in (115672898,346408992):r['heights']=[0,3]
        elif ident in (1436726289,1436726290):r['heights']=[3,6]
        else:r['heights']=[3]*len(r['nodes'])
    # Actual elevator links are vertical circulation, not ramps across a sidewalk.
    for r in walking:
        if not r['bridge'] and r['highway']!='steps' and max(r['heights'])>0 and min(r['heights'])==0:
            r['verticalLink']=True
    # Route-graph heights also remain on the vehicle solution. Every walking
    # way carries its own explicit heights, so a shared node is not ambiguous.
    for r in roads:
        if r['highway'] not in WALK:
            for n,h in zip(r['nodes'],r['heights']):elev[n]=h
    return roads


def parts(g,kind='Polygon'):
    if g.is_empty:return []
    if g.geom_type==kind:return [g]
    return [p for child in getattr(g,'geoms',[]) for p in parts(child,kind)]


def interior_route(poly,start,end):
    """Visibility graph keeps generic connectors inside concave building outlines."""
    a,b=Point(start),Point(end);safe=poly.buffer(-.7)
    if safe.is_empty:safe=poly
    if not safe.covers(a):a=nearest_points(a,safe)[1]
    if not safe.covers(b):b=nearest_points(b,safe)[1]
    a,b=tuple(a.coords[0]),tuple(b.coords[0])
    if poly.buffer(.1).covers(LineString([a,b])):return [a,b]
    vertices=[a,b]
    for p in parts(safe.simplify(.15)):
        for ring in [p.exterior,*p.interiors]:vertices.extend(list(ring.coords)[:-1])
    graph=collections.defaultdict(list);allowed=poly.buffer(.15)
    for i,p in enumerate(vertices):
        for j in range(i):
            q=vertices[j]
            if allowed.covers(LineString([p,q])):
                length=math.dist(p,q);graph[i].append((j,length));graph[j].append((i,length))
    costs={0:0};previous={};queue=[(0,0)]
    while queue:
        cost,i=heapq.heappop(queue)
        if i==1:break
        if cost!=costs[i]:continue
        for j,d in graph[i]:
            if cost+d<costs.get(j,1e20):costs[j]=cost+d;previous[j]=i;heapq.heappush(queue,(cost+d,j))
    if 1 not in costs:raise ValueError('No indoor path through building')
    path=[b];i=1
    while i: i=previous[i];path.append(vertices[i])
    return path[::-1]


class AccessPlanner:
    def __init__(self,survey,roads,cut,replacement_ids):
        self.plans=[];self.voids=[];self.upper_mask=Polygon();self.ramp_mask=Polygon()
        buildings=[]
        for b in survey['buildings']:
            if (b['id'] in replacement_ids and b['id']!='relation/1599958') or b['height']<8 or b['base']>6:continue
            shape=unary_union([Polygon([(x,-z) for x,z in p[0]],[[(x,-z) for x,z in ring] for ring in p[1:]]).buffer(0) for p in b['polygons']])
            buildings.append((b,shape))
        tree=STRtree([p for b,p in buildings]);hits=collections.defaultdict(list)
        for r in roads:
            if not r['bridge'] or r['highway'] not in WALK:continue
            for i in (0,-1):
                p=Point(r['points'][i]);candidates=[]
                for index in tree.query(p.buffer(1.2)):
                    b,poly=buildings[index]
                    if poly.distance(p)>1.2 or cut.buffer(.5).covers(p):continue
                    candidates.append((index,poly.area))
                if candidates:
                    index=min(candidates,key=lambda x:x[1])[0]
                    if all(p.distance(Point(hit['p']))>3 for hit in hits[index]):hits[index].append(dict(p=list(p.coords[0]),approach=r['points'][1 if i==0 else -2],way=r['id'],y=r.get('heights',[6])[i]+.035))
        for index,entries in hits.items():
            b,poly=buildings[index]
            # Only walkable bridge decks, not below-grade/tiny source artifacts.
            entries=[e for e in entries if e['y']>2]
            if not entries:continue
            if b['id']=='relation/1599958':self.bellagio(poly);continue
            self.generic(b,poly,entries)
        # North entry terminates on a non-bridge landing. Keep both Bellagio doors.
        if not any(p['id']=='bellagio-via' for p in self.plans):
            b,poly=next((b,p) for b,p in buildings if b['id']=='relation/1599958');self.bellagio(poly)
        self.upper_mask=unary_union([p['upper'] for p in self.plans])
        self.ramp_mask=unary_union([p['stairArea'] for p in self.plans])
        self.voids=[(p['void'].buffer(.45),0,p['y']+6.3) for p in self.plans]
        self.tree=STRtree([v[0] for v in self.voids])

    def bellagio(self,poly):
        # Centerlines from OSM ways 1351221643/1415781861/1551178830;
        # arrangement checked against MGM's North Valet / Via Bellagio map.
        paths=[[( -68.46,169.7),(-68.17,205.91)],
            [(-33.9,194.64),(-41.43,194.59),(-41.63,197.16),(-68.17,205.91),(-105.07,216.55),(-141.76,216.88),(-176.9,236.22)]]
        # East descent follows the corner's street-facing flank. The former
        # southbound flight and U-shaped ground hall projected into the lake.
        stairs=[((-48,204),(-29,215)),((-180,239),(-190,225))]
        lower=[[(-29,215),(-23,216),(-18,219)],[(-190,225),(-193,221),(-195,215),(-193,207),(-198,196)]]
        # The eastern lower landing is outdoors: no freestanding exit door.
        portals=[dict(p=[-72.2,171.83],direction=[1,0],y=6.085,label='VIA BELLAGIO'),dict(p=[-68.44,174.0],direction=[0,1],y=6.085,label='VIA BELLAGIO'),dict(p=[-37.5,194.64],direction=[-1,0],y=6.085,label='VIA BELLAGIO'),dict(p=[-195,199],direction=[-.75,-.66],y=.18,label='NORTH VALET')]
        if Path('build/resort-blocks/bellagio/replacement-ids.json').exists():
            portals.append(dict(p=[-192.4,227.6],direction=[-.67,.74],y=.18,label='CASINO / MAIN LOBBY'))
        self.add('bellagio-via','Via Bellagio',poly,paths,stairs,lower,portals,6.085,True)

    def generic(self,b,poly,entries):
        # Work within the connected polygon owning the first bridge endpoint.
        poly=min(parts(poly),key=lambda p:p.distance(Point(entries[0]['p'])))
        ident=b['id'].replace('/','-');center=poly.representative_point();paths=[];portals=[]
        for e in entries:
            p=Point(e['p']);q=nearest_points(p,poly.boundary)[1];inside=nearest_points(p,poly.buffer(-6))[1] if not poly.buffer(-6).is_empty else center
            dx,dz=inside.x-q.x,inside.y-q.y;length=math.hypot(dx,dz) or 1;direction=[dx/length,dz/length]
            inside=Point(p.x+direction[0]*6,p.y+direction[1]*6)
            ax,az=e['approach'][0]-p.x,e['approach'][1]-p.y;length=math.hypot(ax,az) or 1
            outer=[p.x+ax/length*5,p.y+az/length*5]
            paths.append([outer,list(p.coords[0]),list(inside.coords[0])]);portals.append(dict(p=list(p.coords[0]),direction=direction,y=e['y']+.05,label=b['name'] if b['name']!='Unnamed building' else 'PEDESTRIAN CONCOURSE'))
        hub=paths[0][-1]
        if b['tags'].get('highway')=='elevator':
            # A mapped lift kiosk is not a hotel. Keep its compact landings and
            # provide a two-way lift instead of inventing an external stair bay.
            landing=list(center.coords[0]);paths=[[*path,landing] for path in paths]
            lower=[paths[0]]
            portals.append(dict(p=portals[0]['p'],direction=portals[0]['direction'],y=.18,label='PEDESTRIAN LIFT'))
            self.add(ident,'Pedestrian lift',poly,paths,[],lower,portals,entries[0]['y']+.05,False)
            self.plans[-1]['lift']=landing
            return
        joins=[interior_route(poly,hub,path[-1]) for path in paths[1:]];paths+=joins
        # Find a straight escalator bay behind an entrance, with street egress
        # at the same facade. Its footprint is reserved before building walls.
        direction=portals[0]['direction'];side=[-direction[1],direction[0]]
        top=[hub[0]+side[0]*8,hub[1]+side[1]*8]
        bottom=[top[0]+direction[0]*16,top[1]+direction[1]*16]
        for angle in [0,math.pi/2,-math.pi/2,math.pi]:
            dx=direction[0]*math.cos(angle)-direction[1]*math.sin(angle);dz=direction[0]*math.sin(angle)+direction[1]*math.cos(angle)
            candidate=[top[0]+dx*16,top[1]+dz*16]
            if poly.buffer(.3).covers(LineString([top,candidate]).buffer(2.5)):
                bottom=candidate;break
        paths.append([hub,top])
        v=[bottom[0]-top[0],bottom[1]-top[1]];length=math.hypot(*v)
        landing=[bottom[0]+v[0]/length*3,bottom[1]+v[1]/length*3]
        # The lower portal must be beyond the escalator discharge, not the
        # nearest wall behind it (which puts its jamb through the incline).
        run=LineString([top,bottom]);boundary=poly.exterior
        candidates=[boundary.interpolate(d) for d in range(0,math.ceil(boundary.length),3)]
        candidates=[q for q in candidates if q.distance(run)>5]
        q=min(candidates,key=lambda q:q.distance(Point(landing))) if candidates else nearest_points(Point(landing),boundary)[1]
        safe=poly.buffer(3).union(LineString([bottom,landing]).buffer(5)).difference(run.buffer(3.5,cap_style=2))
        
        try:route=interior_route(safe,landing,list(q.coords[0]))
        except ValueError:
            print('Disconnected lower hall',ident,poly.bounds,top,bottom,landing,list(q.coords[0]),flush=True)
            raise
        d=[q.x-route[-2][0],q.y-route[-2][1]];length=math.hypot(*d) or 1;d=[v/length for v in d]
        exit=[q.x+d[0]*3,q.y+d[1]*3]
        lower=[[bottom,landing]+route+[list(q.coords[0]),exit]]
        portals.append(dict(p=list(q.coords[0]),direction=d,y=.18,label='STREET EXIT'))
        self.add(ident,b['name'],poly,paths,[(top,bottom)],lower,portals,entries[0]['y']+.05,False)

    def add(self,ident,name,poly,paths,stairs,lower,portals,y,bellagio):
        # Keep through routes around the stair opening rather than letting a
        # diagonal corridor cross the well and lose its walking surface.
        forbidden=unary_union([LineString(stair).buffer(3.5,cap_style=2) for stair in stairs])
        routed=[]
        for path in paths:
            result=[path[0]]
            for a,b in zip(path,path[1:]):
                if LineString([a,b]).intersects(forbidden) and not any(math.dist(b,t)<.1 or math.dist(a,t)<.1 for t,_ in stairs):
                    result+=interior_route(poly.buffer(3).difference(forbidden),a,b)[1:]
                else:result.append(b)
            routed.append(result)
        paths=routed
        # Generous horizontal landings before the inclined escalator run.
        for top,bottom in stairs:
            dx,dz=bottom[0]-top[0],bottom[1]-top[1];length=math.hypot(dx,dz)
            approach=(top[0]-dx/length*2,top[1]-dz/length*2)
            network=unary_union([LineString(path) for path in paths]);q=nearest_points(Point(approach),network)[1]
            paths.append([list(q.coords[0]),approach,top])
        stair_area=unary_union([LineString(s).buffer(2.7,cap_style=2) for s in stairs])
        upper=unary_union([LineString(p).buffer(4 if bellagio else 3,cap_style=1,join_style=2) for p in paths])
        lower_shape=unary_union([LineString(p).buffer(3.5,cap_style=1,join_style=2) for p in lower])
        footprint=unary_union([upper,lower_shape,stair_area.buffer(.6)])
        self.plans.append(dict(id=ident,name=name,building=poly,upper=upper,lower=lower_shape,stairArea=stair_area,void=footprint,paths=paths,stairs=stairs,lowerPaths=lower,portals=portals,y=y,bellagio=bellagio))

    def wall(self,a,b,base,top):
        """Clip only wall openings in height, keeping roofs and upper storeys solid."""
        line=LineString([a,b]);length=line.length
        if length<1e-6:return []
        face=box(0,base,length,top)
        for index in self.tree.query(line):
            poly,lo,hi=self.voids[index]
            for segment in parts(line.intersection(poly),'LineString'):
                ts=[line.project(Point(p)) for p in segment.coords];face=face.difference(box(min(ts)-.01,lo,max(ts)+.01,hi))
        result=[]
        for p in parts(face):
            for tri in triangulate(p):
                if not p.covers(tri):continue
                vertices=[]
                for t,y in list(tri.exterior.coords)[:-1]:
                    xz=line.interpolate(t);vertices.append([xz.x,y,xz.y])
                result.append(vertices)
        return result

    def roof_triangle(self,vertices):
        """Cut entrances into sloped dome/podium surfaces as well as walls."""
        poly=Polygon([(v[0],v[2]) for v in vertices])
        if poly.area<1e-8:
            # Dome sectors can have a vertical radial seam whose X/Z
            # projection is a line. Clip it in distance/height space, just
            # like a facade, instead of leaving an invisible door-sized fin.
            points=[(v[0],v[2]) for v in vertices]
            a,b=max(((a,b) for a in points for b in points),key=lambda pair:math.dist(*pair))
            line=LineString([a,b])
            if line.length<1e-7:return []
            face=Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in vertices])
            if face.area<1e-8:return []
            for index in self.tree.query(line):
                void,lo,hi=self.voids[index]
                for segment in parts(line.intersection(void),'LineString'):
                    ts=[line.project(Point(p)) for p in segment.coords]
                    face=face.difference(box(min(ts)-.01,lo,max(ts)+.01,hi))
            result=[];kit=StreetBuilder(None,None,parts)
            for piece in parts(face):
                for tri in kit.triangles(piece):
                    points=[[line.interpolate(t).x,y,line.interpolate(t).y] for t,y in list(tri.exterior.coords)[:-1]]
                    if np.linalg.norm(np.cross(np.subtract(points[1],points[0]),np.subtract(points[2],points[0])))>1e-6:result.append(points)
            return result
        candidates=self.tree.query(poly)
        if not len(candidates):return [vertices]
        plane=np.linalg.solve(np.array([[v[0],v[2],1] for v in vertices]),np.array([v[1] for v in vertices]))
        remainder=poly
        for index in candidates:
            void,lo,hi=self.voids[index]
            band=list(vertices)
            for limit,above in [(lo,True),(hi,False)]:
                clipped=[]
                for a,b in zip(band,band[1:]+band[:1]):
                    ain=a[1]>=limit if above else a[1]<=limit;bin=b[1]>=limit if above else b[1]<=limit
                    if ain:clipped.append(a)
                    if ain!=bin:
                        t=(limit-a[1])/(b[1]-a[1]);clipped.append([a[j]+(b[j]-a[j])*t for j in range(3)])
                band=clipped
            if len(band)>=3:remainder=remainder.difference(void.intersection(Polygon([(v[0],v[2]) for v in band])))
        if remainder.equals(poly):return [vertices]
        result=[];kit=StreetBuilder(None,None,parts)
        for piece in parts(remainder):
            for tri in kit.triangles(piece):
                points=list(tri.exterior.coords)[:-1]
                if not poly.exterior.is_ccw:points.reverse()
                triangle=[[x,float(plane[0]*x+plane[1]*z+plane[2]),z] for x,z in points]
                # GEOS can leave collinear boundary slivers after subtraction.
                # Float32 physics quantization turns those into phantom fins.
                if np.linalg.norm(np.cross(np.subtract(triangle[1],triangle[0]),np.subtract(triangle[2],triangle[0])))>1e-6:result.append(triangle)
        return result

    def emit(self,out):
        folder=out/'access';folder.mkdir(exist_ok=True);manifest=[]
        for p in self.plans:
            meshes={};physics=dict(vertices=[],indices=[],spans=[])
            def mesh(key,mat,v,f):
                g=meshes.setdefault(mat,dict(material=mat,vertices=[],faces=[]));offset=len(g['vertices']);g['vertices']+=v;g['faces'] += [[i+offset for i in face] for face in f]
                if mat=='access-carpet':
                    uv=g.setdefault('uv',[]);line=s.uvline
                    for x,yy,z in v:
                        distance=line.project(Point(x,z));q=line.interpolate(distance);a=line.interpolate(max(0,distance-.1));b=line.interpolate(min(line.length,distance+.1));dx,dz=b.x-a.x,b.y-a.y;length=math.hypot(dx,dz) or 1
                        uv.extend([.5+((x-q.x)*(-dz/length)+(z-q.y)*(dx/length))/4.1,distance/6])
            def phys(key,v,f):
                physics['spans'].append([s.collision_material,len(physics['indices'])//3,len(f)])
                offset=len(physics['vertices'])//3;physics['vertices'] += [x for pt in v for x in pt];physics['indices'] += [i+offset for face in f for i in face]
            s=StreetBuilder(mesh,phys,parts);self.build(p,s)
            bounds=p['void'].bounds
            (folder/(p['id']+'-plan.json')).write_text(json.dumps(dict(upper=[list(q.exterior.coords) for q in parts(p['upper'])],lower=p['lowerPaths'],stairs=p['stairs'],portals=p['portals'],paths=p['paths'])))
            data=dict(lift=p.get('lift'),id=p['id'],name=p['name'],bounds=list(bounds),height=p['y']+6.3,portals=p['portals'],lights=p['lights'],signs=p['signs'],routes=p['routes'],meshes=list(meshes.values()),collision=physics)
            (folder/(p['id']+'.json')).write_text(json.dumps(data,separators=(',',':')))
            manifest.append({k:data[k] for k in ['id','name','bounds','height','portals']})
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2))
        print('Bridge concourses',len(manifest),flush=True)

    def build(self,p,s):
        y=p['y'];upper=p['upper'];stair_area=p['stairArea'];region=p['void'];p['lights']=[];p['signs']=[];p['routes']=[]
        # Both storeys share a clear circulation envelope. The escalator well is
        # cut out of the upper slab; floor and roof have real thickness.
        s.slab(region,.18,-.08,'access-stone')
        upper_floor=upper.difference(stair_area.buffer(-.12))
        s.slab(upper_floor,y,y-.30,'access-marble')
        # The north lakefront now owns the exterior and skylights. Keep this
        # streamed circulation shell inside the mapped building, never wrap
        # the outdoor descent in a featureless full-height tube.
        enclosure=region.intersection(p['building']) if p['bellagio'] else region
        s.slab(enclosure,y+5.6,y+5.35,'access-plaster')
        openings=[]
        for portal in p['portals']:
            x,z=portal['p'];dx,dz=portal['direction'];nx,nz=-dz,dx
            openings.append(LineString([(x-dx*12,z-dz*12),(x+dx*12,z+dz*12)]).buffer(2.25,cap_style=2))
            # A portal is a frame, not a second solid wall through circulation.
            # The enclosing shell owns the surrounding wall surfaces.
            # Marble portal surround with transom, bronze glazing mullions.
            for side in [-1,1]:s.beam([x+nx*side*2.23,portal['y'],z+nz*side*2.23],[x+nx*side*2.23,portal['y']+3.65,z+nz*side*2.23],.34,.34,'access-stone',True)
            s.beam([x-nx*2.4,portal['y']+3.55,z-nz*2.4],[x+nx*2.4,portal['y']+3.55,z+nz*2.4],.42,.30,'access-stone',True)
            p['signs'].append(dict(text=portal['label'],position=[x,portal['y']+3.26,z],yaw=math.atan2(dx,dz),width=3.8,height=.4))
        openings=unary_union(openings)
        # Continuous concourse walls, with proper ground and upper portal holes.
        for ring in [q.exterior for q in parts(region)]:
            for a,b in zip(ring.coords,list(ring.coords)[1:]):
                line=LineString([a,b])
                for part in parts(line.difference(openings).intersection(p['building']) if p['bellagio'] else line.difference(openings),'LineString'):
                    a,b=list(part.coords)[0],list(part.coords)[-1]
                    s.beam([a[0],(y+5.35)/2,a[1]],[b[0],(y+5.35)/2,b[1]],.25,y+5.35,'access-plaster',True)
                    s.beam([a[0],y+.25,a[1]],[b[0],y+.25,b[1]],.31,.50,'access-bronze')
        covered_runner=Polygon()
        walking_clearance=unary_union([LineString(path).buffer(2.5) for path in p['paths']]).union(stair_area.buffer(.8))
        for path in p['paths']:
            line=LineString(path);p['routes'].append([[x,y,z] for x,z in path])
            # A bordered blue runner below paired lanterns identifies Via Bellagio.
            runner=line.buffer(2.05,cap_style=2,join_style=2).intersection(upper_floor).difference(covered_runner.buffer(.16))
            covered_runner=covered_runner.union(runner)
            s.uvline=line
            if p['bellagio']:s.slab(runner,y+.012,y+.008,'access-carpet',False,False)
            for d in range(4,int(line.length)-2,6):
                q=line.interpolate(d);a=line.interpolate(max(0,d-.1));b=line.interpolate(d+.1);dx,dz=b.x-a.x,b.y-a.y;length=math.hypot(dx,dz);dx/=length;dz/=length;nx,nz=-dz,dx
                if stair_area.buffer(1).contains(q):continue
                for side in [-1,1]:
                    xx,zz=q.x+side*nx*3.55,q.y+side*nz*3.55
                    bay=LineString([(xx-dx*.4,zz-dz*.4),(xx+dx*5.5,zz+dz*5.5)]).buffer(.55)
                    # Leave crossing corridors and the escalator well open.
                    if bay.intersects(walking_clearance):continue
                    if p['bellagio']:
                        # Cylindrical marble shafts, with separate capitals/base.
                        for lo,hi,radius in [(0,.22,.34),(.22,3.65,.23),(3.65,3.9,.36)]:
                            vertices=[[xx+math.cos(k*math.tau/16)*radius,y+h,zz+math.sin(k*math.tau/16)*radius] for h in [lo,hi] for k in range(16)]
                            faces=[]
                            for k in range(16):
                                n=(k+1)%16;faces.extend([[k,n,n+16],[k,n+16,k+16]])
                            s.emit('access-marble',vertices,faces)
                    else:s.beam([xx,y,zz],[xx,y+3.8,zz],.4,.4,'access-stone')
                    # Window bays between columns: back wall, lit display plinths
                    # and bronze-framed glazing, rather than opaque flat panels.
                    cx,cz=xx+dx*3,zz+dz*3
                    if not p['bellagio']:continue
                    for off in [-2.45,2.45]:
                        fx,fz=cx+dx*off,cz+dz*off
                        s.beam([fx,y+.25,fz],[fx,y+3.45,fz],.12,.12,'access-bronze')
                    s.beam([cx-dx*2.4+nx*side*.24,y+1.8,cz-dz*2.4+nz*side*.24],[cx+dx*2.4+nx*side*.24,y+1.8,cz+dz*2.4+nz*side*.24],.08,2.9,'access-shop')
                    s.beam([cx-dx*2.4-nx*side*.35,y+1.8,cz-dz*2.4-nz*side*.35],[cx+dx*2.4-nx*side*.35,y+1.8,cz+dz*2.4-nz*side*.35],.035,2.9,'bridge-glass')
                    for off in [-1.45,0,1.45]:
                        px,pz=cx+dx*off,cz+dz*off
                        s.beam([px-dx*.30,y+.65,pz-dz*.30],[px+dx*.30,y+.65,pz+dz*.30],.48,.65,'access-marble')
                        s.beam([px-dx*.18,y+1.10,pz-dz*.18],[px+dx*.18,y+1.10,pz+dz*.18],.2,.25,'access-bronze')
                    s.beam([cx-dx*2.4,y+3.32,cz-dz*2.4],[cx+dx*2.4,y+3.32,cz+dz*2.4],.12,.12,'access-light')
                    brands=['LOUIS VUITTON','TIFFANY & CO.','CHANEL','BVLGARI','BOTTEGA VENETA','DIOR','GUCCI','FENDI']
                    p['signs'].append(dict(text=brands[(d//6+(0 if side==1 else 3))%8],position=[cx-nx*side*.4,y+3.10,cz-nz*side*.4],yaw=math.atan2(-nx*side,-nz*side),width=4.1,height=.28))
                # Vault ribs and the pale blue glazed panels below the structural roof.
                if p['bellagio']:
                    for i in range(12):
                        t0=math.pi*i/12;t1=math.pi*(i+1)/12
                        a=[q.x+nx*3.65*math.cos(t0),y+3.85+1.28*math.sin(t0),q.y+nz*3.65*math.cos(t0)]
                        b=[q.x+nx*3.65*math.cos(t1),y+3.85+1.28*math.sin(t1),q.y+nz*3.65*math.cos(t1)]
                        s.beam(a,b,.10,.10,'access-vault')
                        aa=[a[0]+dx*6,a[1]+.04,a[2]+dz*6];bb=[b[0]+dx*6,b[1]+.04,b[2]+dz*6]
                        s.emit('access-glazing',[a,b,bb,aa],[[0,2,1],[0,3,2]])
                        if i%3==0:s.beam(a,aa,.055,.055,'access-vault')
                for side in [-1,1]:
                    xx,zz=q.x+nx*side*1.5,q.y+nz*side*1.5
                    s.beam([xx,y+3.5,zz],[xx,y+4.8,zz],.045,.045,'access-bronze')
                    s.beam([xx,y+3.25,zz],[xx,y+3.70,zz],.28,.28,'access-light')
                    for a in [-1,1]:s.beam([xx+a*.17,y+3.18,zz],[xx+a*.17,y+3.78,zz],.035,.035,'access-bronze')
                p['lights'].append([q.x,y+3.2,q.y])
        for top,bottom in p['stairs']:
            line=LineString([top,bottom]);length=line.length;dx=(bottom[0]-top[0])/length;dz=(bottom[1]-top[1])/length;nx,nz=-dz,dx
            p['routes'].append([[top[0]+nx*1.05,y,top[1]+nz*1.05],[bottom[0]+nx*1.05,.18,bottom[1]+nz*1.05]])
            # Two escalators, stationary physical treads over a smooth collision
            # ramp. Feet remain supported, without individual step colliders.
            for side in [-1,1]:
                ax,az=top[0]+nx*side*1.05,top[1]+nz*side*1.05;bx,bz=bottom[0]+nx*side*1.05,bottom[1]+nz*side*1.05
                s.beam([ax,y-.12,az],[bx,.06,bz],1.8,.24,'bridge-metal',True)
                n=math.ceil((y-.18)/.16)
                for j in range(n):
                    t=(j+.5)/n;xx,zz=ax+(bx-ax)*t,az+(bz-az)*t;yy=y-(y-.18)*t+.03
                    s.beam([xx-dx*length/n/2,yy,zz-dz*length/n/2],[xx+dx*length/n/2,yy,zz+dz*length/n/2],1.6,.06,'access-tread')
                for sign in [-1,1]:
                    a=[ax+nx*sign*.94,y+.9,az+nz*sign*.94];b=[bx+nx*sign*.94,1.08,bz+nz*sign*.94]
                    # End caps sit beyond the pedestrian turning space.
                    ca=[a[j]+(b[j]-a[j])*.07 for j in range(3)];cb=[a[j]+(b[j]-a[j])*.93 for j in range(3)]
                    s.beam(a,b,.09,.12,'bridge-metal')
                    s.beam(ca,cb,.09,.12,'bridge-metal',True)
                    s.beam([ca[0],ca[1]-.45,ca[2]],[cb[0],cb[1]-.45,cb[2]],.08,.78,'bridge-glass',True)
            # Shared landings across both lanes.
            for pt,yy in [(top,y),(bottom,.18)]:
                pad=Point(pt).buffer(3.1,resolution=1)
                pad=pad.difference(stair_area.buffer(-.2)).difference(upper_floor) if yy==y else pad.difference(region)
                s.slab(pad,yy,yy-.25,'access-marble')
        for path in p['lowerPaths']:
            p['routes'].append([[x,.18,z] for x,z in path]);line=LineString(path)
            for d in range(2,int(line.length),7):
                q=line.interpolate(d);p['lights'].append([q.x,3.5,q.y]);s.beam([q.x-.4,3.7,q.y],[q.x+.4,3.7,q.y],.5,.05,'access-light')
