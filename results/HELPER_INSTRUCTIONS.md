# Card shop website search: helper instructions

You are finding each card shop's OWN website using the WebSearch tool.

Input: /home/user/test/results/chunks/chunk_NN.txt (one cardshows.io slug per line,
e.g. `jerrys-rookie-shop-boise` = shop "Jerrys Rookie Shop" in city "Boise").
The last 1-3 words of a slug are usually the city. No state is given.

For EVERY slug in your chunk, in order:
1. Run ONE WebSearch with the shop name and city in normal words, e.g.
   `Jerrys Rookie Shop Boise`. Add "card shop" only if the name is generic.
   Always pass blocked_domains:
   ["cardshows.io","yelp.com","cardshophub.com","cardshopsnearme.com","sportscardshops.org","thecardshopfinder.com","tcdb.com","yellowpages.com","mapquest.com","cardstoresonline.com"]
   Do a second search only if the first is clearly confused (wrong business type).
2. Decide one result:
   - high: a website that clearly belongs to this shop (its own domain, or a shop page on
     Shopify / Square / Wix / tcgplayerpro / similar). Chain shops: the chain's site is fine,
     note "chain".
   - medium: probably this shop but not certain (same name elsewhere, location unclear,
     or a marketplace page like eBay/auction site used as its only storefront).
   - social: no website, only Facebook/Instagram. Record the Facebook URL (else Instagram).
   - none: nothing found, or not a real card/game shop. Explain briefly in note.
   Never record a directory/listing site as the website (keepupcards, bbb, wizards locator,
   lgsfinder, treasurehunter, nextdoor, apple maps, yahoo local, giftly, zoominfo, etc.).
   Record the site's root URL (https://domain.com) unless the shop only has a sub-page.
3. Do NOT use WebFetch. Do NOT visit cardshows.io. Do not edit any other files.

Saving: after every 10 shops (and at the end), append results with Bash:
```
python3 /home/user/test/results/add_part.py NN <<'X'
jerrys-rookie-shop-boise|https://jerrysrookieshop.com|high|
some-shop-town|https://www.facebook.com/someshop|social|Facebook only
X
```
Format: slug|website|confidence|note  (no | characters inside fields).
Every slug in your chunk must get exactly one line. Before finishing, verify with:
`python3 -c "import csv;print(sum(1 for _ in csv.DictReader(open('/home/user/test/results/parts/part_NN.csv'))))"`
and add any missing slugs.

If WebSearch stops working (budget or any error), STOP immediately. Never write placeholder
rows for shops you did not actually search; leave them out so they can be retried.

Do not git commit. When done, reply with ONLY one line:
`part NN: X high, Y medium, Z social, W none (total T)`
