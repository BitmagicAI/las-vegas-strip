"""Build original sign geometry only, without rewriting shared venue metadata."""
from common import *
from shake_shack_frontage import burger_emblem
B=Meshes();B.property='shakeShackRefinement-exterior';B.source='shake-shack-emblem';B.detail=0
burger_emblem(Frame(B,-50.943,1431.246,-math.pi/2,y=0));B.save_all()
