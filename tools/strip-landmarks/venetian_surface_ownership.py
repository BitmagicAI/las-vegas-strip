"""Cut shared render faces at authoring time. Physics and interior files are untouched.

The podium owns its lower shell. Tower shells own the volume above it. Trim and
shop fittings own their visible faces rather than drawing over a coincident cap.
"""
from collections import defaultdict
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from common import parts,triangles

def plane(t):
 n=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(n)
 if length<1e-7:return None
 n/=length;ax=int(np.argmax(abs(n)));n*=np.sign(n[ax]);d=float(n@t[0])
 return (*np.round(n,4),round(d,3)),ax,n,d

def subtract(B,owner,subject):
 masks=defaultdict(list)
 for g in B.groups.values():
  if not owner(g):continue
  for t in np.asarray(g['vertices'])[g['faces']]:
   info=plane(t)
   if info:masks[info[0]].append(Polygon(np.delete(t,info[1],axis=1)))
 masks={key:unary_union(ps) for key,ps in masks.items()}
 removed=0.
 for g in B.groups.values():
  if not subject(g):continue
  vertices=[];faces=[]
  def add(t):
   k=len(vertices);vertices.extend(t);faces.append([k,k+1,k+2])
  for t in np.asarray(g['vertices'])[g['faces']]:
   info=plane(t)
   if not info or info[0] not in masks:add(t.tolist());continue
   key,ax,n,d=info;p=Polygon(np.delete(t,ax,axis=1));remainder=p.difference(masks[key])
   if p.area-remainder.area<1e-8:add(t.tolist());continue
   removed+=p.area-remainder.area
   axes=[i for i in range(3) if i!=ax];orig=np.cross(t[1]-t[0],t[2]-t[0])
   for poly in parts(remainder):
    if poly.area<1e-8:continue
    for tri in triangles(poly):
     points=[]
     for xy in list(tri.exterior.coords)[:-1]:
      v=np.zeros(3);v[axes]=xy;v[ax]=(d-n@v)/n[ax];points.append(v)
     if np.dot(np.cross(points[1]-points[0],points[2]-points[0]),orig)<0:points.reverse()
     add([v.tolist() for v in points])
  g['vertices']=vertices;g['faces']=faces
 return removed

def reconcile(B):
 def named(source,material=None):
  return lambda g:g['property']=='venetian-exterior' and g['source']==source and (material is None or g['material']==material)
 report={}
 report['tower bases against podium']=subtract(B,named('venetian-podium'),lambda g:g['property']=='venetian-exterior' and g['source'].startswith('tower/') and g['material']=='ivory')
 report['north facade trim against podium']=subtract(B,named('venetian-north-frontage','ivory'),named('venetian-podium','pinkstone'))
 report['shop mullions']=subtract(B,named('palazzo-front','blackiron'),named('palazzo-front','champagne'))
 return report
