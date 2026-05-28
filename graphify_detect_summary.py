import json
from pathlib import Path
p = Path('graphify-out/.graphify_detect.json')
if not p.exists():
    print('No detect file found')
    raise SystemExit(1)

d = json.loads(p.read_text(encoding='utf-8'))
files = d.get('files', {})
total = sum(len(v) for v in files.values())
words = d.get('total_words', 0)
print(f'Corpus: {total} files · ~{words} words')
for k in ['code','document','paper','image','video','audio']:
    lst = files.get(k, [])
    if lst:
        print(f'  {k:8}: {len(lst)} files')
if d.get('skipped_sensitive'):
    print(f"Skipped sensitive: {len(d.get('skipped_sensitive', []))} files")

# If very large, show top 5 subdirs by file count
if total > 200 or words > 2000000:
    from collections import Counter
    paths = [str(Path(f).parent) for v in files.values() for f in v]
    cnt = Counter(paths)
    top = cnt.most_common(5)
    print('\nWarning: large corpus detected')
    print('Top subdirectories:')
    for p,c in top:
        print(f'  {p}: {c} files')
