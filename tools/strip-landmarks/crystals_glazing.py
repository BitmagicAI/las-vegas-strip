"""Original exterior roof glazing, inferred within retained central roof facets.

Opaque representations preserve the existing roof/interior/collision envelope.
Reference and inference limits: crystals-frontage-refinement/research.md.
"""
import numpy as np

HOSTS = [(6, 10, 9), (10, 11, 15)]


def roof_glazing(builder, points):
    builder.source = 'crystals-central-roof-glazing-2026-11'
    builder.detail = 0
    for ids in HOSTS:
        host = np.array([points[i] for i in ids], dtype=float)
        normal = np.cross(host[1]-host[0], host[2]-host[0])
        normal /= np.linalg.norm(normal)
        if normal[1] < 0:
            normal = -normal
        center = host.mean(axis=0)
        # Leave broad metal borders; offset clears the retained 15mm seam strips.
        pane = center + (host-center)*.66 + normal*.08
        builder.upface('cr-nw-glass', pane.tolist())
        for a, b in zip(pane, np.roll(pane, -1, axis=0)):
            builder.tube('cr-nw-frame', a.tolist(), b.tolist(), .095, 6)
        # Regular glazing bars taper with the triangular opening.
        a, b, c = pane
        for t in np.arange(.08, .96, .08):
            p = a*(1-t)+b*t+normal*.035
            q = a*(1-t)+c*t+normal*.035
            builder.tube('cr-nw-frame', p.tolist(), q.tolist(), .045, 6)
    builder.detail = 0
