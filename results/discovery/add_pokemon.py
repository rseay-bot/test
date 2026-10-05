# usage: python3 add_pokemon.py NN <<'X'   lines: host|verdict|evidence
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
path = f'{D}/pokemon/p_{sys.argv[1]}.txt'
done = {l.split('|')[0] for l in open(path)} if os.path.exists(path) else set()
n = 0
with open(path, 'a') as f:
    for line in sys.stdin:
        p = (line.strip().split('|') + ['', '', ''])[:3]
        if not p[0] or p[0] in done: continue
        if p[1] not in ('pokemon_sealed', 'pokemon_other', 'no_pokemon', 'unknown'):
            print('bad verdict, skipped:', line.strip()); continue
        done.add(p[0]); n += 1
        f.write('|'.join(x.strip() for x in p) + '\n')
print('saved', n, 'total', len(done))
