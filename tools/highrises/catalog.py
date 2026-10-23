"""Identity and architectural intent for the remaining mapped high-rises.
All dimensions come from the local OSM survey; photographs inform materials/details.
"""
# key, display name, facade family, glass, cladding, accent, source records
ROWS=[
('bellagio-spa','Bellagio Spa Tower','classical','#343f3d','#c9bba4','#ac8c58','25723910 114716301'),
('mirage','The Mirage','bronze','#81704a','#ded0ae','#a78b50','27727143'),
('treasure-island','Treasure Island','classical','#354846','#c29a76','#954d36','27727145'),
('park-mgm','Park MGM','classical','#35463b','#dbd1b6','#406343','27831695'),
('luxor','Luxor','dark','#172c35','#c1ad8b','#b49657','27858544 136516669 136516661 136516672 136520124 136520112 136520119'),
('mandalay-bay','Mandalay Bay','gold','#af9150','#ddd5be','#bf9a49','27858550'),
('horseshoe-east','Horseshoe East Tower','classical','#4b5960','#c4b4a4','#7d222d','27897922'),
('encore','Encore','bronze','#71573f','#b6a08a','#c4975c','27910891'),
('wynn','Wynn','bronze','#765a3f','#b7a18c','#b38550','205501268'),
('rio','Rio','rio','#394c73','#8d3035','#be7e3d','27998220 27998223 134938477 134938479 134938481'),
('palazzo','The Palazzo','classical','#38505a','#d6c8a8','#bd984b','30424125'),
('venetian','The Venetian','classical','#40575e','#d8c9aa','#b89c69','30618090 111322067 43875964'),
('westgate','Westgate','classical','#486479','#d0cfc5','#aa4c39','85402000'),
('signature','The Signature at MGM Grand','gold','#998251','#d6cbaf','#7b603b','95223224 95223232 95223231'),
('trump','Trump International','gold','#b19852','#d2c9a8','#b39953','111380664 111380666'),
('mgm-grand','MGM Grand','green','#174e40','#2b7260','#c7a856','115093734 115095167 115095169 115095172 115095174'),
('new-york','New York New York','deco','#34464d','#c1b5a2','#7c6751','115661791 115661792 115661795 115661796 115661797 115661798 115661799 115661800 115661801 115661802 115661805 115661806 115661807'),
('w-las-vegas','W Las Vegas','gold','#b49651','#d9cbae','#87724a','118347176'),
('harrahs','Harrah’s','classical','#52525b','#cbbfae','#8c356c','111367828 128632721'),
('sky','Sky Las Vegas','balcony','#54808b','#d8d1bf','#28495d','134068316 543641002'),
('fontainebleau','Fontainebleau','blue','#2b6885','#b8cbd0','#285992','134068318'),
('turnberry-place','Turnberry Place','balcony','#649193','#dfd3be','#867b61','134677416 134677429 134677425 134677417'),
('turnberry-towers','Turnberry Towers','balcony','#4c7f91','#d4d4c7','#777f78','134679980 134918082'),
('allure','Allure','balcony','#496d7c','#d4c4a6','#a69272','134935559'),
('circus-circus','Circus Circus','classical','#474c5d','#d6caca','#c73d52','135332955 135332957'),
('strat','The STRAT','strat','#36485c','#c9c9c3','#293f64','135457469 543641711'),
('sahara','SAHARA','classical','#3d414b','#d5c7b5','#a17945','276426484'),
('grand-chateau','Marriott’s Grand Chateau','classical','#495e5f','#d8c5ab','#985f41','276427203 358923855'),
('resorts-world','Resorts World','red','#425866','#b72e39','#cc3742','316303708'),
('panorama','Panorama Towers','balcony','#3b7184','#c1ced0','#777c7c','495545499 495545514'),
('martin','The Martin','blue','#3f687a','#a7afb0','#584c42','495695274'),
('springhill','SpringHill Suites','classical','#375b73','#d1c7b5','#56736c','543640999'),
('elara','Elara','dark','#293c5b','#638088','#34516e','r5342155'),
('hgv-boulevard','Hilton Grand Vacations Boulevard','classical','#466470','#d8c4a6','#ad795b','r6138877'),
('palms','Palms','deco','#5c7683','#c3b398','#69503c','r7655651'),
]
APARTMENTS={'sky','turnberry-place','turnberry-towers','allure','panorama','martin'}
SUITES={'signature','elara','grand-chateau','hgv-boulevard','trump','springhill','palazzo','venetian','encore','w-las-vegas'}
REFERENCE_NAMES={'bellagio-spa':'Bellagio','horseshoe-east':'Horseshoe','new-york':'New York New York','w-las-vegas':'W Las Vegas','hgv-boulevard':'Hilton Grand Vacations Boulevard','signature':'Signature MGM','springhill':'SpringHill Suites Convention Center','grand-chateau':'Marriott Grand Chateau','wynn':'Wynn Encore','encore':'Wynn Encore','venetian':'Venetian Palazzo','palazzo':'Venetian Palazzo','martin':'The Martin','sky':'Sky Las Vegas','harrahs':'Harrahs'}
def records():
 return [dict(key=k,name=n,family=f,glass=g,stone=s,accent=a,ids=[('relation/'+i[1:] if i.startswith('r') else 'way/'+i) for i in ids.split()],kind='apartment' if k in APARTMENTS else 'room',suite=k in SUITES or k in APARTMENTS,reference=REFERENCE_NAMES.get(k,n)) for k,n,f,g,s,a,ids in ROWS]
