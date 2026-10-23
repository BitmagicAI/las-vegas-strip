// Pick up a task from the board (tasks/README.md). Claims live on the task's GitHub issue, so two people never
// work on the same thing; this script reads them with the GitHub CLI (`gh`) when it is installed and signed in.
//
//   node tools/tasks/pick.mjs                       # open, unclaimed tasks, best first
//   node tools/tasks/pick.mjs --area interiors --size S,M --limit 20
//   node tools/tasks/pick.mjs show <task-id>        # the full brief: what to do, files, acceptance, rules
//   node tools/tasks/pick.mjs claim <task-id>       # comment /claim on its issue (the claim workflow assigns you)
//   node tools/tasks/pick.mjs release <task-id>     # comment /unclaim
//   node tools/tasks/pick.mjs mine                  # your claimed tasks
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const board = JSON.parse(fs.readFileSync(path.join(ROOT, 'tasks/index.json'), 'utf8'));
const args = process.argv.slice(2);
const opt = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const cmd = args[0] && !args[0].startsWith('--') ? args[0] : 'list';
const byId = new Map(board.tasks.map((t) => [t.id, t]));

function gh(ghArgs) {
  try { return execFileSync('gh', ghArgs, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }); } catch { return null; }
}

/** Open task issues by task id: { number, url, assignees[] }, or null when GitHub cannot be reached. */
function issues() {
  const out = gh(['issue', 'list', '--label', 'task', '--state', 'open', '--limit', '2000', '--json', 'number,title,url,assignees']);
  if (out === null) return null;
  const map = new Map();
  for (const i of JSON.parse(out)) {
    const m = /^\[([a-z0-9-]+)\]/.exec(i.title);
    if (m) map.set(m[1], { number: i.number, url: i.url, assignees: i.assignees.map((a) => a.login) });
  }
  return map;
}

function me() { return (gh(['api', 'user', '--jq', '.login']) || '').trim() || null; }

const ORDER = { P1: 0, P2: 1, P3: 2 };
const SIZE = { S: 0, M: 1, L: 2 };

function list() {
  const iss = issues();
  const areas = opt('--area')?.split(',');
  const sizes = opt('--size')?.split(',');
  const limit = Number(opt('--limit') || 15);
  let tasks = board.tasks.filter((t) => t.status === 'open' && t.owner !== 'maintainer'
    && (!areas || areas.includes(t.area)) && (!sizes || sizes.includes(t.size)));
  if (iss) tasks = tasks.filter((t) => iss.has(t.id) && iss.get(t.id).assignees.length === 0);
  tasks.sort((a, b) => ORDER[a.priority] - ORDER[b.priority] || SIZE[a.size] - SIZE[b.size] || (a.queueOrder ?? 999) - (b.queueOrder ?? 999));
  if (!iss) console.log('(GitHub not reachable with `gh`: claims unknown. Check the task\'s issue before starting.)\n');
  for (const t of tasks.slice(0, limit)) {
    const i = iss?.get(t.id);
    console.log(`${t.id.padEnd(44)} ${t.priority} ${t.size}  ${t.title}${i ? `  (#${i.number})` : ''}`);
  }
  console.log(`\n${tasks.length} open${iss ? ', unclaimed' : ''} task(s). Next: node tools/tasks/pick.mjs show <task-id>`);
}

function show(id) {
  const t = byId.get(id);
  if (!t) { console.error(`No task ${id} in tasks/index.json`); process.exit(1); }
  const i = issues()?.get(id);
  const lines = [
    `# [${t.id}] ${t.title}`,
    `${t.area} · size ${t.size} · ${t.priority}${t.owner === 'maintainer' ? ' · maintainers only' : ''}`,
    i ? `Issue: ${i.url} — ${i.assignees.length ? 'claimed by @' + i.assignees.join(', @') : 'unclaimed'}` : 'Issue: not found (or gh unavailable)',
    '', t.summary, '', '## What to do', ...t.items.map((x) => `- ${x}`),
  ];
  if (t.buildings?.length) lines.push('', `## Mapped buildings (${t.buildings.length})`, ...t.buildings.slice(0, 25).map((b) => `- ${b.name || 'Unnamed'} (${b.id}): ${b.status}`));
  if (t.record) lines.push('', `Record: ${t.record}`);
  const f = t.files || {};
  if (f.reads?.length) lines.push('', '## Read first', ...f.reads.map((x) => `- ${x}`));
  if (f.builders?.length) lines.push('', '## Scripts that build it', ...f.builders.map((x) => `- ${x}`));
  if (f.writes?.length) lines.push('', '## Files you will change', ...f.writes.map((x) => `- ${x}`));
  if (t.needs?.length) lines.push('', '## Needs', ...t.needs.map((x) => `- ${x}`));
  lines.push('', '## Done when', ...t.acceptance.map((x) => `- ${x}`));
  lines.push('', '## Rules', '- Claim it first: node tools/tasks/pick.mjs claim ' + t.id,
    '- Branch task/' + t.id + '; open a draft pull request early with "Closes #<issue>" so the claim stays fresh',
    '- Read AGENTS.md (performance rules: no runtime light changes, no per-frame JS arrays) and CONTRIBUTING.md',
    '- Use public sources; link them in the record, never commit third-party photos or plans');
  console.log(lines.join('\n'));
}

function comment(id, body) {
  const i = issues();
  if (!i) { console.error('Needs the GitHub CLI, signed in: https://cli.github.com (gh auth login)'); process.exit(1); }
  const it = i.get(id);
  if (!it) { console.error(`No open issue titled [${id}]. A maintainer creates them with tools/tasks/sync-issues.mjs.`); process.exit(1); }
  const who = me();
  if (body === '/claim' && it.assignees.length && !it.assignees.includes(who)) {
    console.error(`[${id}] is already claimed by @${it.assignees.join(', @')}. Pick another task.`); process.exit(1);
  }
  if (gh(['issue', 'comment', String(it.number), '--body', body]) === null) { console.error('gh issue comment failed'); process.exit(1); }
  console.log(`${body} posted on #${it.number} (${it.url}).`);
  if (body === '/claim') console.log(`The claim workflow assigns you within a minute. Then: git switch -c task/${id}`);
}

function mine() {
  const who = me();
  const out = who && gh(['issue', 'list', '--label', 'task', '--assignee', who, '--state', 'open', '--json', 'number,title,url']);
  if (!out) { console.error('Needs the GitHub CLI, signed in.'); process.exit(1); }
  for (const i of JSON.parse(out)) console.log(`#${i.number} ${i.title} ${i.url}`);
}

if (cmd === 'list') list();
else if (cmd === 'show') show(args[1]);
else if (cmd === 'claim') comment(args[1], '/claim');
else if (cmd === 'release') comment(args[1], '/unclaim');
else if (cmd === 'mine') mine();
else { console.error('usage: pick.mjs [list|show <id>|claim <id>|release <id>|mine]'); process.exit(1); }
