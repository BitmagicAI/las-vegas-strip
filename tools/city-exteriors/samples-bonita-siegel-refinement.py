"""Regenerate original support grids/routes in memory, without saving geometry."""
import sys
sys.path.insert(0, 'tools/strip-landmarks')
from common import Meshes
import bonita_terrace, siegel_paradise
for module in [bonita_terrace, siegel_paradise]:
    module.exterior(Meshes())
