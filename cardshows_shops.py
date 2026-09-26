#!/usr/bin/env python3
"""Collect every card shop URL listed on cardshows.io.

Strategy:
  1. Read robots.txt and any sitemaps it lists (fast, complete if present).
  2. Fall back to crawling /shops -> state pages -> region pages -> shop pages,
     following pagination links.
  3. Optionally (--websites) visit each shop page and pull the shop's own
     external website link.

Standard library only. Respects robots.txt and waits between requests.

Usage:
  python3 cardshows_shops.py                     # shop page URLs -> shops.csv
  python3 cardshows_shops.py --websites          # also each shop's own site
  python3 cardshows_shops.py --delay 1.5 --out my.csv
"""
import argparse
import csv
import gzip
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from xml.etree import ElementTree

BASE = "https://cardshows.io"
UA = "Mozilla/5.0 (compatible; shop-list-collector/1.0)"
SOCIAL = ("facebook.com", "instagram.com", "twitter.com", "x.com", "tiktok.com",
          "youtube.com", "google.com", "goo.gl", "apple.com", "linkedin.com",
          "pinterest.com", "discord.gg", "discord.com", "yelp.com", "whatnot.com")


def fetch(url, delay, rp):
    if rp and not rp.can_fetch(UA, url):
        return None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                if url.endswith(".gz") or r.headers.get("Content-Encoding") == "gzip":
                    try:
                        data = gzip.decompress(data)
                    except OSError:
                        pass
                time.sleep(delay)
                return data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return None
            wait = 2 ** (attempt + 1) * (5 if e.code == 429 else 1)
            print(f"  HTTP {e.code} on {url}, retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
        except Exception as e:
            wait = 2 ** (attempt + 1)
            print(f"  {e} on {url}, retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    return None


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []  # (href, text)
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None


def links_of(html, page_url):
    p = Links()
    p.feed(html)
    out = []
    for href, text in p.links:
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        out.append((urllib.parse.urljoin(page_url, href).split("#")[0], text))
    return out


def norm(url):
    u = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((u.scheme, u.netloc.lower(), u.path.rstrip("/") or "/", u.query, ""))


def is_internal(url):
    return urllib.parse.urlsplit(url).netloc.lower() in ("cardshows.io", "www.cardshows.io")


def path_of(url):
    return urllib.parse.urlsplit(url).path.rstrip("/")


def is_listing(url):
    # /shops, /texas/shops, /texas/dallas/shops (plus ?page=N variants)
    return path_of(url).endswith("/shops") or path_of(url) == "/shops"


def is_shop_page(url):
    p = path_of(url)
    if not is_internal(url) or is_listing(url):
        return False
    if p.endswith(("/submit", "/new", "/search", "/map")):
        return False
    # Shop detail pages live under a /shops/ or /shop/ segment.
    return bool(re.search(r"/shops?/[^/]+", p))


def from_sitemaps(delay, rp):
    robots = fetch(BASE + "/robots.txt", 0, None) or ""
    maps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots) or [BASE + "/sitemap.xml"]
    seen, shops = set(), set()
    while maps:
        sm = maps.pop()
        if sm in seen:
            continue
        seen.add(sm)
        print(f"sitemap: {sm}", file=sys.stderr)
        xml = fetch(sm, delay, None)
        if not xml:
            continue
        try:
            root = ElementTree.fromstring(xml.encode())
        except ElementTree.ParseError:
            continue
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        for loc in root.iter(ns + "loc"):
            u = (loc.text or "").strip()
            if root.tag.endswith("sitemapindex"):
                maps.append(u)
            elif is_shop_page(u):
                shops.add(norm(u))
    return shops


def crawl(delay, rp):
    queue, seen, shops = [BASE + "/shops"], set(), set()
    while queue:
        url = queue.pop(0)
        if norm(url) in seen:
            continue
        seen.add(norm(url))
        html = fetch(url, delay, rp)
        if not html:
            continue
        before = len(shops)
        for link, _ in links_of(html, url):
            if not is_internal(link):
                continue
            if is_listing(link) and norm(link) not in seen:
                queue.append(link)
            elif is_shop_page(link):
                shops.add(norm(link))
        print(f"{len(seen):5d} pages | {len(shops):6d} shops (+{len(shops) - before}) | {url}",
              file=sys.stderr)
    return shops


def shop_details(url, delay, rp):
    html = fetch(url, delay, rp)
    if not html:
        return "", ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    name = re.sub(r"<[^>]+>|\s+", " ", m.group(1)).strip() if m else ""
    ext = [(l, t) for l, t in links_of(html, url)
           if l.startswith("http") and not is_internal(l)
           and not any(s in urllib.parse.urlsplit(l).netloc.lower() for s in SOCIAL)]
    for l, t in ext:
        if re.search(r"website|visit|site", t, re.I):
            return name, l
    return name, ext[0][0] if ext else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="shops.csv")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    ap.add_argument("--websites", action="store_true", help="also grab each shop's own website")
    ap.add_argument("--crawl-only", action="store_true", help="skip sitemaps")
    a = ap.parse_args()

    rp = urllib.robotparser.RobotFileParser(BASE + "/robots.txt")
    try:
        rp.read()
    except Exception:
        rp = None

    shops = set() if a.crawl_only else from_sitemaps(a.delay, rp)
    print(f"sitemaps gave {len(shops)} shop URLs", file=sys.stderr)
    if len(shops) < 1000:
        print("crawling listing pages to fill gaps...", file=sys.stderr)
        shops |= crawl(a.delay, rp)

    shops = sorted(shops)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cardshows_url", "name", "shop_website"] if a.websites else ["cardshows_url"])
        for i, u in enumerate(shops, 1):
            if a.websites:
                name, site = shop_details(u, a.delay, rp)
                w.writerow([u, name, site])
                if i % 50 == 0:
                    f.flush()
                    print(f"details {i}/{len(shops)}", file=sys.stderr)
            else:
                w.writerow([u])
    print(f"done: {len(shops)} shops -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
