# Store locator mining (search only)

Goal: pull MTG store names from official store locators through WebSearch, find each store's
own website, and save the ones not already in our census. Use ONLY WebSearch (the network blocks
direct access to locator sites and store sites).

You get a list of US states. For EVERY state:
1. Collect store names from locator pages. Run these searches (substitute STATE and its big cities):
   - `STATE store` with allowed_domains ["locator.wizards.com"]
   - `CITY STATE` with allowed_domains ["locator.wizards.com"] for the 3 largest cities in the state
   - `STATE game store` with allowed_domains ["play.pokemon.com", "events.pokemon.com"]
   - `STATE store` with allowed_domains ["tcg.ravensburgerplay.com", "ravensburgerplay.com"]
   Result titles look like "Store Name | 123 Main St, City, ST ... | Store - Official Wizards Store
   & Event Locator". Keep the store name and city. Only US stores.
2. For each store name, ONE search `"Store Name" City ST` (blocked_domains below) and take the
   store's own website from the results (own domain or a Shopify/Square/Wix/etc. shop). Skip it
   if only Facebook/Instagram/directories show up.
3. Check hosts in batches: `python3 /home/user/test/results/discovery/check_hosts.py h1 h2 ...`
   Save only NEW ones that look like they sell MTG sealed online (a shop or store page, not just
   an events page):

       python3 /home/user/test/results/discovery/add_found.py NN <<'EOF'
       host|platform guess|Store Name, City ST, from WPN locator
       EOF

blocked_domains for step 2:
["locator.wizards.com","cardshows.io","yelp.com","facebook.com","instagram.com","reddit.com","youtube.com","tcgplayer.com","ebay.com","amazon.com","mapquest.com","yellowpages.com","bbb.org","nextdoor.com","tripadvisor.com","keepupcards.com","lgsfinder.org","thecardshopfinder.com"]

After finishing each state: `echo "STATE" >> /home/user/test/results/discovery/locator_NN_done.txt`
and skip any state already listed there.
If WebSearch fails (budget or any error), STOP. Never save guesses. Do not git commit.
Final reply ONLY: `locator NN: X stores seen, Y new hosts saved (Z searches)`
