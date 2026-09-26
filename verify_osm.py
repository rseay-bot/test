#!/usr/bin/env python3
"""Sort osm_results.csv matches into keep / check / reject.

keep   = slug is "<OSM name> <city>" and the city matches
check  = name matches but the city differs or is missing in OSM, the name is
         a single generic word, or one website matched several locations
         (a real chain, or unrelated shops sharing a common name)
reject = OSM name only partly matches the shop name

Usage: python3 verify_osm.py osm_results.csv
Writes osm_verified.csv, websites.txt (keep only) and websites_check.txt.
"""
import csv
import re
import sys
import urllib.parse
from collections import defaultdict

STOP = {"the", "and", "of", "llc", "inc", "co", "a"}
SHOP_WORDS = {"card", "cards", "sports", "sportscards", "comics", "comic", "games", "game",
              "gaming", "collectibles", "collectible", "tcg", "llc", "hobbies", "hobby",
              "company", "trading", "toys", "memorabilia", "breaks", "shop", "store",
              "records", "vinyl", "music", "more", "coins", "coin"}


def words(text):
    text = text.lower().replace("&", " and ").replace("+", " and ").replace("'", "").replace("’", "")
    return [w for w in re.split(r"[^a-z0-9]+", text) if w and w not in STOP]


def classify(row):
    slug = words(urllib.parse.urlsplit(row["cardshows_url"]).path.rsplit("/", 1)[-1])
    name = "".join(words(row["osm_name"]))
    joined = ""
    for i, w in enumerate(slug):
        joined += w
        if joined == name:
            rest = slug[i + 1:]
            break
        if len(joined) >= len(name):
            return None, "OSM name only partly matches"
    else:
        return None, "OSM name only partly matches"
    if any(w in SHOP_WORDS for w in rest) or len(rest) > 6:
        return None, "shop name has extra words OSM name lacks"
    return rest, ""


def main(path):
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", "replace")  # file saved by an older Windows run
    rows = list(csv.DictReader(text.splitlines()))
    parsed = {}
    for r in rows:
        parsed[r["cardshows_url"]] = classify(r)

    by_site = defaultdict(list)
    for r in rows:
        rest, _ = parsed[r["cardshows_url"]]
        if rest is not None:
            by_site[r["website"]].append((r, rest))

    out = []
    for r in rows:
        rest, why = parsed[r["cardshows_url"]]
        city = "".join(words(r["city"]))
        group = by_site[r["website"]]
        if rest is None:
            verdict = "reject"
        elif re.search(r"facebook\.com|instagram\.com", r["website"]):
            verdict, why = "check", "social media page, not a website"
        elif rest and "".join(rest) == city:
            verdict, why = "keep", "name and city match"
        elif len(words(r["osm_name"])) < 2:
            verdict, why = "check", "one-word name, too generic to trust"
        elif (len(group) >= 3 and not any("".join(g[1]) == city for g in group)):
            verdict, why = "check", (f"chain or common name, same website matched "
                                     f"{len(group)} locations")
        elif not r["city"]:
            verdict, why = "check", f"name matches, but OSM gives no city (state {r['state']})"
        else:
            verdict, why = "check", f"name matches but OSM location is {r['city']}, {r['state']}"
        out.append({**r, "verdict": verdict, "reason": why})

    with open("osm_verified.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + ["verdict", "reason"])
        w.writeheader()
        w.writerows(sorted(out, key=lambda r: ("keep check reject".split().index(r["verdict"]),
                                                r["cardshows_url"])))

    def uniq(v):
        seen, sites = set(), []
        for r in out:
            host = urllib.parse.urlsplit(r["website"]).netloc.lower().removeprefix("www.")
            if r["verdict"] == v and host not in seen:
                seen.add(host)
                sites.append(r["website"])
        return sorted(sites)
    keep, check = uniq("keep"), uniq("check")
    with open("websites.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(keep) + "\n")
    with open("websites_check.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(check) + "\n")
    n = {v: sum(r["verdict"] == v for r in out) for v in ("keep", "check", "reject")}
    print(f"keep {n['keep']}, check {n['check']}, reject {n['reject']}. "
          f"{len(keep)} trusted websites -> websites.txt, "
          f"{len(check)} to eyeball -> websites_check.txt")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "osm_results.csv")
