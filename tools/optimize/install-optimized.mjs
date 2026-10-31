#!/usr/bin/env node
/*
 * install-optimized.mjs: makes the optimizing-assets candidates (from optimize-runtime-glbs.mjs, in
 * .bitmagic/optimize/<rel minus .glb>/out.glb) the copies the game loads, without touching the originals.
 *
 *   node tools/optimize/install-optimized.mjs [--variant=level|webp-textures] [--only=text,...] [--exclude=text,...] [--dry-run] [--remove]
 *
 * --variant=webp-textures installs out-webp-textures.glb (colour/emissive maps as lossy WebP q90, ORM
 * lossless, normal maps kept) where it exists and passed, else the `level` candidate. Default:
 * webp-textures (owner approved 2026-10-07); --variant=level restores lossless textures. Characters are
 * always skipped: they load from registered remote URLs, so a local copy would never be used.
 *
 * For each runtime GLB in tools/optimize/runtime-glbs.json whose candidate passed (exitCode 0) and was
 * made from the file now on disk (sha256 in source.sha256 equals the current source), copies out.glb to
 * build/optimized/<served path> and records the source's size and modification time in
 * build/optimized/manifest.json. src/work/OptimizedGlb.ts serves the copy only while the source still has
 * that size and time, so a regenerated source always wins. --remove deletes matching installs.
 * --no-stage installs local comparison candidates without staging a release snapshot.
 * Originals stay in place: Blender and the resort pipelines read and patch them byte by byte.
 */
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const ROOT=process.cwd();
if(!fs.existsSync(path.join(ROOT,'src/work/world.json'))){console.error('run from the project root');process.exit(2);}
const arg=n=>{const a=process.argv.find(x=>x===`--${n}`||x.startsWith(`--${n}=`));return a===undefined?undefined:a.includes('=')?a.slice(a.indexOf('=')+1):true;};
const variant=String(arg('variant')??'webp-textures'),only=String(arg('only')??'').split(',').filter(Boolean),exclude=String(arg('exclude')??'').split(',').filter(Boolean),dry=!!arg('dry-run'),remove=!!arg('remove');
const OUT=path.join(ROOT,'build/optimized'),MANIFEST=path.join(OUT,'manifest.json');
const list=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/optimize/runtime-glbs.json'),'utf8')).files;
const manifest=fs.existsSync(MANIFEST)?JSON.parse(fs.readFileSync(MANIFEST,'utf8')):{files:{}};
const served=rel=>rel.startsWith('public/')?rel.slice('public/'.length):rel;
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
let installed=0,skipped=0,removed=0,before=0,after=0;
for(const entry of list){
  const rel=entry.rel;if(rel.includes('/characters/'))continue;if(only.length&&!only.some(t=>rel.includes(t)))continue;if(exclude.some(t=>rel.includes(t)))continue;
  const key=served(rel),target=path.join(OUT,key);
  if(remove){if(manifest.files[key]){delete manifest.files[key];if(!dry&&fs.existsSync(target))fs.unlinkSync(target);removed++;}continue;}
  const dir=path.join(ROOT,'.bitmagic/optimize',rel.replace(/\.glb$/,''));
  const webp=variant==='webp-textures'&&fs.existsSync(path.join(dir,'out-webp-textures.glb'))&&fs.existsSync(path.join(dir,'report-webp-textures.json'))&&JSON.parse(fs.readFileSync(path.join(dir,'report-webp-textures.json'),'utf8')).exitCode===0;
  const candidate=path.join(dir,webp?'out-webp-textures.glb':'out.glb'),reportFile=path.join(dir,webp?'report-webp-textures.json':'report.json'),source=path.join(ROOT,rel);
  const why=!fs.existsSync(candidate)?'no candidate':!fs.existsSync(reportFile)?'no report':JSON.parse(fs.readFileSync(reportFile,'utf8')).exitCode!==0?'encoder exit != 0 (do not ship)':!fs.existsSync(source)?'source missing':null;
  if(why){skipped++;console.log('skip',rel,'-',why);continue;}
  const recorded=fs.readFileSync(path.join(dir,'source.sha256'),'utf8').trim().split(/\s+/)[0];
  if(recorded!==sha(source)){skipped++;console.log('skip',rel,'- source changed since it was optimized; re-run optimize-runtime-glbs.mjs');continue;}
  const stat=fs.statSync(source),size=fs.statSync(candidate).size;
  if(size>=stat.size){skipped++;console.log('skip',rel,'- candidate is not smaller');continue;}
  before+=stat.size;after+=size;installed++;
  if(!dry){fs.mkdirSync(path.dirname(target),{recursive:true});fs.copyFileSync(candidate,target);}
  manifest.files[key]={size:stat.size,modified:stat.mtimeMs,optimized:path.relative(ROOT,target).split(path.sep).join('/'),sourceSha256:recorded,bytes:size,preset:entry.preset,overrides:entry.overrides??[],variant:webp?'webp-textures':'level'};
}
manifest.generated=new Date().toISOString();
if(!dry){fs.mkdirSync(OUT,{recursive:true});fs.writeFileSync(MANIFEST,JSON.stringify(manifest,null,1));}
const MB=n=>(n/1048576).toFixed(1);
console.log(remove?`removed ${removed}`:`installed ${installed} [${variant}] (${MB(before)} -> ${MB(after)} MB), skipped ${skipped}${dry?' (dry run)':''}; manifest has ${Object.keys(manifest.files).length} entries`);
// The repository's runtime set (runtime-assets/, Git LFS) follows every install, ready to commit (docs/ASSETS.md).
if(!dry&&!arg('no-stage')&&(installed||removed)){const r=spawnSync('python3',['tools/release/asset-pack.py','stage'],{cwd:ROOT,stdio:'inherit'});if(r.status!==0)console.warn('runtime-assets/ not staged: run `pnpm assets`');}
