exec(open('tools/geographic-strip/build-access-only.py').read())
for r in roads:
 line=LineString(r['points']);c=line.centroid
 if r['highway'] in WALK and -110<c.x<100 and 90<c.y<220:
  print(r['id'],r['highway'],'bridge',r['bridge'],r['tags'].get('conveying'),r.get('heights'),round(line.length,1),[(round(x,1),round(z,1)) for x,z in r['points']])
