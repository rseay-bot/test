# Retailer-chain search: who sells Magic and Pokemon outside game stores (search only)

Goal: find out which retail chains and non-hobby retailers carry Magic: The Gathering and/or
Pokemon trading cards, whether each sells online, and find retailers we never thought of.
Use ONLY WebSearch (never WebFetch or curl; store sites are blocked from here).
Run searches ONE AT A TIME (never several WebSearch calls in one message).

Input: /home/user/test/results/discovery/chains/cq_NN.txt (one search query per line).
Progress file: chains/done_NN.txt. After each query run
`echo "<query>" >> /home/user/test/results/discovery/chains/done_NN.txt` and skip queries already listed.

Run each query exactly as written. Use these blocked_domains on every search:
["reddit.com","facebook.com","instagram.com","youtube.com","tiktok.com","pinterest.com","yelp.com","cardshows.io"]

From the results, record one line per RETAILER you learn something about:

    python3 /home/user/test/results/discovery/add_chain.py NN <<'EOF'
    retailer|mtg|pokemon|online|evidence_url|note
    EOF

Fields:
- retailer: name (for example "Ace Hardware"), plus root domain in the note if you know it.
- mtg: yes / no / unknown. "yes" only when a result shows the retailer selling Magic: The Gathering
  cards or sealed product (product page, store page, news article, or a credible list).
- pokemon: yes / no / unknown, same standard.
- online: yes if the result shows a product page you could buy from online or ship-to-home;
  store_only if cards are only mentioned as in-store; unknown otherwise.
- evidence_url: the one best result URL.
- note: one short phrase (for example "Pokemon tins on product page; MTG not seen").
No | inside fields. Record each retailer once per query; duplicates are fine across queries.

Also record ANY retailer you did not expect (a chain or regional store that is not a game or
card shop) that appears in a result as carrying Magic or Pokemon. Those are the most valuable rows.

Ignore pure game and card shops, marketplaces (TCGplayer, eBay, Mercari, Whatnot) and price guides.

If WebSearch returns too_many_requests, retry that same search up to 3 times (one call at a time).
If it still fails, or any other error, STOP immediately; never save guesses for queries you did not
run. Do not git commit.
Final reply ONLY: `chains NN: Q queries run, R retailer rows saved`
