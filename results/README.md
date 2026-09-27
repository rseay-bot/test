# Card shop website results

- `all_results.csv`   every shop resolved so far (high / medium / social / none), with source
- `websites.txt`      unique high-confidence shop websites
- `websites_maybe.txt` unique medium-confidence websites (about 2 in 3 correct; confirm before use)
- `search_remaining.txt` shops still to search: unresolved first (2,673), then the medium
  "maybe" shops to confirm (537)
- `chunks/`           search_remaining.txt split into 100-shop chunks (01-27 unresolved,
  27-33 confirm maybes)
- `parts/`            web search results written by helpers, one file per chunk
- `HELPER_INSTRUCTIONS.md` how a helper searches one chunk
- `clean_parts.py`    drops placeholder rows from parts/ and rebuilds the remaining list

To continue in a new session (needs CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION raised):
run helpers on chunks/ per HELPER_INSTRUCTIONS.md, then run clean_parts.py and merge parts/
into all_results.csv (search results override "medium" guesses).
