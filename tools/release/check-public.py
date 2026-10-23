#!/usr/bin/env python3
"""Pre-publish audit of what the public repository would contain: every file git would commit
(`git ls-files --cached --others --exclude-standard`), checked for things that must not go public.

Fails on: files over 50 MB (GitHub refuses 100 MB and warns at 50), secret-shaped strings, private keys, word-for-word
quotes of the owner's messages, fonts outside the allow-list, third-party reference media (photos, PDFs, screenshots) outside the folders that are ours, and missing
licence/contribution files. Warns on: home-folder paths and e-mail addresses in text files.

python3 tools/release/check-public.py               # report; exit 1 on any failure
python3 tools/release/check-public.py --fix-paths   # also rewrite home-folder paths in docs/ and tools/ records
                                                     # (<repo>/... for this checkout, ~/... for the rest)
See docs/OPEN-SOURCE.md for what is excluded and why."""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 50 * 1024 * 1024
TEXT = {'.md', '.txt', '.json', '.py', '.mjs', '.js', '.ts', '.sh', '.html', '.css', '.yml', '.yaml', '.toml', '.csv', '.log', '.svg'}
REQUIRED = ['README.md', 'LICENSE', 'LICENSE-CONTENT.md', 'LICENSE-DATA.md', 'NOTICE.md', 'CONTRIBUTING.md', 'AGENTS.md',
            'tasks/README.md', 'tasks/index.json', 'docs/OPEN-SOURCE.md', 'docs/ASSETS.md', 'tools/release/asset-pack.json']
# Fonts we may redistribute (OFL / public licence, see NOTICE.md). Anything else fails.
FONT_OK = re.compile(r'^(engine/|node_modules/)')
# Images that are ours (renders of the game, proofs, brand marks) may ship; photos and plans of real places may not.
MEDIA = re.compile(r'\.(png|jpe?g|webp|gif|heic|pdf|mp4|mov)$', re.I)
MEDIA_OK = re.compile(r'^(engine/|public/|src/work/|tools/film/brand/|\.agents/skills/|\.claude/skills/)')
SECRETS = [
    ('private key', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('AWS key', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('GitHub token', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b')),
    ('OpenAI/Anthropic-style key', re.compile(r'\bsk-(ant-)?[A-Za-z0-9_-]{24,}\b')),
    ('Google API key', re.compile(r'\bAIza[0-9A-Za-z_-]{35}\b')),
    ('Slack token', re.compile(r'\bxox[abposr]-[A-Za-z0-9-]{10,}\b')),
    ('assigned secret', re.compile(r'''(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*['"][A-Za-z0-9_\-/+=]{20,}['"]''')),
]
# Word-for-word quotes of private conversations (the journals are ignored; reports must paraphrase)
VERBATIM = re.compile(r'(?i)(\(verbatim\)|\(exact words\)|owner\'s words|creator\'s words)\s*:?\s*["“]')
HOME = re.compile(r'/(?:Users|home)/([A-Za-z0-9._-]+)')
EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
EMAIL_OK = re.compile(r'(noreply|no-reply|example\.(com|org)|users\.noreply\.github\.com|@bitmagic\.ai$|\.(png|jpe?g|webp|glb|js|mjs)$|@[0-9])', re.I)


def tracked():
    out = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT,
                         capture_output=True, check=True).stdout
    return [p for p in out.decode().split('\0') if p]


def main():
    fix = '--fix-paths' in sys.argv
    files = tracked()
    fails, warns, fixed = [], [], 0
    total = 0
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            fails.append(f'missing required file: {rel}')
    for rel in files:
        p = ROOT / rel
        if not p.is_file():
            continue
        size = p.stat().st_size
        total += size
        if size > MAX_BYTES:
            fails.append(f'{rel}: {size / 1048576:.1f} MB (over 50 MB: move it to the asset pack)')
        if re.search(r'\.(ttf|otf|woff2?)$', rel, re.I) and not FONT_OK.match(rel):
            fails.append(f'{rel}: font outside the allow-list (check its licence, then ignore it or list it in NOTICE.md)')
        if MEDIA.search(rel) and not MEDIA_OK.match(rel):
            fails.append(f'{rel}: image/PDF/video outside our own asset folders (third-party reference media stay local)')
        if p.suffix.lower() not in TEXT or size > 20 * 1048576:
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        if rel.startswith(('engine/', 'node_modules/')):
            continue
        for name, rx in SECRETS:
            m = rx.search(text)
            if m and 'check-public.py' not in rel:
                fails.append(f'{rel}: {name}: {m.group(0)[:12]}…')
        if VERBATIM.search(text) and rel != 'tools/release/check-public.py':
            fails.append(f'{rel}: quotes the owner word for word (paraphrase it, or keep the file local)')
        homes = HOME.findall(text)
        if homes and rel != 'tools/release/check-public.py':
            if fix and rel.startswith(('docs/', 'tools/')) and p.suffix.lower() in {'.md', '.txt', '.json', '.log', '.csv'}:
                new = text.replace(str(ROOT), '<repo>')
                new = HOME.sub('~', new)
                if new != text:
                    p.write_text(new, encoding='utf-8')
                    fixed += 1
                    continue
            warns.append(f'{rel}: home-folder path ({len(homes)}x, e.g. /{"Users" if "/Users/" in text else "home"}/{homes[0]})')
        for m in (EMAIL.finditer(text) if p.suffix.lower() in {'.md', '.txt', '.json', '.log', '.csv', '.html', '.yml', '.yaml'} else ()):
            if not EMAIL_OK.search(m.group(0)):
                warns.append(f'{rel}: e-mail address {m.group(0)}')
                break
    print(f'{len(files)} files, {total / 1048576:.1f} MB would be committed')
    if fixed:
        print(f'rewrote home-folder paths in {fixed} files')
    for w in warns[:80]:
        print('warn ', w)
    if len(warns) > 80:
        print(f'warn  ... and {len(warns) - 80} more')
    for f in fails:
        print('FAIL ', f)
    print(f'{len(fails)} failures, {len(warns)} warnings')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
