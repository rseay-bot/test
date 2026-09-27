#!/usr/bin/env python3
"""Fill in card shop websites for free: verify OSM matches and guess the rest.

Needs, in the same folder:
  shop_urls.txt      every cardshows.io shop URL
  osm_verified.csv   OpenStreetMap matches sorted by verify_osm.py (optional)

What it does:
  1. Shops marked "keep" in osm_verified.csv are accepted as they are.
  2. Shops marked "check" get their OSM website opened; accepted if the page
     shows the shop's name.
  3. Every other shop gets likely addresses tried, e.g. "jerrys-rookie-shop-boise"
     -> jerrysrookieshop.com, jerrys-rookie-shop.com, ... Each address is first
     looked up in DNS (no page load); only addresses that exist are opened, and
     one is accepted only if its homepage shows the shop's name plus a card or
     game word, and is not a "domain for sale" page.

Confidence:
  high    shop name and city both appear on the site
  medium  shop name appears, city does not (could be a same-name shop elsewhere)

Outputs:
  found_websites.csv     every shop, with website, source, confidence, page title
  websites.txt           unique high-confidence websites (plus OSM "keep")
  websites_maybe.txt     unique medium-confidence websites, worth a glance

Never contacts cardshows.io. Standard library only.
Safe to stop and rerun: finished shops are skipped.

Usage:
  python3 find_websites.py
  python3 find_websites.py --limit 50     # quick test first
  python3 find_websites.py --urls search_remaining.txt   # only shops not yet resolved
"""
import argparse
import concurrent.futures as cf
import csv
import html
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (compatible; cardshop-website-finder/1.0; one homepage visit per site)"
OUT = "found_websites.csv"
COLS = ["cardshows_url", "website", "source", "confidence", "page_title"]
STOP = {"llc", "inc", "co", "ltd"}
SHOP_WORDS = {"card", "cards", "sportscards", "sports", "sport", "games", "game", "gaming",
              "comics", "comic", "collectibles", "collectables", "collectible", "tcg", "hobby",
              "hobbies", "toys", "memorabilia", "breaks", "shop", "store", "trading"}
CARD_WORDS = ("card", "tcg", "pokemon", "magic", "mtg", "comic", "collect", "hobby",
              "game", "sport", "yugioh", "onepiece", "lorcana", "memorabilia", "break")
PARKED = ("domainforsale", "buythisdomain", "isforsale", "hugedomains", "afternic",
          "sedoparking", "parkingcrew", "bodis", "domainnameforsale", "accountsuspended",
          "websiteiscomingsoon", "launchingsoon", "parkeddomain", "domainparking")
FILLER = ("the", "and")


def core(ws):
    return "".join(w for w in ws if w not in FILLER)


def words(text):
    text = text.lower().replace("&", " and ").replace("+", " and ").replace("'", "").replace("’", "")
    return [w for w in re.split(r"[^a-z0-9]+", text) if w]


def squash(text):
    return "".join(words(text))


def slug_words(url):
    return words(urllib.parse.urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1])


def candidates(url):
    """Likely domains for a shop, best guesses first, as (domain, name_words, city_words)."""
    toks = [w for w in slug_words(url) if w not in STOP]
    n = len(toks)
    out, seen = [], set()
    for k in (n - 1, n - 2, n, n - 3):  # city is usually the last 1-2 words
        if k < 1:
            continue
        name, city = toks[:k], toks[k:]
        if any(w in SHOP_WORDS for w in city):
            continue  # "cards", "games", etc. belong to the name, not the city
        variants = [name]
        if name[0] == "the" and len(name) > 1:
            variants.append(name[1:])
        if "and" in name:
            variants.append([w for w in name if w != "and"])
        for v in variants:
            for d in ("".join(v) + ".com", "-".join(v) + ".com", "".join(v) + ".net"):
                if len(core(name)) >= 6 and d not in seen:  # too short to verify
                    seen.add(d)
                    out.append((d, name, city))
    return out


def resolves(domain):
    try:
        socket.getaddrinfo(domain, 443)
        return True
    except (socket.gaierror, UnicodeError, OSError):
        return False


def fetch(url):
    """Return (final_url, html) or (None, None)."""
    ctx = ssl.create_default_context()
    tries = [url] if url.startswith("http") else ["https://" + url, "http://" + url]
    for u in tries:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                if "html" not in r.headers.get("Content-Type", "html"):
                    return None, None
                return r.geturl(), r.read(600_000).decode("utf-8", "replace")
        except ssl.SSLError:
            if u.startswith("https://"):
                tries.append("http://" + u[8:])
        except Exception:
            continue
    return None, None


def page_facts(doc, site_url):
    m = re.search(r"<title[^>]*>(.*?)</title>", doc, re.S | re.I)
    title = " ".join(html.unescape(m.group(1)).split())[:120] if m else ""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", doc, flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text)) + " " + title
    # a parked or default page repeats its own address; don't count that as the name
    host = urllib.parse.urlsplit(site_url if "//" in site_url else "//" + site_url).netloc
    host = host.lower().removeprefix("www.")
    base = host.rsplit(".", 1)[0]
    text = re.sub(re.escape(host) + "|" + re.escape(base) + r"\.[a-z]{2,6}", " ", text, flags=re.I)
    return title, core(words(text))


def judge(doc, site_url, name, city):
    """Return (confidence or None, title)."""
    title, flat = page_facts(doc, site_url)
    if any(p in flat for p in PARKED):
        return None, title
    key = core(name)
    if len(key) < 6 or key not in flat:
        return None, title
    if not any(c in flat.replace(key, " ") for c in CARD_WORDS):
        return None, title
    city_key = core(city)
    return ("high" if city_key and city_key in flat else "medium"), title


def verify_known(url, website, osm_name):
    final, doc = fetch(website)
    if not doc:
        return None
    slug = slug_words(url)
    name = words(osm_name)
    squashed = core(name)
    joined, rest = "", []
    for i, w in enumerate(slug):
        joined += w if w not in FILLER else ""
        if joined == squashed:
            rest = slug[i + 1:]
            break
    conf, title = judge(doc, final, name, rest)
    if conf:
        return {"website": final, "source": "osm, verified on site", "confidence": conf,
                "page_title": title}
    return None


def guess(url):
    for domain, name, city in candidates(url):
        if not resolves(domain):
            continue
        final, doc = fetch(domain)
        if not doc:
            continue
        conf, title = judge(doc, final, name, city)
        if conf:
            return {"website": final, "source": f"guessed {domain}", "confidence": conf,
                    "page_title": title}
    return None


def clean(url):
    u = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((u.scheme, u.netloc.lower(), u.path.rstrip("/"), "", ""))


def load_csv(path):
    try:
        raw = open(path, "rb").read()
    except FileNotFoundError:
        return []
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", "replace")
    return list(csv.DictReader(text.splitlines()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only process this many shops (test)")
    ap.add_argument("--workers", type=int, default=16, help="sites checked at once")
    ap.add_argument("--urls", default="shop_urls.txt",
                    help="list of shops to process (full URLs or bare slugs), e.g. search_remaining.txt")
    a = ap.parse_args()

    with open(a.urls, encoding="utf-8", errors="replace") as f:
        urls = [l.strip() for l in f if l.strip()]
    urls = [u if u.startswith("http") else "https://cardshows.io/shops/" + u for u in urls]
    osm = {r["cardshows_url"]: r for r in load_csv("osm_verified.csv")}
    if not osm:
        print("note: osm_verified.csv not found, guessing for every shop", file=sys.stderr)
    done = {r["cardshows_url"]: r for r in load_csv(OUT)}
    todo = [u for u in urls if u not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"{len(done)} already done, {len(todo)} to process", file=sys.stderr)

    def work(url):
        o = osm.get(url)
        if o and o.get("verdict") == "keep":
            res = {"website": o["website"], "source": "osm, name and city match",
                   "confidence": "high", "page_title": ""}
        else:
            res = None
            if o and o.get("verdict") == "check":
                res = verify_known(url, o["website"], o["osm_name"])
            res = res or guess(url) or {"website": "", "source": "not found",
                                        "confidence": "", "page_title": ""}
        if res["website"]:
            res["website"] = clean(res["website"])
        return {"cardshows_url": url, **res}

    counts = {"high": 0, "medium": 0, "": 0}
    new_file = not done
    with open(OUT, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new_file:
            w.writeheader()
        pool = cf.ThreadPoolExecutor(max_workers=a.workers)
        step = a.workers * 2  # small batches so Ctrl+C stops quickly
        i = 0
        try:
            for start in range(0, len(todo), step):
                for row in pool.map(work, todo[start:start + step]):
                    i += 1
                    w.writerow(row)
                    done[row["cardshows_url"]] = row
                    counts[row["confidence"]] = counts.get(row["confidence"], 0) + 1
                f.flush()
                print(f"{i}/{len(todo)}  high {counts['high']}, medium {counts['medium']}, "
                      f"none {counts['']}", file=sys.stderr)
        except KeyboardInterrupt:
            pool.shutdown(wait=False, cancel_futures=True)
            f.flush()
            sys.exit("\nStopped. Progress is saved; run the same command to continue.")
        pool.shutdown()

    def unique(conf):
        seen, out = set(), []
        for r in done.values():
            host = urllib.parse.urlsplit(r["website"]).netloc.removeprefix("www.")
            if r["confidence"] == conf and host and host not in seen:
                seen.add(host)
                out.append(r["website"])
        return sorted(out)
    high, medium = unique("high"), unique("medium")
    with open("websites.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(high) + "\n")
    with open("websites_maybe.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(medium) + "\n")
    total = {c: sum(r["confidence"] == c for r in done.values()) for c in ("high", "medium", "")}
    print(f"\ndone: {len(done)} shops. {total['high']} high, {total['medium']} medium, "
          f"{total['']} not found.\n{len(high)} websites -> websites.txt, "
          f"{len(medium)} -> websites_maybe.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
