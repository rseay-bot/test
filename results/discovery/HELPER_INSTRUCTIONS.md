# Sealed MTG store discovery: helper instructions

Goal: find US online stores that sell Magic: The Gathering SEALED product (booster boxes,
bundles, Commander decks, Secret Lair, prerelease kits, collector boosters) and are NOT
already in our census. Use ONLY the WebSearch tool. Do NOT use WebFetch or curl on store sites
(the network blocks them).

You get a list of US states (your slice). For EVERY state, run these searches (substitute STATE,
use blocked_domains below on all of them), then read result titles and URLs for store websites:
1. `Magic the Gathering booster box buy online STATE game store`
2. `STATE local game store ships Magic the Gathering sealed product online shop`
3. `STATE Magic the Gathering Commander precon bundle buy online`
4. `STATE card shop "add to cart" Magic the Gathering booster box`
5. `STATE hobby shop MTG play booster box collector booster online order`
6. `STATE comic and game store MTG sealed in stock shop online`
7. `MTG booster boxes for sale STATE shopify`
8. `MTG sealed product STATE "powered by" store`
Vary freely if a query is thin (city names, "tcg store", "gaming cafe shop").

blocked_domains on every search:
["cardshows.io","yelp.com","facebook.com","instagram.com","reddit.com","youtube.com","tcgplayer.com","ebay.com","amazon.com","walmart.com","target.com","gamestop.com","bestbuy.com","costco.com","mapquest.com","yellowpages.com","tiktok.com","pinterest.com","wizards.com","cardkingdom.com","coolstuffinc.com","miniaturemarket.com","starcitygames.com","cardhoarder.com","mtggoldfish.com","whatnot.com","etsy.com","mercari.com","linkedin.com","tripadvisor.com","bbb.org","nextdoor.com"]

What counts: a store with its OWN website (own domain, or a shop on Shopify / Square / Wix /
Squarespace / WooCommerce / BigCommerce etc.) that appears to sell MTG sealed product online.
US stores only (skip Canada, UK, EU, AU). Skip marketplaces, price guides, blogs, news, big-box
and national chains, non-hobby businesses, singles-only sites, TCGplayer Pro storefronts, and
stores with no MTG at all.

Record the ROOT domain of every qualifying store. Check each batch first:

    python3 /home/user/test/results/discovery/check_hosts.py host1 host2 ...

It prints NEW or KNOWN per host. Only NEW ones are worth saving. Save after every state:

    python3 /home/user/test/results/discovery/add_found.py NN <<'EOF'
    examplegames.com|shopify|Example Games, Ohio, sells MTG boxes
    another.square.site|square|short note incl. state
    EOF

(no indentation on the lines in a real heredoc). Format: host|platform guess|note. Platform is one
of shopify, woocommerce, wix, squarespace, bigcommerce, square, lightspeed, godaddy, custom,
unknown. No | inside fields.

If WebSearch fails (budget or any error), STOP. Never write guesses for searches you did not run.
Do not git commit. Final reply ONLY one line: `found NN: X new hosts (Y searches)`
