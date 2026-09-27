# Card shop website results

Every one of the 4,165 cardshows.io shops now has a result: 2,769 high, 184 medium,
709 social only, 503 none.

- `all_results.csv`   every shop (high / medium / social / none), with source and note
- `websites.txt`      unique high-confidence shop websites (2,542)
- `websites_maybe.txt` unique medium-confidence websites (134); probably right, confirm before use
- `websites_social.txt` Facebook/Instagram pages for shops with no website (706)
- `chunks/`, `parts/` round 2 web search input and helper output (one file per 100-shop chunk)
- `HELPER_INSTRUCTIONS.md` how a helper searches one chunk
- `clean_parts.py`    drops placeholder rows from parts/ and rebuilds search_remaining.txt (now empty)
- `merge_parts.py`    merges parts/ into all_results.csv (search results override earlier guesses)
  and rebuilds the websites*.txt lists
