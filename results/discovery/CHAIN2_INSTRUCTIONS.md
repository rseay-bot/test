# Retailer follow-up: do they sell sealed cards online? (search only)

Input: /home/user/test/results/discovery/chains2/ret_NN.txt (one retailer per line).
Use ONLY WebSearch (never WebFetch or curl; retailer sites are blocked from here).
Run searches ONE AT A TIME. Skip retailers already listed in chains2/r2_NN.txt.

For EVERY retailer run these searches (no domain filter; blocked_domains ["reddit.com","facebook.com","instagram.com","youtube.com","tiktok.com","pinterest.com","ebay.com","tcgplayer.com"]):
1. `RETAILER Magic the Gathering booster box OR commander deck product page`
2. `RETAILER Pokemon booster box OR elite trainer box product page`
3. If either found nothing from the retailer's OWN site, one more: `RETAILER.com trading cards sealed`

Decide, from result URLs and snippets only:
- mtg_sealed: yes only if a result is a product page ON THE RETAILER'S OWN SITE for a sealed Magic item
  (booster box/pack, bundle, Commander deck, Secret Lair). no = results show the retailer but no MTG;
  unknown = nothing from the retailer's site.
- pokemon_sealed: same standard for sealed Pokemon (booster pack/bundle/box, ETB, tin, collection box).
- how: ship (ships to home), pickup_only (in-store or curbside pickup only), both, in_store_only
  (cards mentioned in stores only, no product page), unknown. Third-party delivery apps (Instacart,
  DoorDash) count as unknown unless the retailer's own site shows shipping.
- example_url: the best single product page URL on the retailer's own site (blank if none).
- note: one short phrase (price visible? out of stock? marketplace seller?).

Save after each retailer:

    python3 /home/user/test/results/discovery/add_chain2.py NN <<'EOF2'
    retailer|mtg_sealed|pokemon_sealed|how|example_url|note
    EOF2

(Write the heredoc terminator you choose on its own line.) No | inside fields. If WebSearch returns
too_many_requests, retry that search up to 3 times. If it still fails, or any other error, STOP; never
save guesses. Do not git commit.
Final reply ONLY: `chains2 NN: R retailers saved`
