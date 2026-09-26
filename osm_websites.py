#!/usr/bin/env python3
"""Find card shop websites for free using OpenStreetMap.

Downloads game, hobby, collectible, comic and trading card shops in each US
state from the public Overpass API (free, no key), then matches them to the
shops in shop_urls.txt by name and city.

Outputs:
  osm_results.csv  one row per matched shop, with a match rating
                   high = name and city match
                   low  = name matches but city could not be confirmed
  websites.txt     unique websites from all matches
  not_found.txt    cardshows.io URLs with no website in OpenStreetMap
                   (feed these to places_websites.py --urls not_found.txt)

Standard library only. Downloads are cached in osm_cache/, so reruns are fast.

Usage:
  python3 osm_websites.py
"""
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Public Overpass servers; the script rotates to the next one when a server is busy.
MIRRORS = ["https://overpass-api.de/api/interpreter",
           "https://overpass.private.coffee/api/interpreter",
           "https://overpass.kumi.systems/api/interpreter"]
UA = "cardshop-website-finder/1.0 (personal research)"
STATES = ("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT "
          "NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR").split()
SHOP_TYPES = "games|collector|hobby|toys|trade|comic|anime|video_games|second_hand|variety_store"
NAME_HINT = "card|tcg|pokemon|magic|game|gaming|collect|comic|hobby|sports|memorabilia|breaks"
STOP = {"the", "and", "of", "llc", "inc", "co", "a"}
CACHE = "osm_cache"


def query(state):
    return f"""[out:json][timeout:300];
area["ISO3166-2"="US-{state}"]->.s;
(
  nwr["shop"~"^({SHOP_TYPES})$"](area.s);
  nwr["shop"]["name"~"{NAME_HINT}",i](area.s);
);
out tags;"""


def fetch_state(state):
    path = os.path.join(CACHE, f"{state}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    data = urllib.parse.urlencode({"data": query(state)}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(MIRRORS[attempt % len(MIRRORS)], data=data,
                                         headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=360) as r:
                body = json.load(r)
            remark = body.get("remark", "")
            if "error" in remark.lower() or "timed out" in remark.lower():
                raise RuntimeError(f"incomplete answer ({remark[:80]})")
            elements = body.get("elements", [])
            os.makedirs(CACHE, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(elements, f)
            time.sleep(5)  # be polite to the free public server
            return elements
        except urllib.error.HTTPError as e:
            wait = 30 if e.code in (429, 504) else 10
            nxt = urllib.parse.urlsplit(MIRRORS[(attempt + 1) % len(MIRRORS)]).netloc
            print(f"  {state}: HTTP {e.code} (server busy), trying {nxt} in {wait}s",
                  file=sys.stderr)
            time.sleep(wait)
        except Exception as e:
            wait = 10 * (attempt + 1)
            print(f"  {state}: {e}, waiting {wait}s", file=sys.stderr)
            time.sleep(wait)
    print(f"  {state}: skipped after repeated failures (rerun later to retry)", file=sys.stderr)
    return None


def words(text):
    text = text.lower().replace("&", " and ").replace("'", "").replace("’", "")
    out = [w for w in re.split(r"[^a-z0-9]+", text) if w]
    return out[1:] if out[:1] == ["the"] else out


def website(tags):
    for k in ("website", "contact:website", "url"):
        v = tags.get(k, "").split(";")[0].strip()
        if v:
            return v if v.startswith("http") else "https://" + v
    return ""


def main():
    osm = []  # (name_words, city_words, name, city, state, website)
    failed = []
    for i, st in enumerate(STATES, 1):
        els = fetch_state(st)
        if els is None:
            failed.append(st)
            continue
        n = 0
        for e in els:
            t = e.get("tags", {})
            site = website(t)
            if not site or not t.get("name"):
                continue
            osm.append((words(t["name"]), words(t.get("addr:city", "")),
                        t["name"], t.get("addr:city", ""), st, site))
            n += 1
        print(f"{i:2d}/{len(STATES)} {st}: {n} shops with websites", file=sys.stderr)

    # index OSM shops by first name word for fast lookup
    index = {}
    for rec in osm:
        if rec[0]:
            index.setdefault(rec[0][0], []).append(rec)

    with open("shop_urls.txt", encoding="utf-8", errors="replace") as f:
        urls = [l.strip() for l in f if l.strip()]

    rows, missing = [], []
    for url in urls:
        slug = words(urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1])
        best, best_rank = None, 0
        for rec in index.get(slug[0], []) if slug else []:
            name, city = rec[0], rec[1]
            core = [w for w in name if w not in STOP]
            if slug[:len(name)] == name:          # slug is "<name> <city>"
                rest = slug[len(name):]
                rank = 3 if city and rest == city else 2 if not city or not rest else 1
            elif core and all(w in slug for w in core):
                rank = 1
            else:
                continue
            if rank > best_rank:
                best, best_rank = rec, rank
        if best and best_rank >= 2:
            match = "high" if best_rank == 3 else "low"
        elif best:
            match = "low"
        else:
            missing.append(url)
            continue
        rows.append({"cardshows_url": url, "match": match, "osm_name": best[2],
                     "city": best[3], "state": best[4], "website": best[5]})

    with open("osm_results.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["cardshows_url", "match", "osm_name", "city",
                                          "state", "website"])
        w.writeheader()
        w.writerows(rows)
    sites, hosts = [], set()
    for r in rows:
        host = urllib.parse.urlsplit(r["website"]).netloc.lower().removeprefix("www.")
        if host and host not in hosts:
            hosts.add(host)
            sites.append(r["website"])
    with open("websites.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(sites)) + "\n")
    with open("not_found.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(missing) + "\n")

    high = sum(r["match"] == "high" for r in rows)
    print(f"\ndone: {len(rows)} of {len(urls)} shops matched ({high} high, "
          f"{len(rows) - high} low). {len(sites)} unique websites -> websites.txt\n"
          f"{len(missing)} shops not found -> not_found.txt", file=sys.stderr)
    if failed:
        print(f"states that failed to download: {' '.join(failed)}. Rerun to retry.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
