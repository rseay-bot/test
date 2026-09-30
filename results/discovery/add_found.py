# usage: python3 add_found.py NN <<'X'
#   host|platform|note    one line per NEW store that sells MTG sealed online
# Skips hosts already in the census, blocklist, or found files. Prints what was kept.
import sys, os, glob, re, urllib.parse
D = os.path.dirname(os.path.abspath(__file__))
def host(u):
    u = u.strip().lower()
    if '//' not in u: u = 'http://' + u
    return urllib.parse.urlsplit(u).netloc.removeprefix('www.')
seen = {host(l) for l in open(f'{D}/known_hosts.txt') if l.strip()}
for f in glob.glob(f'{D}/found/*.txt'):
    seen |= {host(l.split('|')[0]) for l in open(f) if l.strip()}
out = open(f'{D}/found/found_{sys.argv[1]}.txt', 'a')
kept = dup = 0
for line in sys.stdin:
    if not line.strip(): continue
    p = (line.strip().split('|') + ['', ''])[:3]
    h = host(p[0])
    if not h or h in seen: dup += 1; continue
    seen.add(h); kept += 1
    out.write(f'{h}|{p[1].strip()}|{p[2].strip()}\n')
print(f'kept {kept}, already known {dup}')
