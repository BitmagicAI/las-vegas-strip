// Sets up build/ so a fresh clone runs (docs/ASSETS.md).
//
//   node tools/release/fetch-assets.mjs                 # copy runtime-assets/ (the Git LFS copy in the clone) into build/
//   node tools/release/fetch-assets.mjs --pack          # or download the pack named in tools/release/asset-pack.json
//   node tools/release/fetch-assets.mjs --from <file>   # or unpack a pack already on disk
//   node tools/release/fetch-assets.mjs --verify        # only check build/ against the list
//
// runtime-assets/ holds the same files as the pack (tools/release/asset-pack.py stage). Re-run after `git pull`.
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
// builders may write into, and the tracked copy only changes through `asset-pack.py stage`. Files that already match
// are skipped, so re-running after `git pull` copies only what changed; on APFS/btrfs the copies are clones (no extra
// space). Returns false when the clone has no runtime-assets/.
async function sync() {
  const runtime = path.join(ROOT, 'runtime-assets');
  if (!fs.existsSync(runtime)) return false;
  const glb = list.files.find((f) => f.path.endsWith('.glb'));
  const probe = glb && path.join(runtime, glb.path.slice('build/'.length));
  if (probe && fs.existsSync(probe) && fs.readFileSync(probe).subarray(0, 40).toString().startsWith('version https://git-lfs')) {
    console.error('runtime-assets/ holds Git LFS pointers, not the files: install Git LFS, then run\n' +
      '  git lfs install && git lfs pull\nand run this again.');
    process.exit(2);
  }
  const pending = await verify(false);
  if (!pending.length) { console.log(`build/ already has all ${list.files.length} runtime files (${list.revision}).`); return true; }
  let copied = 0;
  for (const [, rel] of pending) {
    const src = path.join(runtime, rel.slice('build/'.length)), dst = path.join(ROOT, rel);
    if (!fs.existsSync(src)) continue;
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.rmSync(dst, { force: true });
    fs.copyFileSync(src, dst, fs.constants.COPYFILE_FICLONE);
    copied++;
  }
  console.log(`copied ${copied} of ${list.files.length} runtime files from runtime-assets/ into build/`);
  const bad = await verify(true);
  if (bad.length) { console.error('Some files do not match the list: run `git lfs pull`, or check `git status` for local edits.'); process.exit(1); }
  console.log('Ready: run `bitmagic dev`.');
  return true;
}

async function main() {
  if (args.includes('--verify')) process.exit((await verify(true)).length ? 1 : 0);
  // A full working checkout keeps the ORIGINAL GLBs in build/ (the Blender pipelines patch them byte by byte) and
  // their optimized copies in build/optimized/. runtime-assets/ and the pack store optimized bytes at the original
  // paths, so copying them there would replace sources with meshopt copies the pipelines cannot read.
  if (fs.existsSync(path.join(ROOT, 'build/optimized/manifest.json')) && !args.includes('--force')) {
    console.error('build/optimized/manifest.json exists: this is a full working checkout, and copying would overwrite\n' +
      'its original GLBs with optimized copies. Use --verify to compare, or --force if you really mean it.');
    process.exit(2);
  }
  if (!args.includes('--pack') && !arg('--from') && await sync()) return;
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
