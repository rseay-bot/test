# usage: python3 add_part.py NN <<'X'
#   slug|website|confidence|note     (one line per shop)
import csv, sys, os
part = sys.argv[1]
path = f'/home/user/test/results/parts/part_{part}.csv'
new = not os.path.exists(path)
with open(path, 'a', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    if new:
        w.writerow(['cardshows_url', 'website', 'confidence', 'note'])
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        slug, site, conf, note = (line.split('|') + ['', '', ''])[:4]
        w.writerow(['https://cardshows.io/shops/' + slug.strip(), site.strip(), conf.strip(), note.strip()])
