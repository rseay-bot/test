# Handoff: card shop and MTG sealed store search (as of 2026-10-26)

Repo: rseay-bot/test, branch claude/nice-shannon-vxwktp. All work is committed and pushed.
Target app: https://alerts.power10cards.com (project "CBBs NOW"). The session could not open
the site or the project, so how the site is fed with stores is UNKNOWN. Ask the user.

## Session limits to know
- Store sites, Reddit, the Wizards locator and TCGplayer API are blocked from the cloud session. Only
  web search works (US results only). Search cannot see stock or prices.
- Running many search helpers at once hits rate and usage limits. Run searches one at a time, 3 or 4 helpers.

## 1. cardshows.io shop websites (results/)
- All 4,165 shops resolved: 2,769 own website, 184 medium, 709 social only, 503 none.
- Lists: websites.txt (2,542), websites_maybe.txt (134), websites_social.txt (706), all_results.csv.
- Scripts: clean_parts.py, merge_parts.py. README.md is current.

## 2. New MTG sealed stores (results/discovery/), all by web search
- Place searches (states, cities): 226 candidates. Product-title searches (booster boxes and Commander
  precon decks per set and deck): 110 stores, each with a sealed product page. Round 2 ran 6 of 14
  query files (product2/qq_00 to 05); qq_06 to qq_13 not run (about 3 stores each, low yield).
- Verification by search (verify/): 637 of 1,173 candidates checked, 93 confirmed MTG sealed sellers,
  255 carry MTG with no sealed page seen. 536 unchecked (mostly sports-card shops, about 1 in 20 hit).
- Pokemon sealed check (pokemon/): 549 hosts, 77 sell Pokemon sealed, 53 sell both, 117 either.
- Key files: product_search_stores.txt (110), new_sealed_candidates.txt (336), stores_combined.csv (600
  with both verdicts), stores_sealed_either.txt (117), unknown_platform_stores.txt (23, platform unknown).

## 3. Retailer chains (results/discovery/retailers_combined.csv)
- 92 retailers: 24 carry both MTG and Pokemon (Walmart, Target, Kroger, CVS, Walgreens, Meijer, Costco, Sam's
  Club, Best Buy, Barnes & Noble and others), 9 MTG only, 48 Pokemon only (Ace Hardware, Lowe's, Menards,
  7-Eleven, Circle K, Wawa, Cracker Barrel, TJ Maxx, Hobby Lobby, Michaels, Five Below and others), 11 neither shown.
- A few non-US rows slipped in (Australia, Canada). Most are shelf stock only, not online listings.
- The sweep tool had a rule excluding big-box and national chains. The user now wants chains tracked; that
  needs a decision on how (the tool has no readers for them, and per-store stock is mostly not public).

## 4. Sweep tool update (artifact claude.ai/artifact/LkJVcAgVbr3gM47tRgc6wd, version 22, label R59)
- Added 67 product-search stores to the host lists: 43 Shopify, 15 WooCommerce, 8 Wix, 1 BigCommerce.
  EXPECTED counts in mtgsweep/hosts.py updated. Routes are UNTESTED (store sites unreachable here).
- Left out of the 110: 16 already present, 3 name twins (tatesgaming.company.site, waywardcitygames.com,
  greatescapeadventures.com), 1 possibly non-US (tistaminis.com), 23 unknown platform.
- Staged files: results/discovery/sweep_update/ and sweep_add_plan.json.

## Open items
1. How does alerts.power10cards.com get its stores (does it read the sweep tool lists)? Add stores there.
2. Run the sweep tool (python3 -m mtgsweep run --profile sealed) from a machine with internet on the new
   hosts and on the 23 unknown-platform ones, then check preflight.
3. Decide on chains (Ace, etc.) and which of the 17 retailers marked as selling online to follow up.
4. Optional: round 2 files qq_06 to qq_13, the 536 unchecked candidates, the store-locator mining step.
5. Reddit stores: the user can paste store names or links; dedupe with results/discovery/check_hosts.py.
