"""Re-export only guest lobbies connected to the new public arrivals."""
import sys
sys.path.insert(0,'tools/highrises')
import interiors as h
for key in ['park-mgm','palazzo','treasure-island','harrahs']:
 for tower in h.bykey[key]['towers']:h.lobby(h.bykey[key],tower)
 print('CONNECTED GUEST LOBBY',key,flush=True)
