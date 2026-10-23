// The installed Bitmagic CLI, found on this machine: the probes and recorders borrow its Chrome launcher and its
// playwright-core instead of installing their own. Set BITMAGIC_CLI_ROOT to the package folder to override the search
// (the folder holding @bitmagic/cli's package.json).
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

function isCliRoot(dir) {
  try { return JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8')).name === '@bitmagic/cli'; } catch { return false; }
}

function findCliRoot() {
  const tried = [];
  const env = process.env.BITMAGIC_CLI_ROOT;
  if (env) { if (isCliRoot(env)) return env; tried.push(env); }
  // the node running this script usually has the CLI installed next to it (nvm, Homebrew, system node)
  const nextToNode = path.join(path.dirname(path.dirname(process.execPath)), 'lib/node_modules/@bitmagic/cli');
  if (isCliRoot(nextToNode)) return nextToNode;
  tried.push(nextToNode);
  // otherwise follow the `bitmagic` on PATH back to its package
  try {
    const bin = execFileSync(process.platform === 'win32' ? 'where' : 'which', ['bitmagic'], { encoding: 'utf8' }).split(/\r?\n/)[0].trim();
    let dir = path.dirname(fs.realpathSync(bin));
    for (let i = 0; i < 6; i++, dir = path.dirname(dir)) if (isCliRoot(dir)) return dir;
    tried.push(bin);
  } catch { /* not on PATH */ }
  try {
    const root = path.join(execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim(), '@bitmagic/cli');
    if (isCliRoot(root)) return root;
    tried.push(root);
  } catch { /* npm missing */ }
  throw new Error(`The Bitmagic CLI was not found (tried ${tried.join(', ') || 'nothing'}). Install it with \`npm i -g @bitmagic/cli\`, or set BITMAGIC_CLI_ROOT.`);
}

export const cliRoot = findCliRoot();
/** require() resolving from the CLI package: cliRequire('playwright-core'). */
export const cliRequire = createRequire(path.join(cliRoot, 'package.json'));
export const { chromium } = cliRequire('playwright-core');
const dist = (file) => import(pathToFileURL(path.join(cliRoot, 'dist', file)).href);
export const { launchSystemChrome } = await dist('chrome-launch.js');
export const { browserRendererArgs } = await dist('browser-gl.js');
