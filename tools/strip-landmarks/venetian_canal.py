"""Mapped outdoor canal geometry; OSM horizontal outline, estimated water datum.
Reference cache is committed with project records. No network or runtime generation.
"""
import json,math
from pathlib import Path
from shapely.geometry import Polygon,Point,box,LineString
from common import Frame,parts,footprint
from venetian_waterways import WATER_Y
SOURCE=Path('docs/project-records/venetian-exterior-2026-10-09/canal-osm-reference.json')

def outlines():
 data=json.loads(SOURCE.read_text());result=[]
 for e in data['elements']:
  if e['id'] not in (115776193,180831029):continue
  points=[(6378137*math.radians(p['lon']+115.173)*math.cos(math.radians(36.116)),-6378137*math.radians(p['lat']-36.116)) for p in e['geometry']]
  poly=Polygon(points)
  assert poly.is_valid and poly.area>100, 'Invalid mapped canal outline'
  result.append((e['id'],poly))
 assert len(result)==2,'Both exterior basins required'
 return result

def canal(B):
 B.source='venetian-canal';B.detail=0
 boats=[(199,-726,.02),(203,-669,.8)]
 envelopes=[LineString([(x-5.5*math.sin(yaw),z-5.5*math.cos(yaw)),(x+5.5*math.sin(yaw),z+5.5*math.cos(yaw))]).buffer(1.55) for x,z,yaw in boats]
 for ident,water in outlines():
  B.planar('canal-water',water,WATER_Y)
  if ident==115776193:
   # OSM water outlines omit the covered bridge footprint; continue the water
   # underneath it so the two visible basins form one continuous outdoor route.
   from venetian_plaza import STEM
   B.planar('canal-water',Polygon(STEM).intersection(box(186,-1000,204,0)),WATER_Y)
  # Low stone coping follows actual concave basin/branch boundaries.
  # Keep it low at adjoining public routes; no invented tall blocking parapet.
  rim=water.buffer(.42,join_style=2).difference(water)
  if ident==115776193:
   rim=rim.difference(box(185.9,-702,204.1,-682))
  # Narrow pedestrian apron constrained to the basin edge; no road regeneration.
  buildings=footprint('relation/7770314').union(footprint('way/43875964'))
  apron=water.buffer(1.65,join_style=2).difference(water.buffer(.48,join_style=2)).difference(buildings)
  B.planar('marble',apron,.28)
  B.extrude('ivory',rim,.04,.48,True)
  for poly in parts(rim):B.planar('marble',poly,.485)
  if ident!=115776193:continue
  # Mooring poles stand inside water, not on roads; spacing follows shoreline.
  line=water.buffer(-1.15,join_style=2).exterior
  for i in range(int(line.length//7)):
   p=line.interpolate(i*7)
   if p.x>213 or any(e.contains(p) for e in envelopes):continue # narrow under-building branches remain unobstructed
   C=Frame(B,p.x,p.y,y=0)
   C.lathe('white',0,0,[(.15,.13),(1.95,.13),(2.10,.20),(2.25,0)],12)
   B.detail=1
   for j in range(5):C.lathe('red',0,0,[(.4+j*.3,.135),(.52+j*.3,.135)],12)
   B.detail=0
  for x,z,yaw in boats:
   from venetian_plaza import DECK
   assert water.contains(Point(x,z).buffer(3.5)) and not DECK.intersects(Point(x,z).buffer(3.5)), 'Gondola outside clear mapped basin'
   from venetian_gondola import gondola
   gondola(B,x,z,yaw)
 return {'eye':[-40,225,-1050],'target':[260,50,-650]}
