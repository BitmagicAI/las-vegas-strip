#!/usr/bin/env python3
"""Join V8 --trace-gc lines (from `DEBUG=pw:browser node tools/probe-streaming.mjs --trace-gc ...`) with the
probe's report.json: which garbage collections fall inside each long frame, and why they ran.

  python3 tools/analyze-gc.py build/probe/streaming/<name>.out build/probe/streaming/<name>/report.json
"""
import json,re,sys
out,report=sys.argv[1],sys.argv[2]
rep=json.load(open(report))
line_re=re.compile(r'\[(\d+):(0x[0-9a-f]+)\]\s+(\d+) ms: (.+?) ([\d.]+) \(([\d.]+)\) -> ([\d.]+) \(([\d.]+)\) MB(?:, pooled: [\d.]+ MB)?, (?:[\d.]+ / )?([\d.]+) / ([\d.]+) ms\s+\(average mu = [\d.]+, current mu = [\d.]+\)\s*(.*)$')
gcs=[]
for raw in open(out,errors='replace'):
    m=line_re.search(raw)
    if not m: continue
    pid,iso,ms,kind,b,bt,a,at,dur,ext,reason=m.groups()
    gcs.append(dict(pid=pid,iso=iso,v8=int(ms),kind=kind,before=float(b),after=float(a),dur=float(dur),reason=reason.strip()))
testing=[g for g in gcs if 'testing' in g['reason'] or 'testing' in g['kind']]
print(len(gcs),'gc lines;',len(testing),'calibration lines')
if len(testing)<2: sys.exit('no calibration lines: run with --trace-gc and DEBUG=pw:browser')
iso=testing[0]['iso'];pid=testing[0]['pid']
main=[g for g in gcs if g['iso']==iso and g['pid']==pid]
mark=rep['gcMark'];offset=testing[0]['v8']-mark['before']  # v8 time = page time + offset (the GC ends a little after the call starts)
for g in main: g['t']=g['v8']-offset-g['dur']  # page time at the start of the pause
drive=[g for g in main if g['t']>=mark['after']]
tot=sum(g['dur'] for g in drive)
print(f"renderer isolate {pid}:{iso}: {len(drive)} collections during the drive, {tot:.0f} ms paused in total")
from collections import defaultdict
by=defaultdict(lambda:[0,0.0])
for g in drive:
    k=(g['kind'],g['reason'][:60]);by[k][0]+=1;by[k][1]+=g['dur']
print('\nby kind / reason:')
for (k,r),(n,d) in sorted(by.items(),key=lambda x:-x[1][1]): print(f'  {n:4d} x {d:8.0f} ms  {k} | {r}')
print('\nlong pauses (>= 100 ms):')
for g in sorted(drive,key=lambda g:g['t']):
    if g['dur']>=100: print(f"  t={g['t']:.0f} {g['dur']:.0f} ms {g['kind']} {g['before']:.0f}->{g['after']:.0f} MB  {g['reason']}")
print('\nlong frames and the collections inside them:')
for gap in rep['longGaps']:
    a,b=gap['at'],gap['at']+gap['gap']
    inside=[g for g in drive if g['t']<=b and g['t']+g['dur']>=a]
    sd=sum(g['dur'] for g in inside)
    print(f"  lap{gap['lap']} gap {gap['gap']} ms at z={gap['pos']['z'] if gap['pos'] else None}: {len(inside)} gc = {sd:.0f} ms ({100*sd/max(1,gap['gap']):.0f}%) loading={','.join(gap['coveredByLoadingJobs']) or 'NONE'}  " + '; '.join(f"{g['kind']} {g['dur']:.0f}ms {g['reason'][:40]}" for g in inside if g['dur']>=20))
