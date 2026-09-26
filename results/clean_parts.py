# Drop placeholder rows (shops never actually searched) and rebuild search_remaining.txt
import csv, glob, re
from collections import Counter
VALID = {'high', 'medium', 'social', 'none'}
FAKE = re.compile(r'budget|quota|exhausted|not searched|not researched|unable to search|could not search', re.I)
allrows = []
for p in sorted(glob.glob('parts/part_*.csv')):
    rows = list(csv.DictReader(open(p, encoding='utf-8')))
    keep = []
    for r in rows:
        if r['confidence'] not in VALID or FAKE.search(r['note']):
            continue
        if r['website'].strip().lower() == 'none':
            r['website'] = ''
        keep.append(r)
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['cardshows_url', 'website', 'confidence', 'note'])
        w.writeheader(); w.writerows(keep)
    allrows += keep
allrows += list(csv.DictReader(open('search_results.csv', encoding='utf-8')))
done = {r['cardshows_url'] for r in allrows}
todo = [l.strip() for c in sorted(glob.glob('chunks/chunk_*.txt')) for l in open(c) if l.strip()]
left = [s for s in todo if 'https://cardshows.io/shops/' + s not in done]
open('search_remaining.txt', 'w').write('\n'.join(left) + '\n')
print('searched', len(done), dict(Counter(r['confidence'] for r in allrows)), '| remaining', len(left))
