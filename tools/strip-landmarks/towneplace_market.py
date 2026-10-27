"""Original market cabinet based on official Marriott market8528 photograph.
Dimensions and room placement inferred; packages use generic colours, no copied art.
"""
from common import *
def build_market(B,F):
 # Front faces east; tall drink refrigerator at the photograph's right (north).
 F.box('ts-wood',(20.14,1.58,9.3),(.12,2.68,3.8),True)
 for z in [7.4,8.55,11.2]:F.box('ts-wood',(20.55,1.58,z),(.78,2.68,.08),True)
 for y in [.28,2.88]:F.box('ts-wood',(20.55,y,9.3),(.82,.08,3.88))
 # Tall stainless refrigerator with a vented lower plinth and five shelves.
 F.box('ts-frame-paint',(20.56,.45,7.97),(.78,.32,1.04),True)
 F.box('ts-frame-paint',(20.56,2.71,7.97),(.78,.29,1.04))
 F.box('ts-screen',(20.23,1.57,7.97),(.04,2.1,1.02))
 for z in [7.46,8.48]:F.box('ts-frame-paint',(20.98,1.58,z),(.07,2.1,.05))
 for y in [.55,2.6]:F.box('ts-frame-paint',(20.98,y,7.97),(.07,.05,1.07))
 for y in np.arange(.32,.58,.055):F.box('ts-screen',(20.97,float(y),7.97),(.015,.018,.94))
 F.box('ts-metal',(21.04,1.62,8.39),(.045,.51,.035))
 for row,y in enumerate([.68,1.04,1.4,1.76,2.12]):
  F.box('ts-counter',(20.62,y,7.97),(.60,.035,.94))
  for col,z in enumerate(np.linspace(7.58,8.36,6)):
   mat=['ts-market-paint','ts-blue','ts-red-paint'][ (row+col)%3 ]
   F.lathe(mat,20.74,float(z),[(y+.02,.048),(y+.20,.048),(y+.24,.025),(y+.29,.023)],10)
   F.lathe('ts-letter',20.74,float(z),[(y+.11,.049),(y+.17,.049)],10)
   F.lathe('ts-frame-paint',20.74,float(z),[(y+.29,.025),(y+.31,.025)],10)
 # Twin lower chilled cabinets with stocked trays and framed doors.
 for z in [9.2,10.5]:
  F.box('ts-screen',(20.23,.83,z),(.04,1.02,1.20))
  for yy in [.30,1.36]:F.box('ts-frame-paint',(20.98,yy,z),(.07,.055,1.22))
  for zz in [z-.59,z+.59]:F.box('ts-frame-paint',(20.98,.83,zz),(.07,1.1,.045))
  F.box('ts-metal',(21.04,.91,z+.49),(.04,.36,.035))
  for row,y in enumerate([.43,.73,1.03]):
   F.box('ts-counter',(20.62,y,z),(.60,.035,1.14))
   for col in range(4):
    zz=z-.42+col*.28
    F.box(['ts-market-paint','ts-red-paint','ts-blue'][(row+col)%3],(20.7,y+.11,zz),(.23,.18,.22))
    F.box('ts-letter',(20.823,y+.11,zz),(.014,.07,.13))
 # Wood open shelves and generic snack packages above the lower pair.
 for z in [8.61,9.85,11.14]:F.box('ts-wood',(20.56,2.12,z),(.78,1.44,.08))
 for y in [1.42,1.86,2.31,2.84]:F.box('ts-wood',(20.57,y,9.87),(.80,.07,2.6))
 for row,y in enumerate([1.47,1.91,2.36]):
  for col,z in enumerate(np.linspace(8.76,10.99,9)):
   mat=['ts-red-paint','ts-market-paint','ts-blue'][(row+col)%3]
   F.box(mat,(20.69,y+.16,float(z)),(.26,.29,.19))
   F.box('ts-letter',(20.827,y+.17,float(z)),(.012,.09,.12))
 # The reference's upper centre glass-front cabinet: retain open sight of contents
 # rather than reuse the opaque curtained hotel-window material.
 for y in [2.31,2.84]:F.box('ts-frame-paint',(20.99,y,10.5),(.04,.035,1.23))
 for z in [9.89,11.11]:F.box('ts-frame-paint',(20.99,2.57,z),(.04,.52,.035))
 F.lathe('ts-metal',21.02,10.5,[(2.34,.025),(2.38,.025)],8)
