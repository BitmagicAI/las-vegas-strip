// Maintainers: mirror tasks/index.json to GitHub issues, one issue per task titled "[task-id] title", so contributors
// can claim them (tasks/README.md). Dry run by default; nothing is created, edited or closed without --apply.
//
//   node tools/tasks/sync-issues.mjs                  # show what would change
//   node tools/tasks/sync-issues.mjs --apply          # create missing issues, refresh changed bodies and labels,
//                                                     # close issues whose task left the board
//   node tools/tasks/sync-issues.mjs --apply --limit 50   # in batches (GitHub rate-limits issue creation)
// Needs the GitHub CLI signed in with write access to the repository.
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const board = JSON.parse(fs.readFileSync(path.join(ROOT, 'tasks/index.json'), 'utf8'));
const apply = process.argv.includes('--apply');
const li = process.argv.indexOf('--limit');
const limit = li > 0 ? Number(process.argv[li + 1]) : Infinity;
const gh = (a, input) => execFileSync('gh', a, { cwd: ROOT, encoding: 'utf8', input });

function body(t) {
  const f = t.files || {};
  const lines = [t.summary, '', '### What to do', ...t.items.map((x) => `- ${x}`)];
  if (t.buildings?.length) lines.push('', `### Mapped buildings (${t.buildings.length})`, ...t.buildings.slice(0, 30).map((b) => `- ${b.name || 'Unnamed'} \`${b.id}\``));
  if (t.record) lines.push('', `Record: \`${t.record}\``);
  if (f.builders?.length) lines.push('', '### Scripts that build it', ...f.builders.map((x) => `- \`${x}\``));
  if (f.writes?.length) lines.push('', '### Files you will change', ...f.writes.map((x) => `- \`${x}\``));
  lines.push('', '### Done when', ...t.acceptance.map((x) => `- [ ] ${x}`));
  lines.push('', '---', t.owner === 'maintainer'
    ? '_Maintainers only._'
    : `**To work on this:** comment \`/claim\` (or run \`node tools/tasks/pick.mjs claim ${t.id}\`). Open a draft pull request on branch \`task/${t.id}\` with "Closes #<this issue>" early; claims without activity for 14 days are released. Full brief: \`node tools/tasks/pick.mjs show ${t.id}\`.`);
  const text = lines.join('\n');
  return text + `\n\n<!-- task:${t.id} sha:${createHash('sha256').update(text).digest('hex').slice(0, 12)} -->`;
}

const labels = (t) => ['task', `area:${t.area}`, `size:${t.size}`, `priority:${t.priority}`].concat(t.owner === 'maintainer' ? ['maintainers'] : []);

const existing = new Map();
for (const i of JSON.parse(gh(['issue', 'list', '--label', 'task', '--state', 'all', '--limit', '5000', '--json', 'number,title,body,state']))) {
  const m = /^\[([a-z0-9-]+)\]/.exec(i.title);
  if (m) existing.set(m[1], i);
}
if (apply) {
  const want = new Set(board.tasks.flatMap(labels));
  const have = new Set(JSON.parse(gh(['label', 'list', '--limit', '500', '--json', 'name'])).map((l) => l.name));
  for (const l of want) if (!have.has(l)) gh(['label', 'create', l, '--force']);
  if (!have.has('claimed')) gh(['label', 'create', 'claimed', '--color', 'FBCA04', '--description', 'Someone is working on this task']);
}

let changes = 0;
for (const t of board.tasks) {
  if (changes >= limit) break;
  const b = body(t), i = existing.get(t.id), title = `[${t.id}] ${t.title}`;
  if (!i) {
    console.log(`create  ${title}`); changes++;
    if (apply) gh(['issue', 'create', '--title', title, '--body-file', '-', ...labels(t).flatMap((l) => ['--label', l])], b);
  } else if (i.state === 'OPEN' && (i.title !== title || !i.body.includes(b.slice(-30)))) {
    console.log(`update  #${i.number} ${title}`); changes++;
    if (apply) gh(['issue', 'edit', String(i.number), '--title', title, '--body-file', '-', ...labels(t).flatMap((l) => ['--add-label', l])], b);
  }
}
const ids = new Set(board.tasks.map((t) => t.id));
for (const [id, i] of existing) {
  if (changes >= limit) break;
  if (i.state === 'OPEN' && !ids.has(id)) {
    console.log(`close   #${i.number} [${id}] (no longer on the board)`); changes++;
    if (apply) gh(['issue', 'close', String(i.number), '--comment', 'This task is no longer on the board (tools/tasks/build-board.py): it was finished or folded into another task.']);
  }
}
console.log(`${changes} change(s)${apply ? ' applied' : ' (dry run: add --apply)'}`);
