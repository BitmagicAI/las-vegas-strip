"""Fast local iteration: routes/architecture without rebuilding all pavements."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
source=Path('tools/geographic-strip/prepare.py').read_text().split('county_road,county_walk,county_counts=county_geometry')[0]
exec(compile(source,'tools/geographic-strip/prepare.py','exec'))
