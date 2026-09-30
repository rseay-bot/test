# usage: python3 check_hosts.py host1 host2 ...   prints NEW or KNOWN per host
import sys, os, glob, urllib.parse
D = os.path.dirname(os.path.abspath(__file__))
def host(u):
    u = u.strip().lower()
    if '//' not in u: u = 'http://' + u
    return urllib.parse.urlsplit(u).netloc.removeprefix('www.')
seen = {host(l) for l in open(f'{D}/known_hosts.txt') if l.strip()}
for f in glob.glob(f'{D}/found/*.txt'):
    seen |= {host(l.split('|')[0]) for l in open(f) if l.strip()}
for a in sys.argv[1:]: print(host(a), 'KNOWN' if host(a) in seen else 'NEW')
