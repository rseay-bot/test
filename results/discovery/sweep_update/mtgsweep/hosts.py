"""Host masters, blocklist, pending non-US list, and the pre-flight census checks."""
import os, re
from .net import bare

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
HOSTS = os.path.join(DATA, "hosts")

PLATFORMS = ("shopify", "woocommerce", "shadowpos", "wix", "bigcommerce", "squarespace", "crystalcommerce",
             "squareonline", "lightspeed", "jsonld", "godaddy", "retailer")

# Expected master sizes after the 2026-09-23 purge, R46/R47 intakes, R48 blocks, R51 Square/Lightspeed routes + discovery, R52 WPN/Ravensburger/locator intake + JSON-LD route, R53 GoDaddy store route (+22), headless Shopify (+3), big-retailer route (3), R54 comic shop / Konami intake (+20), R55 Overture Maps intake (+793), R59 product-title web search intake (+67), R59c preorder-search intake (+4), R59b search-verified intake (+40). A mismatch means a bad reload or an unrecorded edit.
EXPECTED = {"shopify": 2848, "woocommerce": 931, "shadowpos": 59, "wix": 407, "bigcommerce": 113,
            "squarespace": 558, "crystalcommerce": 698, "blocklist": 956,
            "squareonline": 828, "lightspeed": 204, "jsonld": 72, "godaddy": 138, "retailer": 3}

# CrystalCommerce infrastructure / exchange sub-sites, not storefronts
CC_INFRA = re.compile(r"^(cdn\d*|crystal-cdn\d*|cloudfront|ns\d+|store|explore|expo\w*|exchange[\w-]*|"
                      r"[\w-]+-exchange|frontend\.prd|fw\.prd|cdmgmt|boost[\w-]*|cloudy\w*|noriadv|trowaadv|"
                      r"distributorstore|manufacturerstore|tcgbuylist|bluedefault)\.crystalcommerce\.(com|info)$")


def _lines(path):
    with open(path) as f:
        return [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]


def blocklist():
    return set(_lines(os.path.join(DATA, "blocklist.txt")))


def pending_non_us():
    p = os.path.join(DATA, "pending_non_us.txt")
    return set(_lines(p)) if os.path.exists(p) else set()


def is_blocked(bl, *hosts):
    for h in hosts:
        if not h:
            continue
        h = h.lower()
        if h in bl or bare(h) in bl or ("www." + bare(h)) in bl:
            return True
    return False


def master(platform):
    return _lines(os.path.join(HOSTS, f"{platform}.txt"))


def load(platform, bl=None):
    """Master hosts for a platform, blocklist applied (rule 0, place 1 of 3)."""
    bl = blocklist() if bl is None else bl
    hs = [h for h in master(platform) if not is_blocked(bl, h)]
    if platform == "crystalcommerce":
        hs = [h for h in hs if not CC_INFRA.match(h)]
    seen, out = set(), []
    for h in hs:
        if h not in seen:
            seen.add(h); out.append(h)
    return out


def preflight():
    """Skill session-start checks 3, 4 and 6: counts, blocklist/master overlap, duplicates.
    Returns (ok, lines)."""
    lines, ok = [], True
    bl = blocklist()
    n = len(bl)
    lines.append(f"blocklist: {n} hosts (expected {EXPECTED['blocklist']})")
    if n != EXPECTED["blocklist"]:
        lines.append("  WARN blocklist count differs from expected; recount and update EXPECTED if intended")
        ok = False
    for p in PLATFORMS:
        path = os.path.join(HOSTS, f"{p}.txt")
        if not os.path.exists(path):
            lines.append(f"{p}: MISSING {path}"); ok = False; continue
        m = master(p)
        over = [h for h in m if is_blocked(bl, h)]
        dup = len(m) - len(set(m))
        exp = EXPECTED.get(p)
        flag = "" if exp is None or len(m) == exp else f"  WARN expected {exp}"
        lines.append(f"{p}: {len(m)} hosts, {len(over)} blocklisted still in master, {dup} duplicates{flag}")
        if over:
            ok = False
            lines.append("  remove from master: " + ", ".join(over[:20]))
        if flag:
            ok = False
    return ok, lines
