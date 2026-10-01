# Sealed MTG store discovery: helper instructions

Goal: find US online stores that sell Magic: The Gathering SEALED product (booster boxes,
bundles, Commander decks, Secret Lair, prerelease kits, collector boosters) and are NOT
already in our census. Use ONLY the WebSearch tool. Do NOT use WebFetch or curl on store sites
(the network blocks them).

CITY MODE: your input is /home/user/test/results/discovery/cities_NN.txt (one "City ST" per line).
For EVERY city run these 3 searches (substitute CITY, e.g. `Tulsa OK`), with blocked_domains below:
1. `CITY game store Magic the Gathering booster box shop online`
2. `CITY MTG sealed product local game store website`
3. `CITY comic card shop Magic the Gathering Commander decks buy`
After finishing each city run: `echo "City ST" >> /home/user/test/results/discovery/cities_NN_done.txt`
Skip any city already listed in cities_NN_done.txt.
Do a 4th varied query only if the first three turn up 3+ NEW stores (the area is rich).

blocked_domains on every search:
["cardshows.io","yelp.com","facebook.com","instagram.com","reddit.com","youtube.com","tcgplayer.com","ebay.com","amazon.com","walmart.com","target.com","gamestop.com","bestbuy.com","costco.com","mapquest.com","yellowpages.com","tiktok.com","pinterest.com","wizards.com","cardkingdom.com","coolstuffinc.com","miniaturemarket.com","starcitygames.com","cardhoarder.com","mtggoldfish.com","whatnot.com","etsy.com","mercari.com","linkedin.com","tripadvisor.com","bbb.org","nextdoor.com"]

What counts: a store with its OWN website (own domain, or a shop on Shopify / Square / Wix /
Squarespace / WooCommerce / BigCommerce etc.) that appears to sell MTG sealed product online.
US stores only (skip Canada, UK, EU, AU). Skip marketplaces, price guides, blogs, news, big-box
and national chains, non-hobby businesses, singles-only sites, TCGplayer Pro storefronts, and
stores with no MTG at all.

Record the ROOT domain of every qualifying store. Check each batch first:

    python3 /home/user/test/results/discovery/check_hosts.py host1 host2 ...

It prints NEW or KNOWN per host. Only NEW ones are worth saving. Save after every 3 cities:

    python3 /home/user/test/results/discovery/add_found.py NN <<'EOF'
    examplegames.com|shopify|Example Games, Ohio, sells MTG boxes
    another.square.site|square|short note incl. state
    EOF

(no indentation on the lines in a real heredoc). Format: host|platform guess|note. Platform is one
of shopify, woocommerce, wix, squarespace, bigcommerce, square, lightspeed, godaddy, custom,
unknown. No | inside fields.

If WebSearch fails (budget or any error), STOP. Never write guesses for searches you did not run.
Do not git commit. Final reply ONLY one line: `found NN: X new hosts (Y searches)`
