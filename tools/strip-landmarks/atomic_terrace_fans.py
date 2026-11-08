"""Original static eight-blade ceiling fans; placement/size inferred, not surveyed."""
from common import Frame, math, footprint
FAN_CENTERS=((1633,-3663),(1634,-3675))
def terrace_fans(b):
    b.property='atomicGolf-exterior';b.source='podium/south-terrace-fans';b.detail=0
    b.planar('ag-terrace-soffit-paint',footprint('way/1553042969'),9.0)
    for x,z in FAN_CENTERS:
        b.tube('ag-fan-paint',(x,8.18,z),(x,8.96,z),.045,8)
        b.tube('ag-fan-paint',(x,8.10,z),(x,8.26,z),.17,12)
        for i in range(8):
            f=Frame(b,x,z,i*math.tau/8)
            f.box('ag-fan-paint',(.9,8.16,0),(1.46,.035,.14))
