# Pokemon sealed check (search only)

Input: /home/user/test/results/discovery/pokemon/q_NN.txt (one host per line).
Use ONLY WebSearch. Do NOT WebFetch or curl store sites (the network blocks them).
Run searches ONE AT A TIME (never several WebSearch calls in one message). Skip hosts already
listed in pokemon/p_NN.txt.

For EVERY host:
1. Search `site:HOST pokemon booster box` (allowed_domains: ["HOST"]).
2. If nothing useful, ONE more: `site:HOST pokemon elite trainer box` (allowed_domains ["HOST"]).
Decide from titles, URLs and snippets:
- pokemon_sealed: product pages for Pokemon sealed items (booster box/bundle, elite trainer box,
  collection box, tin, sealed case) with a shop URL pattern (/products/, /product/, /shop/,
  add to cart, price). Online store confirmed.
- pokemon_other: sells or mentions Pokemon (singles, graded, events) but no sealed product page seen.
- no_pokemon: store is indexed but no Pokemon at all.
- unknown: nothing indexed.

Save after every 10 hosts:

    python3 /home/user/test/results/discovery/add_pokemon.py NN <<'EOF'
    host|verdict|evidence (one short phrase, e.g. "151 elite trainer box product page")
    EOF

No | inside fields. One line per host. If WebSearch returns too_many_requests, retry that same
search up to 3 times (one call at a time). If it still fails, or any other error, STOP immediately;
never write rows for hosts you did not search. Do not git commit.
Final reply ONLY: `pokemon NN: S pokemon_sealed, O pokemon_other, N no_pokemon, U unknown (total T)`
