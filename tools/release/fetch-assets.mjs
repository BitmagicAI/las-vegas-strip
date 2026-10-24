// Sets up build/ so a fresh clone runs (docs/ASSETS.md).
//
//   node tools/release/fetch-assets.mjs                 # copy runtime-assets/ (the Git LFS copy in the clone) into build/
//   node tools/release/fetch-assets.mjs --auto          # the same, quietly, never failing; `pnpm install` and the git
//                                                       # hooks it adds (post-merge, post-checkout) run this
//   node tools/release/fetch-assets.mjs --pack          # or download the pack named in tools/release/asset-pack.json
//   node tools/release/fetch-assets.mjs --from <file>   # or unpack a pack already on disk
//   node tools/release/fetch-assets.mjs --verify        # only check build/ against the list
//
// runtime-assets/ holds the same files as the pack (tools/release/asset-pack.py stage).
// The pack's sha256 is checked before unpacking, and every unpacked file against tools/release/asset-pack.json.
// Files already present with the right hash are left alone, so re-running after a new pack only rewrites what changed.
// Needs `tar` on PATH (macOS, Linux and Windows 10+ ship one).
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const list = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/release/asset-pack.json'), 'utf8'));
const args = process.argv.slice(2);
const arg = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; };
const MiB = (n) => (n / 1048576).toFixed(1) + ' MiB';

async function hashFile(file) {
  const h = createHash('sha256');
  await pipeline(fs.createReadStream(file), h);
  return h.digest('hex');
}

async function verify(report) {
  const bad = [];
  for (const f of list.files) {
    const p = path.join(ROOT, f.path);
    if (!fs.existsSync(p)) { bad.push(['missing', f.path]); continue; }
    if (fs.statSync(p).size !== f.bytes || await hashFile(p) !== f.sha256) bad.push(['differs', f.path]);
  }
  if (report) {
    for (const [why, p] of bad.slice(0, 30)) console.log(`${why.padEnd(8)} ${p}`);
    if (bad.length > 30) console.log(`... and ${bad.length - 30} more`);
    console.log(`${list.files.length - bad.length}/${list.files.length} runtime files present and current (pack ${list.revision})`);
  }
  return bad;
}

async function download(url, dest) {
  console.log(`downloading ${url}`);
  const res = await fetch(url, { redirect: 'follow' });
  if (!res.ok || !res.body) throw new Error(`download failed: HTTP ${res.status} for ${url}`);
  const total = Number(res.headers.get('content-length')) || list.pack.bytes || 0;
  let got = 0, shown = 0;
  const body = Readable.fromWeb(res.body);
  body.on('data', (c) => {
    got += c.length;
    if (got - shown > 32 * 1048576) { shown = got; process.stdout.write(`\r  ${MiB(got)}${total ? ' of ' + MiB(total) : ''}   `); }
  });
  await pipeline(body, fs.createWriteStream(dest));
  process.stdout.write(`\r  ${MiB(got)} done${' '.repeat(20)}\n`);
}

// Copies the clone's runtime-assets/ (Git LFS) into build/, file by file: build/ stays an ignored working folder that
// builders may write into, and the tracked copy only changes through `asset-pack.py stage`. Only what differs from the
// list is copied, so re-running after `git pull` is quick; on APFS/btrfs the copies are clones (no extra space).
// build/.runtime-sync.json remembers what was copied, so a file the contributor rebuilt since (and has not staged yet)
// is kept, never overwritten. Returns false when the checkout has no runtime-assets/.
const AUTO = args.includes('--auto');
const say = (msg) => console.log(AUTO ? `[assets] ${msg}` : msg);
async function sync() {
  const runtime = path.join(ROOT, 'runtime-assets');
  if (!fs.existsSync(runtime)) return false;
  const glb = list.files.find((f) => f.path.endsWith('.glb'));
  const probe = glb && path.join(runtime, glb.path.slice('build/'.length));
  if (probe && fs.existsSync(probe) && fs.readFileSync(probe).subarray(0, 40).toString().startsWith('version https://git-lfs')) {
    // (a ZIP download from GitHub carries pointers too: the repository leaves LFS objects out of its archives)
    console.error('runtime-assets/ holds Git LFS pointers, not the files. In a git clone, install Git LFS, then run\n' +
      '  git lfs install && git lfs pull\nand run this again. From a ZIP download, run\n' +
      '  node tools/release/fetch-assets.mjs --pack\nto download the same files as one release archive.');
    if (AUTO) return true;
    process.exit(2);
  }
  const stateFile = path.join(ROOT, 'build/.runtime-sync.json');
  let state = {};
  try { state = JSON.parse(fs.readFileSync(stateFile, 'utf8')); } catch { /* first run */ }
  let copied = 0, current = 0;
  const kept = [], missing = [];
  for (const f of list.files) {
    const src = path.join(runtime, f.path.slice('build/'.length)), dst = path.join(ROOT, f.path);
    if (!fs.existsSync(src)) { missing.push(f.path); continue; }
    if (fs.existsSync(dst)) {
      const digest = await hashFile(dst);
      if (digest === f.sha256) { state[f.path] = f.sha256; current++; continue; }
      // changed here since the last copy: the contributor's own build, not a stale copy
      if (state[f.path] && state[f.path] !== digest) { kept.push(f.path); continue; }
    }
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.rmSync(dst, { force: true });
    fs.copyFileSync(src, dst, fs.constants.COPYFILE_FICLONE);
    state[f.path] = f.sha256;
    copied++;
  }
  fs.mkdirSync(path.dirname(stateFile), { recursive: true });
  fs.writeFileSync(stateFile, JSON.stringify(state));
  if (copied || kept.length || missing.length || !AUTO) say(`build/: ${copied} copied from runtime-assets/, ${current} already current` +
    (kept.length ? `, ${kept.length} kept (your rebuilds: ${kept.slice(0, 3).join(', ')}${kept.length > 3 ? ', ...' : ''}; \`pnpm assets\` stages them)` : '') +
    (missing.length ? `, ${missing.length} missing from runtime-assets/ (run \`git lfs pull\`)` : ''));
  if (!AUTO) console.log(missing.length ? 'Some runtime files are missing.' : 'Ready: run `bitmagic dev`.');
  if (missing.length && !AUTO) process.exit(1);
  return true;
}

// After `git pull` or a checkout, refresh build/ by itself: post-merge and post-checkout hooks that run this tool with
// --auto. Appended to any existing hook (Git LFS installs its own there), never replacing it.
function installHooks() {
  const res = spawnSync('git', ['rev-parse', '--git-path', 'hooks'], { cwd: ROOT, encoding: 'utf8' });
  if (res.status !== 0) return;
  const dir = path.resolve(ROOT, res.stdout.trim()), line = 'node tools/release/fetch-assets.mjs --auto || true';
  fs.mkdirSync(dir, { recursive: true });
  for (const name of ['post-merge', 'post-checkout']) {
    const file = path.join(dir, name);
    const text = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '#!/bin/sh\n';
    if (text.includes('fetch-assets.mjs')) continue;
    fs.writeFileSync(file, text.replace(/\n*$/, '\n') + '# runtime assets: copy what `git pull` changed into build/ (tools/release/fetch-assets.mjs)\n' + line + '\n');
    fs.chmodSync(file, 0o755);
  }
}

async function main() {
  if (args.includes('--verify')) process.exit((await verify(true)).length ? 1 : 0);
  // A full working checkout keeps the ORIGINAL GLBs in build/ (the Blender pipelines patch them byte by byte) and
  // their optimized copies in build/optimized/. runtime-assets/ and the pack store optimized bytes at the original
  // paths, so copying them there would replace sources with meshopt copies the pipelines cannot read.
  if (fs.existsSync(path.join(ROOT, 'build/optimized/manifest.json')) && !args.includes('--force')) {
    if (AUTO) return; // a full working checkout: build/ is the maintainer's own
    console.error('build/optimized/manifest.json exists: this is a full working checkout, and copying would overwrite\n' +
      'its original GLBs with optimized copies. Use --verify to compare, or --force if you really mean it.');
    process.exit(2);
  }
  if (!args.includes('--pack') && !arg('--from') && await sync()) { if (AUTO) installHooks(); return; }
  if (AUTO) { say('no runtime-assets/ here: run `node tools/release/fetch-assets.mjs --pack` to download the runtime files'); return; }
  const pending = await verify(false);
  if (!pending.length) { console.log(`build/ already has all ${list.files.length} runtime files (pack ${list.revision}).`); return; }
  console.log(`${pending.length} of ${list.files.length} runtime files missing or out of date.`);

  let pack = arg('--from');
  if (!pack) {
    if (!list.pack.url) {
      console.error('No download URL yet: tools/release/asset-pack.json has an empty pack.url.\n' +
        'Ask a maintainer for the pack, or make it from a full checkout with `python3 tools/release/asset-pack.py build`,\n' +
        'then run: node tools/release/fetch-assets.mjs --from <las-vegas-strip-assets-*.tar.gz>');
      process.exit(2);
    }
    const dir = path.join(ROOT, '.bitmagic/release');
    fs.mkdirSync(dir, { recursive: true });
    pack = path.join(dir, list.pack.name);
    if (!fs.existsSync(pack) || (list.pack.sha256 && await hashFile(pack) !== list.pack.sha256)) await download(list.pack.url, pack);
  }
  if (list.pack.sha256 && path.basename(pack) === list.pack.name) {
    const digest = await hashFile(pack);
    if (digest !== list.pack.sha256) throw new Error(`${pack}: sha256 ${digest} does not match the list (${list.pack.sha256}); delete it and retry`);
  }
  console.log(`unpacking ${path.relative(ROOT, pack) || pack} into build/`);
  const tar = spawnSync('tar', ['-xzf', path.resolve(pack), '-C', ROOT], { stdio: 'inherit' });
  if (tar.status !== 0) throw new Error('tar failed to unpack the asset pack');
  const bad = await verify(true);
  if (bad.length) { console.error('Some files do not match the list: the pack is older or newer than this checkout.'); process.exit(1); }
  console.log('Ready: run `bitmagic dev`.');
}

main().catch((e) => { console.error(e.message); process.exit(1); });
