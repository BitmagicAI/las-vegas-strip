"""Resolve lake-bank surface ownership without moving roads, lawns or railings.

Cuts affect render faces only. The existing physical bank remains closed. The
same operation runs on a full authoring build and the selective cached repair.
"""
from venetian_surface_ownership import subtract


def named(source, material):
    return lambda g: (g['property']=='bellagioBlock-exterior' and
                      g['source']==source and g['material']==material)


def reconcile(b):
    earth=named('south-arrival-landscape','lake-earth')
    paving=named('lakefront-strip-promenade','lake-paving')
    rock=named('lakefront-lake','lake-rock')
    stone=named('lakefront-strip-promenade','lake-stone')
    cream=named('lakefront-strip-promenade','lake-cream')
    steel=named('lakefront-strip-promenade','steel')
    report={}
    # The raised garden's edge owns its .02–.51m face, the walk owns the rest
    # of its slab, and the deep bank owns everything below those surfaces.
    report['garden_over_walk_m2']=subtract(b,earth,paving)
    report['garden_over_bank_m2']=subtract(b,earth,rock)
    report['walk_over_bank_m2']=subtract(b,paving,rock)
    # Remove hidden, coplanar caps below the rail plinths, not their visible trim.
    report['rail_caps_m2']=subtract(b,stone,cream)
    report['rail_over_walk_m2']=subtract(b,lambda g:stone(g) or cream(g) or steel(g),paving)
    report['garden_over_roadside_caps_m2']=subtract(b,earth,lambda g:g['source']=='lakefront-roadside-closures')
    return report


def close_roadside(b,city):
    """Cap the exposed cross-section of the existing city cut at x=-22.

    The city mesh and its top levels are authoritative. Cut faces are missing,
    not the pavement itself, so leave every horizontal road/walk face intact.
    Lower caps extend into the ground to close the view through the slab.
    """
    import numpy as np
    from common import Polygon,box,unary_union,parts,triangles
    masks={'sidewalk':[],'road':[],'gutter':[]}
    for g in city:
        if g['material'] not in masks:continue
        v=np.asarray(g['vertices'])
        if not len(v) or v[:,0].min()>-21.99 or v[:,0].max()<-22.01 or v[:,2].max()<398 or v[:,2].min()>595:continue
        for t in v[g['faces']]:
            n=np.cross(t[1]-t[0],t[2]-t[0])
            if abs(n[1])<np.linalg.norm(n)*.95 or t[:,1].max()>.4 or t[:,1].min()<.05:continue
            ps=[]
            for a,c in zip(t,np.roll(t,-1,axis=0)):
                if abs(a[0]+22)<1e-5:ps.append(a)
                if (a[0]+22)*(c[0]+22)<-1e-10:ps.append(a+(c-a)*((-22-a[0])/(c[0]-a[0])))
            if len(ps)<2:continue
            a=min(ps,key=lambda p:p[2]);c=max(ps,key=lambda p:p[2])
            if c[2]-a[2]<.001:continue
            p=Polygon([(a[2],-.20),(c[2],-.20),(c[2],c[1]),(a[2],a[1])]).intersection(box(398,-.2,595,.4))
            if p.area>1e-7:masks[g['material']].append(p)
    b.property='bellagioBlock-exterior';b.source='lakefront-roadside-closures';b.detail=0
    covered=Polygon();report={}
    for mat,ps in masks.items():
        p=unary_union(ps).difference(covered);covered=covered.union(p)
        report[mat]=p.area
        for part in parts(p):
            for t in triangles(part):
                points=[[-22,y,z] for z,y in list(t.exterior.coords)[:-1]]
                a=np.asarray(points)
                if np.cross(a[1]-a[0],a[2]-a[0])[0]>0:points.reverse()
                b.face('lake-paving' if mat=='sidewalk' else 'charcoal',points,True)
    return report


def support_roadside_verge(b,city):
    """Give the narrow retained verge beside the cut its visible floor height.

    City verges are visual-only. Once the old terrain was cut away this seam
    could lose support, so add collision for just the existing verge triangles
    in the four-metre transition strip. No duplicate render surfaces.
    """
    import numpy as np
    from common import Polygon,box,parts,triangles
    c=b.solids['bellagioBlock-exterior'];v=c['vertices'];idx=c['indices']
    def signature(points):return tuple(sorted(tuple(round(float(n),5) for n in p) for p in points))
    existing=set()
    for i in range(0,len(idx),3):
        t=[v[j*3:j*3+3] for j in idx[i:i+3]]
        if all(-22.01<=p[0]<=-17.99 and 397.99<=p[2]<=595.01 and -.01<=p[1]<=.05 for p in t):existing.add(signature(t))
    region=box(-22,398,-18,595);added=0
    for g in city:
        if g['material']!='verge':continue
        a=np.asarray(g['vertices'])
        if not len(a) or a[:,0].min()>-18 or a[:,0].max()<-22 or a[:,2].max()<398 or a[:,2].min()>595:continue
        for t in a[g['faces']]:
            if t[:,1].max()>.05 or t[:,1].min()<-.01:continue
            p=Polygon(t[:,[0,2]])
            if p.area<1e-8:continue
            coeff=np.linalg.solve(np.column_stack((t[:,0],t[:,2],np.ones(3))),t[:,1])
            for piece in parts(p.intersection(region)):
                for tri in triangles(piece):
                    points=[[x,float(coeff[0]*x+coeff[1]*z+coeff[2]),z] for x,z in list(tri.exterior.coords)[:-1]]
                    if signature(points) in existing:continue
                    existing.add(signature(points));aa=np.asarray(points)
                    if np.cross(aa[1]-aa[0],aa[2]-aa[0])[1]<0:points.reverse()
                    n=len(v)//3;v.extend(value for pt in points for value in pt);idx.extend([n,n+1,n+2]);added+=1
    return added
