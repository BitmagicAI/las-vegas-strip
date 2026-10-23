"""Research photographs only. No downloaded photograph is shipped with the game."""
import json,urllib.request,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path('build/public-resorts/references')
REFS=[
('paris-entry','https://www.thevegasshoot.com/post/parking-guide-the-vegas-shoot-2025','https://static.wixstatic.com/media/ed5f02_8223fc82045e4b0ea04a4a82aadf14a3~mv2.jpg/v1/fill/w_1250%2Ch_763%2Cal_c/ed5f02_8223fc82045e4b0ea04a4a82aadf14a3~mv2.jpg'),
('paris-lobby','https://www.wyndhamhotels.com/caesars-rewards/las-vegas-nevada/paris-las-vegas/photo-gallery','https://www.wyndhamhotels.com/content/dam/property-images/en-us/ce/us/nv/las-vegas/51493/51493_lobby_view_3.jpg'),
('paris-casino','https://thehopefultraveler.blogspot.com/2012/04/paris-las-vegas-main-casino-floor.html','https://3.bp.blogspot.com/-wI1gBzTmpIM/UB17q0sOaPI/AAAAAAAALQk/R2JDsohTZ3M/s1600/4851433594_ba0afcbcfe_b.jpg'),
('caesars-arrival','https://www.bwaltd.com/project-detail/caesars-entry-remodel','https://static.wixstatic.com/media/3c87da_7841839a1a984ad1ba79acf4f0802778~mv2.jpg/v1/fill/w_5676%2Ch_3784%2Cal_c%2Cq_90/Copy%20of%20Caesars%20Palace%20Renovated%20Main%20Entrance_3224_w1a.jpg'),
('caesars-dome','https://www.vegasbusinessdigest.com/caesars-palace-enhances-guest-arrival-experience-with-multimillion-dollar-main-entrance-renovation/','https://www.vegasbusinessdigest.com/content/images/2022/09/Caesars-Palace-Renovated-Main-Entrance_3281_w1a.jpg'),
('cosmo-columns','https://thehopefultraveler.blogspot.com/2012/05/the-cosmopolitan-las-vegas-reception.html','https://2.bp.blogspot.com/-rufa1N-CmQk/UCggKd3RZQI/AAAAAAAAMUM/g4NMapz2FeA/s1600/Jan%2B11%2B069c.JPG'),
('cosmo-chandelier','https://www.cosmopolitanlasvegas.com/lounges-bars/chandelier','https://live.staticflickr.com/5017/5497080714_51ef660c4b_b.jpg'),
('aria-lobby','https://www.architecturalrecord.com/articles/7839-aria-resort-casino','https://www.architecturalrecord.com/ext/resources/archives/projects/portfolio/2010/08/images/aria_resort_casino-3_interior.jpg'),
('aria-river','https://www.3blmedia.com/news/world-water-day-we-all-play-role-conserving-earths-most-precious-resource','https://3blaws.s3.amazonaws.com/styles/carousel_2x/s3/images/ARI00024.jpg'),
('aria-entry','https://www.vegasalways.com/aria-las-vegas-parking/','https://www.vegasalways.com/wp-content/uploads/2022/05/Aria-Valet-Parking-768x512.jpg'),
('flamingo-lobby','https://www.lvtravelguide.com/hotel/flamingo-las-vegas','https://cdn.prod.website-files.com/67e18db02475cf19b5ce89ab/6844148874d0c67269c05610_flamingo-hotel-and-casino-lobby.webp'),
('flamingo-entry','https://www.booking.com/hotel/us/flamingo-casino.html','https://cf.bstatic.com/xdata/images/hotel/max1024x768/272998379.jpg?hp=1&k=80219426947fd538516bccef3149f84178e684045452806ef00a1d82fd87e848&o='),
('flamingo-casino','https://unsplash.com/photos/XUPeCYoDpvM','https://images.unsplash.com/photo-1650149044622-472659e87813?w=1200&q=80'),
('horseshoe-lobby','https://vegaschanges.com/2022/12/13/horseshoe-las-vegas-hotel-casino/','https://i0.wp.com/vegaschanges.com/wp-content/uploads/2022/12/DSC01229.jpg?resize=1200%2C900'),
('horseshoe-casino','https://www.bookonline.com/hotel/horseshoe-las-vegas','https://hotelmedia.s3.amazonaws.com/720/480/cad47927461e7de413f31174841320e535dc71ff'),
('horseshoe-entry','https://www.mapquest.com/us/nevada/the-lock-speakeasy-at-horseshoe-las-vegas-529767136','https://media-cdn.tripadvisor.com/media/photo-o/2d/a7/a5/7f/caption.jpg'),
('planet-hollywood-entry','https://www.atrapalo.com/hoteles/22520-0_hotel-planet-hollywood-resort-i-casino','https://cdn.atrapalo.com/hoteles/picture/l/225/2/0/415664531.jpg'),
('planet-hollywood-lobby','https://www.lasvegas.com/resorts/planethollywood/','https://www.lasvegas.com/media/slideshows/hotels/planethollywood/lg_planet-hollywood-20-lobby.jpg'),
('planet-hollywood-checkin','https://www.grealpha.com/about-us/project-showcase/planet-hollywood-resort--casino/','https://www.grealpha.com/images/about/thumb/70.jpg'),
('vdara-lobby','https://kensphotogallery.blogspot.com/2017/01/frank-stella.html','https://2.bp.blogspot.com/-QMPwPv9zvUY/WOEqI1xwOLI/AAAAAAABPX0/39UqE9S5hU0NGg3RB5HgE8_QG--NDot9ACLcB/s1600/EFP-P1040779.JPG'),
('waldorf-lobby','https://www.aliciatenise.com/waldorf-astoria-las-vegas-review/','https://www.aliciatenise.com/wp-content/uploads/2023/12/wa_lobby_0001.jpg'),
('waldorf-entry','https://moneyat30.com/travel-tuesday-waldorf-astoria-las-vegas-hotel-review/','https://moneyat30.com/wp-content/uploads/2020/11/waldorf-astoria-entrance-1000x666-1.jpg'),
('veer-lobby','https://ie.pinterest.com/pin/veer-towers-las-vegas-east-lobby--573153490050117254/','https://i.pinimg.com/736x/d2/ba/a8/d2baa82b4a4a076ae7aa050a59449f4a.jpg'),
('crystals-treehouse','https://blog.his-j.com/lasvegas/2016/07/post-382d-1.html','https://blog.his-j.com/.service/smartphone/thumb/photos/uncategorized/2016/07/12/ls2_8.jpg?alt=%2Flasvegas%2Fimages%2F2016%2F07%2F12%2Fls2_8.jpg'),
('bellagio-lobby','https://thepointsguy.com/hotel/reviews/bellagio-las-vegas/','https://runway-media-production.global.ssl.fastly.net/us/originals/2019/09/20190913_Las-Vegas-Bellagio_SHull-46.jpg?width=1200'),
]
REFS += [
 ('cosmo-entry','https://authority.cosmopolitanlasvegas.com/','https://thelibrary.mgmresorts.com/transform/6P1NoCensY076lkC/TCO151807276.jpg'),
 ('planet-hollywood-casino','https://www.agoda.com/planet-hollywood-resort-casino/hotel/las-vegas-nv-us.html','https://pix10.agoda.net/hotelImages/514/5143/5143_14041903350019131876.jpg?s=1024x768'),
 ('vdara-entry','https://www.vrbo.com/20108878ha','https://media.vrbo.com/lodging/113000000/112810000/112809300/112809237/f094bebb_edited_432f.jpg?impolicy=resizecrop&ra=fill&rh=575&rw=575'),
]
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'sources.json').write_text(json.dumps(REFS,indent=2))
def fetch(r):
 p=OUT/(r[0]+'.jpg')
 try:
  if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(r[2],headers={'User-Agent':'Mozilla/5.0'}),timeout=35).read())
  im=Image.open(p);im.load();return r[0],'ok'
 except Exception as e:return r[0],str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as p:
 for result in p.map(fetch,REFS):print(result,flush=True)
for start in range(0,len(REFS),9):
 board=Image.new('RGB',(1500,1080),'#182029');draw=ImageDraw.Draw(board)
 for j,r in enumerate(REFS[start:start+9]):
  x=(j%3)*500;y=(j//3)*360;draw.text((x+8,y+8),r[0],fill='white')
  try:
   im=Image.open(OUT/(r[0]+'.jpg')).convert('RGB');im.thumbnail((495,329));board.paste(im,(x,y+28))
  except:pass
 board.save(OUT/f'board-{start//9}.jpg')
