"""Original shallow eight-panel terrace shades; dimensions inferred from official photos."""
import math

def terrace_shade(frame):
    builder = frame.b
    # Keep the existing pole and placement. Shallow canopy replaces the old cone.
    peak = frame.p(0, 2.60, 0)
    underside = frame.p(0, 2.56, 0)
    edge = [frame.p(1.2*math.cos(i*math.tau/8), 2.35,
                    1.2*math.sin(i*math.tau/8)) for i in range(8)]
    for i, a in enumerate(edge):
        b = edge[(i+1)%8]
        builder.upface('c63-shade-fabric', [peak, a, b])
        builder.face('c63-shade-fabric', [underside, a, b])
        builder.tube('ph-metal', underside, (a[0],a[1]-.025,a[2]), .018, 5)
