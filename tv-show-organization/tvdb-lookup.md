# TVDB metadata lookup (by show name)

Use this procedure to retrieve TheTVDB series IDs for a list of TV show names when you do NOT have a registered TheTVDB API key. The official v4 API requires a key; use the site's internal search endpoint instead.

## When to Use

- Assigning TVDB IDs to TV show folders
- Re-confirming ambiguous TVDB matches (requires the detail endpoint re-confirmation pass)

## Procedure

1. Collect show names (one per line).
2. Clean each name with `clean_for_search` (see `references/name-cleaning.md`).
3. Query `POST https://api4.thetvdb.com/web/search/queries` with JSON body `{"requests": [{"indexName": "TVDB", "query": NAME, "limit": 8, "params": {"query": NAME}}]}`. On HTTP 429, back off and retry once.
4. Match the best hit: fuzzy-score each hit's `name` and `aliases` (difflib ratio); take the highest. Record the query you searched. **Flag any hit with score < 60 for manual review.**
5. Write the output: `library_name`, `tvb_id`, `tvb_show`, `score`, `status` (`ok` / `low` / `unresolved`). Sort alphabetically.

## Key endpoints

**Search:** `POST https://api4.thetvdb.com/web/search/queries` — returns a `results` array with the top hits per index query.

**Detail:** `GET https://api4.thetvdb.com/web/series/{id}` — returns the full series record for a given `id`. Used for the re-confirmation pass.

## Key pitfalls

- **`params` must be an OBJECT, not a string.** `params: {"query": NAME}` works; `params: "query=NAME"` returns HTTP 400.
- **Long / multi-word queries can return 0 hits.** Search word prefixes and drop articles (`The`, `An`, `A`).
- **A one-word fallback finds the wrong show.** When the cleaned title has 2+ words, never search only the first word (e.g., `The` from `The 4400` returns `Thea`). The search is popularity-ranked. Resolve the **full cleaned title** first; on 0 hits fall back to the **first TWO words only** (e.g., `The 4400`, `Winter 2026`), never the first word alone.
- **The search is popularity-ranked.** Always fuzzy-match and score; never assume the first hit is correct.

## Re-confirmation pass

After matching, run the re-confirmation pass on every row with status `low` or `unresolved`:
1. Look up the full series record for the candidate TVDB id via the detail endpoint (`GET https://api4.thetvdb.com/web/series/{id}`).
2. Confirm the id corresponds to the intended show (or mark it unresolved if it does not).
3. Re-write the output with the confirmed status.

## Output preference

Keep the final answer short and direct: one line per show (`library name` -> `tvdb id`), sorted alphabetically. No narrative, no explanation of the lookup. The data file is the deliverable; flag low-confidence rows and stop.

## Reference

See `references/matching-decisions.md` for score thresholds and ambiguous-match handling.
