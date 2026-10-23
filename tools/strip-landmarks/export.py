"""Export locally-authored landmark surfaces with reusable PBR texture atlases."""
import bpy,json,math,hashlib,sys
import numpy as np
from pathlib import Path
OUT=Path('build/strip-landmarks');materials={}
colors={'white':'e8e7de','ivory':'e4dac7','stone':'bfb5a3','sandstone':'bbaa90','marble':'e2ded3','plaster':'ddd9d0','panel':'877467','roof':'8b8580','silver':'afb8bd','steel':'52616a','brass':'b99a56','bronze':'94704c','gold':'cfb060','blackiron':'242a2a','charcoal':'22292b','blue':'17619c','blue2':'4a91af','blue3':'9cbbc9','red':'bb3c44','warm':'fff2d2','screen':'1595ac','glass':'adc4cb','shopglass':'b0cbd0','cabinglass':'8faebc','darkglass':'293e47','water':'398f90','velvet':'777066','walnut':'614a39','grout':'b2afa6','foliage':'395942','bark':'77614a','vortex0':'937797','vortex1':'75638f','vortex2':'6989ab','ledblue':'356daa','cloudskin':'ddd9cc','pinkstone':'bb9d93','brick':'9a6650','bricklight':'b07c60','copper':'719588','copperpanel':'9e624d','copper2':'a7755c','copper3':'92593e','concrete':'8e8c89','magenta':'db146e','ice':'d6e6e6','fresco':'adb9c1','tile':'d5cec1','letter':'f5eedc','carpet':'31343f','floralcarpet':'43373b','skyglass':'c9d8df'}
colors.update({'cv-service-asphalt':'424345','cv-concrete-paint':'b7b1a4'})
colors.update({'fg-path':'b4a28c','fg-soil-paint':'475d36','fg-floor':'b5aa96','fg-pond_water':'457b76','fg-basin-paint':'33473e','fg-stone':'8f8b77','fg-roof-paint':'c7c5b8','fg-white-stucco':'d9d7c7','fg-coping-paint':'b9bcae','fg-glass':'344648','fg-frame-paint':'77756b','fg-tan-stucco':'b4a389','fg-green-roof-paint':'405b4c','fg-wood-paint':'574e3d','fg-equipment-paint':'b4b7ac','fg-dark-paint':'343c38'})
colors.update({'pl-dark-stucco':'535856'})
colors.update({'hel-panel-paint':'aeb5b5','hel-cap-paint':'c2c7c5','hel-metal-paint':'9fa9aa','hel-dark-paint':'30383b','hel-joint-paint':'737e80','hel-sign-paint':'dadcd5','hel-letter-paint':'30383b','hel-concrete':'bcbab0','hel-floor':'a6a8a2','hel-step':'8f9491','hel-paving':'b2afa4','hel-guard-glass':'a8c3c9'})
colors.update({'dos-wall-paint':'d2cebf','dos-roof-paint':'cdc9bc','dos-base-paint':'959184','dos-coping-paint':'bab9ad','dos-trim-paint':'b9b5aa','dos-door-paint':'aaa69c','dos-metal-paint':'7b807c','dos-dark-paint':'353c3b','dos-equipment-paint':'b4b7b1','dos-paving':'666661','dos-line-paint':'c3bfae'})
colors.update({'bcr-cream-stucco':'cbbfa7','bcr-cornice-paint':'d9cbb1','bcr-tile-paint':'b17e61','bcr-curved-tile-paint':'b17e61','bcr-rooflight-glass':'364a4a','bcr-metal-paint':'aaa996','bcr-service-paint':'b2afa1','bcr-cap-paint':'c6c1ad'})
colors.update({'nya-stone':'c8bfae','nya-pale-stone':'e2d8c5','nya-shadow-paint':'a09683','nya-roof-paint':'8a8780','nya-gold-paint':'b49b61','nya-ceiling-paint':'e1dbc7','nya-red-paint':'a6342c','nya-bulb-paint':'efe2b5','nya-dark-paint':'302f29','nya-letter':'eee8d9','nya-floor-concrete':'aaa49a'})
colors.update({'nik-green-paint': '357228', 'nik-edge-paint': '568b37', 'nik-panel-paint': '416f30', 'nik-base-paint': '3a682b', 'nik-roof-paint': '475545', 'nik-floor-concrete': 'aaa69b', 'nik-menu-frame-paint': '55554a', 'nik-paper-paint': 'c9c4b0', 'nik-ink-paint': '636052', 'nik-sign-paint': '1d2d21', 'nik-gold-letter': 'c2b263', 'nik-counter-paint': '493d2b', 'nik-dark-paint': '253d25', 'nik-handle-paint': '92998e'})
colors.update({'prb-wall-stucco': 'bdbdb2', 'prb-roof-paint': '9fa6a4', 'prb-coping-paint': 'bec7c5', 'prb-ceiling-paint': 'b7b9af', 'prb-floor-tile': '9f9f94', 'prb-trim-paint': 'c4c3b7', 'prb-gold-letter': 'ad9457', 'prb-panel-paint': 'a3a39a', 'prb-counter-paint': '353936', 'prb-green-paint': '315c49', 'prb-brass-paint': '9e8451', 'prb-bottle-paint': '2f4f35', 'prb-label-paint': 'b4ae87', 'prb-seat-paint': '4c4c42', 'prb-metal-paint': '4f5854', 'prb-service-paint': '9fa6a3', 'prb-vent-paint': '434e4c'})
colors.update({'re-white-stucco': 'd2d0bd', 're-fascia-paint': '966b50', 're-roof-paint': 'b2b4a5', 're-soffit-paint': 'a4a184', 're-cream-paint': 'aca886', 're-shadow-paint': '555745', 're-screen-concrete': 'c9c5ad', 're-downpipe-paint': '9d9b83', 're-gallery-concrete': 'b6b19c', 're-curb-paint': '878a7b', 're-service-paint': 'a2a698', 're-vent-paint': '454d44', 're-paving-concrete': 'bcb39f', 're-pool-tile': '8baca5', 're_pool': '449b9d', 're-coping-concrete': 'c5b399', 're-line-paint': 'b8b19e', 're-gravel': '786953', 're-frame-paint': 'b9bdaf', 're-glass': '3c4b49', 're-door-paint': '756e53', 're-metal-paint': '9fa292', 're-rail-paint': '6b6a53'})
colors.update({'bhs-green-metal-paint': '285344', 'bhs-roof-metal-paint': '527c61', 'bhs-trim-paint': '3c6652', 'bhs-rooflight-frame-paint': '909e8d', 'bhs-rooflight-paint': 'c0c5a4', 'bhs-service-paint': 'abb1a4', 'bhs-cap-paint': 'c1c6b7', 'bhs-shadow-paint': '29362d', 'bhs-base-concrete': '777b68', 'bhs-doorframe-paint': '717c6b', 'bhs-shutter-paint': 'afb4a2', 'bhs-shutter-joint-paint': '6c7b69', 'bhs-lamp-paint': 'b4b6a7', 'bhs-door-paint': '49614d', 'bhs-handle-paint': '939e91', 'bhs-vent-paint': '74846d', 'bhs-rib-paint': '3c634b', 'bhs-yard-concrete': '999d8b', 'bhs-block-concrete': '92937e', 'bhs-block-joint-paint': '6d7466', 'bhs-container-paint': '6a7053', 'bhs-muted-blue-paint': '485f70', 'bhs-frame-paint': '7d8578', 'bhs-pallet-paint': '837054', 'bhs-storage-paint': '7d806e'})
colors.update({'hc-cream-stucco': 'c3bca9', 'hc-roof-paint': '969b99', 'hc-coping-paint': '6a6b62', 'hc-rust-paint': '87493f', 'hc-frame-paint': 'c6c9c2', 'hc-glass': '3c4b50', 'hc-sill-paint': 'a5a69b', 'hc-plinth-paint': '8c897a', 'hc-downpipe-paint': 'aaa99b', 'hc-door-paint': '777165', 'hc-handle-paint': 'adb3b1', 'hc-curb-paint': '767a76', 'hc-service-paint': '8b9491', 'hc-grille-paint': '333e3b', 'hc-gallery-concrete': 'b9b5a6', 'hc-paving-concrete': 'b2afa2', 'hc-gravel': '6c6552', 'hc-rail-paint': '716f61', 'hc-asphalt': '555953', 'hc-line-paint': 'a9a58a', 'hc-wheelstop-concrete': '999785', 'hc-dark-letter': '635a46'})
colors.update({'san-tan-brick-paint': 'b7a281', 'san-coping-paint': 'b8aa92', 'san-brown-paint': '5b4934', 'san-mortar-paint': '8b7a60', 'san-awning-paint': '897961', 'san-frame-paint': '4b473b', 'san-door-paint': '736b5a', 'san-glass': '303c38', 'san-handle-paint': 'b2b6ad', 'san-service-paint': 'a2a9a5', 'san-vent-paint': '4c5250', 'san-shadow-paint': '292e2c', 'san-conduit-paint': '787d77', 'san-curb-paint': '95978e', 'san-roof-seam-paint': '969e9e', 'san-membrane-paint': 'c4cdcc', 'san-line-paint': 'baa35b', 'san-paving-concrete': 'b3ac9f', 'san-asphalt': '5e605b'})
colors.update({'s558-tan-brick-paint': '857052', 's558-brown-paint': '36261a', 's558-cream-paint': 'ada185', 's558-coping-paint': '8f8063', 's558-mortar-paint': '5e5240', 's558-shadow-paint': '110e0b', 's558-glass': '1f2421', 's558-frame-paint': '2e291f', 's558-door-paint': '4a4233', 's558-vent-paint': '1f211f', 's558-roof-metal-paint': '5c5c42', 's558-roof-rib-paint': '3d4030', 's558-service-paint': '858573', 's558-membrane-paint': 'a3a191', 's558-gravel': '614c38', 's558-paving-concrete': '87806e'})
colors.update({'rg-deck-concrete':'9d9b91','rg-edge-paint':'aaa899','rg-soffit-paint':'74776c','rg-ramp-concrete':'999b92','rg-rail-paint':'b5ae94','rg-tan-stucco':'c2ad83','rg-line-paint':'d7c18d','rg-curb-concrete':'b7b4a5','rg-coping-paint':'d3bea0','rg-service-paint':'8e958f','rg-shadow-paint':'343b39','rg-red-paint':'672c35','rg-white-letter':'eee8da','rg-paving-concrete':'afa99a'})
colors.update({'rr-tan-stucco':'b5a079','rr-cream-paint':'d4c6a0','rr-paving-concrete':'b6afa0','rr-roof-paint':'b2b2ab','rr-glass':'263b3d','rr-frame-paint':'c0beb5','rr-burgundy-paint':'742d2d','rr-red-paint':'ae2d24','rr-shadow-paint':'343530','rr-louver-paint':'8c8d7c','rr-escalator-paint':'777f7e','rr-white-letter':'f3eddb','rr-gold-paint':'e1b833','rr-gold-trim-paint':'b8932b','rr-service-paint':'909691'})
colors.update({'ha-ground-asphalt':'454544','ha-fascia-paint':'b4b7b4','ha-roof-paint':'c6c3b6','ha-soffit-paint':'a7a59c','ha-steel-paint':'b7bcba','ha-frame-paint':'d2d7d4','ha-panel-glass':'b1bebe','ha-roof-glass':'a5bdb7','ha-paving-concrete':'a8a59c'})
colors.update({'bap-stone':'b5a183','bap-cream':'dcc7a5','bap-trim':'e8d8ba'})
colors.update({'pc-paving-concrete':'b6b1a8','pc-silver-paint':'b3b0ad','pc-roof-paint':'a8aaa6','pc-soffit-paint':'7e7b78','pc-trim-paint':'d6d1ce','pc-joint-paint':'55555a'})
colors.update({'cv-white-paint':'e4e4dd','cv-roof-paint':'bfc4c4','cv-dark-paint':'151d23','cv-glass':'27343a','cv-frame-paint':'7b8587','cv-screen-paint':'9fa7aa','cv-white-letter':'eeeeea','cv-red-letter':'a81020','cv-red-paint':'ad1627','cv-door-frame-paint':'5a6264','cv-joint-paint':'51585b','cv-service-paint':'b1b8b7','cv-vent-paint':'4d565a'})
colors.update({'cr-nw-glass':'52616b','cr-nw-frame':'929b9e'})
colors.update({'rc-pale-stucco': 'c4d4ca', 'rc-roof-edge-paint': 'adbfaf', 'rc-roof-paint': 'cbd0c5', 'rc-floor-concrete': 'b2b7a7', 'rc-frame-paint': 'b6c1b4', 'rc-glass': '52645f', 'rc-louver-paint': 'a3b0a3', 'rc-screen-paint': 'd6d7c9', 'rc-door-paint': '819b88', 'rc-handle-paint': 'a0ada1', 'rc-rail-paint': 'acbfb0', 'rc-pool-tile': '619b9c', 'rc_pool': '569898', 'rc-coping-concrete': 'c9c9b2', 'rc-apron-concrete': 'b4b8a8'})
colors.update({'cga-white-paint': 'c4c7c0', 'cga-roof-paint': 'c4c7be', 'cga-cap-paint': 'a1a89d', 'cga-dark-brick': '5b5852', 'cga-black-paint': '333e3c', 'cga-glass': '526364', 'cga-frame-paint': '575e59', 'cga-gray-paint': '8a9389', 'cga-blue-letter': '45649e', 'cga-black-letter': '343b39', 'cga-blue-brick-paint': '7c9ac1', 'cga-rib-paint': 'b1b8ad', 'cga-shutter-paint': 'acb6af', 'cga-shutter-line-paint': '8c9b91', 'cga-service-paint': '8d9290', 'cga-red-letter': 'a45b55', 'cga-mortar-paint': 'afb5aa', 'cga-vent-paint': '535f57', 'cga-paving-concrete': 'a5a99a'})
colors.update({'cm-white-brick-paint': 'c4c6bd', 'cm-white-paint': 'd0d1c6', 'cm-roof-paint': '979b92', 'cm-red-roof-paint': '924a45', 'cm-seam-paint': '753a39', 'cm-gray-paint': '949e97', 'cm-red-paint': 'b54a43', 'cm-blue-paint': '354e8a', 'cm-glass': '42575b', 'cm-aluminum-paint': 'aab8b2', 'cm-dark-paint': '353e3a', 'cm-dark-letter': '353c36', 'cm-red-letter': '993c39', 'cm-blue-letter': '354c82', 'cm-wheelstop-concrete': 'aeb0a3', 'cm-line-paint': 'c8c8b5', 'cm-bollard-paint': 'd2aa41', 'cm-mortar-paint': 'b2b8ae', 'cm-door-paint': '9fa89f', 'cm-vent-paint': '4c5b55', 'cm-service-paint': 'a0a89a', 'cm-paving-concrete': 'abaea1', 'cm-asphalt': '565958'})
colors.update({'o515-brick':'956b5e','o515-white-paint':'d1d5c8','o515-frame-paint':'abb9aa','o515-glass':'677d73','o515-door-paint':'bdc7b9','o515-dark-letter':'45544c','o515-step-concrete':'a6afa0','o515-service-paint':'b1b4a4','o515-conduit-paint':'848d81','o515-mansard-paint':'566657','o515-roof-paint':'c7c9bb','o515-terrace-concrete':'acb2a3','o515-ramp-concrete':'adb4a4','o515-rail-paint':'37463c','o515-apron-concrete':'b1b0a0','o515-vent-paint':'59685c'})
colors.update({'ccc-gray-stucco':'999a90','ccc-roof-paint':'bdc1b6','ccc-roof-trim-paint':'b7bfb4','ccc-white-paint':'cbd1c6','ccc-frame-paint':'c2cdc3','ccc-glass':'526763','ccc-door-paint':'6b7e78','ccc-handle-paint':'aab4ab','ccc-ac-paint':'949d91','ccc-gallery-concrete':'a7aaa1','ccc-post-paint':'c2c8bb','ccc-service-paint':'a2a89d','ccc-office-stucco':'858f86','ccc-trim-paint':'7a837a','ccc-mansard-paint':'68756c','ccc-dark-letter':'343f39','ccc-court-concrete':'9a998b','ccc-pool-tile':'4b777b','ccc-pool-floor':'688c84','ccc_pool':'53918f','ccc-coping-concrete':'bcc4b8','ccc-boundary-stucco':'9fa496','ccc-gate-paint':'b7c3b8'})
colors.update({'ad-dark-brick':'4f514b','ad-flat-roof-paint':'b9b9aa','ad-coping-paint':'62645c','ad-charcoal-roof-paint':'3c4440','ad-red-roof-paint':'9e433e','ad-seam-paint':'6f6157','ad-white-paint':'c7cec4','ad-glass':'485c58','ad-handle-paint':'a3aca5','ad-red-letter':'9b343b','ad-white-letter':'dfdfca','ad-black-paint':'262d2a','ad-vent-paint':'59625c','ad-dark-paint':'353e39','ad-service-paint':'aaa99b','ad-patio-concrete':'777468','ad-table-wood':'69523b','ad-seat-wood':'66513b','ad-red-sign-paint':'a54c4a','ad-pavement-concrete':'a49e8e'})
colors.update({'sls-red-roof-paint':'a34b40','sls-roof-seam-paint':'913b34','sls-white-paint':'d7d6cb','sls-cornice-paint':'e1ded3','sls-flat-roof-paint':'bfc2b7','sls-brick':'986a55','sls-ivory-stucco':'c7c5b7','sls-glass':'5d7972','sls-frame-paint':'8d9b8f','sls-grille-paint':'525d52','sls-handle-paint':'adb6ac','sls-awning-fabric':'713e3f','sls-awning-stripe-paint':'a47c72','sls-service-paint':'a8ada5','sls-vent-paint':'59635f','sls-plaza-concrete':'afa996'})
colors.update({'spc-roof-paint':'b2b6b1','spc-fascia-paint':'cbd0c8','spc-tan-stucco':'c3b99d','spc-white-stucco':'c9cfc2','spc-frame-paint':'d3d8cb','spc-base-stucco':'a9ad9c','spc-glass':'536861','spc-sill-paint':'d4d8cc','spc-door-paint':'b7c1b4','spc-handle-paint':'7c8e85','spc-step-concrete':'b5b7aa','spc-veranda-concrete':'b9b9aa','spc-veranda-roof-paint':'b6bcb1','spc-white-rail-paint':'d4d8cb','spc-fence-paint':'35443c','spc-private-fence-paint':'677267','spc-service-paint':'b0b4aa','spc-vent-paint':'6b7970','spc-courtyard-concrete':'b7b5a6','spc-path-concrete':'b4b6a6','spc-parking-concrete':'b2b3a6','spc-joint-paint':'8c9589','spc-lawn':'647751'})
colors.update({'c525-bark':'897c66','c525-palm-stem':'7b805b','c525-palm-leaf':'66794d','c525-palm-light':'81905b'})
colors.update({'c525-core-paint':'5b6260','c525-mint-paint':'98bcb4','c525-blue-paint':'486d7c','c525-gravel':'a69b87'})
colors.update({'c525-ivory-stucco':'d4d4c4','c525-white-stucco':'d8d9d0','c525-terracotta-paint':'ac6853','c525-frame-paint':'d9dfdb','c525-glass':'627c7c','c525-metal-paint':'303c41','c525-door-paint':'ac4b2c','c525-coping-paint':'3c4649','c525-charcoal-paint':'515858','c525-tile-joint-paint':'7b8280','c525-gallery-concrete':'a8aeaa','c525-balcony-concrete':'c7cbc7','c525-soffit-paint':'c8ccc4','c525-roof-paint':'b9bbb4','c525-court-concrete':'c0bcad','c525-pool-tile':'3b7e85','c525-pool-floor':'6da8b0','c525_pool':'62a8b5','c525-coping-stone':'c7c4b7','c525-seat-fabric':'b4b8af','c525-asphalt':'62645f','c525-line-paint':'cdcec2','c525-planter-stone':'a69a80','c525-service-paint':'a7aca8','c525-dark-letter':'323f42'})
colors.update({'spo-boundary-block':'b3b7a9','spo-palm-stem':'78846a','spo-palm-leaf':'53694d','spo-palm-light':'71815a','spo-palm-dry':'887858','spo-frame-paint':'d2d5ca','spo-glass':'4c5f56','spo-siding-paint':'b7bdb1','spo-roof-paint':'9b9f97','spo-stone-base':'a79a7f','spo-siding-seam-paint':'a6ae9f','spo-door-paint':'abb6a4','spo-step':'b4b3a6','spo-asphalt':'62665c','spo-gravel':'9e9278','spo-vent':'9ba497','spo-fence-paint':'364236'})
colors.update({'oo-roof-paint':'877260','oo-fascia-paint':'777263','oo-window-frame-paint':'696e63','oo-glass':'364340','oo-bars-paint':'424b43','oo-door-frame-paint':'80877b','oo-door-paint':'778177','oo-handle':'a1a79d','oo-step':'b1b0a2','oo-fence-paint':'333c35','oo-fence-seam-paint':'444c43','oo-fence-post-paint':'515b4f','oo-asphalt':'65675c','oo-white-stucco':'c7c9bf','oo-base-paint':'b8bcb0','oo-sign-paint':'a8aaa0','oo-dark-letter':'343c33','oo-service-paint':'a1aa9c','oo-vent':'535e50','oo-carport-roof-paint':'b6b49c','oo-post-paint':'9b9e87','oo-line-paint':'b7b6a3','oo-wheelstop':'b8b3a0','oo-banner-paint':'59404d','oo-white-letter':'d4d1c5'})
colors.update({'ocs-stucco':'b7b3a3','ocs-roof-paint':'afa995','ocs-metal-paint':'afb6b1','ocs-metal-roof-paint':'a5b0ad','ocs-roof-seam-paint':'818d89','ocs-cap-paint':'a2a799','ocs-door-paint':'969b8b','ocs-door-seam':'747e70','ocs-frame-paint':'747e71','ocs-wall-seam-paint':'969f98','ocs-vent':'525c51','ocs-block':'a59880','ocs-timber':'87714c','ocs-yard-gravel':'9d9279','ocs-slab':'a9a79b','ocs-fence-paint':'6f6451','ocs-sign-paint':'d8d6c6','ocs-red-letter':'a74635','ocs-dark-letter':'333d34','ocs-service-paint':'a3a89b'})
colors.update({'wca-stucco':'c3c2b0','wca-roof-paint':'b6bab3','wca-cap-paint':'c9cabc','wca-shadow-paint':'51483c','wca-board-paint':'78634d','wca-board-joint-paint':'66533f','wca-soffit-paint':'aaa796','wca-tile-paint':'9d6c4d','wca-tile-roll-paint':'ac7958','wca-pier-paint':'d3d3c5','wca-paving':'b3ad9d','wca-sign-paint':'d6d7c9','wca-green-letter':'647b53','wca-red-letter':'a34d41','wca-joint-paint':'aeb0a1','wca-service-paint':'aaaFA3','wca-vent':'616b60','wca-asphalt':'585a51','wca-line-paint':'c3c2af','wca-fence-paint':'8b958b','wca-fence-wire':'697468','wca-roof-seam-paint':'c4c9c2'})
colors.update({'cu-gray-stucco':'929d9b','cu-roof-paint':'b3b9b5','cu-base-paint':'677576','cu-fascia-paint':'7c898b','cu-cap-metal-paint':'596a6d','cu-board0':'75685b','cu-board1':'817160','cu-board2':'6e6256','cu-board-joint':'675441','cu-stacked-ashlar':'a99b82','cu-service-paint':'8e9a97','cu-dark-letter':'303d42','cu-frame-paint':'3c4d50','cu-tower-paint':'405560','cu-tile-light':'4a606a','cu-tile-dark':'3b505b','cu-white-letter':'d4ddd7','cu-yellow-paint':'b4a65a','cu-asphalt':'4d5350','cu-paving':'b3b4a8','cu-gravel':'a89f82','cu-line-paint':'c8c9b9','cu-glass':'36504d','cu-vent':'4e5b56','cu-leaf':'597145','cu-leaf-light':'8d9c62','cu-wood':'86694b','cu-wood-joint':'6e573f'})
colors.update({'mp-white-paint':'d6d8d2','mp-roof-paint':'aeb3ad','mp-fascia-paint':'52595b','mp-coping-paint':'777e7b','mp-joint-paint':'c5c8c2','mp-turquoise-paint':'64a7ad','mp-drain-paint':'c2c6bf','mp-door-paint':'d4d7d1','mp-handle-paint':'767b79','mp-ink-letter':'454e4f','mp-rail-paint':'454c4e','mp-ramp':'aaa99e','mp-paving':'b8b5ab','mp-asphalt':'515451','mp-soil':'8d826b','mp-line-paint':'c3c1b3','mp-service-paint':'a6ada8','mp-vent':'606a65','mp-post-paint':'b0b8b4','mp-sign-paint':'ab7254','mp-white-letter':'e5e5da'})
colors.update({'sar-white':'deded3','sar-soffit':'cccbbd','sar-tile':'976b58','sar-roof':'b2b4a8','sar-blue':'284d85','sar-red':'a63a45','sar-cream':'c8c2a6','sar-island':'a6a797','sar-black':'29322d','sar-display':'687d73','sar-yellow':'b9a854','sar-light':'ded8b9','sar-orange':'c7673e','sar-panel':'77726b','sar-joint':'64645b','sar-glass':'3b534e','sar-frame':'394b49','sar-poster':'585a86','sar-metal':'969f97','sar-service':'aaa996','sar-vent':'5e6861','sar-asphalt':'494d47','sar-line':'c2c3b1','sar-paving':'a9aa9a'})
colors.update({'ps-stucco':'c8c4ad','ps-roof':'aaa99c','ps-trim':'bcb8a3','ps-dentil':'b3af9a','ps-door':'554a48','ps-glass':'364341','ps-metal':'7d8179','ps-frame':'414b44','ps-sill':'a7a993','ps-burgundy':'69414d','ps-sign-paint':'e4dfc5','ps-red':'9f3f49','ps-ink':'2e3033','ps-purple':'544358','ps-blue':'5266b1','ps-gold':'c1ad69','ps-bulb':'ded1a5','ps-white':'ddd8be','ps-panel':'ada995','ps-joint':'aaa68f','ps-service':'a4a28f','ps-vent':'555b53','ps-asphalt':'4b4c46','ps-line':'c1c0ab','ps-paving':'a6a596'})
colors.update({'lj-stucco':'b4a078','lj-roof':'aaa38e','lj-soffit':'9c8e72','lj-shadow':'4f493b','lj-board':'a48959','lj-board-joint':'7e6947','lj-trim':'b9a984','lj-poster':'aba492','lj-poster-ink':'3b3a35','lj-gray':'68706a','lj-recess':'b2a583','lj-metal-roof':'566167','lj-gold':'b19e62','lj-sign-paint':'c6bea5','lj-bulb':'c1b582','lj-joint':'8d7d61','lj-door':'766a50','lj-metal':'9d998a','lj-paving':'a79d85'})
colors.update({'do-sign-paint':'d7cbb2','do-stucco':'c3bba3','do-tile':'d7cbb2','do-roof':'aaa79b','do-ceiling':'aaa38f','do-joint':'b9ac92','do-red':'863c3e','do-ink':'34312d','do-gold':'9f8a5d','do-glass':'39443d','do-eave':'534b40','do-frame':'938979','do-sill':'b0a68b','do-door':'7e7862','do-metal':'928d80','do-walkway':'a29b88','do-rail':'4c4a3f','do-white':'e3d5b7','do-worn':'b9ae94','do-asphalt':'4a4842','do-paving':'b1a78d','do-pool':'578f92','do-line':'c3ba9e'})
colors.update({'ap-stucco':'c7bfa9','ap-cream':'dfdace','ap-roof':'b9b8aa','ap-roof-metal':'5b6a6b','ap-burgundy':'82454a','ap-gray':'92938d','ap-glass':'394c4b','ap-frame':'303937','ap-metal':'b2b7ad','ap-white':'e8e5d9','ap-red':'aa3335','ap-blue':'397491','ap-yellow':'d6b646','ap-ink':'28322e','ap-service':'827c6c','ap-joint':'aba18c','ap-asphalt':'4a4d49','ap-paving':'bab5a7','ap-line':'d3d0bb'})
colors.update({'ss-tan':'b4a389','ss-cream':'d4d0ba','ss-roof':'c6c6b4','ss-yellow':'d5b550','ss-red':'ab3a32','ss-white':'deded2','ss-black':'242d2e','ss-glass':'455953','ss-metal':'8d9794','ss-screen':'929f8f','ss-light':'dedbc3','ss-asphalt':'505451','ss-paving':'aaa99d'})
colors.update({'mv-stucco':'aaa593','mv-service':'b7b8ad','mv-roof':'787a72','mv-metal':'777e7e','mv-silver':'a4afaf','mv-joint':'8d8d81','mv-door':'989d95','mv-glass':'3d5256','mv-dark':'303837','mv-red':'ab4355','mv-asphalt':'494c49','mv-line':'c5c6b5','mv-paving':'b1b1a5','mv-gravel':'a5967b','mv-soil':'675b48','mv-stone':'9d9380'})
colors.update({'cw-cedar':'614637','cw-batten':'725746','cw-trim':'473a30','cw-shingles':'574b3b','cw-roof-edge':'786951','cw-glass':'b4a76b','cw-door':'302920','cw-metal':'746d61','cw-office':'b5a68b','cw-office-roof':'c4c5bb','cw-office-glass':'434e49','cw-asphalt':'444744','cw-paving':'b1ac9b','cw-grass':'50613a','cw-line':'d3ccb9','cw-sign':'ded9b8','cw-gold':'b89f5b'})
colors.update({'nv-masonry':'dedfd7','nv-white':'e5e4db','nv-roof':'bfc3bd','nv-fascia':'303332','nv-joint':'d0d1c9','nv-glass':'394c47','nv-door':'d9dacf','nv-panel':'cecec4','nv-metal':'797f7b','nv-ac':'bfc1b7','nv-shadow':'515b58','nv-paving':'a9aaa1','nv-asphalt':'454a48','nv-line':'cacbc1','nv-planter':'b9ac98','nv-leaf':'426948','nv-flower':'bb785d','nv-lotus':'a73157','nv-bulb':'e5cea4'})
colors.update({'di-white':'d4d6ca','di-roof':'c3c4bb','di-blue':'37678b','di-red':'a13440','di-glass':'476371','di-frame':'abb3ac','di-door':'50697b','di-ac':'a8ada6','di-shadow':'4f5a5d','di-paving':'bab6aa','di-asphalt':'505252','di-pool':'8ca6b1','di-letter':'eee8d7','di-pink':'aa6a91','di-toe':'deb2bc','di-eye':'262d30','di-ivory':'daceb9','di-leaf':'4c6750','di-soil':'82725b','di-line':'c8c8b7'})
colors.update({'om-stucco':'d5d2c5','om-ochre':'ac8b4e','om-trim':'b7b8ae','om-gray':'7c8583','om-glass':'34484c','om-frame':'9fa399','om-door':'626c68','om-roof':'b5b4a7','om-reveal':'4d534d','om-ac':'a6aca6','om-paving':'b4aca0','om-red':'9b4145','om-teal':'36787a','om-letter':'eee9db','om-soil':'7a6b53','om-leaf':'456341'})
colors.update({'ih-paving':'b8b3a8','ih-silver':'aeb5b7','ih-rib':'c1c8c9','ih-roof':'b8bdbb','ih-blue':'225681','ih-red':'a53535','ih-glass':'3d6a72','ih-metal':'a4b4b8','ih-letter':'eee9de','ih-dark':'333c41','ih-cream':'c9c3b5','ih-red-roof':'9d5442'})
colors.update({'ag-white':'e1e2df','ag-floor':'9b9d9d','ag-gray':'8b8e8f','ag-black':'20252b','ag-mat':'496257','ag-screen':'293354','ag-metal':'8a9398','ag-joint':'b5b9ba','ag-blue':'313f65','ag-purple':'684d80','ag-glass':'304553','ag-paving':'abaeaa','ag-range':'a2aeab','ag-green':'4d6658','ag-red':'a64e5a','ag-net':'4b5155'})
colors.update({'pb-gray':'777a78','pb-joint':'555a58','pb-white':'e6e4db','pb-charcoal':'252b2e','pb-red':'b3212b','pb-blue':'29485c','pb-yellow':'dec345','pb-glass':'30434b','pb-metal':'9da6a8','pb-roof':'aaa9a2'})
colors.update({'hd-asphalt':'383b3c','hd-silver':'aeb3b2','hd-concrete':'a4a59e','hd-orange':'bf5824','hd-red':'90352c','hd-cream':'d2bd90','hd-charcoal':'292e30','hd-joint':'60666a','hd-letter':'eee9db','hd-glass':'344b50','hd-roof':'a1a09a'})
colors.update({'luxor-pool-paving':'c3bbaa','luxor-pool-tile':'619497','luxor_pool':'398a93','luxor-chair-frame-paint':'595b58','luxor-chair-cushion':'376074','luxor-cabana-fabric':'bab8aa'})
colors.update({'ti-coral-paint':'b96c64','ti-retail-paint':'8c514d','ti-sign-paint':'24242c'})
colors.update({'palazzo-slate-paint':'52636b'})
colors.update({'cr-metal-paint':'a5afb0','cr-metal-light-paint':'bcc4c3','cr-soffit':'c1c2ba','cr-seam-paint':'929f9f'})
colors.update({'sky':'9ec3e6','sage':'566849','champagne':'c8b799','ochre':'bda483','purple':'734298','pinkled':'d647da','yellowled':'d6c04c','orchid':'a050a1','rose':'d085a1','teal':'2b8792','amethyst':'9781a5','rootwood':'8e785c','shipwood':'594432','rope':'a38b62','bottle':'304b39','mirror':'bbc7be','botanical':'899986','nautical':'859e9e','parkcarpet':'414739','palazzocarpet':'716153','ticarpet':'9b7755','harrahscarpet':'46414f'})
colors.update({'terracotta':'b77b5e','palazzo-stone':'d1ba95','palazzo-warm':'bb9570','palazzo-glass':'385b76'})
colors.update({'campanile-brick':'96726c','campanile-brick-light':'b19488'})
colors.update({'venetian-taupe':'aa947c','venetian-salmon':'c6957b','venetian-burgundy':'743347'})
colors.update({'palace-limestone':'c4b2b4','plaza-paving-dark':'525258','campanile-patina':'a3bfc0','rialto-roof':'d9dbd4'})
colors.update({'canal-water':'226f73','gondola-lacquer':'101d1e','gondola-upholstery':'83152a','gondola-brass':'c1a361','gondola-chrome':'b9cccf','gondola-wood':'776044'})
colors.update({'harrahs-purple':'665d87','harrahs-window':'24333e','harrahs-curtain':'706d69','harrahs-logo':'b64c79','harrahs-joint':'cccdc7'})
colors.update({'linq-blue':'235991','linq-glass':'284763','linq-facet-light':'87accc','linq-facet-dark':'21364e','linq-hex-grey':'aaaeb0','linq-hex-dark':'4b5265','linq-joint':'bfc4c7'})
colors.update({'linq-glass':'3376ac','linq-glass-side':'184779','linq-blue':'256498','linq-facet-light':'5995bb','linq-facet-dark':'143450','linq-mullion':'255275','linq-curtain':'9cacae'})
colors.update({'ti-stone':'e2dacf','ti-brick':'955d4c','ti-window':'30414a','ti-mullion':'c1b6a7','ti-roof':'c5c1b7'})
colors.update({'wf-stone':'c2b09c','wf-glass':'3b4d51','wf-metal':'65767a','wf-sill':'b4a694','wf-plinth':'8d8271','wf-roof':'a69d8b','wf-roof-metal':'94857c','wf-roof-rib':'75675d','wf-cornice':'c7bca9','wf-gold':'c3a56a','wf-paving':'c3bcb0'})
colors.update({'lvw-white':'d9dedb','lvw-panel':'bdc8c8','lvw-glass':'41616b','lvw-frame':'92a6aa','lvw-joint':'87969a','lvw-loading':'61757b','lvw-doorframe':'b6c4c6','lvw-door':'31484d','lvw-roof':'d3dcd9','lvw-soffit':'bcc9c7','lvw-service':'9eaba9','lvw-letter':'d9e2df','lvw-paving':'b8bbb2'})
colors.update({'oy-white':'d2d5cf','oy-blue':'788e9d','oy-glass':'394f5a','oy-frame':'a3b1b4','oy-sill':'daddd5','oy-mural':'576365','oy-mansard':'718590','oy-roof':'b9c0bc','oy-service':'929e9c','oy-red':'bf2b38','oy-letter':'e5e4d9','oy-orange':'c46b35','oy-paving':'bcb5a4','oyo_pool':'398b98'})
colors.update({'gd-cream':'d7d6c7','gd-gray':'9da69c','gd-trim':'dfdfd2','gd-glass':'465459','gd-frame':'a3aaa5','gd-reveal':'68716c','gd-roof':'bec3b9','gd-tile':'ab826b','gd-vent':'65726d','gd-service':'8c9690','gd-sign':'334f66','gd-paving':'c2b6a0','gd-coping':'d0c8b2','gd-pool-tile':'55938e','grand_desert_pool':'318d97'})
colors.update({'rh-cream':'d2cfbe','rh-stone':'b3ac99','rh-trim':'dbdacb','rh-glass':'46565b','rh-frame':'9aa5a1','rh-reveal':'626b69','rh-roof':'c3c5bb','rh-blue-roof':'7b9cae','rh-roof-seam':'a1b8c0','rh-sign':'364544'})
colors.update({'pk-white':'d5d7ce','pk-glass':'436e64','pk-frame':'81968a','pk-rail':'718378','pk-sill':'bcc7b8','pk-roof':'b1b8ad','pk-patina':'8faeb5','pk-service':'828d86'})
colors.update({'skg-sand':'c7b19e','skg-slab':'b7b7af','skg-rail':'c5c5bd','skg-deck':'a9aaa4','skg-line':'e3e2d4'})
colors.update({'wd-white':'d4d3ca','wd-pink':'bb8d84','wd-glass':'315a70','wd-frame':'a2b3b8','wd-sill':'e0dfd3','wd-cornice':'dbded8','wd-roof':'aab1ad','wd-soffit':'b5aea3','wd-service':'aeb6b5','wd-plant':'7f8c8d','wd-letter':'323f4b'})
colors.update({'pt-white':'d3d6d0','pt-blue':'526777','pt-glass':'2d4554','pt-frame':'86989e','pt-sill':'bdc6c5','pt-shadow':'18212a','pt-roof':'b4b8b3','pt-rail':'7b9098','pt-letter':'e9e5d5','pt-service':'979f9c','pt-coping':'c6c8b7','platinum_pool':'338e98','pt-chair':'bcbcb2'})
colors.update({'we-white':'d0d0c8','we-gray':'4c5964','we-stone':'a4a99f','we-glass':'304858','we-mullion':'778a93','we-sill':'babebc','we-shadow':'18232a','we-roof':'b4b6af','we-service':'949c9d','we-letter':'e8e5d5','we-coping':'c6c5b3','westin_pool':'337f88','we-chair':'bcb9ad'})
colors.update({'es-stone':'c7c2b3','es-gray':'526872','es-glass':'537d83','es-bronze':'82684c','es-copper':'946b55','es-salmon':'be9683','es-sill':'bcb8aa','es-roof':'c5c6be','es-shadow':'293638','es-service':'868d8c','es-letter':'eee9d4'})
colors.update({'as-yellow':'dfbb53','as-orange':'d79743','as-black':'111923','as-glass':'202f39','as-lanai':'445a67','as-frame':'727b7c','as-silver':'8d999f','as-joint':'323d47','as-roof':'727e85','as-etfe':'c9d5da','as-rib':'abbcc5','as-pier':'969d9d','as-letter':'e8e9e3'})
colors.update({'fl-stucco':'c6c4bc','fl-panel-joint':'aaa89e','fl-shop-glass':'687f87','fl-shop-frame':'242b2d','fl-membrane-paint':'c8c9c5','fl-service-paint':'a6aaa5','fl-petal-pink':'cd578c','fl-petal-cream':'e6ddcb','fl-petal-gold':'c3ae76','fl-patio-paving':'b8aea0','fl-table-wood':'85614c','fl-chair-fabric':'b96e53','fl-sign-dark':'41344a','luxor-membrane-paint':'cacbc5','luxor-service-paint':'a8aaa6','luxor-shadow':'655f54','luxor-sculpt-stone':'d8ceaf','luxor-sculpt-blue':'91b6bd','luxor-sculpt-gold':'c5b57d','luxor-sculpt-shadow':'897e66'})
# The Venetian's public interiors (2026-10-23): every 'vi-*' material, its textures and UVs (venetian_materials.py)
sys.path.insert(0,'tools/strip-landmarks');import venetian_materials as VM;colors.update(VM.COLORS)
patterns={'marble','stone','sandstone','brick','bricklight','copperpanel','copper2','copper3','walnut','velvet','panel','tile','fresco','roof','carpet','floralcarpet','botanical','nautical','parkcarpet','palazzocarpet','ticarpet','harrahscarpet','amethyst','shipwood','rootwood'}
colors.update({'blvd-painted-metal':'40494b','blvd-green-paint':'648b32','blvd-copper':'b65d32','forum-flat-roof':'c3c3bd','forum-skylight':'355571','forum-limestone':'d6caba','forum-plinth':'b9ab95','forum-panel':'c5b7a2','forum-roof':'c3c3bd','forum-roof-trim':'a9aaa5','forum-service':'b0b5b2','forum-shadow':'4b4c46','forum-glass':'344c54','forum-bronze':'807664','forum-relief':'b7a384','forum-joint':'a79983'})
colors.update({'stadium-concrete':'b6b3aa','stadium-steel':'6a7070','stadium-arch-paint':'deded6','stadium-shoring-paint':'367368','stadium-hoarding':'435b55','stadium-soil':'a6957c'})
colors.update({'wy-red-fabric':'8f2636','wy-theater-roof-paint':'8c7f68','wy-theater-center-paint':'b9ac90','wy-theater-wall-paint':'9d9075','wy-equipment-paint':'a9aaa1'})
colors.update({'sc-blue-paint':'7b8b9f','sc-blue-relief':'abb6c5','sc-rim-paint':'303b47','sc-atrium-glass':'477a96','sc-yellow-paint':'d8b521','sc-gold-paint':'c9a552'})
colors.update({'coke-glass':'447967','showcase-roof':'426b73'})
colors.update({'mgm-glass':'173e34','mgm-green':'33765f','mgm-frame':'688477','mgm-stone':'c8bfa9','mgm-bronze':'8f7950','mgm-joint':'79766b','mgm-screen':'182b3e','mgm-lit':'e6dcb9'})
colors.update({'ph-stone':'c5b7a6','ph-paving':'b2aaa0','ph-silver':'aeb5b8','ph-metal':'555f65','ph-black':'20262a','ph-white':'dfded8','ph-glass':'456474','ph-red':'9e2436','ph-disc':'57646a','ph-awning':'c7c1b6','ph-joint':'827e78','ph-letter':'f8e5b7','ph-led-blue':'18344e','ph-led-purple':'372849','ph-led-line':'36546a'})
colors.update({'ph-led-cylinder':'575687','ph-stucco':'d8c9b6','ph-roof':'b2aaa0','ph-window':'3d5260','ph-spandrel':'575357','ph-mullion':'8c8f91'})
colors.update({'park-white':'dbdad3','park-green':'7c885f','park-window':'465759','park-shadow':'343d3c','park-trim':'c7c8bc','park-joint':'b5b5ac','park-stone':'b6ad98','park-roof':'b7a991'})
colors.update({'luxor-glass':'615845','luxor-pyramid':'202e33','luxor-stone':'cbc6b7','luxor-band':'b9b7a9','luxor-mullion':'5c6666','luxor-joint':'aaa79a'})
colors.update({'mandalay-glass':'84764d','mandalay-white':'dbd9c8','mandalay-stone':'c9c2a7','mandalay-band':'aaa48d','mandalay-bronze':'8b8061','mandalay-window':'425951','mandalay-roof':'c1c0ae','mandalay-mint':'8eae98','mandalay-solar':'313d50'})
colors.update({'cc-flat-roof':'a7a6a0','cc-metal':'444c51','cc-door':'465866','cc-gold':'ae874b','cc-brown':'6b5043','cc-asphalt':'535354','circus_pool':'367f8d'})
colors.update({'cc-white':'dedbd7','cc-pink':'cf719d','cc-window':'505763','cc-sill':'c9c6c3','cc-shadow':'3b3d40','cc-blue':'497a9a','cc-yellow':'d6b535','cc-dome-glass':'aa668a','cc-dome-frame':'7e536b'})
colors.update({'rw-red':'a62c3b','rw-bronze':'685848','rw-mullion':'61554b','rw-white':'dfdbd2','rw-stone':'cec4ae','rw-fin':'8f806a','rw-gold':'b9995a','rw-joint':'b7afa0','rw-shadow':'303033','rw-metal':'747579','rw-led':'511629'})
colors.update({'rw-flat-roof':'c7c8bc','rw-blue-panel':'4a6477','rw-paving':'c5b9a1','rw-planter':'b7ac95','rw-soil':'454638','rw-garden':'526142'})
colors.update({'fb-flat-roof':'c9ceca','fb-canopy-white':'dedfd8','fb-soffit':'3c4549','fb-rib-metal':'a8b1b5','fb-limestone':'d6d7d1','fb-silver':'bbc4c8','fb-metal':'7e919b','fb-glass':'22566c','fb-joint':'284a59','fb-shadow':'293b45','fb-paving':'c5b99e','fb-pool-tile':'699b9f','fb_pool':'2a879a'})
colors.update({'castle-limestone':'dbd8cd'})
colors.update({'harrahs-membrane-paint':'c7c7bd','harrahs-service-paint':'a8aaa1'})
colors.update({'linq-membrane-paint':'cbccc5','linq-service-paint':'aab2b4'})
colors['nyny-membrane-paint']='c1c3bd'
colors.update({'nyny-concrete':'b7b8ad','nyny-shadow':'293232','nyny-white':'ddd9cb','nyny-stone':'bdae98','nyny-brick':'926650','nyny-window':'384b49','nyny-metal':'414b48','nyny-green':'699252'})
colors.update({'sa-white':'deddd8','sa-limestone':'cec6b6','sa-sand':'bba98d','sa-glass':'53626b','sa-sill':'aaaeb0','sa-gold':'b49a59','sa-shadow':'363b40','sa-roof':'c7c7bf','sa-flat-roof':'c7c9c3','sa-soffit':'d3c7ab','sa-trim':'d6d2c9','sa-wood':'513b2a','sa-champagne':'bdb4a0','sa-joint':'615e54','sa-blue-reveal':'52949d','sa-basin':'384f52','sa-screen':'142437','sa-paving':'b5afa0','sahara_pool':'3b929b'})
colors.update({'allure-glass':'4b6476','allure-white':'dcdddd','allure-spandrel':'4a5864','allure-rail':'657988','allure-frame':'adb5b9','allure-red':'8d3e46','allure-joint':'68565a','allure-roof':'d4d3cf'})
colors.update({'sky-glass':'355a73','sky-white':'dedfdc','sky-spandrel':'304c61','sky-balcony':'54768a','sky-mullion':'99a8ad','sky-roof':'b6bcc0','sky-shadow':'303e47'})
colors.update({'hgv-paving':'b9a78e','hgv_pool':'327c88','hgv-pool-tile':'698b91','hgv-sand':'c7a795','hgv-cream':'d9c3ad','hgv-window':'434e53','hgv-sill':'ac8e7b','hgv-shadow':'343637','hgv-roof':'c8c3ba'})
colors.update({'chy-tile':'b6b4a8','chy-cream-paint':'c8c2a6','chy-glass':'344846','chy-black-paint':'292d2a','chy-orange-paint':'b85e39','chy-rail-paint':'c7c8b7','chy-canopy-glass':'8aaca6','chy-timber-paint':'776252','chy-red-fabric':'91492f','chy-white-letter':'e9e1c4','chy-tan-paint':'b49a79','chy-table-stone':'d3cec1','chy-leaf':'38684b'})
colors.update({'fct-concrete-paint':'999b95','fct-roof-paint':'595c58','fct-metal-paint':'a6afb1','fct-dark-paint':'252e30','fct-rail-paint':'c1c5c1','fct-fan-paint':'c6cbc6','fct-louver-paint':'586366','fct-pipe-paint':'778b86','fct-foot-paint':'91928a'})
colors.update({'mm-white-stone':'ddd9cf','mm-white-paint':'e9e6de','mm-metal-paint':'9e9f9b','mm-joint-paint':'717675','mm-dark-metal-paint':'252c2c','mm-display-paint':'171d20','mm-bronze-paint':'82785a','mm-dark-letter':'212827','mm-gold-letter':'e4cc8d','mm-white-letter':'f1e8cc','mm-gold-paint':'b3a073','mm-paving-stone':'bcb4a0','mm-lamp':'f8eac5'})
colors.update({'wm-bronze-paint':'73615a','wm-roof-paint':'a6a091','wm-joint-paint':'94817a','wm-led-paint':'191d22','wm-eraser-paint':'484346','wm-metal-paint':'292b30','wm-gold-letter':'e4ce82','wm-screen-letter':'d4c59b','wm-paving-stone':'a89c83'})
colors.update({'wlf-red-fabric':'8e302a','wlf_water':'385d63','wlf-basin-paint':'344c47','wlf-coping-stone':'a29a82','wlf-rock-stone':'8e8873','wlf-waterfall-paint':'d6ded9','wlf-terrace-stone':'aba18d','wlf-cream-stucco':'ddd3b9','wlf-fabric-paint':'e5e0d0','wlf-metal-paint':'373b38','wlf-rail-glass':'778c87','wlf-ochre-stucco':'aa7655','wlf-window-glass':'25383b','wlf-awning-dark-paint':'393d37'})
colors.update({'wpc-roof-paint':'a9a698','wpc-travertine-stone':'b7a486','wpc-soffit-paint':'cac7b9','wpc-cream-stucco':'d7d2bf','wpc-bronze-paint':'665740','wpc-lantern-glass':'aab8b2','wpc-paving-stone':'999185'})
colors.update({'etsc-glass':'36484d','etsc-black-fabric-paint':'20232a','etsc-white-fabric-paint':'e5e1d4','etsc-white-frame-paint':'dddcd4','etsc-paving-stone':'aba296'})
colors.update({'st-ride-green-paint':'80b234','st-white':'ddded9','st-stone':'cac7bc','st-grey':'a4a7a6','st-glass':'4b5a60','st-sill':'bdc0bc','st-shadow':'333b41','st-blue':'254769','st-red':'a33735','st-roof':'c6c8c0','st-flat-roof':'c6c8c0','st-joint':'aaa69b','st-panel-dark':'202b37','st-planter':'8b897d','st-soil':'494736'})
colors.update({'tt-court':'44696c','tt-white':'e2e3df','tt-glass':'4a747d','tt-spandrel':'42606a','tt-balcony-glass':'77989e','tt-frame':'a1afb0','tt-roof':'bcbdb7','tt-shadow':'333e43','tt-shade':'99b4b1'})
colors.update({'tp-white':'e3e2da','tp-stone':'d6c8b1','tp-glass':'406c70','tp-spandrel':'435d61','tp-balcony-glass':'76918e','tp-frame':'bdc4c0','tp-roof':'b9bdb5','tp-patina':'a4cacc','tp-tile':'ac7562'})
colors.update({'mi-drive':'484843','mirage_water':'295c5b','mi-garden':'485643','mi-rock':'766d5b','mi-rock-light':'817563'})
colors.update({'rc-stucco':'cec4ae','rc-roof':'b9ae94'})
colors.update({'ri-paving':'c3b8a6','ri-blueglass':'244b77','ri-redglass':'78402f','ri-blueframe':'407ac3','ri-redframe':'bc4831','ri-white':'deded6','ri-sand':'b9a17d','ri-cream':'d5c5a8','ri-plinth':'8b7767','ri-roof':'b3a58c','ri-vent':'626665','ri-entryglass':'384a4f','ri-bronze':'9c8a61','ri-awning':'9b714c','ri-shadow':'303b43','ri-letter':'bc3629'})
colors.update({'ma-white':'d6dadb','ma-glass':'375b70','ma-balcony-glass':'577886','ma-spandrel':'314b5c','ma-frame':'9eadae','ma-shadow':'263239','ma-roof':'bbc0c0','ma-vent':'737c7d','ma-paving':'bfc2bd','ma-lobby':'3c535b','ma-letter':'c9b881'})
colors.update({'pa-white':'d6d9d7','pa-glass':'4c7c89','pa-spandrel':'365966','pa-metal':'869797','pa-shadow':'293638','pa-roof':'b4b9b9','pa-parking':'989e9e','pa-vent':'737c7d','pa-line':'e6e2d7','pa-paving':'c7c5b9'})
colors.update({'sg-stone':'c5b99e','sg-white':'dddcd4','sg-gold':'9a885d','sg-glass':'3f484a','sg-frame':'8c887c','sg-rail':'55564e','sg-roof':'bcbcb5','sg-vent':'6b6c68','sg-paving':'c4b9a6'})
colors.update({'gc-cream':'d2c7ac','gc-white':'e3e0d2','gc-taupe':'a3947f','gc-window':'373b3b','gc-shadow':'393b36','gc-roof':'c3c1b2','gc-green':'85a797'})
colors.update({'el-glass':'304e6b','el-spandrel':'304158','el-frame':'547086','el-roof':'c7cbca','el-white':'deded4','el-red':'9d354c','el-metal':'737f84','el-vent':'5d676a'})
colors.update({'mi-white':'e1dfd3','mi-cream':'cbbd9e','mi-glass':'8e7750','mi-frame':'b4a078','mi-shadow':'333c3a','mi-roof':'bca886','mi-window':'424c48','mi-awning':'9b4641','mi-dome':'557c89','mi-banner':'564455','mi-letter':'424644'})
colors.update({'wy-white':'ded6c2','wy-stone':'c8b89c','wy-bronze':'5b4035','wy-band':'c3bdb3','wy-joint':'7b695d','wy-rim':'74523f','wy-trim':'ded2bc','wy-window':'3d4846','wy-shadow':'343637','wy-roof':'c4c0b2','wy-skylight':'94b7bf'})
colors.update({'tr-white':'dddcd2','tr-glass':'a58b48','tr-spandrel':'8c784d','tr-frame':'ceba7e','tr-shadow':'343c3c','tr-roof':'c2c2b9','tr-letter':'70633e'})
colors.update({'sh-white':'dededa','sh-window':'566c75','sh-frame':'aeb7b8','sh-sill':'c6cecf','sh-joint':'b8bfbd','sh-shadow':'303d42','sh-roof':'c7cbc8'})
colors.update({'wg-white':'d9dcd9','wg-stone':'bdad99','wg-glass':'384752','wg-frame':'7d898e','wg-shadow':'3b4146','wg-joint':'9c9184','wg-roof':'c5c3b9','wg-blue-roof':'70899d'})
colors.update({'pm-white':'e0dfd8','pm-stone':'c4bbaa','pm-plinth':'8b8172','pm-glass':'34434e','pm-frame':'818b90','pm-sill':'b5b6ae','pm-shadow':'30383b','pm-roof':'c6c9c3','pm-vent':'6c7474','pm-letter':'604b40'})
colors.update({'hf-white':'d9dbd4','hf-burgundy':'69454b','hf-cornice':'c0c5bf','hf-reveal':'333c43','hf-glass':'364c56','hf-frame':'96a7a7','hf-stone':'bab9a8','hf-roof':'bec4be','hf-service':'adafac','hf-vent':'555e61','hf-paving':'bcb6a6','hf-pool-tile':'57928f','hf-cushion':'d8e1d6'})
colors.update({'gco-white':'e1dfd3','gco-stone':'c4b39a','gco-window':'414e53','gco-reveal':'343d41','gco-frame':'9c9f96','gco-tile':'a96a4c','gco-roof':'c3c4b9','gco-service':'8d9691','gco-paving':'c4b5a0','gco-pooltile':'75a09b'})
colors.update({'vh-blueglass':'355b75','vh-white':'deded7','vh-spandrel':'3b5361','vh-metal':'91a2a9','vh-grayglass':'56636a','vh-stone':'c7bcaa','vh-shadow':'303a3f','vh-roof':'c3c5bd','vh-service':'858d8b','vh-paving':'c3b5a0','vh-lawn':'64734c','vh-pool-tile':'63918a','vh-cushion':'ded7c6'})
colors.update({'wa-glass':'627782','wa-skyglass':'2e424e','wa-spandrel':'758993','wa-metal':'a0a8a8','wa-metal-light':'b8bdbb','wa-metal-dark':'788489','wa-frame':'89999e','wa-shadow':'37434b','wa-stone':'c4c3b7','wa-roof':'bfc5c3','wa-vent':'616d72','wa-paving':'c6c1b0','wa-guard':'69838d','wa-cushion':'e1dccb'})
colors.update({'cp-colosseum-sand':'c4b08a','cp-colosseum-recess':'b2a795','cp-colosseum-joint':'9c8c71','cp-flat-roof':'c6c5bc','cp-deck':'b9a68e','cp-inlay':'ddd3c0','cp-basin':'92baba','cp-pool-tile':'406f7b','cp_pool':'53a1ac','cp-flute':'b7b4a8','cp-patina':'628c87','cp-patina-seam':'4f706f','cp-cushion':'cf6445','cp-chair-frame':'ded9c9','cp-fabric':'e2e0d6'})
colors.update({'cp-gold':'89734d','cp-white':'dedbd0','cp-stone':'bcae97','cp-glass':'384c54','cp-shadow':'303536','cp-frame':'989d95','cp-sill':'bab5a8','cp-roof':'c4c2b9','cp-tile':'a65f4e','cp-service':'9eaaa4'})
colors.update({'fl-white':'d6d7d0','fl-glass':'574649','fl-spandrel':'716369','fl-curtain':'9e8987','fl-frame':'a3a5a1','fl-letter':'9a4779','fl-screen':'a1a49c','fl-roof':'bfc3b9','fl-service':'8c9390','fl-shadow':'353d3f'})
colors.update({'hs-stone':'c8bba1','hs-white':'dedacf','hs-glass':'424b50','hs-spandrel':'5c5b57','hs-frame':'a1a6a1','hs-joint':'a69a87','hs-letter':'ab976b','hs-blue':'425c7a','hs-roof-seam':'65758b','hs-roof':'c6c5ba','hs-service':'92958d','hs-shadow':'323b3c'})
colors.update({'baz-deck':'867466','baz-brick':'805248','baz-glass':'526775','baz-metal':'38383b','baz-shade':'ac8b72','baz-red':'b33335','baz-letter':'deded2','baz-stucco':'b8ada0','baz-roof':'afa89d','baz-awning':'95484b','baz-service':'7f8988'})
colors.update({'ps-white':'d9d8ce','ps-stone':'b7aa94','ps-glass':'48535c','ps-frame':'879093','ps-shadow':'303637','ps-joint':'a89f8d','ps-trim':'b9b6aa','ps-red':'a43640','ps-roof':'b3b7b4','ps-deck':'a4a5a0','ps-service':'90968f'})
colors.update({'ub-stone':'a98685','ub-glass':'30313c','ub-frame':'55535a','ub-trim':'b39a95','ub-roof':'b9b5aa','ub-shadow':'34333b','ub-service':'8b8984','ub-letter':'deded9'})
colors.update({'nm-cream':'d4ccb9','nm-sand':'ba9d7d','nm-eaves':'c2b7a5','nm-tile-roof':'ad8178','nm-grey-roof':'777c80','nm-door':'686868','nm-sill':'b6ab99','nm-shadow':'30383b','nm-rail':'615d58','nm-red':'a94c48','nm-green':'388264','nm-orange':'c58349','nm_pool':'398c9a'})
colors.update({'sr-red-stucco':'b66560','sr-cream':'d8d2c2','sr-tan-stucco':'b39c85','sr-brick':'a67764','sr-yellow':'d7bb54','sr-dark':'313338','sr-billboard':'343c4e','sr-pink-stucco':'b48182','sr-joint':'8c8075'})
colors.update({'cr-peach-stucco':'bd927d','cr-purple-stucco':'876a85','cr-blue-stucco':'687b8d','cr-lavender-stucco':'aaa4af','cr-sage-stucco':'8c9c99','cr-cream':'d6cfc2','cr-flat-roof':'b9b7ad','cr-slate-roof':'515b64','cr-roof-joint':'75818a','cr-burgundy':'80554a','cr-sign-blue':'244f76','cr-letter':'d6be74','cr_pool':'36888f'})
colors.update({'aria_pool':'318c99','aria-trim':'859292','aria-paving':'c3bcb0','aria-mulch':'434a38'})
colors.update({'paris-stone':'d1c4ad','pg-glass':'9cabb4'})
colors.update({'ga-asphalt':'45484a','ga-concrete':'d8d4c5','ga-roof':'3b4249','ga-seam':'545d65','ga-glass':'344047','ga-frame':'8a9291','ga-paving':'c5b7a4','ga-gravel':'b3a080','ga-rose-paving':'b99183','ga-flat-roof':'c8c9c0','ga-door':'262a2a','ga-mosaic-blue':'49647c','ga-mosaic-gold':'bda466','ga-mosaic-cream':'c4c5b8','ga-mosaic-slate':'7c8b8f','ga-mosaic-rust':'a37d67'})
colors.update({'cf-asphalt':'45494a','cf-white':'d8d8ce','cf-blue':'32516c','cf-glass':'3b535d','cf-frame':'a5aaa6','cf-joint':'aaa99d','cf-flat-roof':'bcbeb7','cf-screen':'253443','cf-paving':'b9b1a0','cf-gravel':'a9997c','cf-pool-dry':'b0b7ac','cf-red':'a13b43','cf-tan':'c3ad88','cf-red-tile':'974447','cf-metal-roof':'a57462','cf-roof-seam':'bb9680','cf-service':'848c88'})
colors.update({'fs-white':'d7d8d0','fs-stone':'c5bda8','fs-sand':'b5a389','fs-sand-light':'d0bfa4','fs-taupe':'a69d89','fs-flat-roof':'c5c8c0','fs-glass':'355961','fs-metal':'9ba6a8','fs-joint':'91968e','fs-service':'828b89','fs-sign':'303b3d','fs-solar':'263a50','fs-screen':'285d83'})
colors.update({'park-membrane-paint':'a4a7a1','park-theatre-paint':'d8dad3','park-canopy-paint':'959d9f','park-roof-rib-paint':'737d80'})
colors.update({'ph-lightbox-paint':'d9c997','ph-disc':'9ba79d'})
colors.update({'vp-stucco':'c7b39c','vp-cream':'dedbd1','vp-shadow':'353c40','vp-glass':'52646b','vp-frame':'777d7d','vp-metal-paint':'34383a','vp-letter':'d8d0bd','vp-service-paint':'9fa6a1','vp-joint':'988e7f','vp-deck':'b7ad9a','vp-roof-paint':'cbcfc8','vp-fabric':'9d4663','vp-cushion':'c8bdae','vp-table-wood':'886e52','vp-parasol-fabric':'e0d7be','vanderpump_pool':'408997'})
colors.update({'mandalay-pool-paving':'c8bca5','mandalay-pool-tile':'7eacae','mandalay_pool':'498c99','mandalay-sand':'d8c9a8','mandalay-chair-frame':'d2ccc0','mandalay-cushion':'c8c5bb','mandalay-shade':'d6d1bf'})
colors.update({'scp-brick':'94705c','scp-brick-rib':'ad856c','scp-stucco':'cec3a3','scp-flat-roof':'bdbcb0','scp-metal-roof':'9c6751','scp-roof-seam':'b27e60','scp-coping':'a6785e','scp-sill':'b5a38b','scp-frame':'59685c','scp-glass':'304e4d','scp-canopy':'b9ad8d','scp-metal':'959c92','scp-letter':'4b493e','scp-asphalt':'484b44','scp-paving':'b9b09a','scp-line':'c9c5af','scp-gravel':'99896b','scp-shrub':'4e633c','scp-dark':'454c44'})
colors.update({'sig-line':'bcbdb2','sig-gravel':'a68c72','sig-curb':'b0aea1','sig-metal-paint':'c6c9c4','sig-flat-roof-paint':'a8a99d','sig-coping':'deded5','sig-panel-joint':'8a938f','sig-dark':'293c42','sig-glass':'3b5965','sig-frame':'a5ada9','sig-letter':'505c59','sig-pier':'b1b8ae','sig-canopy-metal-paint':'919d95','sig-canopy-soffit-paint':'a7b3a8','sig-service':'b9bdb0','sig-paving':'b9afa0','sig-asphalt':'555552','sig-bollard':'a8b5ad'})
colors.update({'bhc-ochre-stucco':'a58a51','bhc-flat-roof':'9b9d93','bhc-terrace-stone':'a59d86','bhc-roof-paint':'4b6c59','bhc-dark-timber':'423d29','bhc-stacked-ashlar':'75786b','bhc-stone-cap':'9a9d8b','bhc-glass':'2c433e','bhc-sage-shade':'78806a','bhc-bronze':'797143','bhc-service':'a7afa6','bhc-paving':'a8a08b','bhc-garden':'736c48','bhc-rail':'353c32'})
colors.update({'f11-stucco':'b8b3a9','f11-flat-roof-paint':'c6c5bc','f11-roof-metal-paint':'a8afad','f11-roof-rib-paint':'c4c7bc','f11-coping':'a8a99f','f11-frame':'696e67','f11-door':'898b7e','f11-door-joint':'666c64','f11-glass':'334c4a','f11-service':'a0a49a','f11-red':'8b5952','f11-metal':'bbc0b7','f11-dark':'414945','f11-canopy':'817c66','f11-letter':'d7d2bd','f11-concrete':'ada795','f11-gravel':'b6a88b','f11-paving':'bcb6a5','f11-joint':'8e8c7d','f11-line':'c7c5b4','f11-bollard':'354e44','f11-white':'d3d5ca'})
colors.update({'thq-flat-roof-paint':'b9bbb0','thq-cactus-foliage':'69734b','thq-cactus-rib':'778257','thq-stone-joint':'706e60','thq-white-stucco':'d1d0c7','thq-coping':'c9cbc2','thq-roof-paint':'343b3c','thq-soffit-paint':'303737','thq-frame':'3c4240','thq-glass':'384a4d','thq-stacked-ashlar':'9a9481','thq-stone-cap':'b5ae9b','thq-red-letter':'a42426','thq-handle':'b6bcb8','thq-service':'a4aaa0','thq-asphalt':'51534e','thq-paving':'a99e8a','thq-gravel':'a69f87','thq-curb':'a57164'})
colors.update({'pf-white-metal-paint':'c4c8c4','pf-roof-paint':'cccec6','pf-coping':'b2b9b7','pf-base':'b2b2a5','pf-seam':'a5ada9','pf-door':'babfb9','pf-door-seam':'909e9a','pf-track':'9ca7a2','pf-frame':'747f7c','pf-service-door':'9caaa4','pf-glass':'344c50','pf-canopy':'b0b9b1','pf-service':'bec3bb','pf-grille':'515d5a','pf-concrete':'a9a99c','pf-paving-joint':'92958b','pf-bollard':'b4a954'})
colors['hd-flat-roof-paint']='bebfb6'
colors.update({'bp-stucco':'b9bbb6','bp-flat-roof-paint':'b5b8ad','bp-coping':'90928a','bp-base':'7f8176','bp-black':'303a39','bp-gray-panel':'9badae','bp-red':'993e43','bp-glass':'31474a','bp-red-letter':'a84845','bp-fascia':'81877f','bp-rail':'303a38','bp-letter':'d5d1bc','bp-frame':'abb1a6','bp-sign':'c5bda4','bp-metal':'8a938e','bp-light':'bec1aa','bp-service':'9ca69b','bp-paving':'b3ac98'})
colors.update({'tf-cream-stucco':'c8c9be','tf-flat-roof-paint':'bdc0b5','tf-coping':'a0a99a','tf-sage':'919778','tf-green':'59705c','tf-frame':'b9bdae','tf-glass':'3a4d48','tf-maroon':'795354','tf-fascia':'c5c9be','tf-gold':'b9a543','tf-black':'343c35','tf-letter':'d9c7bc','tf-metal':'9ba799','tf-paving':'b1ac97','tf-service':'a1a99a'})
colors.update({'tm-blue-stucco':'424f61','tm-flat-roof-paint':'8a8c85','tm-coping':'606d75','tm-trim':'354652','tm-board':'4b5868','tm-dark-panel':'263138','tm-canopy-paint':'4e5a60','tm-sign':'aaa58b','tm-letter':'d8c684','tm-paving':'a5a294','tm-service':'8d9290'})
colors.update({'ms-white-brick-paint':'c2c5bd','ms-flat-roof-paint':'a1a29a','ms-coping':'b7bab2','ms-gray-stone':'747e80','ms-stone-joint':'596263','ms-black':'252b2c','ms-red':'903b43','ms-letter':'d7d4c5','ms-metal':'a7b2b0','ms-canopy-metal':'a0aba8','ms-asphalt':'62635c','ms-paving':'aea898','ms-line':'c4bca4','ms-service':'969e99'})
colors.update({'os-gray-stucco':'828689','os-roof-paint':'aaa99e','os-coping-paint':'c4c6bf','os-glass':'304951','os-black-paint':'262d30','os-dark-paint':'424c51','os-paving':'aaa99f','os-plinth':'929891','os-rail-collision':'242b2e','os-metal-paint':'9ba5a2','os-service-paint':'8c9592','os-vent':'39494a','os-red-letter':'a33237','os-dark-letter':'303737','os-green-letter':'697e4b','os-white-letter':'d6d7cc','os-awning-paint':'303331','os-white-paint':'dadbd3','os-green-paint':'619847','os-asphalt':'676e70'})
colors.update({'ph-white-stucco':'bfc1b8','ph-roof-paint':'959b9b','ph-white-paint':'d4d6ce','ph-black-paint':'353a3d','ph-red-paint':'994b50','ph-glass':'4f5964','ph-window-frame-paint':'b9c3c4','ph-red-metal-paint':'a05a60','ph-light-housing-paint':'9ba6a3','ph-service-paint':'a1a49c','ph-red-letter':'bb5962','ph-gold-letter':'bfa77a','ph-paving':'a7a69d','ph-gravel':'a8a294'})
colors.update({'mk-blue-paint':'3a5ea6','mk-roof-paint':'92978d','mk-peeling-white-paint':'c8ccc5','mk-panel-joint-paint':'949fa2','mk-board-paint':'3e62a8','mk-blue-shadow-paint':'334a7f','mk-metal-paint':'8b9594','mk-paving':'aaa69e','mk-black-paint':'333d3e','mk-wire-paint':'899592','mk-red-sign-paint':'9e5a55','mk-white-letter':'deded5','mk-blue-letter':'4264b0','mk-green-sign-paint':'7e995d','mk-white-paint':'d3d6cd','mk-service-paint':'8c9891','mk-vent':'3d4c4e','mk-step':'999c8f','mk-yellow-paint':'b8aa4d'})
colors.update({'oa-white-paint':'d5d6c8','oa-roof-paint':'9b9e92','oa-blue-paint':'496b9d','oa-white-letter':'e2e3d8','oa-island':'abaea5','oa-black-paint':'343b3d','oa-display':'66837d','oa-yellow-paint':'c2a542','oa-tan-stucco':'b0a08a','oa-terracotta-paint':'a47350','oa-orange-paint':'ad7855','oa-glass':'405860','oa-metal-paint':'909c98','oa-orange-letter':'be5b3e','oa-vent':'4b585b','oa-service':'8b958b','oa-asphalt':'727778','oa-paving':'aba99d'})
colors.update({'li-blue-paint':'526ba7','li-blue-shadow-paint':'3e5389','li-roof-paint':'b7b6aa','li-white-paint':'d9dbd1','li-glass':'3e4c54','li-door-paint':'c8ccc4','li-dark-letter':'39404b','li-red-letter':'ae3945','li-sign-frame':'b7c2c0','li-cone-paint':'bca75f','li-cream-paint':'e1d9b9','li-service':'84928d','li-paving':'b0ada3'})
colors.update({'bj-teal-paint':'68a49f','bj-blue-paint':'3f7c9d','bj-glass':'344f57','bj-roof-paint':'adae9f','bj-aluminum-paint':'afb8b5','bj-awning-paint':'dbded7','bj-white-letter':'e7e8dd','bj-sign-blue':'23445d','bj-white-paint':'d2d6ce','bj-vent':'485e60','bj-service':'8a958e','bj-paving':'aaa797'})
colors.update({'cg-red-stucco':'a94943','cg-flat-roof-paint':'a7aaa1','cg-white':'d2d1c3','cg-gray':'8b8d81','cg-coping':'b9bbab','cg-red-letter':'a13f39','cg-glass':'384c4e','cg-metal-paint':'939f9a','cg-canopy-paint':'b0b5a7','cg-paving':'b4ae9e','cg-table':'3e4944','cg-service':'8e9a95'})
colors.update({'sc17-white-paint':'d6d6d0','sc17-gray-paint':'999e9c','sc17-roof-paint':'aaa99d','sc17-black-paint':'303534','sc17-black-roof-paint':'3a403f','sc17-glass':'657c7e','sc17-metal-paint':'838b89','sc17-service-paint':'aaaead','sc17-vent':'424c4a','sc17-green-paint':'258250','sc17-red-letter':'ac3f3d','sc17-white-letter':'e1e4dc','sc17-dark-letter':'474f4a','sc17-paving':'aaa9a2','sc17-island':'989f98','sc17-display':'82918a','sc17-button':'baac63','sc17-asphalt':'555956'})
colors.update({'cf-stucco':'d8d9cc','cf-white-paint':'e3e4da','cf-tile-paint':'828277','cf-roof-seam-paint':'6d6f66','cf-roof-paint':'aeaea2','cf-glass':'536b70','cf-door-paint':'b5b8a7','cf-gold-paint':'9f9268','cf-louver-paint':'879487','cf-iron-paint':'3b4740','cf-service-paint':'979c93','cf-pavers':'a49a85','cf-paving':'b6b5a7','cf-grass':'5e7149','cf-fabric-paint':'d4d5c9'})
colors.update({'tm-stucco':'d6d4c3','tm-red-paint':'ad4c4b','tm-white-paint':'d9dad1','tm-roof-paint':'aaa79d','tm-glass':'4e6768','tm-metal-paint':'67736f','tm-service-paint':'8e9894','tm-vent':'394845','tm-asphalt':'575b58','tm-paving':'b1afa6','tm-red-letter':'b84946','tm-white-letter':'e0dfd3'})
colors.update({'dn-gray-paint':'b2b6b0','dn-cream-paint':'d0d2c7','dn-roof-paint':'aaa99d','dn-red-paint':'984848','dn-black-paint':'333c39','dn-glass':'657f7a','dn-panel-seam-paint':'a2a99e','dn-metal-paint':'84918a','dn-yellow-paint':'b4a65c','dn-sign-red-paint':'a74742','dn-sign-gold-paint':'c0a765','dn-white-letter':'e3e4d8','dn-red-letter':'ac4946','dn-paving':'aaa99c','dn-service-paint':'949e99','dn-vent':'414d48','dn-asphalt':'565a55','dn-line-paint':'c8c9bb'})
colors.update({'ad-white-stucco':'ced3cf','ad-fascia-paint':'a4aeaa','ad-roof-paint':'b9bcb1','ad-soffit-paint':'c5cbc4','ad-belt-paint':'8b9897','ad-downpipe-paint':'8b9591','ad-paving-concrete':'b1aea2','ad-gravel':'8b8771','ad-line-paint':'c5c9bc','ad-service-paint':'999f99','ad-vent-paint':'444e4a','ad-sign-frame-paint':'c3c7be','ad-sign-paint':'696f69','ad-white-letter':'e5e6db','ad-entry-frame-paint':'727a73'})

colors.update({'w17-white-stucco':'d5d7cf','w17-red-paint':'ba4f42','w17-cream-paint':'e0d39d','w17-roof-paint':'bbbdb2','w17-frame-paint':'a0aaa6','w17-glass':'415453','w17-metal-paint':'858e86','w17-grille-paint':'3f4844','w17-paper-paint':'c9c7ae','w17-fixture-paint':'565f5a','w17-door-paint':'919e93','w17-vent-paint':'4b5650','w17-service-paint':'9da69b','w17-rooflight-paint':'c2c5b8','w17-billboard-back-paint':'9b9f94','w17-paving-concrete':'b6b1a1','w17-shed-paint':'b9b7a2'})

colors.update({'ww-yard-paint':'737955','ww-fence-paint':'444c41','ww-green-screen-paint':'52654e'})
colors.update({'hs-yard-gravel-paint': 'a99a78'})
colors.update({'hs-red-fascia-paint':'98674e','hs-solar-glass':'293942','hs-solar-frame-paint':'82908c'})
colors.update({'rpw-gray-roof-paint':'777f7b'})
colors.update({'rpw-yard-paint':'b6ad94','rpw-membrane-paint':'c3c9c3'})
colors.update({'rpw-white-stucco': 'd0d0bf', 'rpw-cream-stucco': 'c3baa3', 'rpw-tan-stucco': 'b3a284', 'rpw-rose-stucco': 'bca18e', 'rpw-frame-paint': 'd2d3cb', 'rpw-glass': '657673', 'rpw-sill-paint': 'c7c8be', 'rpw-fascia-paint': '8b8067', 'rpw-plinth-paint': '989584', 'rpw-door-trim-paint': 'cecec2', 'rpw-door-paint': '887866', 'rpw-hardware-paint': 'a3a99f', 'rpw-awning-paint': 'babfb2', 'rpw-post-paint': 'abb4a7', 'rpw-concrete': 'b7b7a8', 'rpw-garage-trim-paint': 'c4c7b9', 'rpw-garage-paint': 'bec3b7', 'rpw-garage-seam-paint': '959e93', 'rpw-gravel': 'b4a386', 'rpw-block-stucco': 'c4c6b8', 'rpw-fence-cap-paint': 'c3c9ba', 'rpw-fence-paint': '7a887b', 'rpw-service-paint': 'a7afa5', 'rpw-vent-paint': '3d4b42', 'rpw-flue-paint': 'a6aca3'})
colors.update({'bap-roof-terracotta':'a77659'})
colors.update({'spn-olive-stucco': '8a8972', 'spn-cream-stucco': 'c9c6ad', 'spn-gray-stucco': 'a7aaa3', 'spn-pale-stucco': 'bfc1b5', 'spn-charcoal-stucco': '626866', 'spn-white-stucco': 'd0d2c8', 'spn-olive-paint': '82836c', 'spn-blue-paint': '6c8197', 'spn-slate-paint': '737e80', 'spn-pale-paint': 'b7bbb1', 'spn-charcoal-paint': '626866', 'spn-purple-paint': '9a93bb', 'spn-brown-roof-paint': '756c58', 'spn-gray-roof-paint': '818480', 'spn-frame-paint': 'd5d5c8', 'spn-glass': '566773', 'spn-sill-paint': 'c1c2b5', 'spn-fascia-paint': 'a4a497', 'spn-trim-paint': 'aeb2a5', 'spn-plinth-paint': '909287', 'spn-number-paint': '39474c', 'spn-accent-paint': 'd2a58d', 'spn-door-paint': '7e8580', 'spn-siding-shadow-paint': '6a7375', 'spn-gallery-concrete': 'a4a99f', 'spn-soffit-paint': 'b1b4a6', 'spn-rail-paint': '5b655e', 'spn-service-paint': 'a8b1aa', 'spn-vent-paint': '394742', 'spn-concrete': 'b2b5a7', 'spn-gravel': 'a99b7d', 'spn-fence-paint': '525c55'})
colors.update({'spf-gray-stucco':'c0c3bb','spf-membrane-paint':'c9d0cd','spf-roof-paint':'bfc8c5','spf-fascia-paint':'a9b2b1','spf-trim-paint':'cbd0c6','spf-plinth-paint':'aeb4a9','spf-frame-paint':'d0d6cc','spf-glass':'6b8184','spf-sill-paint':'c8cfc7','spf-door-paint':'b4b9ac','spf-hardware-paint':'8d9993','spf-gallery-concrete':'b1b6af','spf-soffit-paint':'abb1a5','spf-rail-paint':'9aa5a1','spf-number-paint':'5c6870','spf-curb-paint':'b7bfb5','spf-service-paint':'b3bdb7','spf-vent-paint':'4a5754','spf-gravel':'ac9f80','spf-grass':'5e724a','spf-concrete':'b1b4a8','spf-fence-paint':'909d94'})
colors.update({'spad-yellow-stucco':'c9ad61','spad-charcoal-paint':'42484a','spad-roof-paint':'c5cbc8','spad-frame-paint':'d9ddd4','spad-glass':'405758','spad-sill-paint':'d3d8ce','spad-door-paint':'807b68','spad-hardware-paint':'7e8a85','spad-trim-paint':'dddccc','spad-downpipe-paint':'b9bba8','spad-gallery-concrete':'b9bbad','spad-concrete':'b0ac9b','spad-service-paint':'bbc2b8','spad-vent-paint':'4e5956','spad-rail-paint':'8a9390','spad-pool-tile':'a9c4bf','spad_pool':'4f8f97','spad-coping-paint':'d4c9ab','spad-sign-paint':'3f668f','spad-white-letter':'dce0d6'})
colors.update({'rsv-tan-stucco':'c8bda6','rsv-coping-paint':'857567','rsv-plinth-paint':'a3947f','rsv-membrane-paint':'cbd0c9','rsv-frame-paint':'ada998','rsv-door-paint':'a19e8e','rsv-hardware-paint':'8b958c','rsv-fixture-paint':'555e53','rsv-vent-paint':'4a514d','rsv-drain-paint':'b1b5a8','rsv-joint-paint':'aa9e89','rsv-curb-paint':'b9baab','rsv-service-paint':'adb4ad','rsv-grille-paint':'89928a','rsv-roof-seam-paint':'b9bfb5','rsv-concrete':'b3b0a1','rsv-asphalt':'5d6259'})
colors.update({'wsc-cream-stucco':'d2c5a1','wsc-trim-stone':'e1d5b6','wsc-plinth-stone':'bbad8c','wsc-relief-paint':'b78565','wsc-soffit-paint':'bfb292','wsc-roof-paint':'b4a58b','wsc-hip-metal-paint':'737d7a'})
colors.update({'ccourt-column-color-paint':'ffffff','ccourt-roof-paint':'8e9692','ccourt-soffit-paint':'6d7770','ccourt-fascia-paint':'ffffff','ccourt-trim-paint':'b1b5a9','ccourt-steel-paint':'a2aba5','ccourt-fixture-paint':'292f2b','ccourt-column-stone':'d2d1c4','ccourt-gold-paint':'c4aa52','ccourt-floor-stone':'a7a28b','ccourt-bar-purple':'735879','ccourt-counter-paint':'555b58','ccourt-service-paint':'626c65','ccourt-bottle-paint':'69785d','ccourt-seat-paint':'625b72','ccourt-rail-paint':'3b443d','ccourt-sign-purple':'4a3d67','ccourt-white-letter':'dedfd5','ccourt-gold-letter':'d9bd6a'})
colors.update({'bt-tan-stucco':'b5aa8d','bt-roof-paint':'8c7963','bt-fascia-paint':'b4a991','bt-membrane-paint':'d5d9cc','bt-frame-paint':'c4c8b8','bt-door-paint':'89594b','bt-handle-paint':'909987','bt-drain-paint':'aba48d','bt-white-paint':'d9dccf','bt-infill-paint':'d0d4c7','bt-plinth-paint':'a39b83','bt-curb-paint':'b9b9a7','bt-service-paint':'a7afa1','bt-vent-paint':'525e52','bt-gallery-concrete':'a5a38f','bt-rail-paint':'81745a','bt-asphalt':'5e6659','bt-court-concrete':'b4b29d','bt-pool-tile':'9fbcb4','bt_pool':'528f8c','bt-coping-paint':'c4c6b6','bt-shade-paint':'c6cbbc','bt-soil-paint':'767453','bt-sign-paint':'b3b5a4','bt-line-paint':'cdd0c0','bt-wheelstop-concrete':'a7a995','bt-glass':'52685f','bt-sill-paint':'c2c8b5'})
colors.update({'ssk-cladding-paint':'545d58','ssk-rib-paint':'3b443f','ssk-frame-paint':'3d4944','ssk-glass':'34514f','ssk-steel-paint':'a7aaa0','ssk-awning-paint':'626c63','ssk-soffit-paint':'d6d8cc','ssk-roof-paint':'aab2a5','ssk-seam-paint':'6c756b','ssk-deck-concrete':'9a9a8e','ssk-wall-concrete':'b1afa1','ssk-step-concrete':'b0b1a4','ssk-counter-paint':'9b9e8d','ssk-seat-paint':'a1ad70','ssk-letter-paint':'e2e5d5','ssk-paving-concrete':'b0aa96'})
colors.update({'fgs-tan-stucco':'b7aa8f','fgs-roof-paint':'d7dbce','fgs-red-plinth-paint':'ad7469','fgs-cream-coping-paint':'c9c7b6','fgs-frame-paint':'a5a28c','fgs-door-paint':'9c9984','fgs-hardware-paint':'989e94','fgs-light-paint':'565c55','fgs-vent-paint':'424b44','fgs-drain-paint':'b4b7a6','fgs-curb-paint':'bbb9a7','fgs-service-paint':'b3b7a7','fgs-grille-paint':'7f877c','fgs-canopy-paint':'6e7952','fgs-concrete':'aaa793'})
colors.update({'perception-white-paint':'deded2','perception-black-paint':'242927','perception-coping-paint':'c7c9bf','perception-yellow-paint':'cbbb62','perception-black-letter':'252d29','perception-door-frame-paint':'636f69','perception-glass':'354d4b','perception-vent-paint':'424d48','perception-roof-paint':'bbbcb0','perception-servicewall-paint':'b3b6aa','perception-service-paint':'9aa397','perception-gravel':'b8b29b','perception-paving-concrete':'b9b6aa','perception-bollard-paint':'344039','perception-utility-paint':'aaa48b','perception-leaf':'566a41'})

colors.update({'spool-deck-concrete': 'c5bfaa', 'spool_pool': '278c9a', 'spool-basin-paint': '8dbdbb', 'spool-blue-tile': '3c6f85', 'spool-coping-concrete': 'c8c5af', 'spool-white-stucco': 'd3d2c3', 'spool-roof-paint': 'b2b8ad', 'spool-white-frame-paint': 'd7d9cf', 'spool-window-frame-paint': 'aab4a7', 'spool-glass': '385a5c', 'spool-blue-letter': '2c566a', 'spool-service-paint': '919c8e', 'spool-dark-frame-paint': '3c4943', 'spool-yellow-fabric-paint': 'cfb34d', 'spool-white-fabric-paint': 'dedccc', 'spool-cushion-paint': 'cfceba', 'spool-blue-fabric-paint': '2d6681'})
colors.update({'mc-canopy-roof-paint': 'c3c7bd', 'mc-soffit-paint': 'afb3a8', 'mc-fascia-paint': 'bbb9a7', 'mc-coping-paint': 'd0d2c7', 'mc-white-letter': 'e1e2d8', 'mc-post-paint': 'd0d3c8', 'mc-base-paint': 'aaa99a', 'mc-yellow-paint': 'c1a63c', 'mc-roof-curb-paint': '989d94', 'mc-vent-paint': '46544b', 'mc-service-paint': 'a1ac9e', 'mc-concrete': 'aaa99c', 'mc-light-paint': 'dedcc5'})
colors.update({'pr-white-stucco': 'd4d4c5', 'pr-cream-stucco': 'c5c2aa', 'pr-tan-stucco': 'a58b73', 'pr-dark-stone': '4d4d42', 'pr-pale-stone': 'bbbba5', 'pr-red-paint': 'a34038', 'pr-membrane-paint': 'a5aaa1', 'pr-white-trim-paint': 'd1d2c7', 'pr-brown-trim-paint': '756754', 'pr-plinth-paint': '74796c', 'pr-red-brick': '966955', 'pr-window-frame-paint': 'b8bbaa', 'pr-glass': '44544d', 'pr-bar-paint': '5d6257', 'pr-black-paint': '242e29', 'pr-door-paint': '7b8174', 'pr-handle-paint': 'a0a99b', 'pr-awning-paint': '91988c', 'pr-light-paint': 'd1cdb2', 'pr-sign-paint': 'bcb8a1', 'pr-sign-letter': '823e36', 'pr-drain-paint': '858b7d', 'pr-service-paint': '9ba495', 'pr-vent-paint': '4e5b50', 'pr-asphalt': '65685d', 'pr-concrete': 'b5b4a5', 'pr-line-paint': 'c3c2b0'})
colors.update({'jm-cream-stucco': 'c4c3ac', 'jm-gray-stone': '8c8d7e', 'jm-roof-paint': '757d63', 'jm-roof-seam-paint': '5d6755', 'jm-membrane-paint': '9da496', 'jm-frame-paint': '4c5147', 'jm-glass': '405457', 'jm-menu-white-paint': 'd0d1c1', 'jm-red-paint': '9a4d43', 'jm-red-sign-paint': 'a73435', 'jm-white-letter': 'e3e2d1', 'jm-menu-ink-paint': '474d44', 'jm-dark-paint': '3c463d', 'jm-door-paint': '778175', 'jm-vent-paint': '465247', 'jm-handle-paint': 'adb8a8', 'jm-dark-letter': '3b443a', 'jm-concrete': 'a7a99a', 'jm-asphalt': '5a6057', 'jm-line-paint': 'c7c9b6', 'jm-bed-stone': 'a5a589', 'jm-gravel-paint': 'b1a780', 'jm-service-paint': 'a8b1a4'})

colors.update({'lob-stone-paint':'c8bda8','lob-glyph-paint':'c8bda8','lob-paving':'aaa28f','lob-blue-letter':'263553','lob-sculpt-stone':'bcb29d','lob-carve-paint':'8b816c','lob-metal-paint':'47504e'})

colors.update({'arc-roof-paint':'c3c8c2','arc-soffit-paint':'b0b7b0','arc-edge-paint':'b2b8b0','arc-timber':'a58b69','arc-foot-paint':'969c90','arc-bolt-paint':'68736c','arc-container-paint':'c2c8bb','arc-rib-paint':'a8b3a8','arc-door-paint':'b4beb1','arc-asphalt':'555b53','arc-line-paint':'b9bcb0'})

def material(k):
 if k in materials:return materials[k]
 rgb=np.array([int(colors[k][i:i+2],16)/255 for i in (0,2,4)]);linear=np.where(rgb<.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
 m=bpy.data.materials.new('Strip / '+k);m.use_nodes=True;m.diffuse_color=(*linear,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*linear,1)
 if k.startswith('vi-'):
  VM.build(bpy,m,bs,k,linear);materials[k]=m;return m
 metal=k in ['silver','steel','brass','bronze','gold','blackiron','copper','copperpanel','copper2','copper3'];glass=k in ['glass','shopglass','cabinglass','darkglass','water','palazzo-glass','harrahs-window','linq-glass','linq-blue'];bs.inputs['Metallic'].default_value=.62 if metal else .2 if glass else .0;bs.inputs['Roughness'].default_value=.28 if metal else .14 if glass else .74
 if k in ['hel-panel-paint','hel-cap-paint','hel-metal-paint']:
  bs.inputs['Metallic'].default_value=.6;bs.inputs['Roughness'].default_value=.43
 if k=='hel-guard-glass':
  bs.inputs['Alpha'].default_value=.24;bs.inputs['Roughness'].default_value=.25;m.surface_render_method='DITHERED'
 if k in ['fl-shop-glass','fs-glass','fs-solar','cf-glass','ga-glass','pg-glass','lvw-glass','lvw-door','oy-glass','gd-glass','rh-glass','pk-glass','wf-glass','wd-glass','pt-glass','we-glass','as-glass','as-lanai','es-glass','ub-glass','ps-glass','baz-glass','hs-glass','fl-glass','cp-glass','gco-window','vh-blueglass','vh-grayglass','hf-glass','wa-glass','wa-skyglass','wa-guard','pm-glass','perception-glass','ssk-glass','ri-blueglass','ri-redglass','ri-entryglass','ma-glass','ma-balcony-glass','ma-lobby','pa-glass','sg-glass','gc-window','el-glass','ph-window','ph-glass','sc17-glass','ti-window','forum-skylight','forum-glass','mgm-glass','coke-glass','showcase-roof','park-window','luxor-glass','luxor-pyramid','mandalay-glass','mandalay-window','mandalay-solar','nyny-window','fb-glass','rw-bronze','cc-window','cc-dome-glass','sa-glass','st-glass','hgv-window','sky-glass','sky-balcony','allure-glass','allure-rail','tt-glass','tt-balcony-glass','tp-glass','tp-balcony-glass','wg-glass','sh-window','tr-glass','wy-bronze','wy-window','wy-skylight','mi-glass','mi-window','mi-dome']:
  bs.inputs['Metallic'].default_value=.30;bs.inputs['Roughness'].default_value=.24
 if k in ['ap-glass','sar-glass','scp-glass','f11-glass','sig-glass','thq-glass','pf-glass','bp-glass','tf-glass','oa-glass','ph-glass','sc17-glass','os-glass','li-glass','bj-glass','cg-glass','cu-glass','oo-glass','spo-glass','c525-glass','spc-glass','sls-glass','ad-glass','ccc-glass','o515-glass','cm-glass','cga-glass','rc-glass','cr-nw-glass','cv-glass']:
  bs.inputs['Metallic'].default_value=.12;bs.inputs['Roughness'].default_value=.27
 if k in ['ap-asphalt','sar-asphalt','scp-asphalt']:
  bs.inputs['Roughness'].default_value=.96;bs.inputs['Specular IOR Level'].default_value=.12
 if k in ['bcr-tile-paint','bcr-curved-tile-paint']:
  # Original repeatable clay barrel tiles: four columns/rows per texture.
  n=512;yy,xx=np.mgrid[0:n,0:n];u=xx/n*4;v=yy/n*4
  fu=u%1;fv=v%1;variation=.94+.055*np.sin(np.floor(u)*17+np.floor(v)*31)
  edge=(fv<.045);roll=.018*np.cos(fu*math.tau)
  base=np.ones((n,n,4),dtype=np.float32)
  for c,value in enumerate([.69,.49,.37]):base[:,:,c]=value*variation*(1-.13*edge)+.014*np.cos(fu*math.tau)
  image=bpy.data.images.get('Original Bellagio clay tile albedo')
  if image is None:
   image=bpy.data.images.new('Original Bellagio clay tile albedo',width=n,height=n);image.pixels.foreach_set(base.flatten());image.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Base Color'].default_value=(1,1,1,1)
  normal=bpy.data.images.get('Original Bellagio clay tile normal')
  if normal is None:
   sx=-.018*math.tau/.28*np.sin(fu*math.tau);sy=.10*np.exp(-((fv-.055)/.035)**2);length=np.sqrt(sx*sx+sy*sy+1)
   pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,0]=.5-sx/length/2;pix[:,:,1]=.5-sy/length/2;pix[:,:,2]=.5+1/length/2
   normal=bpy.data.images.new('Original Bellagio clay tile normal',width=n,height=n);normal.colorspace_settings.name='Non-Color';normal.pixels.foreach_set(pix.flatten());normal.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=normal;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal']);bs.inputs['Roughness'].default_value=.88;bs.inputs['Specular IOR Level'].default_value=.18
 if k=='bhs-roof-metal-paint':
  n=256;yy,xx=np.mgrid[0:n,0:n];slope=.16*np.sin(yy/n*math.tau)
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,0]=.5;pix[:,:,1]=.5+slope/2;pix[:,:,2]=.5+np.sqrt(1-slope*slope)/2
  im=bpy.data.images.new('Original service-shed metal corrugation normal',width=n,height=n);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;normal=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],bs.inputs['Normal']);bs.inputs['Roughness'].default_value=.68
 if k=='vp-glass':
  bs.inputs['Metallic'].default_value=.12;bs.inputs['Roughness'].default_value=.3
 if k=='fl-shop-glass':
  bs.inputs['Metallic'].default_value=.08;bs.inputs['Roughness'].default_value=.34
 if k in ['fb-rib-metal','fb-silver','aria-trim','wa-metal','wa-metal-light','wa-metal-dark','wa-frame','ph-metal','ph-silver','ph-disc','mgm-bronze','mgm-frame']:
  bs.inputs['Metallic'].default_value=.65;bs.inputs['Roughness'].default_value=.38
 if k.startswith('ph-led') or k in ['ph-letter','mgm-lit','mgm-screen']:
  bs.inputs['Emission Color'].default_value=(*linear,1);bs.inputs['Emission Strength'].default_value=.65 if k=='ph-letter' else .4
 if k.startswith('linq-glass'):
  bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.22
 if k=='canal-water':
  bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.08;bs.inputs['IOR'].default_value=1.333
 if k=='gondola-lacquer':
  bs.inputs['Roughness'].default_value=.19;bs.inputs['Coat Weight'].default_value=.75;bs.inputs['Coat Roughness'].default_value=.10
 if k in ['gondola-chrome','gondola-brass']:
  bs.inputs['Metallic'].default_value=.92;bs.inputs['Roughness'].default_value=.19 if k=='gondola-chrome' else .3
 if k=='gondola-upholstery':
  bs.inputs['Roughness'].default_value=.8;bs.inputs['Sheen Weight'].default_value=.45
 if k in ['cr-metal-paint','cr-metal-light-paint','cr-seam-paint']:bs.inputs['Metallic'].default_value=.8;bs.inputs['Roughness'].default_value=.34
 if k=='mirror':bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=.04
 if k=='ice':bs.inputs['Metallic'].default_value=.18;bs.inputs['Roughness'].default_value=.12
 if k=='mm-display-paint':
  # Original neutral amber-blue display artwork, no borrowed show advertising.
  n=512;v,u=np.mgrid[0:n,0:n]/n;halo=np.exp(-((u-.5)**2*7+(v-.53)**2*5))
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.array([.025,.035,.06])+halo[:,:,None]*np.array([.30,.13,.045])
  im=bpy.data.images.new('Original Mirage neutral display',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.8;bs.inputs['Roughness'].default_value=.65
 if k=='wm-led-paint':
  # Original low-contrast abstract display; no copied advertising or video.
  n=512;v,u=np.mgrid[0:n,0:n]/n
  glow=np.exp(-((u-.45)**2*14+(v-.62)**2*9))
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.array([.035,.045,.055])+glow[:,:,None]*np.array([.28,.15,.055])
  im=bpy.data.images.new('Original Wynn neutral LED artwork',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1.25;bs.inputs['Roughness'].default_value=.60
 if k in ['wm-screen-letter','wm-gold-letter']:
  bs.inputs['Emission Color'].default_value=(*linear,1);bs.inputs['Emission Strength'].default_value=.18
 if k.startswith('lob-'):
  bs.inputs['Roughness'].default_value=.94;bs.inputs['Specular IOR Level'].default_value=.18
 if k=='lob-glyph-paint':
  for suffix,socket in [('stone','Base Color'),('normal',None)]:
   im=bpy.data.images.load(str((OUT/('textures/luxor-obelisk-original-'+suffix+'.png')).resolve()));im.pack()
   tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;tx.extension='EXTEND'
   if socket:m.node_tree.links.new(tx.outputs['Color'],bs.inputs[socket])
   else:
    im.colorspace_settings.name='Non-Color';nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.55;m.node_tree.links.new(tx.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 if k=='chy-canopy-glass':
  m.use_backface_culling=False
  bs.inputs['Alpha'].default_value=.35;bs.inputs['Roughness'].default_value=.27;m.diffuse_color=(*linear,.35);m.surface_render_method='DITHERED'
 if k=='wlf-rail-glass':
  bs.inputs['Alpha'].default_value=.16;bs.inputs['Roughness'].default_value=.19;m.diffuse_color=(*linear,.16);m.surface_render_method='DITHERED'
 if k=='wlf-window-glass':
  bs.inputs['Metallic'].default_value=.25;bs.inputs['Roughness'].default_value=.25
 if k in ['glass','shopglass','cabinglass']:
  alpha={'glass':.22,'shopglass':.16,'cabinglass':.48}[k];bs.inputs['Alpha'].default_value=alpha;m.diffuse_color=(*linear,alpha);m.surface_render_method='DITHERED'
 if k in ['warm','screen','magenta','ledblue','vortex0','vortex1','vortex2','skyglass','pinkled','purple','yellowled']:
  bs.inputs['Emission Color'].default_value=(*linear,1);bs.inputs['Emission Strength'].default_value=2.3 if k=='warm' else .65
 if k=='mk-peeling-white-paint':
  # Original weathered paint map: irregular chips, not copied Street View imagery.
  n=1024;v,u=np.mgrid[0:n,0:n];rng=np.random.default_rng(1700)
  field=np.zeros((n,n))
  for j in range(14):
   a=rng.uniform(0,math.tau);f=rng.integers(3,17);phase=rng.uniform(0,math.tau)
   field+=np.sin((u*math.cos(a)+v*math.sin(a))*math.tau*f/n+phase)/math.sqrt(f)
  field+=.22*np.sin(u*.71+np.sin(v*.27)*2)+.17*np.sin(v*.93+u*.37)
  chip=field>1.65;edge=(field>1.52)&~chip
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=rgb[None,None,:]*(1+rng.normal(0,.012,(n,n,1)))
  pix[chip,:3]=[.58,.62,.63];pix[edge,:3]=[.7,.72,.7]
  bs.inputs['Base Color'].default_value=(1,1,1,1);bs.inputs['Roughness'].default_value=.98
  im=bpy.data.images.new('Original flaking market paint',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 if k=='ms-white-brick-paint':
  # Original painted masonry relief; avoid tinting it with the red-brick runtime set.
  n=1024;v,u=np.mgrid[0:n,0:n];row=v//32;xx=(u+(row%2)*64)%128
  seam=(v%32<3)|(xx<3);rng=np.random.default_rng(1511)
  value=np.where(seam,.90,1)+rng.normal(0,.009,(n,n))
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=rgb[None,None,:]*value[:,:,None]
  bs.inputs['Base Color'].default_value=(1,1,1,1);bs.inputs['Roughness'].default_value=.96
  im=bpy.data.images.new('Original white painted masonry',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  height=np.where(seam,0.,1.);dy,dx=np.gradient(height)
  normal=np.ones((n,n,4),dtype=np.float32);normal[:,:,:3]=[.5,.5,1];normal[:,:,0]=.5-dx*.16;normal[:,:,1]=.5-dy*.16
  ni=bpy.data.images.new('Original painted masonry normal',width=n,height=n);ni.colorspace_settings.name='Non-Color';ni.pixels.foreach_set(normal.flatten());ni.pack()
  nt=m.node_tree.nodes.new('ShaderNodeTexImage');nt.image=ni;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(nt.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 if k in ['cu-board0','cu-board1','cu-board2']:
  # Original weathered plywood colour/normal maps; local authoring, no photo pasted onto geometry.
  n=512;v,u=np.mgrid[0:n,0:n]/n;rng=np.random.default_rng(840+int(k[-1]))
  grain=np.sin(u*240+np.sin(v*8)*2+np.sin(v*21)*.6)*.025
  patches=np.zeros((n,n))
  for cells,amp in [(3,1),(7,.5),(19,.23),(53,.12)]:
   grid=rng.random((cells+1,cells+1));grid[-1,:]=grid[0,:];grid[:,-1]=grid[:,0]
   t=np.arange(n)*cells/n;i=t.astype(int);f=t-i;f=f*f*(3-2*f)
   rows=grid[i]*(1-f)[:,None]+grid[i+1]*f[:,None];patches+=amp*(rows[:,i]*(1-f)[None,:]+rows[:,i+1]*f[None,:])
  wear=np.clip((patches/1.85-.42)*2.0,0,1)
  pixels=np.ones((n,n,4),dtype=np.float32)
  pixels[:,:,:3]=rgb[None,None,:]*(.87+grain[:,:,None]+rng.normal(0,.025,(n,n,1)))
  pixels[:,:,:3]=pixels[:,:,:3]*(1-wear[:,:,None]*.20)+np.array([.59,.58,.51])*wear[:,:,None]*.20
  bs.inputs['Base Color'].default_value=(1,1,1,1);bs.inputs['Roughness'].default_value=.95
  im=bpy.data.images.new('Original weathered plywood '+k,width=n,height=n);im.pixels.foreach_set(pixels.flatten());im.pack()
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
  normal=np.ones((n,n,4),dtype=np.float32);normal[:,:,:3]=[.5,.5,1];normal[:,:,0]+=.025*np.cos(u*240+np.sin(v*8)*2)
  ni=bpy.data.images.new('Original plywood grain normal '+k,width=n,height=n);ni.colorspace_settings.name='Non-Color';ni.pixels.foreach_set(normal.flatten());ni.pack()
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=ni;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(tx.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 if k in ['bhc-roof-paint','oo-roof-paint','spo-roof-paint','spc-roof-paint','bt-roof-paint']:
  # Original small-scale shingle colour/normal maps, packed in the GLB; no external image reuse.
  n=1024;v,u=np.mgrid[0:n,0:n];row=v//32;col=((u+(row%2)*32)%n)//64
  rng=np.random.default_rng(113);tiles=rng.uniform(.90,1.10,(32,16));seam=(v%32<2)|((u+(row%2)*32)%64<1)
  val=tiles[row,col]+rng.normal(0,.025,(n,n));val*=np.where(seam,.77,1)
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=rgb[None,None,:]*val[:,:,None]
  bs.inputs['Base Color'].default_value=(1,1,1,1)
  im=bpy.data.images.new('Original Bali Hai green shingles',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.92
  normal=np.ones((n,n,4),dtype=np.float32);normal[:,:,:3]=[.5,.5,1];normal[:,:,1]=np.where(v%32==2,.57,.5)
  ni=bpy.data.images.new('Original Bali Hai shingle normal',width=n,height=n);ni.colorspace_settings.name='Non-Color';ni.pixels.foreach_set(normal.flatten());ni.pack()
  nt=m.node_tree.nodes.new('ShaderNodeTexImage');nt.image=ni;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(nt.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 if k in ['ccourt-fascia-paint','ccourt-column-color-paint']:
  n=128;v,u=np.mgrid[0:n,0:n];t=v/(n-1)
  stops=np.array([[.35,.17,.55],[.75,.20,.52],[.90,.42,.20],[.91,.76,.21],[.67,.80,.27]],dtype=np.float32)
  vv=t*4;ii=np.minimum(vv.astype(int),3);ff=vv-ii
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=stops[ii]*(1-ff[:,:,None])+stops[ii+1]*ff[:,:,None]
  im=bpy.data.images.new('Original Carnaval painted colour gradient',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;tx.extension='EXTEND';m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.68
 if k=='luxor-pyramid':
  # Mipmapped joints avoid subpixel geometry scintillation on this huge facade.
  n=256;v,u=np.mgrid[0:n,0:n];seam=(u<3)|(v<3)
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=rgb
  pix[:,:,:3]*=np.where(seam,.58,1.0)[:,:,None]
  im=bpy.data.images.new('Luxor glass panel joints',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 if k=='rw-led':
  n=512;v,u=np.mgrid[0:n,0:n]/n
  glow=np.exp(-((np.sqrt((u-.5)**2+(v-.5)**2)-.22)/.07)**2)
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.array([.21,.025,.055])+glow[:,:,None]*np.array([.42,.15,.065])
  im=bpy.data.images.new('Original Resorts World red halo display',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.45
 if k=='ph-led-cylinder':
  n=512;v,u=np.mgrid[0:n,0:n]/n
  radius=np.sqrt(((u-.5)*1.5)**2+((v-.54)*1.1)**2)
  halo=np.exp(-((radius-.16)/.13)**2);rays=np.sin(np.arctan2(v-.54,u-.5)*13+radius*8)*.5+.5
  rgb=np.zeros((n,n,3));rgb[:]=[.12,.16,.33]
  rgb+=halo[:,:,None]*np.array([.58,.26,.14]);rgb+=(rays*radius*.35)[:,:,None]*np.array([.44,.13,.45])
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.clip(rgb,0,1)
  im=bpy.data.images.new('Original PH radial marquee',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.65
 if k=='sky':
  # The Grand Canal Shoppes' painted sky: soft blue with drifting cumulus, lit evenly (an emissive ceiling, like the real one)
  n=1024;rng=np.random.default_rng(7);acc=np.zeros((n,n))
  for octave,(cells,amp) in enumerate([(4,1.0),(8,.5),(16,.25),(32,.13),(64,.06)]):
   g=rng.random((cells+1,cells+1));g[-1,:]=g[0,:];g[:,-1]=g[:,0]
   t=np.linspace(0,cells,n,endpoint=False);i=t.astype(int);f=t-i;f=f*f*(3-2*f)
   rows=g[i]*(1-f)[:,None]+g[i+1]*f[:,None];acc+=amp*(rows[:,i]*(1-f)[None,:]+rows[:,i+1]*f[None,:])
  acc/=1.94;cloud=np.clip((acc-.50)/.22,0,1);cloud=cloud*cloud*(3-2*cloud)
  v,u=np.mgrid[0:n,0:n]/n;sky=np.stack([.40+.10*v,.60+.08*v,.86+.04*v],-1)
  shade=np.clip(.92+.10*(acc-.6),0,1)[:,:,None]*np.array([1.0,.97,.93])
  rgb=sky*(1-cloud[:,:,None])+shade*cloud[:,:,None]
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.clip(rgb,0,1)
  im=bpy.data.images.new('Original painted sky',width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack()
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
  m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Emission Color'])
  bs.inputs['Emission Strength'].default_value=.9;bs.inputs['Roughness'].default_value=1
 if k=='fresco':
  im=bpy.data.images.load(str((OUT/'textures/venetian-ceiling-fresco.png').resolve()));im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.86
 if k in patterns and k!='fresco':
  n=512;v,u=np.mgrid[0:n,0:n]/n;rng=np.random.default_rng(13);noise=rng.random((n,n))-.5;variation=.035*noise
  if k in ['marble','stone','tile','sandstone']:
   wave=np.sin(u*17+np.sin(v*9)*1.8+np.sin(u*5+v*3)*3+np.sin(v*40)*.12);variation-=np.exp(-abs(wave)*20)*(.13 if k=='marble' else .025)
   if k=='tile':variation-=(((u%(.5))<.003)|((v%(.5))<.003))*.13
  if k.startswith('brick'):
   rows=v*14;col=u*7+(np.floor(rows)%2)*.5;mortar=(rows%1<.045)|(col%1<.04);variation-=mortar*.14;variation+=.025*np.sin(np.floor(col)*11+np.floor(rows)*7)
  if k in ['walnut','panel']:
   # Fine, low-contrast straight grain stays quiet across large wall panels.
   variation+=.018*np.sin(u*130+np.sin(v*8)*.35)+.010*np.sin(u*340+v*.5)
  if k=='velvet':variation+=.02*np.sin(u*1600)*np.sin(v*1600)+.07*np.sin(u*21+v*13)**2
  if k in ['carpet','floralcarpet','parkcarpet','palazzocarpet','ticarpet','harrahscarpet']:
   weave=.018*np.sin(u*1400)*np.cos(v*1300);pattern=np.sin(u*19+np.sin(v*8)*2)*np.sin(v*21+np.sin(u*7)*3);variation=weave+np.where(abs(pattern)<.12,.17,0)
  if k=='ticarpet':
   a=u*2-1;b=v*2-1;rad=np.sqrt(a*a+b*b);ang=np.arctan2(b,a)
   motif=np.exp(-((rad-(.36+.13*np.cos(ang*3)))/.055)**2)
   scroll=np.exp(-((rad-(.72+.065*np.cos(ang*8)))/.022)**2)
   variation=-.14*motif+.10*scroll+.009*np.sin(u*1400)*np.cos(v*1300)
  if k=='parkcarpet':variation=.045*np.sin(u*42+v*8)*np.sin(v*28-u*7)
  if k=='amethyst':variation=.06*np.sin(u*6+v*10+np.sin(v*17))+.03*np.sin(u*29-v*15)
  if k in ['botanical','nautical']:
   variation=.13*np.sin(u*17+np.sin(v*12))*np.cos(v*23)+.09*np.sin(v*8+u*6)
  if k in ['rootwood','shipwood']:variation+=.012*np.sin(u*60+np.sin(v*18))
  if k=='fresco':variation=.15*np.sin(u*7)*np.cos(v*12)+.1*np.sin(u*19+v*7);rgb=np.array([.71,.73,.66])
  pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.clip(rgb+variation[:,:,None],0,1)
  im=bpy.data.images.new('Original '+k,width=n,height=n);im.pixels.foreach_set(pix.flatten());im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 materials[k]=m;return m

def add(name):
 data=json.loads((OUT/(name+'.json')).read_text())
 for g in data['meshes']:
  # Merge identical coordinates within each material batch; keep a flat normal at stone corners.
  lookup={};verts=[];remap=[]
  for x,y,z in g['vertices']:
   p=(round(x,5),round(-z,5),round(y,5))
   if p not in lookup:lookup[p]=len(verts);verts.append(p)
   remap.append(lookup[p])
  faces=[tuple(remap[i] for i in f) for f in g['faces']];faces=[f for f in faces if len(set(f))==3]
  me=bpy.data.meshes.new(g['material']);me.from_pydata(verts,[],faces);me.update();me.materials.append(material(g['material']));o=bpy.data.objects.new(g['property']+'/'+g['source']+'/'+g['material'],me);bpy.context.collection.objects.link(o);o['property']=g['property'].split('-')[0];o['source']=g['source'];o['detail']=g['detail'];o['surface']=g['material']
  if g['material'].startswith('luxor-sculpt-') or g['material'] in ['lob-sculpt-stone','ph-disc','ice','rootwood','rope','gondola-lacquer','gondola-upholstery','gondola-brass','gondola-chrome','gondola-wood'] or (g['material']=='bronze' and g['source']=='polo-lobby'):
   for polygon in me.polygons:polygon.use_smooth=True
  if g['material'].startswith('vi-'):VM.uvs(me,g['material'])
  if g['material'] in patterns or g['material'] in ['bcr-tile-paint','bcr-curved-tile-paint','lob-glyph-paint','mm-display-paint','wm-led-paint','ccourt-fascia-paint','ccourt-column-color-paint','bhs-roof-metal-paint','sky','ph-led-cylinder','luxor-pyramid','rw-led','bhc-roof-paint','oo-roof-paint','spo-roof-paint','spc-roof-paint','bt-roof-paint','ms-white-brick-paint','mk-peeling-white-paint','cu-board0','cu-board1','cu-board2']:
   uv=me.uv_layers.new(name='Metres')
   if g['material']=='fresco':
    zone=next(v for v in json.loads((OUT/'venues.json').read_text()) if v['key']=='venetian')['zones'][0];ox,_,oz=zone['origin'];co,si=math.cos(zone['yaw']),math.sin(zone['yaw'])
   for poly in me.polygons:
    axis=max(range(3),key=lambda i:abs(poly.normal[i]))
    for li in poly.loop_indices:
     p=me.vertices[me.loops[li].vertex_index].co
     if g['material']=='bcr-tile-paint':uv.data[li].uv=((p.y if abs(poly.normal.x)>abs(poly.normal.y) else p.x)/1.12,p.z/.78)
     elif g['material']=='bcr-curved-tile-paint':uv.data[li].uv=(math.atan2(-p.y-294.85,p.x+215.4)*18/1.12,math.hypot(p.x+215.4,-p.y-294.85)/1.6)
     elif g['material']=='ccourt-fascia-paint':uv.data[li].uv=(.5,(p.z-4.6)/1.0)
     elif g['material']=='ccourt-column-color-paint':uv.data[li].uv=(.5,(p.z-3.6)/.95)
     elif g['material']=='lob-glyph-paint':
      width=6.7+(3.55-6.7)*(p.z-6.61)/32.74;uv.data[li].uv=(((p.y+2283.836) if axis==0 else (p.x+28.4755))/width+.5,(p.z-6.61)/32.74)
     elif g['material']=='rw-led':uv.data[li].uv=((p.x-488)/112,(p.z-44)/89)
     elif g['material']=='luxor-pyramid':uv.data[li].uv=((p.x if axis==1 else p.y)/2.1,p.z/1.9)
     elif g['material']=='ph-led-cylinder':uv.data[li].uv=((math.atan2(-p.y-642.5,p.x-43.5)-math.pi/2)%math.tau/math.pi,(p.z-8.5)/21.5)
     elif g['material']=='bhs-roof-metal-paint':uv.data[li].uv=((.881*p.x+.473*p.y)/2,(.473*p.x-.881*p.y)/.85)
     elif g['material']=='bhc-roof-paint':uv.data[li].uv=((.766*p.x-.643*p.y)/6.4,(-.643*p.x-.766*p.y)/6.4)
     elif g['material'] in ['oo-roof-paint','spo-roof-paint','spc-roof-paint','bt-roof-paint']:uv.data[li].uv=(p.x/6.4,p.y/6.4)
     elif g['material']=='ms-white-brick-paint':uv.data[li].uv=((p.y if axis==0 else p.x)/2.4,p.z/2.4)
     elif g['material']=='mk-peeling-white-paint':uv.data[li].uv=((p.y if axis==0 else p.x)/.85,p.z/.85)
     elif g['material']=='sky':uv.data[li].uv=(p.x/64,p.y/64)
     elif g['material']=='mm-display-paint':
      uu=math.cos(-.0244)*(p.x+.252)-math.sin(-.0244)*(-p.y+427.01);uv.data[li].uv=(uu/22+.5,p.z/60)
     elif g['material']=='wm-led-paint':
      uu=math.cos(-.14)*(p.x-432.387)-math.sin(-.14)*(-p.y+1164.56);uv.data[li].uv=(uu/15.24+.5,(p.z-10.668)/30.48)
     elif g['material']=='fresco':
      dx,dz=p.x-ox,-p.y-oz;xx,zz=co*dx-si*dz,si*dx+co*dz;panel=round((zz-5)/9);uv.data[li].uv=(xx/17+.5,(zz-5-panel*9)/7.5+.5)
     else:uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 for t in data['labels']:
  cu=bpy.data.curves.new(t['text'],'FONT');cu.body=t['text'];cu.align_x='CENTER';cu.size=t['size'];cu.extrude=.008;cu.bevel_depth=.002;cu.bevel_resolution=1;cu.materials.append(material(t['material']));o=bpy.data.objects.new(t['text'],cu);bpy.context.collection.objects.link(o);x,y,z=t['position'];o.location=(x,-z,y);o.rotation_euler=(math.pi/2,0,-t['yaw']+math.pi);o['property']=name.split('-')[0];o['source']=t['source'];o['detail']=t.get('detail',1)
  if t['material'] in ['wm-gold-letter','wm-screen-letter']:
   if t['material']=='wm-gold-letter':
    fp=Path('/System/Library/Fonts/Supplemental/SnellRoundhand.ttc')
    if fp.exists():cu.font=bpy.data.fonts.load(str(fp),check_existing=True)
   cu.resolution_u=5
   bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH')
   for vert in o.data.vertices:vert.co.z+=1.65*(vert.co.x/7.62)**2
   o.select_set(False)
  if t['material'] in ['cv-white-letter','lob-blue-letter']:
   fp=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
   if fp.exists():cu.font=bpy.data.fonts.load(str(fp),check_existing=True)
  if t['material'] in ['li-red-letter','tm-red-letter']:
   cu.resolution_u=3;cu.bevel_depth=0
   font_path=Path('/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf')
   if font_path.exists():cu.font=bpy.data.fonts.load(str(font_path),check_existing=True)
 bpy.context.view_layer.update()

if __name__=='__main__':
 names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [f'{k}-{layer}' for k in [v['key'] for v in json.loads((OUT/'venues.json').read_text())] for layer in ['exterior','interior']]
 for name in names:
  bpy.ops.wm.read_factory_settings(use_empty=True);materials.clear();add(name)
  bpy.ops.wm.save_as_mainfile(filepath=str((OUT/(name+'.blend')).resolve()))
  bpy.ops.export_scene.gltf(filepath=str((OUT/(name+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
  print('EXPORTED',name,flush=True)
 h=hashlib.sha256()
 for f in sorted(OUT.glob('*.glb')):h.update(f.read_bytes())
 # Collision-only revisions must also invalidate browser caches.
 for f in sorted(OUT.glob('*-collision.json')):h.update(f.read_bytes())
 h.update((OUT/'venues.json').read_bytes());(OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
