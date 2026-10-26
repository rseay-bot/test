# usage: python3 add_chain2.py NN <<'X'   lines: retailer|mtg_sealed|pokemon_sealed|how|example_url|note
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
path = f'{D}/chains2/r2_{sys.argv[1]}.txt'
n = 0
with open(path, 'a') as f:
    for line in sys.stdin:
        p = (line.strip().split('|') + [''] * 6)[:6]
        if not p[0]: continue
        if p[1] not in ('yes', 'no', 'unknown') or p[2] not in ('yes', 'no', 'unknown') or p[3] not in ('ship', 'pickup_only', 'both', 'in_store_only', 'unknown'):
            print('bad value, skipped:', line.strip()); continue
        f.write('|'.join(x.strip() for x in p) + '\n'); n += 1
print('saved', n)
