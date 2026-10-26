"""Claude's token usage on the Vegas project and its cost at standard Anthropic API prices, from the local Claude Code
transcripts (~/.claude/projects, subagents and workflow agents included). For the info video's agent scene (2026-10-23:
the owner asked for Claude's token usage, shown in the video combined with Codex's without itemising, and the total
estimated cost at API prices).

What counts: every API response of the main Vegas conversation (and its subagents), plus responses in other sessions
that ran with their working directory inside the project, or whose tool calls name it in sessions that otherwise worked
on it (listed in NAMED_OK). Each response is counted once (its usage repeats on every content block of the transcript).
Nothing but counts is kept.

Prices (USD per million tokens, Anthropic first-party API, cached 2026-10-06 in the claude-api reference): cache writes
bill at 1.25x input for the 5-minute TTL and 2x for the 1-hour TTL.
    python3 tools/info-video/claude_tokens.py      -> build/info-video/claude-tokens.json
"""
import json, glob, os, collections

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(PROJ, 'build/info-video/claude-tokens.json')
MAIN = '87d24a54-c6fa-4e76-af84-607fec559efd'                  # the Vegas conversation (2026-10-07 on)
NAMED_OK = ('ddf12c3d', '1869e6b6')                              # sessions whose project-naming calls were Vegas work
PRICE = {  # input, output, cache read
    'claude-opus-5-5': (4.00, 20.00, 0.20),
    'claude-sonnet-5-5': (2.00, 10.00, 0.20),
}

def main():
    seen = set(); by_model = collections.defaultdict(collections.Counter); days = collections.Counter()
    for f in glob.glob(os.path.expanduser('~/.claude/projects/**/*.jsonl'), recursive=True):
        whole = MAIN in f; named_ok = any(s in f for s in NAMED_OK)
        with open(f, errors='replace') as fh:
            for line in fh:
                if '"assistant"' not in line: continue
                try: d = json.loads(line)
                except ValueError: continue
                if d.get('type') != 'assistant': continue
                m = d.get('message') or {}; u = m.get('usage'); mid = m.get('id')
                if not u or not mid or mid in seen: continue
                if not whole:
                    inside = (d.get('cwd') or '').startswith(PROJ)
                    names = named_ok and any(isinstance(c, dict) and c.get('type') == 'tool_use' and 'vegas-afterlight' in json.dumps(c.get('input'))
                                             for c in (m.get('content') or []))
                    if not (inside or names): continue
                seen.add(mid)
                c = by_model[m.get('model', '?')]; cc = u.get('cache_creation') or {}
                c['responses'] += 1
                c['input'] += u.get('input_tokens') or 0
                c['cacheRead'] += u.get('cache_read_input_tokens') or 0
                c['cacheWrite5m'] += cc.get('ephemeral_5m_input_tokens') or 0
                c['cacheWrite1h'] += cc.get('ephemeral_1h_input_tokens') or 0
                # (older transcripts without the TTL split: their whole write counts as 5-minute)
                c['cacheWrite5m'] += max(0, (u.get('cache_creation_input_tokens') or 0) - (cc.get('ephemeral_5m_input_tokens') or 0) - (cc.get('ephemeral_1h_input_tokens') or 0))
                c['output'] += u.get('output_tokens') or 0
                days[(d.get('timestamp') or '')[:10]] += 1
    models = {}; tokens = cost = 0.0
    for model, c in by_model.items():
        if model not in PRICE:
            if any(c[k] for k in ('input', 'cacheRead', 'cacheWrite5m', 'cacheWrite1h', 'output')): print('unpriced model', model, dict(c))
            continue
        pi, po, pr = PRICE[model]
        usd = (c['input'] * pi + c['cacheRead'] * pr + c['cacheWrite5m'] * pi * 1.25 + c['cacheWrite1h'] * pi * 2 + c['output'] * po) / 1e6
        t = c['input'] + c['cacheRead'] + c['cacheWrite5m'] + c['cacheWrite1h'] + c['output']
        models[model] = dict(c, tokens=t, usd=round(usd, 2)); tokens += t; cost += usd
    res = dict(tokens=int(tokens), usd=round(cost, 2), models=models, activeDays=sorted(k for k in days if k),
               note='Claude Code transcripts on this machine; excludes generation services (Bitmagic sparks) and other machines')
    json.dump(res, open(OUT, 'w'), indent=1)
    print(f"Claude: {tokens / 1e9:.3f} billion tokens, ${cost:,.0f} at API prices")
    for k, v in models.items(): print(' ', k, v)

if __name__ == '__main__':
    main()
