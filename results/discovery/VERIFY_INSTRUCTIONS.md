# Verify candidate hosts sell MTG sealed online (search only)

Input: /home/user/test/results/discovery/verify/q_NN.txt (one host per line).
Use ONLY WebSearch. Do NOT WebFetch or curl store sites (the network blocks them).

For EVERY host, in order:
1. Search `site:HOST magic the gathering booster` (pass allowed_domains: ["HOST"]).
2. If that returns nothing useful, ONE more: `site:HOST mtg` (allowed_domains ["HOST"]).
   If still nothing, ONE open search `HOST` (no domain filter) to see what the business is.
Decide from result titles, URLs and snippets:
- sealed: product pages for MTG sealed items (booster box, bundle, commander deck, collector
  booster, play booster, Secret Lair, prerelease) with a shop URL pattern (/products/,
  /product/, /shop/, /store/, /collections/, add to cart, price). Online store confirmed.
- mtg: the site sells or mentions MTG but no sealed product page seen (singles only, events only).
- no_mtg: a real store but no MTG at all (sports cards only, Pokemon only, comics only, etc.).
- not_store: not a retail store, no online shop, parked, closed, or not US.
- unknown: nothing indexed.
Platform guess from URLs: /collections/ or /products/ = shopify, /product/ + ?add-to-cart = woocommerce,
square.site or /shop/p/ = square, wixsite or /product-page/ = wix, crystalcommerce, etc. Else unknown.

Save after every 10 hosts:

    python3 /home/user/test/results/discovery/add_verify.py NN <<'EOF'
    host|verdict|platform|evidence (one short phrase, e.g. "MH3 play booster box product page")
    EOF

No | inside fields. Every host gets exactly one line. If WebSearch fails (budget or any error),
STOP immediately; never write rows for hosts you did not search. Do not git commit.
Final reply ONLY: `verify NN: S sealed, M mtg, N no_mtg, X not_store, U unknown (total T)`
