"""Add original colonnade detail to the preserved Forum Shops source.

Contractor photographs establish dark shafts and pale foliated capitals.
Dimensions follow the existing estimated facade, not a surveyed bay schedule.
"""
from common import *

BASE=Path('.bitmagic/city-exterior-backups/forum-entry')

def column(F,x,z):
    F.box('forum-limestone',(x,1.12,z),(1.12,1.76,1.12),True)
    F.lathe('forum-limestone',x,z,[(2,.57),(2.15,.57),(2.22,.48),(2.36,.48)],24)
    F.lathe('forum-column-dark',x,z,[(2.36,.43),(5.8,.415),(9.9,.35)],24)
    F.lathe('forum-limestone',x,z,[(9.88,.37),(10.04,.42),(10.15,.42),(10.75,.58),(10.88,.60)],24)
    F.box('forum-limestone',(x,11,z),(1.34,.24,1.34))
    # Original low-relief leaf folds and scrolls, not copied sculptural meshes.
    for j in range(8):
        a=j*math.tau/8
        def leaf(t,w=0):
            r=.40+.18*math.sin(math.pi*t)
            return F.p(x+r*math.cos(a)-w*math.sin(a),10.08+t*.66,z+r*math.sin(a)+w*math.cos(a))
        F.b.face('forum-relief',[leaf(0),leaf(.45,-.12),leaf(.98),leaf(.45,.12)])
        F.b.path('forum-limestone',[leaf(t) for t in np.linspace(0,1,5)],.025,5)
    for side in [-1,1]:
        F.path('forum-limestone',[(x+side*(.44+.12*math.cos(t)),10.65+.12*math.sin(t),z-.55) for t in np.linspace(0,math.tau*1.3,22)],.035,6)
    # A few subtle original veins are geometry, requiring no third-party texture.
    for j in range(3):
        pts=[]
        for k in range(13):
            h=2.45+k*.61; a=j*2.1+.22*math.sin(k*.65+j)
            r=.43-(h-2.36)/7.54*.08+.003
            pts.append(F.p(x+r*math.cos(a),h,z+r*math.sin(a)))
        F.b.path('forum-column-vein',pts,.009,4)

def build():
    old=json.loads((BASE/'forumShops-exterior.json').read_text())
    coll=json.loads((BASE/'forumShops-exterior-collision.json').read_text())
    B=Meshes();B.property='forumShops-exterior';B.source='forum-entry-colonnade';B.detail=1
    placed=[]
    for side in [-1,1]:
        def point(t):return (-8+(.012 if side<0 else .004)*(t-9)**2,-350+side*t)
        for j in range(5):
            a,b=point(9+j*6.4),point(9+(j+1)*6.4)
            if b[1]<a[1]:a,b=b,a
            length=math.dist(a,b);ux,uz=(b[0]-a[0])/length,(b[1]-a[1])/length
            F=Frame(B,a[0],a[1],math.atan2(-uz,ux),y=0)
            # One column per bay edge avoids doubling the shared bay junction.
            for x in ([.4,length-.4] if j==(0 if side<0 else 4) else [.4]):
                column(F,x,-.68);placed.append(F.p(x,0,-.68))
    nc=B.solids[B.property];offset=len(coll['vertices'])//3
    coll['vertices']+=nc['vertices'];coll['indices'] += [i+offset for i in nc['indices']]
    groups=list(B.groups.values())
    (OUT/'forumShops-exterior.json').write_text(json.dumps({'meshes':old['meshes']+groups,'labels':old['labels']},separators=(',',':')))
    (OUT/'forumShops-exterior-collision.json').write_text(json.dumps(coll,separators=(',',':')))
    report={'columns':placed,'addedTriangles':sum(len(g['faces']) for g in groups),'preservedGroups':len(old['meshes']),'scope':'Additive facade detail; unchanged old triangles, labels and collision prefix.'}
    Path('build/city-exteriors/forum-entry-detail.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':build()
