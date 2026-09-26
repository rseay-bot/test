#!/usr/bin/env python3
"""Find each card shop's own website with the Google Places API (New).

Reads shop_urls.txt (made by cardshows_shops.py), turns each URL's
"/shops/{name}-{city}" slug into a search like "jerrys rookie shop boise",
and asks Google Places for the matching business and its website.
Never contacts cardshows.io.

Outputs:
  places_results.csv  one row per shop, with a match rating:
                      high = Google's business name clearly matches the shop
                      low  = partial match, worth a quick look
                      none = nothing usable found
  websites.txt        unique websites from "high" and "low" matches

Standard library only. Safe to stop and rerun: finished rows are skipped.
Cost: each lookup is one Text Search Enterprise request (websiteUri field).

Usage:
  python3 places_websites.py --key YOUR_API_KEY
  python3 places_websites.py --key YOUR_API_KEY --limit 20   # small test first
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
FIELDS = "places.displayName,places.formattedAddress,places.websiteUri,places.types"
PRICE_PER_1000 = 35.00  # Text Search Enterprise, first 100k/month
FREE_PER_MONTH = 1000
OUT = "places_results.csv"
COLS = ["cardshows_url", "query", "match", "google_name", "address", "website"]
STOP = {"the", "and", "of", "llc", "inc", "co", "a"}


def words(text):
    text = text.lower().replace("&", " and ").replace("'", "").replace("’", "")
    return [w for w in re.split(r"[^a-z0-9]+", text) if w]


def slug_query(url):
    slug = urllib.parse.urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1]
    return " ".join(slug.split("-"))


def score(query, place):
    """Share of the Google business name's words that appear in the slug."""
    q = set(words(query))
    name = [w for w in words(place.get("displayName", {}).get("text", "")) if w not in STOP]
    if not name:
        return 0.0
    hit = sum(1 for w in name if w in q or (w.endswith("s") and w[:-1] in q) or w + "s" in q)
    return hit / len(name)


def lookup(query, key):
    body = json.dumps({"textQuery": query, "regionCode": "US", "pageSize": 5}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": FIELDS,
    })
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r).get("places", [])
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:300]
            if e.code in (400, 401, 403):
                sys.exit(f"Google rejected the request (HTTP {e.code}). Check the API key "
                         f"and that 'Places API (New)' is enabled.\n{msg}")
            wait = 2 ** (attempt + 1)
            print(f"  HTTP {e.code}, retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
        except Exception as e:
            wait = 2 ** (attempt + 1)
            print(f"  {e}, retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    sys.exit("Too many failures talking to Google. Progress is saved; rerun later.")


def best(query, places):
    if not places:
        return "none", {}
    top = max(places, key=lambda p: score(query, p))
    s = score(query, top)
    return ("high" if s >= 0.75 else "low" if s >= 0.4 else "none"), top


def clean_site(url):
    u = urllib.parse.urlsplit(url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query)
         if not k.lower().startswith("utm_") and k.lower() not in ("ref", "source")]
    return urllib.parse.urlunsplit((u.scheme, u.netloc.lower(), u.path.rstrip("/"),
                                    urllib.parse.urlencode(q), ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("GOOGLE_MAPS_API_KEY"), help="Google API key")
    ap.add_argument("--urls", default="shop_urls.txt")
    ap.add_argument("--limit", type=int, default=0, help="only look up this many (for a test)")
    ap.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    a = ap.parse_args()
    if not a.key:
        sys.exit("Missing API key. Run: python3 places_websites.py --key YOUR_API_KEY")

    with open(a.urls) as f:
        urls = [l.strip() for l in f if l.strip()]
    done = {}
    try:
        with open(OUT, newline="") as f:
            for row in csv.DictReader(f):
                done[row["cardshows_url"]] = row
    except FileNotFoundError:
        pass
    todo = [u for u in urls if u not in done]
    if a.limit:
        todo = todo[:a.limit]

    cost = max(0, len(todo) - FREE_PER_MONTH) * PRICE_PER_1000 / 1000
    print(f"{len(done)} already done, {len(todo)} to look up.\n"
          f"Estimated Google charge: about ${cost:.0f} "
          f"(first {FREE_PER_MONTH} lookups each month are free).", file=sys.stderr)
    if todo and not a.yes and input("Type yes to continue: ").strip().lower() != "yes":
        sys.exit("Cancelled.")

    with open(OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if not done:
            w.writeheader()
        for i, url in enumerate(todo, 1):
            q = slug_query(url)
            match, p = best(q, lookup(q, a.key))
            row = {"cardshows_url": url, "query": q, "match": match,
                   "google_name": p.get("displayName", {}).get("text", ""),
                   "address": p.get("formattedAddress", ""),
                   "website": clean_site(p["websiteUri"]) if p.get("websiteUri") else ""}
            w.writerow(row)
            done[url] = row
            if i % 25 == 0 or i == len(todo):
                f.flush()
                print(f"{i}/{len(todo)}  last: {q} -> {match} {row['website']}", file=sys.stderr)
            time.sleep(0.1)

    sites, hosts = [], set()
    counts = {"high": 0, "low": 0, "none": 0}
    for row in done.values():
        counts[row["match"]] = counts.get(row["match"], 0) + 1
        host = urllib.parse.urlsplit(row["website"]).netloc.removeprefix("www.")
        if row["website"] and row["match"] in ("high", "low") and host not in hosts:
            hosts.add(host)
            sites.append(row["website"])
    with open("websites.txt", "w") as f:
        f.write("\n".join(sorted(sites)) + "\n")
    print(f"done: {counts['high']} high, {counts['low']} low, {counts['none']} no match. "
          f"{len(sites)} unique websites -> websites.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
