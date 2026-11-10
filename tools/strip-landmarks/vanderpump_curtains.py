"""Original gathered cabana curtains; dimensions inferred from official Soleia photos."""
from common import np

def cabana_curtains(frame):
    b=frame.b
    heights=[.2,.65,1.0,1.5,2.1,2.7,3.4]
    widths=[.82,.58,.45,.67,.9,1.12,1.3]
    for side in [-1,1]:
        rows=[]
        for y,w in zip(heights,widths):
            rows.append([frame.p(side*(3.45-w*t),y,3.32+.065*np.sin(t*np.pi*12)) for t in np.linspace(0,1,25)])
        for lower,upper in zip(rows,rows[1:]):
            for j in range(24):
                b.face('vp-soleia-curtain-paint',[lower[j],lower[j+1],upper[j+1],upper[j]])
        # A narrow tie gathers the panel without closing the central opening.
        frame.box('vp-table-wood',(side*(3.45-.225),1.0,3.40),(.49,.07,.06))
    frame.tube('vp-table-wood',(-3.65,3.44,3.34),(3.65,3.44,3.34),.035,8)
