# usage: python3 add.py <<'X'  then lines: slug|website|confidence|note
import csv,sys
w=csv.writer(open('/home/user/test/results/search_results.csv','a',newline='',encoding='utf-8'))
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    slug,site,conf,note=(line.split('|')+['','',''])[:4]
    w.writerow(['https://cardshows.io/shops/'+slug,site,conf,note])
