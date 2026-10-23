"""How much agent work went into vegas-afterlight: Claude Code transcripts (~/.claude/projects, subagents included) and
Codex sessions (~/.codex/sessions), counting only entries whose working directory is inside the project.
A Claude entry counts when its cwd is inside the project or its tool input names the project; a Codex call counts when
its arguments name the project (Codex ran from a parent folder). Counts sessions, tool calls, assistant turns and active
hours (5-minute buckets with any counted activity). No content is kept beyond counts and timestamps. Writes build/info-video/agent-effort.json.
python3 tools/info-video/agent_effort.py"""
import json, os, glob, re, datetime, collections
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(PROJ, 'build/info-video/agent-effort.json')
cwd_re = re.compile(r'"cwd":"([^"]*)"'); ts_re = re.compile(r'"timestamp":"([^"]*)"')
def parse_ts(s):
    try: return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception: return None
res = {}
for agent, pattern in [('claude', os.path.expanduser('~/.claude/projects/**/*.jsonl')), ('codex', os.path.expanduser('~/.codex/sessions/**/*.jsonl'))]:
    sessions = 0; tools = 0; turns = 0; buckets = set(); days = set(); first = last = None; dayb = collections.defaultdict(set)
    for f in glob.glob(pattern, recursive=True):
        inside = False; hit = False; ftools = 0
        with open(f, 'r', errors='replace') as fh:
            for line in fh:
                m = cwd_re.search(line[:4000]) or cwd_re.search(line)
                if m: inside = m.group(1).startswith(PROJ)
                names = 'vegas-afterlight' in line
                if not inside and not names: continue
                t = ts_re.search(line)
                ts = parse_ts(t.group(1)) if t else None
                if agent == 'claude':
                    if '"type":"assistant"' in line:
                        turns += 1; n = line.count('"type":"tool_use"'); tools += n; ftools += n
                    else: continue
                else:
                    if names and ('"type":"function_call"' in line or '"type":"custom_tool_call"' in line or '"type":"local_shell_call"' in line):
                        tools += 1; ftools += 1
                    else: continue
                hit = True
                if ts:
                    b = int(ts.timestamp() // 300); buckets.add(b); d = ts.astimezone().date().isoformat(); days.add(d); dayb[d].add(b)
                    first = ts if not first or ts < first else first; last = ts if not last or ts > last else last
        if hit: sessions += 1
    res[agent] = dict(transcripts=sessions, toolCalls=tools, assistantTurns=turns, activeHours=round(len(buckets) * 5 / 60, 1),
                      activeDays=len(days), perDayHours={d: round(len(v) * 5 / 60, 2) for d, v in sorted(dayb.items())}, first=first.isoformat() if first else None, last=last.isoformat() if last else None)
    print(agent, res[agent], flush=True)
json.dump(res, open(OUT, 'w'), indent=1)
