"""Run each discovery candidate through its real adapter. Prints JSON lines.
Usage: test_new_hosts.py cand.json [profile] out.jsonl [budget_s]  (tests hosts even if already in the masters)   (profile: boxes default; sealed = any MTG sealed, R53)"""
import json, sys, os, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mtgsweep import profiles, hosts as H
from mtgsweep.adapters import get_adapter
from mtgsweep.net import bare
ROUTE = {"shopify": "shopify", "woocommerce": "woocommerce", "wix": "wix", "squarespace": "squarespace", "bigcommerce": "bigcommerce",
         "shadowpos": "shadowpos", "squareonline": "squareonline", "ecwid": "lightspeed", "lightspeed_c": "lightspeed",
         "jsonld": "jsonld", "godaddy": "godaddy"}
MASTER = {"shopify": "shopify", "woocommerce": "woocommerce", "wix": "wix", "squarespace": "squarespace", "bigcommerce": "bigcommerce",
          "shadowpos": "shadowpos", "squareonline": "squareonline", "lightspeed": "lightspeed",
          "jsonld": "jsonld", "godaddy": "godaddy"}
PROFILE = sys.argv[2] if len(sys.argv) > 2 else "boxes"
prof = profiles.load(PROFILE, None)
if hasattr(prof, "load_market"): prof.load_market()
bl = H.blocklist()
known = set()
for p in H.PLATFORMS:
    known |= {bare(h) for h in H.master(p)}
cand = json.load(open(sys.argv[1]))
def one(c):
    h = bare(c["final"] or c["host"])
    if H.is_blocked(bl, h, c["host"]):
        return dict(c, verdict="blocklisted")
    route = ROUTE.get(c["platform"], "jsonld")
    try:
        r = get_adapter(route)(h, prof)
        if route == "woocommerce" and r["status"] != "ok":
            r2 = get_adapter("woocommerce_html")(h, prof)
            if r2["status"] == "ok":
                r = r2
    except Exception as e:
        return dict(c, verdict="adapter_error", err=str(e)[:100])
    return dict(c, add_host=h, route=route, master=MASTER[route], status=r["status"], country=r.get("country"),
                currency=r.get("currency") or ",".join(r.get("currencies") or []), rows=len(r["rows"]),
                tgt_in_stock=sum(1 for x in r["rows"] if x.get("target") and x.get("in_stock")), engine=r.get("engine"))
from concurrent.futures import as_completed
import time
done=set()
outp=sys.argv[3]
if os.path.exists(outp):
    for l in open(outp):
        try: done.add(json.loads(l)["host"])
        except Exception: pass
todo=[c for c in cand if c["host"] not in done]
ex = ThreadPoolExecutor(14)
futs={ex.submit(one,c):c for c in todo}
t0=time.time(); BUDGET=float(sys.argv[4]) if len(sys.argv)>4 else 1e9
with open(outp,"a") as f:
    try:
        for fu in as_completed(futs, timeout=BUDGET):
            f.write(json.dumps(fu.result())+"\n"); f.flush()
    except Exception as e:
        print("timeout/exit:", type(e).__name__, flush=True)
    for fu,c in futs.items():
        if not fu.done():
            f.write(json.dumps(dict(c, verdict="hung"))+"\n")
os._exit(0)
