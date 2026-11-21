---
name: tvdb-metadata-lookup
description: Look up TVDB IDs for TV show names without a registered API key.
version: 1.0.0
author: Nous Research
license: open
hermes:
  tags: [media, metadata]
  related_skills: [media-library-organization]
---

# TheTVDB metadata lookup by show name

Retrieve TheTVDB series IDs for a library of TV show names when you do **not** have a registered API key. The official v4 API requires a key; use the site's internal search endpoint instead.

## When to Use

Use this skill when you need to retrieve TheTVDB series IDs for a list of TV show names and you do not have a registered TheTVDB API key. Primary lookup method is web_search (not the API). The API method is a fallback only. It is the metadata-lookup back end for the TV-library workflow (see media-library-organization).

**Two modes:**
- **Mode 1 — Web search**: used when you need to discover TVDB IDs for show names (no API key). The TVDB site's internal search endpoint is used via web_search.
- **Mode 2 — User-provided IDs**: used when the user already knows the TVDB IDs (from prior lookups, websearch, or direct knowledge) and says "apply these IDs to the database". In this mode, skip the lookup and go directly to applying each ID to the database (see `tv-show-database` skill).

### Mode 1: Web search (PRIMARY)

1. Collect show names (one per line).
2. **Try both formats**: for each show name, run the lookup with:
   - The original name as-is (may contain dots from the folder naming convention).
   - A spaced version: replace ALL dots with spaces (e.g., `The.Blacklist` → `The Blacklist`).

**User correction (this session):** the lookup must include the dotted→spaced version first. The database stores folder names with dots (e.g., `Battlestar.Galactica`); the TVDB search endpoint matches better with spaces (`Battlestar Galactica`). When a name is missing, search both `Name` and `Name with all dots replaced by spaces`.
3. Clean each name with `clean_for_search` (see references/name-cleaning.md).
4. Submit `web_search` calls for the top 8 cleaned shows, one show per call. **Batch at most 5 searches per call** and never exceed 50 searches in a single turn.
4b. **TVDB ID conflict check**: before applying any TVDB ID, verify it is not already assigned to another show in the database. Query: `SELECT show_name FROM shows WHERE tvdb_id = ?`. If any rows are returned besides the current show, the ID is in use by another show — flag it for manual review and do not apply it without resolving the conflict. (Issue fixed this session: V (2009) 94971 vs The X-Files 94971; The X-Files corrected to 77398.)
5. Match the best hit: fuzzy-score each hit's `name` and `aliases` (difflib ratio); take the highest. Record the query you searched. **Flag any hit with score < 0.6 for manual review.**
6. After the batch completes, update the database (sqlite3 `UPDATE shows SET tvdb_id = ? WHERE show_name = ?`) for each confirmed ID. Write the script to a scratch directory file (e.g., `C:/Users/Owner/AppData/Local/hermes/cache/scratch/update_tvdb_idsN.py`).
7. Execute the script via `cd /c/Users/Owner/AppData/Local/hermes/cache/scratch && python3 update_tvdb_idsN.py`.

### Method 2: User-provided IDs

When the user provides a list of show names + TVDB IDs directly (e.g., "Sue Thomas F.B.Eye 2002, Series #78849"), do not run web_search. Apply each ID directly to the database:

1. **Parse the user's list**: extract show name and TVDB ID from each line.
2. **Check exact name** in the database using `SELECT show_name FROM shows WHERE show_name = ?` (with dots, e.g., `Sue Thomas F B (2002)`).
3. **If found**: update the TVDB ID with `UPDATE shows SET tvdb_id = ? WHERE show_name = ?`.
4. **If not found**: add a new row (see "Adding new shows" in the `tv-show-database` skill).
5. **If the user supplies a year correction** (e.g., `Zomvivor 2025`), update the `year` field with `UPDATE shows SET year = ? WHERE show_name = ?`.
6. **Verify** after all updates: count shows with `tvdb_id IS NOT NULL`, print total and missing.

**Example** (this session): user provided
- `Sue Thomas F.B.Eye 2002, Series #78849` → `Sue Thomas F B (2002)` → update tvdb_id to 78849
- `Monty Python: (Almost) The Truth (The Lawyer's Cut) 2009, Series #118861` → `Monty Python Almost the Truth (2009)` → update tvdb_id to 118861
- `Zomvivor 2025, Series #468814` → `Zomvivor.2026 (Unknown)` → update tvdb_id to 468814, year to 2025
- `Side Quest 2025, Series #428425` → not in DB → add new row

## Method 1: web_search (PRIMARY for this user)

1. Collect show names (one per line).
2. **Try both formats**: for each show name, run the lookup with:
   - The original name as-is (may contain dots from the folder naming convention).
   - A spaced version: replace ALL dots with spaces (e.g., `The.Blacklist` → `The Blacklist`).

**User correction (this session):** the lookup must include the dotted→spaced version first. The database stores folder names with dots (e.g., `Battlestar.Galactica`); the TVDB search endpoint matches better with spaces (`Battlestar Galactica`). When a name is missing, search both `Name` and `Name with all dots replaced by spaces`.
3. Clean each name with `clean_for_search` (see references/name-cleaning.md).
4. Submit `web_search` calls for the top 8 cleaned shows, one show per call. **Batch at most 5 searches per call** and never exceed 50 searches in a single turn.
5. Match the best hit: fuzzy-score each hit's `name` and `aliases` (difflib ratio); take the highest. Record the query you searched. **Flag any hit with score < 0.6 for manual review.**
6. After the batch completes, update the database (sqlite3 `UPDATE shows SET tvdb_id = ? WHERE show_name = ?`) for each confirmed ID. Write the script to a scratch directory file (e.g., `C:/Users/Owner/AppData/Local/hermes/cache/scratch/update_tvdb_idsN.py`).
7. Execute the script via `cd /c/Users/Owner/AppData/Local/hermes/cache/scratch && python3 update_tvdb_idsN.py`.

### Web_search pitfalls (THIS SESSION)

- **The per-turn limit is 50 searches.** Once hit, the tool is blocked until the next turn. Do not retry in a loop.
- **Repeated searches return the same result.** When a search returns zero or identical hits, do not re-issue it. Change the query (e.g., drop articles, try the spaced version, or narrow the show list).
- **Batch 5–6 searches per web_search call.** This keeps you inside the limit and gives deterministic, auditable progress.
- **Never exceed 50 searches in a single turn.** The user will see the block and say "continue" — do not let the assistant re-issue the same blocked batch.
- **Do not waste queries on one-word fallbacks.** When the cleaned title has 2+ words, never search only the first word (a one-word fallback returns an unrelated record). Search the first TWO words only, and only if the full cleaned name returns 0 hits.
- **The search is popularity-ranked.** Always fuzzy-match and score; never assume the first hit is correct.
- **The alphabetical-priority batching** sorts the show list alphabetically by name, then batches in groups of ~6. This gives deterministic, auditable progress for the entire missing-ID set.

### Failure to save (this session)

Web_search batches 1-6 and then further batches repeatedly hit the 50-search limit. The assistant reported being "blocked" but the real failure was:
1. Re-issuing the same queries instead of changing them.
2. Searching for one-word fragments of multi-word show names (e.g., searching "Spartacus" or "The" instead of the full title).
3. Applying IDs to the database without verifying which shows they belonged to.
4. The database data (tv_tvdb_show_db.db) lives in `C:/Users/Owner/AppData/Local/hermes/cache/scratch/`, NOT in the O: drive. Verify the path before updating.

## Method 2: TVDB API (FALLBACK)

Only use when web_search batches complete successfully and you have recovered all the searches. Query `POST https://api4.thetvdb.com/web/search/queries` with JSON body `{"requests": [{"indexName": "TVDB", "query": NAME, "limit": 8, "params": {"query": NAME}}]}`. On HTTP 429, back off and retry once.

**`params` must be an OBJECT, not a string.** `params: {"query": NAME}` works; `params: "query=NAME"` returns HTTP 400 (`Unmarshal type error`).

## Key endpoints

**Search:** `POST https://api4.thetvdb.com/web/search/queries` — returns a `results` array with the top hits per index query. JSON body: `{"requests": [{"indexName": "TVDB", "query": NAME, "limit": 8, "params": {"query": NAME}}]}`. **params must be an OBJECT, not a string** (`params: {"query": NAME}`); `params: "query=NAME"` returns HTTP 400.

**Detail:** `GET https://api4.thetvdb.com/web/series/{id}` — returns the full series record for a given `id`. Used for the re-confirmation pass.

## Key pitfalls

- **`params` must be an OBJECT, not a string.** `params: {"query": NAME}` works; `params: "query=NAME"` returns HTTP 400 (`Unmarshal type error`).
- **Web_search per-turn limit is 50.** Never exceed 50 searches in a single turn — do not retry in a loop.
- **Alphabetical priority batching:** sort the show list alphabetically by name, then batch in groups of ~5 searches per web_search call. This gives deterministic, auditable progress.
- **Try both formats**: for each show name, run the lookup with the original name AND a spaced version (replace ALL dots with spaces). The database uses dotted folder names (folder naming convention) but the search endpoint works better with spaces.
- **Long / multi-word queries can return 0 hits.** Search word prefixes and drop articles (`The`, `An`, `A`).
- **A one-word fallback finds the wrong show.** When the cleaned title has 2+ words, never search only the first word (e.g. `The` from `The 4400` returns `Thea`; `Winter` from `Winter 2026` returns a different show; `Hitch` from `Hitch Hikers Guide...` returns a Will Smith comedy). The search is popularity-ranked, so a partial match promotes an unrelated record with a deceptively clean fuzzy score. Resolve the **full cleaned title** first; on 0 hits fall back to the **first TWO words only** (e.g. `The 4400`, `Winter 2026`, `Hitch Hikers`). Do not drop below two words for a multi-word title.
- **The search is popularity-ranked.** Always fuzzy-match and score; never assume the first hit is correct.
- **Dotted folder names are slugs, not IDs.** Resolve the numeric `id` through the search endpoint.
- **Web_search per-turn limit is 50.** Organize lookups into batches of ~5 per web_search call to stay within limits. Never exceed 50 searches in a single turn — do not retry in a loop.
- **Alphabetical priority batching:** sort the show list alphabetically by name, then batch in groups of ~5 searches per web_search call. This gives deterministic, auditable progress.


## Helper (clean_for_search)

```python
import re
def clean_for_search(name):
    s = name.strip()
    s = re.sub(r'\[[^\]]*\]', ' ', s)
    s = re.sub(r'\([^)]*\)', ' ', s)
    s = re.sub(r'\b\d{3,4}p\b', ' ', s)
    s = re.sub(r'x\d+', ' ', s)
    s = re.sub(r'[Bb][Ll][Uu][Rr][Aa][Yy]', ' ', s)
    s = re.sub(r'[Ww][Ee][Bb][Rr][Ii][Pp]', ' ', s)
    s = re.sub(r'[Hh][Dd][Tt][Vv]', ' ', s)
    s = re.sub(r'[Gg][Rr][Ee][Ee][Kk][ _][Ss][Uu][Bb][Ss]', ' ', s)
    s = re.sub(r'[Dd][Vd][Dd][Rr][Ii][Pp]', ' ', s)
    s = re.sub(r'[Rr][Ee][Pp][Aa][Cc]', ' ', s)
    s = re.sub(r'[Aa][Cc]3', ' ', s)
    s = re.sub(r'[Dd][Tt][Ss]', ' ', s)
    s = re.sub(r'[Cc][Cc][Ee][Ss][Ss][Ii][Oo][Nn]', ' ', s)
    s = re.sub(r'\b[Cc][Oo][Mm][Pp][Ll][Ee][Tt][Ee]\b', ' ', s)
    s = re.sub(r'\b[Cc]omplete [Ss]eries\b', ' ', s)
    s = re.sub(r'\b[Cc]omplete [Tt]V\b', ' ', s)
    s = re.sub(r'\b[Ss]eries\b', ' ', s)
    s = re.sub(r'[Ss]eason \d+', ' ', s)
    s = re.sub(r'\b[Ss]\d{1,3}\b', ' ', s)
    s = re.sub(r'\b[Bb][Cc][Cc]\b', ' ', s)
    s = re.sub(r'\b\d{6,}\b', ' ', s)
    s = re.sub(r'\band\b', '&', s, flags=re.I)
    s = re.sub(r'(?<=\s)\w(?=\s)', lambda m: m.group().replace(' ','.'), s)
    s = re.sub(r'[ _]+', ' ', s)
    return s.strip()
```

## Reference

See `references/matching-decisions.md` for score thresholds and ambiguous-match handling.
