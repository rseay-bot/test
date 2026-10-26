# usage: python3 add_chain.py NN <<'X'   lines: retailer|mtg|pokemon|online|evidence_url|note
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
path = f'{D}/chains/r_{sys.argv[1]}.txt'
n = 0
with open(path, 'a') as f:
    for line in sys.stdin:
        p = (line.strip().split('|') + [''] * 6)[:6]
        if not p[0]: continue
        if p[1] not in ('yes', 'no', 'unknown') or p[2] not in ('yes', 'no', 'unknown'):
            print('bad mtg/pokemon value, skipped:', line.strip()); continue
        f.write('|'.join(x.strip() for x in p) + '\n'); n += 1
print('saved', n)
