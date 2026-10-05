# usage: python3 add_verify.py NN <<'X'   lines: host|verdict|platform|evidence
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
path = f'{D}/verify/v_{sys.argv[1]}.txt'
done = {l.split('|')[0] for l in open(path)} if os.path.exists(path) else set()
n = 0
with open(path, 'a') as f:
    for line in sys.stdin:
        p = (line.strip().split('|') + ['', '', ''])[:4]
        if not p[0] or p[0] in done: continue
        if p[1] not in ('sealed', 'mtg', 'no_mtg', 'not_store', 'unknown'):
            print('bad verdict, skipped:', line.strip()); continue
        done.add(p[0]); n += 1
        f.write('|'.join(x.strip() for x in p) + '\n')
print('saved', n, 'total', len(done))
