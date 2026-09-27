# Merge parts/ web search results into all_results.csv and rebuild websites*.txt
# Search results override earlier guesses for the same shop.
import csv, glob, urllib.parse
from collections import Counter
FIELDS = ['cardshows_url', 'website', 'confidence', 'source', 'note']
rows = {r['cardshows_url']: r for r in csv.DictReader(open('all_results.csv', encoding='utf-8-sig'))}
for p in sorted(glob.glob('parts/part_*.csv')):
    for r in csv.DictReader(open(p, encoding='utf-8')):
        rows[r['cardshows_url']] = {'cardshows_url': r['cardshows_url'], 'website': r['website'],
                                    'confidence': r['confidence'], 'source': 'web search', 'note': r['note']}
out = sorted(rows.values(), key=lambda r: r['cardshows_url'])
with open('all_results.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader(); w.writerows(out)

def unique(conf):
    seen, res = set(), []
    for r in out:
        host = urllib.parse.urlsplit(r['website']).netloc.lower().removeprefix('www.')
        if conf == 'social':  # every page shares facebook.com; dedupe on the full URL
            host = r['website'].lower().rstrip('/')
        if r['confidence'] == conf and host and host not in seen:
            seen.add(host); res.append(r['website'])
    return sorted(res)
for name, conf in (('websites.txt', 'high'), ('websites_maybe.txt', 'medium'), ('websites_social.txt', 'social')):
    lst = unique(conf)
    open(name, 'w', encoding='utf-8').write('\n'.join(lst) + '\n')
    print(name, len(lst))
print(len(out), 'shops', dict(Counter(r['confidence'] for r in out)))
