# Product-title store discovery (search only)

Goal: find US online stores that sell Magic: The Gathering sealed product and are NOT already in
our census. Searching a specific product title returns product pages from many different stores,
so a product-page hit is already proof that the store sells that sealed item online.

Input: /home/user/test/results/discovery/product2/qq_NN.txt (one search query per line).
Use ONLY WebSearch (never WebFetch or curl; store sites are blocked from here).
Run searches ONE AT A TIME (never several WebSearch calls in one message).
Progress file: product2/done_NN.txt. After each query run
`echo "<query>" >> /home/user/test/results/discovery/product2/done_NN.txt` and skip queries
already listed there.

For EVERY query, run it exactly as written, with these blocked_domains:
["reddit.com","cardshows.io","yelp.com","facebook.com","instagram.com","youtube.com","tcgplayer.com","ebay.com","amazon.com","walmart.com","target.com","gamestop.com","bestbuy.com","costco.com","pinterest.com","tiktok.com","wizards.com","cardkingdom.com","coolstuffinc.com","miniaturemarket.com","starcitygames.com","cardhoarder.com","mtggoldfish.com","whatnot.com","etsy.com","mercari.com","linkedin.com","scryfall.com","moxfield.com","edhrec.com","archidekt.com","wikipedia.org","fandom.com","gatherer.wizards.com"]

From the results, keep every result whose URL is a PRODUCT or COLLECTION page of an independent
store (paths like /products/, /product/, /shop/, /collections/, /p/, /store/, /item/, or a
tcgplayerpro-free store page). Record the ROOT domain. Skip: big-box and national chains,
marketplaces, price guides, blogs, news, wikis, non-US stores, and stores that only sell
singles. Do not include a store just because it mentions the set.

Check each batch of hosts first:

    python3 /home/user/test/results/discovery/check_hosts.py host1 host2 ...

It prints NEW or KNOWN per host. Save only NEW ones, after every query that found any:

    python3 /home/user/test/results/discovery/add_found.py PNN <<'EOF'
    examplegames.com|shopify|product page: Edge of Eternities play booster box
    EOF

Use PNN = "q" plus your NN (for example q03) as the file name. Platform guess: /collections/ or
/products/ = shopify, /product/ = woocommerce, square.site = square, /product-page/ = wix,
else unknown. Fields: host|platform|note. No | inside fields.

If WebSearch returns too_many_requests, retry that same search up to 3 times (one call at a time).
If it still fails, or any other error, STOP immediately; never save guesses for queries you
did not run. Do not git commit.
Final reply ONLY: `product NN: Q queries run, X new hosts saved`
