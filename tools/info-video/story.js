// "How AI agents built Las Vegas": one deterministic animated story, story.render(t) draws story time t (capture.mjs steps t
// at 60 fps). Timing comes from timeline.json (narration lines + their speech segments); numbers from metrics.json.
// Footage: frames of the game's own recordings (.bitmagic/info-video/footage/<take>/fNNNNN.jpg). Map: OpenStreetMap +
// Clark County data (build/info-video/page/data/map.json), drawn and extruded here with three.js.
// ?refs=soft (default) shows third-party references small and softened; ?refs=sharp unsoftened; ?refs=off hides them.
import * as THREE from 'three';

const P = new URLSearchParams(location.search), DPR = +(P.get('dpr') || 1), REFS = P.get('refs') || 'soft';
const W = 1920, H = 1080, ROOT = '../../';
const C = {acc: '#ff8c3e', eye: '#40e2c8', red: '#ff5462', grn: '#60d68c', txt: '#f3efe8', muted: '#a0a6b4', gold: '#e8c46a'};
const J = async p => (await fetch(p)).json();

// ------------------------------------------------------------------ timing
const TL = await J('timeline.json');
const M = await J('metrics.json');
const LN = id => TL.lines.find(l => l.id === id);
const S = (id, k = 0) => { const s = LN(id).segs; return s[Math.min(k, s.length - 1)][0]; };
const E = (id, k = 0) => { const s = LN(id).segs; return s[Math.min(k, s.length - 1)][1]; };
const L0 = id => LN(id).start, L1 = id => LN(id).start + LN(id).dur;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lin = (t, a, b) => clamp((t - a) / (b - a));
const sm = (t, a, b) => { const x = lin(t, a, b); return x * x * (3 - 2 * x); };
const io = (t, a, b) => { const x = lin(t, a, b); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const out3 = (t, a, b) => 1 - Math.pow(1 - lin(t, a, b), 3);
const win = (t, a, b, fi = .35, fo = .35) => Math.min(sm(t, a, a + fi), 1 - sm(t, b - fo, b));
const pulse = (t, a, d = .35) => t < a ? 0 : Math.max(0, 1 - (t - a) / d);
const mix = (a, b, u) => a + (b - a) * u;
const fmt = n => Math.round(n).toLocaleString('en-US');

// scene windows: each scene runs from just before its line to just before the next scene
const SC = {};
const ORDER = TL.lines.map(l => l.id);
for (let i = 0; i < ORDER.length; i++) { const id = ORDER[i]; SC[id] = [i ? L0(id) - .45 : 0, i < ORDER.length - 1 ? L0(ORDER[i + 1]) - .45 : TL.total]; }
SC['01'][0] = 0;
const T = {
  coverOut: 3.0,
  roads0: L0('02') + .2, outl0: S('02', 1) + .4, n6800: S('02', 3), n20k: S('02', 4),
  noH: L0('03'), est: S('03', 1), raise: S('03', 2), lmk: S('03', 3), bel: S('03', 4), bel156: S('03', 5), eif: S('03', 6), eif165: S('03', 7),
  bm0: S('03', 2) + 2.6, reveal: L1('03') + .05,
  pave: L0('04'), walk: S('04', 1), med: S('04', 2), tiles: S('04', 3), cesium: S('04', 4), check: S('04', 5), looked: S('04', 6), never: S('04', 7),
  earth: L0('05'), outline: S('05', 1), colours: S('05', 2), roofs: S('05', 3), views: S('05', 4),
  photos: L0('06'), ent: S('06', 1), never2: S('06', 2), script: S('06', 3), wall: S('06', 4), windows: S('06', 5),
  compare: L0('07'), notright: S('07', 1), counted: S('07', 2), crown: S('07', 3), arched: S('07', 4), again: S('07', 5),
  plans: L0('08'), shops: S('08', 1), pool: S('08', 2), layout: S('08', 3), heights: S('08', 4), fit: S('08', 5), walkit: S('08', 6),
  rooms: L0('09'), carpet: S('09', 1), head: S('09', 2), chairs: S('09', 3), n49: S('09', 4), each: S('09', 5),
  towers: L0('10'), n64: S('10', 1), floors: S('10', 2), nrooms: S('10', 3), napts: S('10', 5), doors: S('10', 7),
  loop: L0('11'), survey: S('11', 1), build: S('11', 2), render: S('11', 3), cmp: S('11', 4), audits: S('11', 5), door: S('11', 6), flt: S('11', 7), flick: S('11', 8), back: S('11', 9),
  detail: L0('12'), night: S('12', 1), ven: S('12', 2), eiffel: S('12', 4), measured: S('12', 5), leg: S('12', 6),
  agents: L0('13'), codex: S('13', 1), days: S('13', 2), calls: S('13', 3), hours: S('13', 4), mac: S('13', 5),
  numbers: L0('14'), nb: S('14', 0), n604: S('14', 2), ntri: S('14', 4), nmat: S('14', 5), built: S('14', 7), billion: S('14', 8),
  weather: L0('14b'), wNight: S('14b', 3), wRain: S('14b', 4),
  end: L0('15'), browser: S('15', 1), smooth: S('15', 3), streams: S('15', 4), card: S('15', 6) - .2, total: TL.total,
};
const on = (id, t, fo = .45) => t >= SC[id][0] && t < SC[id][1] + fo;

// ------------------------------------------------------------------ data
const ST = await J(ROOT + 'build/info-video/page/data/stills.json');
const FOOT = await J(ROOT + 'build/info-video/page/data/footage.json');
const EFF = await J(ROOT + 'build/info-video/agent-effort.json');
const MAP = await J(ROOT + 'build/info-video/page/data/map.json');
const BM = await J(ROOT + 'tools/film/takes/info-boxmatch.json');
const still = n => ROOT + '.bitmagic/info-video/stills/' + n + '.jpg';
const frameURL = (take, time) => {
  const f = FOOT[take]; if (!f) return still('missing');
  const i = clamp(Math.round(time * f.fps), 0, f.frames - 1);
  return ROOT + f.dir + 'f' + String(i).padStart(5, '0') + '.jpg';
};

// ------------------------------------------------------------------ DOM layers
const hud = document.getElementById('hud'), footEl = document.getElementById('foot'), overEl = document.getElementById('over'), svg = document.getElementById('svg');
const glCanvas = document.getElementById('gl');
function el(cls, html = '', x = 0, y = 0, parent = hud) {
  const d = document.createElement('div'); d.className = 'abs ' + cls; d.innerHTML = html; d.style.left = x + 'px'; d.style.top = y + 'px';
  d.style.opacity = 0; d.style.display = 'none'; parent.append(d); return d;
}
function show(e, o, dx = 0, dy = 0, s = 1, extra = '') {
  if (o <= .001) { if (e.style.display !== 'none') e.style.display = 'none'; return; }
  e.style.display = ''; e.style.opacity = o.toFixed(3); e.style.transform = `translate(${dx.toFixed(1)}px,${dy.toFixed(1)}px) scale(${s.toFixed(4)}) ${extra}`;
}
const NS = 'http://www.w3.org/2000/svg';
function sv(tag, attrs) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); svg.append(e); return e; }

// image slots (footage frames and stills): created on first use, hidden when a frame does not use them
const slots = new Map(); let used = new Set(); const pending = [];
function shot(key, url, r, o = 1, z = 1, opt = {}) {
  let s = slots.get(key);
  if (!s) {
    const box = document.createElement('div'); box.className = 'shot'; const img = new Image(); img.decoding = 'sync'; box.append(img); (opt.over ? overEl : footEl).append(box);
    s = {box, img, url: ''}; slots.set(key, s);
  }
  used.add(key);
  if (o <= .001) { s.box.style.display = 'none'; return s; }
  if (s.url !== url) { s.url = url; s.img.src = url; pending.push(s.img.decode().catch(() => {})); }
  const b = s.box.style; b.display = ''; b.opacity = o.toFixed(3); b.zIndex = z;
  b.left = r.x + 'px'; b.top = r.y + 'px'; b.width = r.w + 'px'; b.height = r.h + 'px'; b.borderRadius = (r.r ?? 0) + 'px';
  b.boxShadow = r.r ? '0 30px 90px rgba(0,0,0,.55)' : 'none'; b.outline = r.r ? '2px solid rgba(255,255,255,.08)' : 'none';
  const zoom = opt.zoom ?? 1, ox = opt.ox ?? 0, oy = opt.oy ?? 0;
  s.img.style.transform = `translate(${ox}%,${oy}%) scale(${zoom})`; s.img.style.transformOrigin = opt.origin ?? '50% 50%';
  s.img.style.objectFit = opt.fit ?? 'cover';
  s.img.style.filter = opt.filter ?? 'none';
  return s;
}
const FULL = {x: 0, y: 0, w: W, h: H};
const third = (o = 1) => REFS === 'off' ? 0 : o;
const thirdFilter = (extra = '') => (REFS === 'soft' ? 'blur(1.2px) saturate(.85) ' : '') + extra;

// ------------------------------------------------------------------ persistent HUD pieces
const kicker = el('kicker', '', 72, 56);
const brand = el('brand', 'BITMAGIC · LAS VEGAS STRIP', 0, 0); brand.style.left = 'auto'; brand.style.top = 'auto';
const dimAll = el('fill', '', 0, 0); dimAll.style.background = 'rgba(10,12,17,.62)';
const vignette = el('fill', '', 0, 0); vignette.style.background = 'radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 55%, rgba(0,0,0,.45) 100%)';
const shade = el('fill', '', 0, 0); shade.style.background = 'linear-gradient(90deg, rgba(10,12,17,.86) 0%, rgba(10,12,17,.55) 36%, rgba(10,12,17,0) 62%)';
const shadeB = el('fill', '', 0, 0); shadeB.style.background = 'linear-gradient(0deg, rgba(10,12,17,.82) 0%, rgba(10,12,17,0) 42%)';
// 14b: the look's name and a note that nothing was remodelled
const weatherTags = [el('chip', '', 72, 900), el('chip', '', 72, 900)];
const sameData = el('cap', 'SAME MODELS · SAME DATA · A LIGHTING AND WEATHER PRESET', 76, 980);
// 15: what the engine does with all that detail (60 fps: docs/project-records/interior- and idle-performance-2026-10-07)
const engineTags = ['RUNS IN A WEB BROWSER · WEBGPU', '60 FPS · MEASURED IN CHROME', 'EACH BUILDING AND ROOM STREAMS IN AS YOU APPROACH'].map((txt, i) => el('chip', txt, 72, 760 + i * 84));
// big counter (bottom-left) and caption, as in the character video
const bigN = el('big', '', 72, 812), bigC = el('cap', '', 76, 930);
const bigN2 = el('big', '', 72, 812), bigC2 = el('cap', '', 76, 930);
function counter(t, n0, n1, t0, t1, cap, slot = 0, x = 72, y = 812, o = 1, suffix = '') {
  const N = slot ? bigN2 : bigN, Cc = slot ? bigC2 : bigC;
  const v = mix(n0, n1, out3(t, t0, t1));
  N.textContent = (typeof n1 === 'number' ? fmt(v) : n1) + suffix; Cc.textContent = cap;
  N.style.left = x + 'px'; N.style.top = y + 'px'; Cc.style.left = (x + 4) + 'px'; Cc.style.top = (y + 118) + 'px';
  const a = o * sm(t, t0 - .25, t0 + .1);
  show(N, a, 0, (1 - sm(t, t0 - .25, t0 + .2)) * 16, 1 + pulse(t, t1, .3) * .04); show(Cc, a);
}

// ------------------------------------------------------------------ three.js: the OSM map and its boxes
const renderer = new THREE.WebGLRenderer({canvas: glCanvas, antialias: true, alpha: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(DPR); renderer.setSize(W, H, false); glCanvas.style.width = W + 'px'; glCanvas.style.height = H + 'px';
renderer.setClearColor(0x12151d, 1);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, W / H, 5, 40000);

const uniforms = {uRoads: {value: 0}, uOutl: {value: 0}, uGrow: {value: 0}, uTagged: {value: 0}, uBoxA: {value: 1}, uFlat: {value: 0},
  uPave: {value: 0}, uWalk: {value: 0}, uMed: {value: 0}, uStrip: {value: 0}, uDim: {value: 1}, uFootA: {value: 1}};
const VS_FLAT = `attribute float aOrd; attribute vec3 aCol; varying float vOrd; varying vec3 vCol;
  void main(){ vOrd=aOrd; vCol=aCol; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`;
function flatMat(reveal, alpha, extra = '') {
  return new THREE.ShaderMaterial({uniforms, transparent: true, depthWrite: false, side: THREE.DoubleSide, vertexShader: VS_FLAT,
    fragmentShader: `uniform float ${reveal}; uniform float uDim; uniform float uFlat; uniform float uFootA; varying float vOrd; varying vec3 vCol;
      void main(){ float a=smoothstep(vOrd, vOrd+.04, ${reveal}*1.04); if(a<.004) discard; ${extra} gl_FragColor=vec4(vCol*uDim, a*${alpha}); }`});
}
function rank(values) { const idx = values.map((v, i) => i).sort((a, b) => values[a] - values[b]); const r = new Float32Array(values.length); idx.forEach((v, i) => r[v] = i / Math.max(1, values.length - 1)); return r; }
const hex = h => new THREE.Color(h);

// roads as ribbons with their real widths
{
  const pos = [], ord = [], col = [];
  const cent = MAP.roads.map(r => { const p = r[2]; let x = 0, z = 0; for (let i = 0; i < p.length; i += 2) { x += p[i]; z += p[i + 1]; } const n = p.length / 2; return Math.hypot(x / n - 60, (z / n - 200) * .55); });
  const rk = rank(cent);
  const cls = h => /motorway|trunk|primary/.test(h) ? hex('#8f9ab4') : /secondary|tertiary/.test(h) ? hex('#6d7892') : /footway|path|pedestrian|steps|cycleway/.test(h) ? hex('#3b4357') : hex('#525b72');
  MAP.roads.forEach((r, i) => {
    const p = r[2], w = Math.max(2.5, r[1]) / 2, c = cls(r[0]);
    for (let k = 0; k + 3 < p.length; k += 2) {
      const ax = p[k], az = p[k + 1], bx = p[k + 2], bz = p[k + 3], dx = bx - ax, dz = bz - az, L = Math.hypot(dx, dz) || 1, nx = -dz / L * w, nz = dx / L * w;
      pos.push(ax + nx, .3, az + nz, bx + nx, .3, bz + nz, bx - nx, .3, bz - nz, ax + nx, .3, az + nz, bx - nx, .3, bz - nz, ax - nx, .3, az - nz);
      for (let v = 0; v < 6; v++) { ord.push(rk[i] * .92); col.push(c.r, c.g, c.b); }
    }
  });
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aOrd', new THREE.Float32BufferAttribute(ord, 1)); g.setAttribute('aCol', new THREE.Float32BufferAttribute(col, 3));
  const m = new THREE.Mesh(g, flatMat('uRoads', '1.')); m.renderOrder = 1; m.frustumCulled = false; scene.add(m);
}
// the Strip route, drawn along its length
{
  const p = MAP.strip, pos = [], ord = [], col = []; let L = 0; const acc = [0];
  for (let k = 2; k < p.length; k += 2) { L += Math.hypot(p[k] - p[k - 2], p[k + 1] - p[k - 1]); acc.push(L); }
  const c = hex(C.acc), w = 14;
  for (let k = 0, j = 0; k + 3 < p.length; k += 2, j++) {
    const ax = p[k], az = p[k + 1], bx = p[k + 2], bz = p[k + 3], dx = bx - ax, dz = bz - az, l = Math.hypot(dx, dz) || 1, nx = -dz / l * w, nz = dx / l * w;
    pos.push(ax + nx, .6, az + nz, bx + nx, .6, bz + nz, bx - nx, .6, bz - nz, ax + nx, .6, az + nz, bx - nx, .6, bz - nz, ax - nx, .6, az - nz);
    const o0 = acc[j] / L, o1 = acc[j + 1] / L; for (const o of [o0, o1, o1, o0, o1, o0]) { ord.push(o); col.push(c.r, c.g, c.b); }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aOrd', new THREE.Float32BufferAttribute(ord, 1)); g.setAttribute('aCol', new THREE.Float32BufferAttribute(col, 3));
  const m = new THREE.Mesh(g, flatMat('uStrip', '.95')); m.renderOrder = 4; m.frustumCulled = false; scene.add(m);
}
// county layers: pavement fills, sidewalk/curb lines and medians (TYPE 10)
{
  const pos = [], ord = [], col = []; const c = hex('#56627f');
  MAP.pavement.forEach((ring, i) => {
    const pts = []; for (let k = 0; k + 1 < ring.length; k += 2) pts.push(new THREE.Vector2(ring[k], ring[k + 1]));
    if (pts.length < 3) return; let tris; try { tris = THREE.ShapeUtils.triangulateShape(pts, []); } catch { return; }
    const o = (i * 7919 % 791) / 791;
    for (const t of tris) for (const v of t) { pos.push(pts[v].x, .15, pts[v].y); ord.push(o * .9); col.push(c.r, c.g, c.b); }
  });
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aOrd', new THREE.Float32BufferAttribute(ord, 1)); g.setAttribute('aCol', new THREE.Float32BufferAttribute(col, 3));
  const m = new THREE.Mesh(g, flatMat('uPave', '.95')); m.renderOrder = 0; m.frustumCulled = false; scene.add(m);
}
for (const [kind, rev, colr] of [['walk', 'uWalk', '#c9cfdb'], ['med', 'uMed', '#60d68c']]) {
  const pos = [], ord = [], col = []; const c = hex(colr), w = kind === 'med' ? 1.6 : 1.1;
  MAP.concrete.forEach(([type, p], i) => {
    if ((type === 10) !== (kind === 'med')) return;
    const o = (i * 104729 % 3555) / 3555;
    for (let k = 0; k + 3 < p.length; k += 2) {
      const ax = p[k], az = p[k + 1], bx = p[k + 2], bz = p[k + 3], dx = bx - ax, dz = bz - az, l = Math.hypot(dx, dz) || 1, nx = -dz / l * w, nz = dx / l * w;
      pos.push(ax + nx, .5, az + nz, bx + nx, .5, bz + nz, bx - nx, .5, bz - nz, ax + nx, .5, az + nz, bx - nx, .5, bz - nz, ax - nx, .5, az - nz);
      for (let v = 0; v < 6; v++) { ord.push(o * .9); col.push(c.r, c.g, c.b); }
    }
  });
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('aOrd', new THREE.Float32BufferAttribute(ord, 1)); g.setAttribute('aCol', new THREE.Float32BufferAttribute(col, 3));
  const m = new THREE.Mesh(g, flatMat(rev, '.95')); m.renderOrder = 3; m.frustumCulled = false; scene.add(m);
}
// footprints (flat outlines) and extruded boxes
const LANDMARK = {bellagio: -1, eiffel: -1}, BOXES = {mesh: null};
{
  const fpos = [], ford = [], fcol = [];
  const bpos = [], bnor = [], bh = [], bbase = [], bord = [], btag = [], bid = [];
  const cent = MAP.buildings.map(b => { const p = b[3]; let x = 0, z = 0; for (let i = 0; i < p.length; i += 2) { x += p[i]; z += p[i + 1]; } const n = p.length / 2; return Math.hypot(x / n - 60, (z / n - 200) * .55); });
  const rk = rank(cent);
  const ct = hex(C.eye), cu = hex('#7d8aa5');
  MAP.buildings.forEach((b, i) => {
    const [base, h, tagged, ring] = b; const pts = [];
    for (let k = 0; k + 1 < ring.length; k += 2) pts.push(new THREE.Vector2(ring[k], ring[k + 1]));
    if (pts.length > 3 && pts[0].distanceTo(pts[pts.length - 1]) < .01) pts.pop();
    if (pts.length < 3) return; let tris; try { tris = THREE.ShapeUtils.triangulateShape(pts, []); } catch { return; }
    let cx = 0, cz = 0; for (const p of pts) { cx += p.x; cz += p.y; } cx /= pts.length; cz /= pts.length;
    if (Math.hypot(cx + 311, cz - 321) < 30 && h > 100) LANDMARK.bellagio = i;
    if (Math.hypot(cx - 74.5, cz - 400.5) < 25 && h > 150) LANDMARK.eiffel = i;
    for (const t of tris) for (const v of t) { fpos.push(pts[v].x, .2, pts[v].y); ford.push(rk[i] * .95); fcol.push(tagged, 0, 0); }
    const push = (x, y, z, nx, ny, nz) => { bpos.push(x, y, z); bnor.push(nx, ny, nz); bh.push(h); bbase.push(base); bord.push(rk[i]); btag.push(tagged); bid.push(i); };
    for (const t of tris) for (const v of [...t].reverse()) push(pts[v].x, 1, pts[v].y, 0, 1, 0);
    // walls: winding-independent outward normals
    let area = 0; for (let k = 0; k < pts.length; k++) { const a = pts[k], q = pts[(k + 1) % pts.length]; area += a.x * q.y - q.x * a.y; }
    const sgn = area > 0 ? 1 : -1;
    for (let k = 0; k < pts.length; k++) {
      const a = pts[k], q = pts[(k + 1) % pts.length], dx = q.x - a.x, dz = q.y - a.y, L = Math.hypot(dx, dz) || 1, nx = dz / L * sgn, nz = -dx / L * sgn;
      push(a.x, 0, a.y, nx, 0, nz); push(q.x, 0, q.y, nx, 0, nz); push(q.x, 1, q.y, nx, 0, nz);
      push(a.x, 0, a.y, nx, 0, nz); push(q.x, 1, q.y, nx, 0, nz); push(a.x, 1, a.y, nx, 0, nz);
    }
  });
  const fg = new THREE.BufferGeometry(); fg.setAttribute('position', new THREE.Float32BufferAttribute(fpos, 3)); fg.setAttribute('aOrd', new THREE.Float32BufferAttribute(ford, 1)); fg.setAttribute('aCol', new THREE.Float32BufferAttribute(fcol, 3));
  const fm = new THREE.Mesh(fg, new THREE.ShaderMaterial({uniforms, transparent: true, depthWrite: false, side: THREE.DoubleSide, vertexShader: VS_FLAT,
    fragmentShader: `uniform float uOutl; uniform float uFlat; uniform float uFootA; uniform float uTagged; varying float vOrd; varying vec3 vCol;
      void main(){ float a=smoothstep(vOrd, vOrd+.04, uOutl*1.04); if(a<.004 || uFlat<.001) discard;
        vec3 c=mix(vec3(.70,.75,.85), vec3(.25,.89,.78), uTagged*vCol.x);
        gl_FragColor=vec4(c, a*.78*uFootA*mix(1., .55, uTagged*(1.-vCol.x))); }`})); fm.renderOrder = 2; fm.frustumCulled = false; scene.add(fm);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(bpos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(bnor, 3));
  g.setAttribute('aH', new THREE.Float32BufferAttribute(bh, 1)); g.setAttribute('aBase', new THREE.Float32BufferAttribute(bbase, 1));
  g.setAttribute('aOrd', new THREE.Float32BufferAttribute(bord, 1)); g.setAttribute('aTag', new THREE.Float32BufferAttribute(btag, 1)); g.setAttribute('aId', new THREE.Float32BufferAttribute(bid, 1));
  uniforms.uBel = {value: 120}; uniforms.uEif = {value: 165}; uniforms.uBelId = {value: LANDMARK.bellagio}; uniforms.uEifId = {value: LANDMARK.eiffel}; uniforms.uHi = {value: 0}; uniforms.uHiId = {value: -1};
  const mat = new THREE.ShaderMaterial({uniforms, transparent: true, side: THREE.DoubleSide,
    vertexShader: `attribute float aH; attribute float aBase; attribute float aOrd; attribute float aTag; attribute float aId;
      uniform float uGrow; uniform float uBel; uniform float uEif; uniform float uBelId; uniform float uEifId;
      varying vec3 vN; varying float vTag; varying float vY; varying float vLm; varying float vId;
      void main(){
        float g=clamp((uGrow*1.35-aOrd*.35),0.,1.); g=g*g*(3.-2.*g);
        float h=aH; vLm=0.; if(abs(aId-uBelId)<.5){h=uBel;vLm=1.;} if(abs(aId-uEifId)<.5){h=uEif;vLm=1.;}
        vec3 p=position; p.y=(aBase+p.y*h)*g+.25; vN=normal; vTag=aTag; vY=position.y; vId=aId;
        gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.); }`,
    fragmentShader: `uniform float uBoxA; uniform float uTagged; uniform float uDim; uniform float uHi; uniform float uHiId;
      varying vec3 vN; varying float vTag; varying float vY; varying float vLm; varying float vId;
      void main(){
        vec3 L=normalize(vec3(.45,.8,.35)); float d=.48+.52*max(dot(normalize(vN),L),0.);
        vec3 base=mix(vec3(.80,.83,.89), vec3(.55,.60,.70), uTagged*(1.-vTag));
        base=mix(base, vec3(.25,.89,.78), uTagged*vTag);
        base=mix(base, vec3(1.,.55,.24), vLm*uHi);
        vec3 c=base*d*(.86+.14*vY);
        gl_FragColor=vec4(c*uDim, uBoxA); }`});
  const boxes = new THREE.Mesh(g, mat); boxes.frustumCulled = false; boxes.renderOrder = 5; scene.add(boxes); BOXES.mesh = boxes;
}
// camera poses
const qLook = (pos, look, up = new THREE.Vector3(0, 1, 0)) => { const m = new THREE.Matrix4().lookAt(pos, look, up); return new THREE.Quaternion().setFromRotationMatrix(m); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const TOP = (cx, cz, h) => ({p: V(cx, h, cz + .01), q: qLook(V(cx, h, cz + .01), V(cx, 0, cz), V(-1, 0, 0)), fov: 40});
const bmKey = (u) => { const k0 = BM.camera[0].keys[0], k1 = BM.camera[0].keys[1], e = u * u * (3 - 2 * u);
  const p = V(...k0.pos).lerp(V(...k1.pos), e), l = V(...k0.look).lerp(V(...k1.look), e); return {p, q: qLook(p, l), fov: k0.fov ?? 45}; };
function pose(a, b, u) { const p = a.p.clone().lerp(b.p, u); p.y += Math.sin(u * Math.PI) * (b.arc ?? 0); return {p, q: a.q.clone().slerp(b.q, u), fov: mix(a.fov, b.fov, u)}; }
function applyPose(o) { camera.position.copy(o.p); camera.quaternion.copy(o.q); if (camera.fov !== o.fov) { camera.fov = o.fov; camera.updateProjectionMatrix(); } camera.updateMatrixWorld(); }
const project = (x, y, z) => { const v = V(x, y, z).project(camera); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H, v.z]; };

// ------------------------------------------------------------------ scene-specific HUD elements
const cover = el('', `<img src="${ROOT}tools/film/brand/bitmagic-logo-white.png" style="height:64px;display:block;margin-bottom:34px">
  <div class="mono" style="font:600 26px 'CF Mono',Menlo,monospace;letter-spacing:.24em;color:${C.acc};margin-bottom:22px">BEHIND THE SCENES</div>
  <div class="title">How AI agents<br>built Las Vegas</div>
  <div style="font:500 30px 'Avenir Next',Avenir,sans-serif;color:${C.muted};margin-top:30px;max-width:900px;line-height:1.35">Open map data, Google Earth, public photos and floor plans, turned into a city you can walk through, by agents that check their own work.</div>`, 96, 250);
const chips01 = ['MAPPED', 'MODELLED', 'CHECKED'].map((w, i) => el('chip', w, 96 + i * 236, 520));
const days01 = el('', `<div class="big">26 days</div><div class="cap" style="margin-top:6px">SEP 27 → OCT 22, 2026</div>`, 96, 300);
const osmAtt = el('att', '© OpenStreetMap contributors · Overpass extract 2026-10-03', 72, 1020);
const nLabel = el('cap', 'N →', 1780, 520);
const ruleChip = el('panel', `<div style="padding:26px 32px"><div class="small" style="color:${C.acc};margin-bottom:14px">HEIGHT, WHEN THE MAP HAS NONE</div>
  <div class="code">home       <b>4.5 m</b>\nshop       <b>6 m</b>\nother      <b>5 m</b>\n+ per floor <b>3 m</b></div></div>`, 1380, 150);
const lmBel = el('label', '', 0, 0), lmEif = el('label', '', 0, 0);
const countyAtt = el('att', 'Clark County GISMO pavement + concrete layers · © OpenStreetMap contributors', 72, 1020);
const layerPanel = el('panel', '', 72, 610); layerPanel.style.width = '760px'; layerPanel.style.height = '270px';
const layerChips = [['PAVEMENT', '#5b6a8a', '759 polygons'], ['SIDEWALKS + CURBS', '#c9cfdb', '1,850 lines'], ['MEDIANS', C.grn, '196 medians']]
  .map(([n, c, s], i) => el('', `<div style="display:flex;align-items:center;gap:16px"><span style="width:26px;height:26px;border-radius:6px;background:${c};display:inline-block"></span><span class="mid" style="font-size:44px">${n}</span><span class="cap" style="font-size:22px">${s}</span></div>`, 96, 640 + i * 78));
const cesiumTag = el('tag', 'GOOGLE PHOTOREALISTIC 3D TILES · VIEWED IN CESIUM', 0, 0); cesiumTag.style.background = 'rgba(18,21,29,.9)'; cesiumTag.style.color = C.txt;
const lookedStamp = el('stamp ok', 'LOOKED AT', 0, 0), neverStamp = el('stamp', 'NEVER COPIED', 0, 0);
const geAtt = el('att', 'Google Earth', 0, 0);
const swatches = [['CREAM', '#ecd9ae'], ['WHITE', '#f3f0e8'], ['PATINA', '#94c4c8']].map(([n, c], i) => el('', `<div style="display:flex;align-items:center;gap:16px"><span style="width:64px;height:64px;border-radius:14px;background:${c};display:inline-block;box-shadow:0 8px 24px rgba(0,0,0,.5)"></span><span class="cap" style="color:${C.txt}">${n}</span></div>`, 1560, 300 + i * 100));
const geLog = el('log', '', 1080, 640);
const GELOG = ['36.1126 N  115.1767 W   imagery 2022-11-09   Bellagio', '36.1215 N  115.1696 W   imagery 2023-04-17   Venetian', '36.1125 N  115.1707 W   imagery 2022-11-09   Paris',
  '36.0955 N  115.1761 W   imagery 2023-04-17   Luxor', '36.1291 N  115.1652 W   imagery 2023-04-17   Wynn', '36.1213 N  115.1615 W   imagery 2023-04-17   Sphere', '36.1022 N  115.1745 W   imagery 2022-11-09   New York-New York'];
const photoLab = el('tag', 'PUBLIC PHOTOS · RESEARCH ONLY · NEVER SHIPPED', 0, 0); photoLab.style.background = 'rgba(18,21,29,.9)'; photoLab.style.color = C.txt;
const entChips = ['ENTRANCES', 'FACADES', 'SIGNS'].map((w, i) => el('chip', w, 96 + i * 300, 860));
const neverPaste = el('stamp ok', 'NO PHOTO TEXTURES', 0, 0);
const CODE = [
  `<s># bellagio_towers.py · main tower, from the podium up</s>`,
  `crown = dict(lower=[(<b>.17</b>,<b>.68</b>), (<b>1.2</b>,<b>1.05</b>), (<b>2.5</b>,<b>1.05</b>)],`,
  `             squares=[(<b>13.27</b>,<b>.86</b>), (<b>14.47</b>,<b>.86</b>)],`,
  `             arches=[(<b>15.65</b>, <b>2.3</b>, 'body')], eave=<b>19.4</b>)`,
  `<u>for</u> wl <u>in</u> bays(t, union, bay=<b>9.6</b>):`,
  `    <u>for</u> k <u>in</u> range(<b>8</b>):   <s># eight square rows</s>`,
  `        wl.window(<b>0</b>, Y(<b>4.3</b> + k + <b>.13</b>), one, <b>.74</b> * U)`,
  `    <u>for</u> s <u>in</u> (-<b>1</b>, <b>1</b>):    <s># paired arched windows</s>`,
  `        wl.window(s * (two + gap) / <b>2</b>, Y(<b>15.65</b>), two, <b>2.3</b> * U, arch=<u>True</u>)`,
  `hip(t, out(body, <b>1.2</b>), eave, <b>32</b>)   <s># patina hip roof</s>`];
const codeBox = el('panel', `<div style="padding:30px 36px"><div class="small" style="color:${C.acc};margin-bottom:16px">BLENDER PYTHON · ONE OF 887 SCRIPTS</div><div class="code" id="codetxt"></div></div>`, 72, 190);
const codeTxt = codeBox.querySelector('#codetxt');
const dims = [['134 m', 'ROOF'], ['155.8 m', 'TIP'], ['9.6 m', 'BAY']].map(([a, b]) => el('label', `<span style="color:${C.acc}">${a}</span> <span class="small">${b}</span>`, 0, 0));
const notRec = el('stamp', 'NOT RECOGNIZABLE', 0, 0);
const segLabs = [['CROWN · ARCHES + 2 ROWS', C.txt], ['MIDDLE · 8 ROWS', C.gold], ['LOWER · 3 ROWS', C.gold]].map(([n, c]) => el('label', `<span style="color:${c}">${n}</span>`, 0, 0));
const callouts07 = ['WHITE CROWN', 'ARCHED WINDOWS', 'COPPER ROOFS'].map(w => el('label', w, 0, 0));
const matchOK = el('check', '<i>✓</i>Matches the reference', 0, 0);
const planLab = el('tag', 'OFFICIAL RESORT MAP · LEVEL 1', 0, 0); planLab.style.background = 'rgba(18,21,29,.9)'; planLab.style.color = C.txt;
const zoneLabs = [['CASINO', C.grn], ['SHOPS', '#5aa0ff'], ['LOBBY', C.acc], ['POOL', C.eye]].map(([n, c]) => el('label', `<span style="color:${c}">${n}</span>`, 0, 0));
const layoutChips = [el('check', '<i>✓</i>Layout + connections', 1400, 640), el('check', '<i class="no">✗</i>Heights', 1400, 716)];
const walkTag = el('tag', 'WALKED · ROUTE CHECKS PASS', 0, 0); walkTag.style.background = C.grn; walkTag.style.color = '#0c1a10';
const roomCallouts = [el('label', 'CARPET PATTERN', 0, 0), el('label', 'HEADBOARD', 0, 0), el('label', 'CHAIR COLOUR', 0, 0)];
const towerStack = el('', '', 96, 250);
const towerRows = [['64', 'TOWERS'], ['2,130', 'FLOORS'], ['30,692', 'HOTEL ROOMS'], ['5,806', 'APARTMENTS']].map(([n, c], i) => el('', `<div class="big" style="font-size:88px">${n}</div><div class="cap" style="margin-top:-4px">${c}</div>`, 96, 170 + i * 168));
const doorTag = el('tag', '36,498 DOORS THAT OPEN', 0, 0); doorTag.style.background = C.acc; doorTag.style.color = '#1a0f05';
const NODES = ['SURVEY', 'BUILD', 'RENDER', 'COMPARE', 'AUDIT', 'FIX'];
const nodeEls = NODES.map(n => el('node', n, 0, 0));
const loopCenter = el('', `<div class="mono" style="font:600 22px 'CF Mono',Menlo,monospace;letter-spacing:.2em;color:${C.muted};text-align:center">ONE BLOCK<br>AT A TIME</div>`, 0, 0);
const audits = [['Every door walkable', '9,889 route checks'], ['Nothing floating', 'roof + ground support'], ['No flickering surfaces', 'coplanar-face scan']]
  .map(([a, b], i) => el('', `<div class="check"><i>✓</i>${a}</div><div class="cap" style="margin:6px 0 0 64px;font-size:21px">${b}</div>`, 1240, 300 + i * 150));
const failTag = el('tag', 'FAILED → BACK TO SURVEY', 0, 0); failTag.style.background = C.red; failTag.style.color = '#1a0606';
const triTag = el('', '', 0, 0);
const rejStamp = el('stamp', 'REJECTED', 0, 0), rebuiltTag = el('tag', 'REMEASURED · 1,309,714 TRIANGLES', 0, 0); rebuiltTag.style.background = C.grn; rebuiltTag.style.color = '#0c1a10';
const agentTitle = el('', '', 96, 150);
const chartBox = el('panel', '', 96, 300); chartBox.style.width = '1180px'; chartBox.style.height = '560px';
// tokens and their API cost: both agents combined, never itemized (the owner, 2026-10-23); metrics.json has the parts
const agentStats = [['26', 'DAYS'], ['20,474', 'TOOL CALLS'], [(M.tokens.value / 1e9).toFixed(1) + ' BILLION', 'TOKENS'], ['212', 'AGENT-HOURS'],
  ['$' + (Math.round(M.apiCostUsd.value / 100) * 100).toLocaleString('en-US'), 'EST. AT API PRICES'], ['1', 'MAC']]
  .map(([n, c], i) => el('', `<div class="mid">${n}</div><div class="cap" style="font-size:22px">${c}</div>`, 1370, 262 + i * 118));
const numRows = el('', '', 0, 0);
const endCard = el('', `<img src="${ROOT}tools/film/brand/bitmagic-logo-white.png" style="height:120px;display:block;margin:0 auto 28px">
  <div style="font:500 36px 'Avenir Next',Avenir,sans-serif;color:${C.txt};text-align:center">Las Vegas · behind the scenes</div>
  <div class="mono" style="font:600 22px 'CF Mono',Menlo,monospace;letter-spacing:.2em;color:${C.muted};text-align:center;margin-top:18px">LAS VEGAS STRIP</div>`, 0, 0);
endCard.style.left = '0'; endCard.style.width = W + 'px'; endCard.style.top = '340px';
// the open-source announcement under the title (the owner, 2026-10-23): the organisation's address, which resolves before
// the repository goes public
const ossCard = el('', `<div style="width:120px;height:2px;background:${C.acc};margin:0 auto 26px;opacity:.8"></div>
  <div class="mono" style="font:600 22px 'CF Mono',Menlo,monospace;letter-spacing:.24em;color:${C.acc};text-align:center">OPEN SOURCE · COMING SOON</div>
  <div style="font:600 40px 'Avenir Next',Avenir,sans-serif;color:${C.txt};text-align:center;margin-top:14px">github.com/BitmagicAI</div>`, 0, 0);
ossCard.style.left = '0'; ossCard.style.width = W + 'px'; ossCard.style.top = '640px';

// agent activity chart (SVG inside the chart panel)
const days = []; { const d0 = new Date('2026-09-27T12:00:00'); for (let i = 0; i < 26; i++) { const d = new Date(d0.getTime() + i * 86400000); days.push(d.toISOString().slice(0, 10)); } }
const hrs = d => [EFF.codex?.perDayHours?.[d] ?? 0, EFF.claude?.perDayHours?.[d] ?? 0];
const maxH = Math.max(...days.map(d => hrs(d)[0] + hrs(d)[1]), 1);
chartBox.innerHTML = `<div class="small" style="position:absolute;left:36px;top:28px;color:${C.acc}">AGENT ACTIVITY PER DAY · ACTIVE HOURS</div>
  <div class="small" style="position:absolute;right:36px;top:28px"><span style="color:${C.eye}">■</span> CODEX &nbsp; <span style="color:${C.acc}">■</span> CLAUDE</div>
  <div id="bars" style="position:absolute;left:36px;right:36px;top:90px;bottom:70px"></div>
  <div class="small" style="position:absolute;left:36px;bottom:26px">SEP 27</div><div class="small" style="position:absolute;right:36px;bottom:26px">OCT 22</div>`;
const barsEl = chartBox.querySelector('#bars'); const barEls = days.map((d, i) => {
  const col = document.createElement('div'); col.style.cssText = `position:absolute;bottom:0;width:${(1108 / 26 - 8).toFixed(1)}px;left:${(i * 1108 / 26).toFixed(1)}px;display:flex;flex-direction:column-reverse`;
  const a = document.createElement('div'), b = document.createElement('div'); a.style.background = C.eye; b.style.background = C.acc; a.style.borderRadius = b.style.borderRadius = '4px';
  col.append(a, b); barsEl.append(col); return [a, b, d];
});

// loop arrows (svg)
const loopArc = sv('circle', {cx: 640, cy: 560, r: 300, fill: 'none', stroke: '#3a4152', 'stroke-width': 4, 'stroke-dasharray': '10 14', opacity: 0});
const loopDot = sv('circle', {cx: 0, cy: 0, r: 14, fill: C.acc, opacity: 0});
const traceLine = sv('polyline', {points: '', fill: 'none', stroke: C.acc, 'stroke-width': 5, 'stroke-linejoin': 'round', opacity: 0});
const bracket = [0, 1, 2].map(() => sv('path', {d: '', fill: 'none', stroke: C.gold, 'stroke-width': 4, opacity: 0}));
const roofArrows = [0, 1].map(() => sv('path', {d: '', fill: 'none', stroke: C.acc, 'stroke-width': 5, 'marker-end': '', opacity: 0}));
const zoneRects = [0, 1, 2, 3].map(() => sv('rect', {x: 0, y: 0, width: 0, height: 0, rx: 10, fill: 'none', stroke: C.grn, 'stroke-width': 5, opacity: 0}));
const leader = [0, 1].map(() => sv('line', {x1: 0, y1: 0, x2: 0, y2: 0, stroke: C.acc, 'stroke-width': 3, opacity: 0}));

// ------------------------------------------------------------------ events (sound effects, read back by mix.py)
const EVENTS = [];
const ev = (t, sfx, gain = 1) => EVENTS.push({t: +t.toFixed(3), sfx, gain});
ev(.15, 'whoosh_big', .8); ev(T.coverOut, 'whoosh', .7);
['MAPPED', 'MODELLED', 'CHECKED'].forEach((w, i) => ev(S('01', 3 + i) + .05, 'pop', .7));
ev(T.roads0, 'scan', .7); ev(T.outl0, 'build', .6); ev(T.n6800, 'ticker', .6); ev(T.n20k, 'ticker', .6);
ev(T.est, 'pop', .7); ev(T.raise, 'build', .8); ev(T.bel, 'joint', .8); ev(T.eif, 'joint', .8); ev(T.reveal - .3, 'reveal', .8);
ev(T.pave, 'scan', .6); ev(T.walk, 'pop', .6); ev(T.med, 'pop', .6); ev(T.tiles, 'whoosh', .7); ev(T.looked, 'check', .8); ev(T.never, 'stamp', .8);
ev(T.earth - .3, 'whoosh_big', .7); ev(T.outline, 'scan', .6); ev(T.colours, 'pop', .6); ev(T.roofs, 'joint', .7); ev(T.views, 'shutter', .6);
ev(T.photos - .3, 'whoosh', .7); ev(T.never2, 'stamp', .8); ev(T.script, 'typing', .6); ev(T.wall, 'build', .6);
ev(T.compare - .3, 'whoosh_big', .7); ev(T.notright, 'stamp', .8); ev(T.counted, 'ticker', .6); ev(T.crown, 'reveal', .7); ev(T.again, 'check', .9);
ev(T.plans - .3, 'whoosh', .7); ev(T.shops, 'pop', .6); ev(T.pool, 'pop', .6); ev(T.heights, 'pop', .6); ev(T.walkit, 'footsteps', .6);
ev(T.rooms - .3, 'whoosh', .7); ev(T.carpet, 'pop', .6); ev(T.head, 'pop', .6); ev(T.chairs, 'pop', .6); ev(T.n49, 'win', .7);
ev(T.n64, 'ticker', .5); ev(T.floors, 'ticker', .5); ev(T.nrooms, 'ticker', .6); ev(T.napts, 'ticker', .5); ev(T.doors, 'check', .7);
ev(T.loop - .3, 'whoosh_big', .7); for (const k of ['survey', 'build', 'render', 'cmp']) ev(T[k], 'joint', .7);
ev(T.door, 'check', .7); ev(T.flt, 'check', .7); ev(T.flick, 'check', .7); ev(T.back, 'crunch', .7);
ev(T.detail - .3, 'whoosh', .7); ev(T.ven, 'ticker', .7); ev(T.eiffel, 'stamp', .8); ev(T.leg, 'build', .7);
ev(T.agents - .3, 'whoosh', .7); ev(T.days, 'bars', .7); ev(T.calls, 'ticker', .6); ev(T.hours, 'ticker', .6);
ev(T.numbers - .3, 'whoosh_big', .7); for (const k of ['nb', 'n604', 'ntri', 'nmat']) ev(T[k], 'ticker', .6); ev(T.billion, 'boom', .8);
ev(T.weather - .3, 'whoosh', .7);
for (const k of ['browser', 'smooth', 'streams']) ev(T[k], 'pop', .6);
ev(T.card, 'reveal', .8);

// ------------------------------------------------------------------ footage clips (take, in-point s); filled in after looking at the takes
const CLIP = {
  // tour-info (tools/film/takes/tour.json): 0 Arc · 13 Bellagio lake · 28 Cromwell lobby · 32 stairs · 38 corridor · 39 room · 41 window
  // · 46 High Roller · 55 Sphere (its screen blinks at 60-61) · 65-68 terrace door (clips the Expo roof: unused) · 68.4 Grand Canal
  // Shoppes · 74 casino · 79 lobby · 86 campanile · 92 Eiffel (through it at 95) · 110 coaster
  est: ['info-establish-info', 0], bm: ['info-boxmatch-info', 0], bel: ['info-bellagio-info', 0], north: ['info-north-info', 0], south: ['info-south-info', 0],
  arc: ['tour-info', .2], lake: ['tour-info', 13.2], corridor: ['tour-info', 36.6], room: ['tour-info', 39.0], wheel: ['tour-info', 46.0], sphere: ['tour-info', 55.0],
  night: ['info-night-info', 0], rain: ['info-rain-info', 0], rainLake: ['info-rain-lake-info', 0],
  // the Venetian's interiors as rebuilt on 2026-10-23 (the tour's 68-86 s still shows the old ones): their own takes
  shoppes: ['info-shoppes-info', 0.3], casino: ['info-casino-info', 0.3], lobbyv: ['info-lobby-info', 0.3], strip: ['tour-info', 86.0], eiffel: ['tour-info', 92.0], coaster: ['tour-info', 110.5],
};
const play = (key, t, t0, speed = 1) => frameURL(CLIP[key][0], CLIP[key][1] + Math.max(0, t - t0) * speed);
const have = k => !!FOOT[CLIP[k][0]];

// ------------------------------------------------------------------ render
async function render(t) {
  used = new Set(); pending.length = 0;
  for (const c of hud.children) if (c !== kicker && c !== brand) { /* scene code shows what it needs */ }
  for (const e of hud.querySelectorAll(':scope > .abs')) e.style.display = 'none';
  for (const e of svg.children) e.setAttribute('opacity', 0);
  let gl = 0;   // 3D map opacity this frame
  let kick = '';

  // ---- 01 cover + intro: the establishing aerial
  if (on('01', t)) {
    const o = 1 - sm(t, SC['01'][1] - .2, SC['01'][1] + .35);
    shot('A', play('est', t, 0), FULL, o, 1, {zoom: 1.04 - .04 * lin(t, 0, 13)});
    show(shade, o * (1 - .45 * sm(t, T.coverOut, T.coverOut + 1)));
    show(cover, 1 - sm(t, T.coverOut - .1, T.coverOut + .5), -60 * sm(t, T.coverOut - .1, T.coverOut + .5));
    if (t > T.coverOut) kick = 'BEHIND THE SCENES · LAS VEGAS';
    show(days01, win(t, S('01', 2), SC['01'][1], .35, .4), 0, 0);
    chips01.forEach((c, i) => show(c, win(t, S('01', 3 + i), SC['01'][1], .2, .4), 0, (1 - out3(t, S('01', 3 + i), S('01', 3 + i) + .3)) * 20));
  }

  // ---- 02-04: the map, the boxes, the county layers (three.js)
  if (t >= SC['02'][0] - .4 && t < SC['04'][1] + .5) {
    gl = Math.min(sm(t, SC['02'][0] - .4, SC['02'][0] + .2), 1 - sm(t, T.reveal - .05, T.reveal + 1.3) + sm(t, L0('04') - .6, L0('04') - .1), 1 - sm(t, T.tiles - .2, T.tiles + .5) * .65);
    // camera: whole map top-down → central Strip → tilt into the box-match pose → dolly → (reveal) → county close-up
    const whole = TOP(40, 72, 6540), centre = TOP(30, 200, 3400);
    const bmStart = bmKey(0);
    let cam;
    if (t < T.noH) cam = pose(whole, centre, io(t, T.n6800 - 1, T.noH + 1.5));
    else if (t < T.bm0) { cam = pose(pose(whole, centre, 1), {...bmStart, arc: 300}, io(t, T.est + .8, T.bm0)); }
    else if (t < L0('04') - .6) cam = bmKey(lin(t, T.bm0, T.bm0 + 12));
    else cam = pose(TOP(70, 230, 1500), TOP(40, 180, 1150), sm(t, L0('04') - .6, T.tiles));
    applyPose(cam);
    uniforms.uRoads.value = sm(t, T.roads0, T.roads0 + 6.5);
    uniforms.uStrip.value = sm(t, T.roads0 + .6, T.roads0 + 3.2);
    uniforms.uOutl.value = sm(t, T.outl0, T.outl0 + 5.5);
    uniforms.uFlat.value = t < T.raise + 2 || t > L0('04') - .7 ? 1 : 0;
    uniforms.uTagged.value = win(t, T.noH, T.raise + 1.2, .4, .6);
    uniforms.uGrow.value = t > L0('04') - .7 ? 0 : sm(t, T.raise - .3, T.raise + 3.2); BOXES.mesh.visible = uniforms.uGrow.value > .002;
    uniforms.uBel.value = mix(120, M.bellagioHeightM.value, out3(t, T.bel, T.bel + 1.2));
    uniforms.uHi.value = Math.max(win(t, T.bel - .2, T.eif + 2.5, .3, .5));
    uniforms.uPave.value = sm(t, T.pave, T.pave + 1.6); uniforms.uWalk.value = sm(t, T.walk, T.walk + 1.4); uniforms.uMed.value = sm(t, T.med, T.med + 1.2);
    uniforms.uDim.value = 1; uniforms.uFootA.value = 1 - .72 * sm(t, L0('04') - .6, T.pave + .4);
    // real footage takes over from the boxes (same camera)
    if (t > T.reveal - .4 && t < L0('04') - .1) shot('A', play('bm', t, T.bm0), FULL, sm(t, T.reveal - .3, T.reveal + 1.0) * (1 - sm(t, L0('04') - .7, L0('04') - .15)), 1);
    kick = t < L0('03') - .3 ? '01 · OPENSTREETMAP' : t < L0('04') - .3 ? '02 · FROM OUTLINES TO BOXES' : '03 · CLARK COUNTY GIS + A VISUAL CHECK';
    if (t < L0('03') - .3) {
      show(osmAtt, win(t, T.roads0, L0('03') - .2)); show(nLabel, win(t, T.roads0, L0('03') - .2));
      if (t > T.n6800 - .3) counter(t, 0, M.osmOutlines.value, T.n6800, T.n6800 + 1.6, 'BUILDING OUTLINES', 0, 96, 640);
      if (t > T.n20k - .3) counter(t, 0, M.osmRoadSegments.value, T.n20k, T.n20k + 1.6, 'ROAD SEGMENTS', 1, 96, 812);
    } else if (t < L0('04') - .4) {
      show(osmAtt, win(t, L0('03') - .3, T.reveal));
      if (t < T.lmk) counter(t, 0, M.heightsUnknown.value, T.noH + .2, T.noH + 1.8, 'OUTLINES WITH NO HEIGHT', 0, 96, 812, 1 - sm(t, T.lmk - .6, T.lmk - .1));
      show(ruleChip, win(t, T.est, T.lmk, .35, .5), (1 - out3(t, T.est, T.est + .5)) * 40);
      for (const [elx, id, h, t0, txt] of [[lmBel, LANDMARK.bellagio, M.bellagioHeightM.value, T.bel, 'BELLAGIO'], [lmEif, LANDMARK.eiffel, M.eiffelHeightM.value, T.eif, 'EIFFEL TOWER']]) {
        if (id < 0) continue;
        const ring = MAP.buildings[id][3]; let cx = 0, cz = 0; for (let k = 0; k < ring.length; k += 2) { cx += ring[k]; cz += ring[k + 1]; } cx /= ring.length / 2; cz /= ring.length / 2;
        const hh = elx === lmBel ? uniforms.uBel.value : h;
        const [sx, sy] = project(cx, hh * uniforms.uGrow.value, cz);
        elx.innerHTML = `${txt} <span style="color:${C.acc}">${(elx === lmBel ? hh : h).toFixed(elx === lmBel && t < T.bel + 1.3 ? 0 : 1)} m</span> <span class="small">PUBLISHED</span>`;
        elx.style.left = (sx + 30) + 'px'; elx.style.top = (sy - 70) + 'px'; show(elx, win(t, t0 - .1, T.reveal - .2, .3, .4));
        const li = leader[elx === lmBel ? 0 : 1]; li.setAttribute('x1', sx); li.setAttribute('y1', sy); li.setAttribute('x2', sx + 30); li.setAttribute('y2', sy - 40); li.setAttribute('opacity', win(t, t0 - .1, T.reveal - .2, .3, .4));
      }
    } else {
      show(countyAtt, win(t, T.pave - .2, T.tiles + .3)); show(layerPanel, win(t, T.pave - .2, T.tiles + .2, .3, .4) * .92);
      layerChips.forEach((c, i) => show(c, win(t, [T.pave, T.walk, T.med][i], T.tiles + .2, .3, .4), (1 - out3(t, [T.pave, T.walk, T.med][i], [T.pave, T.walk, T.med][i] + .4)) * -30));
      // Cesium / Google 3D tiles: a visual check
      const co = sm(t, T.tiles - .2, T.tiles + .5) * (1 - sm(t, SC['04'][1] - .3, SC['04'][1] + .3));
      if (co > 0) {
        const r = {x: 330, y: 150, w: 1260, h: 1260 * 831 / 1168, r: 22};
        shot('cesium', still('cesium'), r, third(co), 5, {filter: thirdFilter(), fit: 'cover', over: true});
        cesiumTag.style.left = r.x + 'px'; cesiumTag.style.top = (r.y - 66) + 'px'; show(cesiumTag, co);
        lookedStamp.style.left = (r.x + 60) + 'px'; lookedStamp.style.top = (r.y + r.h - 130) + 'px'; show(lookedStamp, sm(t, T.looked, T.looked + .2), 0, 0, 1 + pulse(t, T.looked, .3) * .25, 'rotate(-4deg)');
        neverStamp.style.left = (r.x + 470) + 'px'; neverStamp.style.top = (r.y + r.h - 130) + 'px'; show(neverStamp, sm(t, T.never, T.never + .2), 0, 0, 1 + pulse(t, T.never, .3) * .25, 'rotate(-4deg)');
      }
    }
  }
  glCanvas.style.opacity = gl.toFixed(3);
  if (gl > .001) renderer.render(scene, camera);

  // ---- 05 Google Earth
  if (on('05', t)) {
    const o = win(t, SC['05'][0], SC['05'][1] + .3, .5, .5);
    const shrink = io(t, T.views - .2, T.views + .9);
    const r = {x: mix(96, 72, shrink), y: mix(150, 160, shrink), w: mix(1440, 900, shrink), h: mix(1440, 900, shrink) * 1122 / 2000, r: 22};
    shot('A', still('ge-bellagio'), r, third(o), 2, {filter: thirdFilter()});
    geAtt.style.left = (r.x + 18) + 'px'; geAtt.style.top = (r.y + r.h - 30) + 'px'; show(geAtt, third(o));
    kick = '04 · GOOGLE EARTH';
    // outline trace of the main tower (image coordinates on the 2000×1122 view)
    const sx = r.w / 2000, OUT = [[548, 352], [538, 300], [690, 300], [690, 205], [1110, 200], [1150, 130], [1210, 125], [1240, 200], [1660, 252], [1660, 312], [1800, 375], [1810, 400], [1745, 880], [1610, 880], [1560, 820], [790, 740], [600, 790], [548, 352]];
    const tr = sm(t, T.outline, T.outline + 1.4) * (1 - shrink);
    if (tr > 0) { const n = Math.max(2, Math.ceil(OUT.length * tr)); traceLine.setAttribute('points', OUT.slice(0, n).map(([x, y]) => `${(r.x + x * sx).toFixed(1)},${(r.y + y * sx).toFixed(1)}`).join(' ')); traceLine.setAttribute('opacity', third(o)); }
    swatches.forEach((s, i) => show(s, win(t, T.colours + i * .18, T.views, .25, .4) * o, (1 - out3(t, T.colours + i * .18, T.colours + i * .18 + .4)) * 40));
    for (const [i, [x, y]] of [[0, [690, 300]], [1, [1660, 312]]]) {
      const a = win(t, T.roofs, T.views, .25, .4) * (1 - shrink); const X = r.x + x * sx, Y = r.y + y * sx;
      roofArrows[i].setAttribute('d', `M ${X + (i ? 60 : -60)} ${Y - 110} Q ${X + (i ? 40 : -40)} ${Y - 40} ${X} ${Y - 8}`); roofArrows[i].setAttribute('opacity', third(a));
    }
    // more than two hundred views: tiles + a log
    const tiles = ['ge-venetian', 'ge-bellagio', 'venetian-rejected'];
    if (t > T.views - .3) {
      counter(t, 0, M.googleEarthViews.value, T.views, T.views + 1.6, 'GOOGLE EARTH VIEWS', 0, 1080, 160);
      const lines = GELOG.slice(0, Math.floor(clamp((t - T.views - .3) / .35, 0, GELOG.length)));
      geLog.textContent = lines.join('\n'); show(geLog, o);
    }
  }

  // ---- 06 public photos → Blender script
  if (on('06', t)) {
    const o = win(t, SC['06'][0], SC['06'][1] + .3, .5, .5);
    kick = '05 · PUBLIC PHOTOS → BLENDER';
    const boardOut = sm(t, T.script - .4, T.script + .4);
    // research board: small tiles drifting left
    const list = ST.refTiles.list; const cols = 14, tw = 150, th = 100, gap = 10, drift = (t - SC['06'][0]) * 22;
    for (let i = 0; i < list.length; i++) {
      const c = i % cols, rr = Math.floor(i / cols);
      const x = 60 + c * (tw + gap) - drift + (rr % 2) * 40, y = 170 + rr * (th + gap);
      const a = o * (1 - boardOut) * sm(t, SC['06'][0] + .02 * i, SC['06'][0] + .02 * i + .4);
      shot('ref' + i, still(list[i]), {x, y, w: tw, h: th, r: 8}, third(a) * .9, 2, {filter: thirdFilter('brightness(.9)')});
    }
    photoLab.style.left = '72px'; photoLab.style.top = '960px'; show(photoLab, third(o * (1 - boardOut)));
    entChips.forEach((c, i) => show(c, win(t, T.ent + i * .45, T.never2 - .1, .2, .3), 0, (1 - out3(t, T.ent + i * .45, T.ent + i * .45 + .3)) * 20));
    neverPaste.style.left = '640px'; neverPaste.style.top = '470px'; show(neverPaste, win(t, T.never2, T.script, .15, .35), 0, 0, 1 + pulse(t, T.never2, .3) * .25, 'rotate(-4deg)');
    // the script types itself, then the render builds row by row
    const typed = clamp((t - T.script) / 2.6, 0, 1), nl = Math.floor(typed * CODE.length + .001);
    codeTxt.innerHTML = CODE.slice(0, Math.max(1, nl)).join('\n') + (typed < 1 ? '<b>▍</b>' : '');
    show(codeBox, win(t, T.script - .2, T.wall + .3, .35, .5) * o, (1 - out3(t, T.script - .2, T.script + .3)) * -40, 0);
    const rv = sm(t, T.wall - .1, T.windows + 1.6);
    if (rv > 0) {
      const r = {x: 240, y: 150, w: 1440, h: 810, r: 18};
      const s = shot('B', still('blender-bellagio'), r, o * sm(t, T.wall - .2, T.wall + .2), 3, {});
      s.box.style.clipPath = `inset(0 0 ${(100 - rv * 100).toFixed(2)}% 0)`;
      const dpos = [[r.x + 330, r.y + 175], [r.x + 830, r.y + 120], [r.x + 1150, r.y + 470]];
      dims.forEach((d, i) => { d.style.left = dpos[i][0] + 'px'; d.style.top = dpos[i][1] + 'px'; show(d, win(t, T.windows + .6 + i * .3, SC['06'][1], .25, .3) * o); });
    } else { const s = slots.get('B'); if (s) s.box.style.clipPath = 'none'; }
  } else { const s = slots.get('B'); if (s) s.box.style.clipPath = 'none'; }

  // ---- 07 Bellagio: compare, recount, rebuild
  if (on('07', t)) {
    const o = win(t, SC['07'][0], SC['07'][1] + .3, .5, .5);
    kick = '06 · COMPARE AND REBUILD';
    const full = io(t, T.crown - .3, T.crown + .7) * (1 - io(t, T.again - .2, T.again + .6));
    const L = {x: 72, y: 190, w: 870, h: 870 * 1122 / 2000, r: 18};
    const R = {x: mix(978, 0, full), y: mix(190, 0, full), w: mix(870, W, full), h: mix(870 * 9 / 16, H, full), r: mix(18, 0, full)};
    shot('A', still('ge-bellagio'), L, third(o), 2, {filter: thirdFilter()});
    geAtt.style.left = (L.x + 14) + 'px'; geAtt.style.top = (L.y + L.h - 28) + 'px'; show(geAtt, third(o));
    const after = sm(t, T.crown - .5, T.crown + .2);
    shot('B', still('game-before-bellagio'), {...R, y: R.y + (1 - full) * 0}, o * (1 - after), 3, {});
    if (after > 0) shot('C', play('bel', t, T.crown - .5), R, o * after, 4, {});
    notRec.style.left = (978 + 160) + 'px'; notRec.style.top = (190 + 360) + 'px'; show(notRec, win(t, T.notright + .6, T.crown - .5, .15, .3), 0, 0, 1 + pulse(t, T.notright + .6, .3) * .25, 'rotate(-4deg)');
    // counted rows: brackets on the reference's right wing (image coordinates)
    const sx = L.w / 2000, segs = [[255, 470], [470, 775], [775, 880]];
    segs.forEach(([y0, y1], i) => {
      const a = win(t, T.counted + i * .35, T.crown, .2, .3) * (REFS === 'off' ? 0 : 1);
      const X = L.x + 1835 * sx, Y0 = L.y + y0 * sx, Y1 = L.y + y1 * sx;
      bracket[i].setAttribute('d', `M ${X - 14} ${Y0 + 3} L ${X} ${Y0 + 3} L ${X} ${Y1 - 3} L ${X - 14} ${Y1 - 3}`); bracket[i].setAttribute('opacity', a);
      segLabs[i].style.left = (X - 30) + 'px'; segLabs[i].style.top = ((Y0 + Y1) / 2 - 24) + 'px'; show(segLabs[i], a, 0, 0, 1, 'translateX(-100%)');
    });
    const cpos = [[1180, 520], [1330, 360], [520, 300]];
    callouts07.forEach((c, i) => { c.style.left = cpos[i][0] + 'px'; c.style.top = cpos[i][1] + 'px'; show(c, win(t, [T.crown + .4, T.arched, T.arched + .9][i], T.again - .2, .25, .3)); });
    matchOK.style.left = '640px'; matchOK.style.top = '920px'; show(matchOK, win(t, T.again + .3, SC['07'][1] + .3, .25, .4), 0, (1 - out3(t, T.again + .3, T.again + .7)) * 20);
  }

  // ---- 08 floor plans → fitted interiors → walked
  if (on('08', t)) {
    const o = win(t, SC['08'][0], SC['08'][1] + .3, .5, .5);
    kick = '07 · FLOOR PLANS → INTERIORS';
    const toWalk = sm(t, T.fit - .2, T.fit + .8);
    const r = {x: 160, y: 170, w: 1200, h: 1200 * 1272 / 2000, r: 18};
    shot('A', still('plan-venetian'), r, third(o * (1 - toWalk)), 2, {filter: thirdFilter(), fit: 'contain'});
    planLab.style.left = r.x + 'px'; planLab.style.top = (r.y - 66) + 'px'; show(planLab, third(o * (1 - toWalk)));
    // zones on the plan (image coordinates on 2000×1272)
    // on the official map's colour key (2000×1272): green = casino, navy = shopping; the front desk; the pool garden
    const sx = r.w / 2000, Z = [[1455, 545, 120, 130, C.grn, T.shops], [1255, 360, 115, 110, '#5aa0ff', T.shops + .35], [1665, 612, 125, 85, C.acc, T.pool], [1795, 532, 105, 55, C.eye, T.pool + .35]];
    Z.forEach(([x, y, w, h, col, t0], i) => {
      const a = win(t, t0, T.fit, .25, .3) * (1 - toWalk) * (REFS === 'off' ? 0 : 1);
      const zr = zoneRects[i]; zr.setAttribute('x', r.x + x * sx); zr.setAttribute('y', r.y + y * sx); zr.setAttribute('width', w * sx); zr.setAttribute('height', h * sx); zr.setAttribute('stroke', col); zr.setAttribute('opacity', a);
      zoneLabs[i].style.left = (r.x + x * sx) + 'px'; zoneLabs[i].style.top = (r.y + y * sx - 52) + 'px'; show(zoneLabs[i], a);
    });
    layoutChips.forEach((c, i) => show(c, win(t, [T.layout, T.heights][i], T.fit + .3, .25, .3) * (1 - toWalk), (1 - out3(t, [T.layout, T.heights][i], [T.layout, T.heights][i] + .4)) * 30));
    if (toWalk > 0) shot('B', play(t < T.walkit + .2 ? 'shoppes' : 'casino', t, t < T.walkit + .2 ? T.fit - .2 : T.walkit + .2), FULL, o * toWalk, 3, {});
    walkTag.style.left = '72px'; walkTag.style.top = '960px'; show(walkTag, win(t, T.walkit + .3, SC['08'][1] + .3, .25, .4));
  }

  // ---- 09 rooms and corridors
  if (on('09', t)) {
    const o = win(t, SC['09'][0], SC['09'][1] + .3, .5, .5);
    kick = '08 · CORRIDORS + ROOMS';
    const grid = sm(t, T.n49 - .9, T.n49 + .3);
    // close-ups for carpet / headboard / chairs, then the grid of 49 designs
    const closeups = [['corridor-linq', T.carpet, 0], ['headboard', T.head, 1], ['room-planet-hollywood', T.chairs, 2]];
    if (t < T.carpet) shot('A', play('corridor', t, SC['09'][0]), FULL, o * (1 - grid), 2, {});
    for (const [n, t0, i] of closeups) {
      const a = win(t, t0 - .15, i < 2 ? closeups[i + 1][1] + .1 : T.n49 - .5, .2, .25);
      if (a > 0) shot('cu' + i, still(n), FULL, o * a, 3 + i, {zoom: 1.04 + .06 * lin(t, t0, t0 + 2)});
      const cp = [[880, 820], [820, 380], [1250, 520]][i];
      roomCallouts[i].style.left = cp[0] + 'px'; roomCallouts[i].style.top = cp[1] + 'px'; show(roomCallouts[i], a * sm(t, t0 + .1, t0 + .3));
    }
    const BAD = new Set(['room-linq']);   // that capture landed inside a wall
    const rooms = ST.rooms.filter(r => !BAD.has(r.n)), tiles = rooms.map(r => r.n); const seen = new Set(rooms.map(r => r.set));
    for (const c of ST.corridors) if (!seen.has(c.set)) tiles.push(c.n);
    const cols = 7, tw = 180, th = 101, gx = 10, x0 = 540, y0 = 160;
    tiles.slice(0, 49).forEach((n, i) => {
      const c = i % cols, rr = Math.floor(i / cols), a = o * sm(t, T.n49 - .9 + i * .022, T.n49 - .5 + i * .022);
      shot('g' + i, still(n), {x: x0 + c * (tw + gx), y: y0 + rr * (th + gx), w: tw, h: th, r: 8}, a, 8, {});
    });
    if (t > T.n49 - .3) counter(t, 0, 49, T.n49, T.n49 + 1, 'ROOM DESIGNS', 0, 72, 640, o);
    if (t > T.each - .3) { bigC2.textContent = 'ONE PER PROPERTY'; bigC2.style.left = '76px'; bigC2.style.top = '800px'; show(bigC2, o * sm(t, T.each - .2, T.each + .2)); }
  }

  // ---- 10 towers, floors, rooms
  if (on('10', t)) {
    const o = win(t, SC['10'][0], SC['10'][1] + .3, .5, .5);
    kick = '09 · WALK INTO ANY OF THEM';
    const k = t < T.nrooms ? 'room' : 'wheel';
    shot('A', play(k, t, k === 'room' ? SC['10'][0] : T.nrooms), FULL, o, 2, {});
    show(shade, o * .9);
    towerRows.forEach((r, i) => show(r, win(t, [T.n64, T.floors, T.nrooms, T.napts][i], SC['10'][1] + .3, .25, .4), (1 - out3(t, [T.n64, T.floors, T.nrooms, T.napts][i], [T.n64, T.floors, T.nrooms, T.napts][i] + .4)) * -40));
    doorTag.style.left = '96px'; doorTag.style.top = '880px'; show(doorTag, win(t, T.doors, SC['10'][1] + .3, .25, .4));
  }

  // ---- 11 the loop
  if (on('11', t)) {
    const o = win(t, SC['11'][0], SC['11'][1] + .3, .5, .5);
    kick = '10 · THE AGENT LOOP';
    // before/after wall behind, dimmed
    const pairs = ST.pairs; const cols = 8, tw = 236, th = 133;
    for (let i = 0; i < 40; i++) {
      const p = pairs[i % pairs.length], c = i % cols, rr = Math.floor(i / cols), flip = (t * .9 + i * .37) % 2 > 1;
      shot('w' + i, still(`pair-${p}-${flip ? 'a' : 'b'}`), {x: c * (tw + 4), y: rr * (th + 4) + 200, w: tw, h: th, r: 0}, o * .22, 1, {});
    }
    const cx = 640, cy = 560, R = 300;
    loopArc.setAttribute('opacity', o);
    const times = [T.survey, T.build, T.render, T.cmp, T.audits, T.back];
    let active = -1; times.forEach((tt, i) => { if (t >= tt - .1) active = i; });
    nodeEls.forEach((n, i) => {
      const a = -Math.PI / 2 + i * Math.PI / 3, x = cx + R * Math.cos(a), y = cy + R * Math.sin(a);
      n.style.left = (x - 110) + 'px'; n.style.top = (y - 36) + 'px'; n.style.width = '220px'; n.style.textAlign = 'center';
      const hl = i === active; n.style.borderColor = hl ? C.acc : '#3e4556'; n.style.color = hl ? C.acc : C.txt;
      show(n, o * sm(t, SC['11'][0] + i * .08, SC['11'][0] + i * .08 + .3), 0, 0, 1 + (hl ? pulse(t, times[i], .4) * .12 : 0));
    });
    if (active >= 0) { const prev = Math.max(0, active - 1), u = out3(t, times[active] - .1, times[active] + .4); const a0 = -Math.PI / 2 + (active === 0 ? 0 : prev) * Math.PI / 3, a1 = -Math.PI / 2 + active * Math.PI / 3, a = mix(a0, a1, u);
      loopDot.setAttribute('cx', cx + R * Math.cos(a)); loopDot.setAttribute('cy', cy + R * Math.sin(a)); loopDot.setAttribute('opacity', o); }
    loopCenter.style.left = (cx - 120) + 'px'; loopCenter.style.top = (cy - 30) + 'px'; loopCenter.style.width = '240px'; show(loopCenter, o * .9);
    audits.forEach((a, i) => show(a, win(t, [T.door, T.flt, T.flick][i], SC['11'][1] + .3, .25, .4), (1 - out3(t, [T.door, T.flt, T.flick][i], [T.door, T.flt, T.flick][i] + .4)) * 40));
    failTag.style.left = '1240px'; failTag.style.top = '780px'; show(failTag, win(t, T.back, SC['11'][1] + .3, .2, .4), 0, 0, 1 + pulse(t, T.back, .3) * .15);
  }

  // ---- 12 detail per pass: the Venetian overnight, the Eiffel Tower rebuilt
  if (on('12', t)) {
    const o = win(t, SC['12'][0], SC['12'][1] + .3, .5, .5);
    kick = '11 · EVERY PASS ADDS DETAIL';
    const toE = sm(t, T.eiffel - .4, T.eiffel + .2);
    const vAfter = sm(t, T.ven + 1.2, T.ven + 2.2);
    shot('A', still('venetian-rejected'), FULL, o * (1 - vAfter) * (1 - toE), 2, {zoom: 1.03});
    shot('B', still('venetian-after'), FULL, o * vAfter * (1 - toE), 3, {zoom: 1.03 + .03 * lin(t, T.ven + 1.2, T.eiffel)});
    show(shadeB, o);
    const tri = t < T.ven + 1.2 ? mix(0, 527496, out3(t, T.night, T.night + 1)) : mix(527496, 999101, out3(t, T.ven + 1.2, T.ven + 2.6));
    if (toE < 1) counter(t, 0, Math.round(tri), T.night, T.night + .01, 'VENETIAN TRIANGLES · ONE NIGHT', 0, 72, 812, 1 - toE);
    const eAfter = sm(t, T.leg - .3, T.leg + .5);
    if (toE > 0) {
      shot('C', still('eiffel-rejected'), FULL, o * toE * (1 - eAfter), 4, {zoom: 1.02});
      shot('D', still('eiffel-after'), FULL, o * eAfter, 5, {zoom: 1.02 + .03 * lin(t, T.leg, T.leg + 3)});
      rejStamp.style.left = '760px'; rejStamp.style.top = '460px'; show(rejStamp, win(t, T.eiffel + .3, T.leg - .2, .15, .3), 0, 0, 1 + pulse(t, T.eiffel + .3, .3) * .25, 'rotate(-4deg)');
      rebuiltTag.style.left = '72px'; rebuiltTag.style.top = '960px'; show(rebuiltTag, win(t, T.measured, SC['12'][1] + .3, .25, .4));
    }
  }

  // ---- 13 two agents
  if (on('13', t)) {
    const o = win(t, SC['13'][0], SC['13'][1] + .3, .5, .5);
    kick = '12 · TWO AGENTS';
    show(chartBox, o);
    barEls.forEach(([a, b, d], i) => { const [h0, h1] = hrs(d), g = out3(t, T.days + i * .03, T.days + i * .03 + .6); a.style.height = (h0 / maxH * 400 * g).toFixed(1) + 'px'; b.style.height = (h1 / maxH * 400 * g).toFixed(1) + 'px'; });
    agentTitle.innerHTML = `<div class="mid" style="font-size:56px"><span style="color:${C.eye}">Codex</span> + <span style="color:${C.acc}">Claude</span></div>`;
    show(agentTitle, win(t, T.codex - .1, SC['13'][1] + .3, .3, .4));
    // (unspoken: the tokens follow the tool calls, the cost the hours)
    const at = [T.days, T.calls, T.calls + .7, T.hours, T.hours + .7, T.mac];
    agentStats.forEach((s, i) => show(s, win(t, at[i], SC['13'][1] + .3, .25, .4), (1 - out3(t, at[i], at[i] + .4)) * 30));
  }

  // ---- 14 the numbers, over a fly-through montage
  if (on('14', t)) {
    const o = win(t, SC['14'][0], SC['14'][1] + .3, .5, .5);
    kick = '13 · THE CITY TODAY';
    const cuts = [['north', SC['14'][0]], ['eiffel', T.ntri - .3], ['south', T.built - .3]];
    let k = 0; for (let i = 0; i < cuts.length; i++) if (t >= cuts[i][1]) k = i;
    const [clip, t0] = cuts[k]; const cf = k > 0 ? sm(t, t0, t0 + .5) : 1;
    if (k > 0) shot('A' + (k - 1), play(cuts[k - 1][0], t, cuts[k - 1][1]), FULL, o, 2, {});
    shot('A' + k, play(clip, t, t0), FULL, o * cf, 3, {});
    show(shadeB, o); show(vignette, o);
    const rows = [[T.nb, M.buildings.value, 'BUILDINGS'], [T.n604, M.replacedByDetailed.value, 'REPLACED BY DETAILED MODELS'], [T.ntri, M.triangles.value, 'TRIANGLES'], [T.nmat, M.materials.value, 'MATERIALS']];
    let cur = 0; rows.forEach((r, i) => { if (t >= r[0] - .2) cur = i; });
    const [t0r, n, cap] = rows[cur];
    if (t < T.billion - .3) counter(t, cur ? rows[cur - 1][1] * 0 : 0, n, t0r, t0r + 1.4, cap, 0, 72, 812, o);
    else counter(t, M.triangles.value, M.fullyBuiltTriangles.value, T.billion - .2, T.billion + 1.2, 'TRIANGLES WITH EVERY HOTEL FLOOR BUILT', 0, 72, 812, o);
  }

  // ---- 14b any hour, any weather: the same city under the film presets (take.look), no new models
  if (on('14b', t)) {
    const o = win(t, SC['14b'][0], SC['14b'][1] + .3, .5, .5);
    kick = '14 · ANY HOUR, ANY WEATHER';
    const cuts = [['night', SC['14b'][0]], ['rain', T.wRain - .35]];
    let k = 0; for (let i = 0; i < cuts.length; i++) if (t >= cuts[i][1]) k = i;
    const [clip, t0] = cuts[k]; const cf = k > 0 ? sm(t, t0, t0 + .5) : 1;
    if (k > 0) shot('W' + (k - 1), play(cuts[k - 1][0], t, cuts[k - 1][1]), FULL, o, 2, {});
    shot('W' + k, play(clip, t, t0), FULL, o * cf, 3, {});
    show(shadeB, o * .8); show(vignette, o);
    const lab = [['NIGHT · NEON', T.wNight - .2, T.wRain - .35], ['RAIN · WET STREETS', T.wRain - .2, SC['14b'][1] + .3]];
    lab.forEach(([txt, a, b], i) => { weatherTags[i].textContent = txt; show(weatherTags[i], o * win(t, a, b, .3, .3), 0, (1 - out3(t, a, a + .4)) * 20); });
    show(sameData, o * win(t, SC['14b'][0] + .6, SC['14b'][1] + .3, .4, .4));
  }

  // ---- 15 end
  if (on('15', t)) {
    const o = win(t, SC['15'][0], TL.total + 1, .5, .1);
    // the coaster, then into a hotel corridor and room (the tour footage runs out 11.8 s into the ride)
    const toRoom = sm(t, T.streams - .3, T.streams + .2);
    shot('A', play('coaster', t, SC['15'][0]), FULL, o, 2, {});
    if (toRoom > 0) shot('B', play('corridor', t, T.streams - .3), FULL, o * toRoom, 3, {});
    show(vignette, o); show(shade, o * .55 * win(t, T.browser - .3, T.card + .2, .4, .5));
    engineTags.forEach((e, i) => { const a = [T.browser, T.smooth, T.streams][i]; show(e, o * win(t, a - .1, T.card + .2, .3, .4), (1 - out3(t, a - .1, a + .3)) * -30); });
    const c = sm(t, T.card, T.card + 1.0);
    show(dimAll, o * c); show(endCard, c, 0, (1 - c) * 20);
    const oc = sm(t, T.card + 1.1, T.card + 1.9); show(ossCard, oc, 0, (1 - oc) * 16);
    if (t < T.card) kick = 'THE GAME ITSELF · IN THE BROWSER';
  }

  kicker.textContent = kick; show(kicker, kick ? 1 : 0);
  show(brand, t > T.coverOut && t < T.card ? .9 : 0);
  for (const [k, s] of slots) if (!used.has(k)) s.box.style.display = 'none';
  await Promise.all(pending);
}

window.story = {render, ready: true, fps: TL.fps, total: TL.total, events: EVENTS};
