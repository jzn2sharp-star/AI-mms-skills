---
name: tv-show-database
description: "Use when building a TV show database."
version: 1.0.0
author: Nous Research
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [media, tv, database, tvdb, organization]
    category: media
---

# TV Show Database

Build a structured database of TV show metadata (names, years, TVDB IDs, season counts, episode counts) from a TV library.

**Use when:**
- Building a database from `T:\Media\TV` (or similar root)
- Cross-referencing folder structure with `mapping_fixes.csv`
- Correcting year/episode/season counts for ambiguous shows

## Procedure

1. **Scan** the TV library root recursively; inventory every show folder and file.
2. **Parse** each show folder: extract show name, year, season folders, episode files.
3. **Cross-reference** with `mapping_fixes.csv` (or similar master mapping) to get TVDB IDs, years, and quality tags.
4. **Merge** show metadata:
   - First, try exact name match in the mapping.
   - Then, try partial match (lowercase, strip quality tags) or keyword match.
   - For unmatched shows, mark `tvdb_id = NULL` and leave `year` as the folder year.
5. **Apply corrections** (see rules below):
   - Year disambiguation: folder year vs show year.
   - Movie vs series: exclude movies/recaps from episode counts.
   - 4-digit episode parsing: `0101` → S01E01.
   - Season counting from episode map when all episodes are in one folder.
6. **Count seasons**: use the 4-digit episode map if present; otherwise count distinct season folders.
7. **Count episodes**: count video files in season folders (exclude movies/recaps/extras).
8. **Determine bucket**: `#` for numeric-leading collections, `T` for "The "-prefixed, else first letter of show name.
9. **Write output** to SQLite/JSON/CSV with: show_name, year, tvdb_id, bucket, season_count, episode_count, total_files.

## Parsing rules

### 4-digit episode-number parsing

- `0101` → S01E01 (first 2 digits = season, last 2 digits = episode)
- `11213` in `burn.notice.11213.avi` → two episodes **S01E12** and **S01E13** (not season 11, episode 213)
- Rule: extract first `S##E##` pattern, then fall back to 4-digit pattern `(\d{2})(\d{2})`

### Year disambiguation

The folder year and show year are often different:

- `American Horror Story (2016)(SD) Season 01` → show year is **2011**, folder year 2016 is the season/year.
- `Killjoys 20152019 S01S05 COMPLETE` → `20152019` is a date range; show year is **2015**.
- `NIKITA 20102013 Complete...` → `20102013` is a date range; show year is **2010**.
- `Grimm 2011 Season 16 S01S06...` → folder says "16" but content is S01–S06; season 1–6, not season 16.

### Movie vs series separation

- Movie/recap files (e.g., `La.Femme.Nikita.1990.720p.BluRay.mp4`, `game.of.thrones.the.story.so.far.2017.hdtv.x264plutonium.mkv`) are **not** TV series episodes.
- Exclude them from episode counts.
- `La.Femme.Nikita.1990.720p.BluRay.mp4` is the 1990 movie; `NIKITA (2010)` is a separate series (sequel/remake).

### Filename parsing edge cases

- `burn.notice.11213.avi` → parsed as **S01E12** and **S01E13** (two episodes), not season 11 episode 213.
- 4-digit tokens are always season+episode, never a single episode number.

## Quality classification

When building the database, classify each video file by actual video stream resolution from ffprobe:

- If no video stream → **not a video** (audio-only, corrupt, or metadata-only).
- Classify by resolution: SD (< 720p), 480p, 720p, 1080p, 1440p/2K, 2160p/4K.
- Preferred quality tags (most specific first): 2160p, 1080p, 720p, 480p, SD, Unknown.

## Output

- SQLite: `tv_tvdb_show_db.db` with table `shows(show_name TEXT PRIMARY KEY, tvdb_id INTEGER, year TEXT, bucket TEXT, season_count INTEGER, episode_count INTEGER, total_files INTEGER, content_type TEXT)`
- JSON: `show_database.json` (list of show objects)
- CSV: `show_database.csv` (transposed for Excel)

## Content-type classification (NEW - this session)

When adding a `content_type` column to the `shows` table (values: `Anime`, `Cartoon`, `Documentary`, `Live Action`), use a **specific-show-title approach**, NOT broad keywords.

**Pitfall**: Broad keyword classification (matching "kids", "children", "family", "teen", "young", "adult", "couple", "lovers", "husband", "wife", "father", "mother", "sister", "brother", "son", "daughter", "parent") misclassifies live-action shows as "Cartoon". Example: "13 Reasons Why [SD] (2017)" matched "teen" and was classified as Cartoon. The user explicitly abandoned the "cartoon etc." classification approach after 106 broken scripts (v52–v106) produced inconsistent results.

**Correct approach**:
1. **Add the column**: `ALTER TABLE shows ADD COLUMN content_type TEXT`
2. **Classify all shows with TVDB IDs** using specific, known-title lists:
   - **Anime** = Japanese animation (Naruto, One Piece, Death Note, Steins;Gate, Evangelion, Dragon Ball, Pokémon, Bleach, etc.)
   - **Cartoon** = Western animation (The Simpsons, SpongeBob, Family Guy, South Park, Tom and Jerry, Looney Tunes, etc.)
   - **Documentary** = non-fiction (nature, history, biography, science, documentary films, etc.)
   - **Live Action** = everything else (real people)
3. **Priority order**: Documentary first, then Cartoon, then Anime, then Live Action (default).

**Verification after classification:**
```sql
SELECT content_type, COUNT(*) FROM shows WHERE content_type IS NOT NULL GROUP BY content_type;
```

**Rule**: Do not claim classification is done without the verification query output.

## Related skills

- `tv-show-organization` — organizing a TV show library
- `tvdb-metadata-lookup` — TVDB ID lookup (already loaded)

## Reference

See `references/tvdb-database-update.md` for the complete workflow and example scripts.

## Verification

After building:
- Count shows: should match number of distinct show folders.
- Count seasons and episodes: sum should equal library totals.
- Check TVDB IDs: count shows with non-NULL IDs.
- Spot-check ambiguous shows (AHS 2016→2011, Killjoys 2015, Grimm S01–S06, Game of Thrones recap).

## Show name validation (always-on rule)

When extracting, filtering, or outputting shows from any show database:

1. **Skip entries with no show name**: if `show_name` is NULL, empty, or whitespace-only, treat the entry as "not a show" — default to folder contents (skip it). Do not include it in any output.
2. **Minimum name length**: a valid show name must have length ≥ 3 after stripping whitespace.
3. **Filter non-show rows**: when extracting shows for output, exclude file rows, alias rows, triplet entries (e.g., `Season.1 [720p max]`, `Bonus (Unknown)(SD) Season 01`), and name-less entries.
4. **Report the filter**: when writing an output file (txt, csv, json), print how many total rows were found and how many were excluded as non-shows (no name, name < 3 chars).

**Example**: when outputting remaining shows to `missing_tvdb_shows.txt`:
- Total shows missing TVDB: 397
- Shows with no name (NULL/empty/whitespace): 0 → all excluded
- Shows with name length < 3: 0 → all excluded
- Actual shows written to file: 263 (remaining 134 = file/alias/triplet rows)

**Rule**: "If there is no show name then not a show, default to folder contents" — a row without a valid name is not a show and is skipped, not written to output.

## TVDB batch update workflow (database)

When TVDB IDs are gathered from web searches or provided directly by the user, apply them to the database in batches:

1. **Pull the full list** of shows with `tvdb_id IS NULL` from the database.
2. **Sort alphabetically** by show name.
3. **Match each show name** (with both dot-separated and spaced versions) to the collected TVDB IDs using exact-name lookups in the database.
4. **Update the database** in batches using a script (`update_tvdb_idsN.py`) that:
   - Reads the mapping (show_name → tvdb_id, seasons, episodes)
   - Executes `UPDATE shows SET tvdb_id=?, season_count=?, episode_count=? WHERE show_name=?` for each row
   - Commits after each batch
   - Prints applied/unmatched counts
5. **Verify** after each batch: count shows with `tvdb_id IS NOT NULL`, print total and missing.
6. **Continue** until all shows are updated or no more IDs are available.

**Key rules:**
- Update scripts live in `C:/Users/Owner/AppData/Local/hermes/cache/scratch/update_tvdb_idsN.py`.
- **Database path**: `tv_tvdb_show_db.db` lives on the C: drive (`C:/Users/Owner/AppData/Local/hermes/cache/scratch/`), NOT on the O: drive. Verify the path before updating.
- Use exact `show_name` matches (with dots). Do not use LIKE patterns.
- After each batch, print the new totals (shows with TVDB, shows missing, seasons, episodes).
- If a show name is not found in the database, investigate before adding a new record — the show may be a file/alias.

## TVDB ID conflict detection and resolution (NEW - this session)

When applying TVDB IDs (whether from paste files, web searches, or user-provided data), always verify that the TVDB ID is not already assigned to a different show:

1. **After each TVDB ID update**, run a duplicate check:
   ```sql
   SELECT show_name, tvdb_id, COUNT(*) as cnt
   FROM shows
   WHERE tvdb_id = ?
   GROUP BY tvdb_id
   HAVING cnt > 1;
   ```
   Using the TVDB ID just applied (e.g., 94971).

2. **If a conflict is found** (same TVDB ID assigned to multiple shows):
   - **Verify** the correct TVDB ID by web search (see `tvdb-metadata-lookup` skill).
   - **Identify the correct show** for the new ID (the show the user provided it for).
   - **Update the wrong show** to the correct ID (do not remove the ID — assign it to the right show).

3. **Document the correction** in the tracker database (see `tvdb_data_tracker.db`).

**Example (this session):**
- User provided: `V (2009) 2009, Series #94971`
- Database had: `The X-Files` with TVDB 94971 (previously incorrectly assigned)
- Action: web search confirmed V (2009) = TVDB 94971, The X-Files = TVDB 77398
- Fix: Updated `The X-Files` from TVDB 94971 → 77398
- No shows now share TVDB 94971

**Warning:** A duplicate TVDB ID means one show was assigned the wrong ID previously. Never merge two shows to share a TVDB ID. Each show must have a unique TVDB ID.

#### Paste file processing workflow (NEW - this session)

When the user provides a paste file (e.g., `pasted_content_2026-11-17_12-42-40-184_d1855c.txt`) containing TVDB show data, apply it to the database in this order:

1. **Read and parse** the paste file: extract each show entry with its TVDB ID and year. Entries may include:
   - Show name + year + Series #TVDB_ID
   - Alternate titles (ignore)
   - Notes/edge cases in `>` format (apply these to the show name or DB)

2. **Apply show name corrections** (from the paste file `>` notes or user direct corrections):
   - `the xfiles > The X-files` → normalize "The X-files", not "The XFiles"
   - `Brooklyn NineNine > Brooklyn Nine-Nine` → correct hyphenation
   - `The I Land > The I-Land` / `The ILand > The I-Land` → use "The I-Land"
   - `The Returned US > The Returned` → drop "US" suffix
   - `The Tomorrow People US > The Tomorrow People` → drop "US" suffix
   - `The Librarians US > The Librarians` → drop "US" suffix
   - `The Magicians US > The Magicians` → drop "US" suffix
   - `Time After Time US > Time After Time` → drop "US" suffix
   - `The XFiles > The X-Files` → correct spelling
   - `Cleopatra 2525` → the title is "Cleopatra 2525" (not "Cleopatra 2000"), the year is 2000
   - `The Continental From the World of John Wick > The Continental (2023)` → use alternate title
   - `SSGB > SS-GB is the actual showname` → use correct name
   - `Six > use the alternate title SIX (2017)` → use correct title
   - `The Pendragon Cycle Rise of the Merlin` → correct order (not "Rise of the (2024)")
   - `The Cape 2011 (2011)` → keep as shown
   - `The Cape 2011` → keep as shown (year in title, not folder)

3. **Handle edge cases in extraction**:
   - `SD` = extraction error, ignore (skip it)
   - `GB` = probably SS-GB, an extraction error (skip or correct)
   - `extant` = not a show (skip)
   - `incomplete Stranger Things` = remove "incomplete" (this is a note, not part of the title)
   - `arrow` = Arrow (lowercase to proper case)
   - `blue bloods` = Blue Bloods (lowercase to proper case)
   - `bones` = Bones (lowercase to proper case)
   - `breaking in` = Breaking In (lowercase to proper case)
   - `mad men` = Mad Men (lowercase to proper case)
   - `mike and molly` = Mike and Molly (lowercase to proper case)
   - `neXt 2020` = Next 2020 (proper case)
   - `person of interest` = Person of Interest (lowercase to proper case)
   - `rizzoli and isles` = Rizzoli and Isles (lowercase to proper case)
   - `spartacus blood and sand` = Spartacus Blood and Sand (lowercase to proper case)
   - `www Cpasbien pw Mad Men` = remove website "www Cpasbien pw"
   - `Torrent9 cz Fear The Walking Dead` = remove website "Torrent9 cz"
   - `TorrentCouch com The Good Doctor` = remove website "TorrentCouch com"
   - `TorrentCouch net The Good Doctor` = remove website "TorrentCouch net"
   - `V (2009)` = V (2009), Series #94971 (use alternate title)

4. **Apply to the database**:
   - Read the paste file and build a list of `(show_name, tvdb_id, year)` tuples
   - For each show:
     - Check if the show exists in the DB using exact name match
     - If found: update the TVDB ID and year (do not add a duplicate)
     - If not found: insert a new row with the show name, TVDB ID, year, bucket, season_count, episode_count, total_files
   - Verify: count shows with `tvdb_id IS NOT NULL`, print total and missing

5. **Verify** after all updates:
   - Count shows with `tvdb_id IS NOT NULL`, print total and missing
   - Check for duplicate show names in the database
   - Validate show names: no NULL/empty names, no name length < 3

**Example**: user provided paste file with:
- `Tales From the Cryptkeeper` 1993, Series #73540
- `The Pendragon Cycle: Rise of the Merlin` 2026, Series #463624
- `Bet > 2025, Series #450686` (Bet is 2025, TVDB 450686)
- `Brooklyn NineNine > Brooklyn Nine-Nine` 2013, Series #269586
- `Cleopatra 2525 > actual show name title not the show year` 2000, Series #71906
- `The XFiles` → `The X-Files` (user correction)

Resulting DB updates:
- `Tales From the Cryptkeeper` → TVDB 73540, year 1993
- `The Pendragon Cycle: Rise of the Merlin` → TVDB 463624, year 2026
- `Bet (2025)` → TVDB 450686, year 2025
- `Brooklyn Nine-Nine` → TVDB 269586, year 2013
- `Cleopatra 2525` → TVDB 71906, year 2000
- `The X-Files` → TVDB 94971, year 2009 (if not already present)

## Database state verification (always-on rule)

After any database update (adding shows, updating TVDB IDs, correcting years, etc.), run a full verification before reporting completion:

1. **Count shows**: `SELECT COUNT(*) FROM shows` — total show count.
2. **Count with TVDB**: `SELECT COUNT(*) FROM shows WHERE tvdb_id IS NOT NULL` — shows with TVDB IDs.
3. **Count missing TVDB**: `SELECT COUNT(*) FROM shows WHERE tvdb_id IS NULL` — shows missing TVDB IDs.
4. **Count seasons**: `SELECT SUM(season_count) FROM shows` — total seasons (use `COALESCE` since SUM returns NULL for empty).
5. **Count episodes**: `SELECT SUM(episode_count) FROM shows` — total episodes (use `COALESCE`).
6. **Print all five counts** with percentages. Never claim completion without these numbers.

**Example** (this session):
```
Total shows: 1,557
With TVDB: 1,172 (75.3%)
Missing TVDB: 385 (24.7%)
Total seasons: 1,685
Total episodes: 26,262
```

## Conflict detection (always-on rule)

After any batch of TVDB ID updates, run a conflict check before reporting completion:

1. **Duplicate TVDB IDs**: `SELECT show_name, tvdb_id, COUNT(*) as cnt FROM shows WHERE tvdb_id IS NOT NULL GROUP BY tvdb_id HAVING cnt > 1` — lists all TVDB IDs shared by multiple shows.
2. **Duplicate show names**: `SELECT show_name, COUNT(*) as cnt FROM shows GROUP BY show_name HAVING cnt > 1` — lists duplicate show names.
3. **Missing years**: `SELECT show_name, tvdb_id FROM shows WHERE tvdb_id IS NOT NULL AND year IS NULL` — shows with TVDB IDs but no year.
4. **Year anomalies**: `SELECT show_name, year FROM shows WHERE year IS NOT NULL AND (year < 1900 OR year > 2030 OR year = 0 OR year = 1900)` — suspicious year values.
5. **Season/episode mismatch**: `SELECT show_name, season_count, episode_count FROM shows WHERE season_count > 0 AND episode_count = 0` — shows with seasons but no episodes.

**Rule**: If the conflict check finds TVDB ID duplicates, investigate each one:
- The TVDB ID was previously assigned to the wrong show. Verify the correct ID via web search.
- Assign the correct ID to the correct show. Never merge two shows to share a TVDB ID.

**Example (this session)**: User provided `V (2009) 2009, Series #94971`. The database already had `The X-Files` with TVDB 94971. Conflict check found the duplicate. Action: web search confirmed V (2009) = TVDB 94971, The X-Files = TVDB 77398. Fixed The X-Files to 77398. No shows now share TVDB 94971.

## Missing years workflow

When asked to fill missing years for shows with TVDB IDs:

1. **Query for missing years**: `SELECT show_name, tvdb_id FROM shows WHERE tvdb_id IS NOT NULL AND year IS NULL` — get all shows with TVDB IDs but no year.
2. **Resolve each year** from available data:
   - From the show name itself (e.g., `Beauty.and.the.beast.2012 (2012)` → 2012, `Black.Lightning (2018)` → 2018, `The.Iland (2019)` → 2019).
   - From the show's known history (e.g., `Better Call Saul` → 2015, `Burn Notice` → 2007, `Black Mirror` → 2011, `The Blacklist` → 2013, `SS-GB` → 2017).
   - From web search when name-based resolution is ambiguous.
3. **Apply updates** in batches using the standard database update script pattern.
4. **Verify** after each batch: count shows with `year IS NOT NULL` and print total and remaining missing.
5. **Report** final counts.

**Example (this session)**: 99 shows had TVDB IDs but no years. After resolution and batch updates, all 99 were filled. Final state: 0 shows with missing years.

### Common year patterns to check

| Query | Expected result | Action |
|-------|----------------|--------|
| Name contains "(2018)" | Year 2018 | Use from name |
| Name contains "20152019" | Year 2015 | Take first year (show year, not date range) |
| Name contains "20102013" | Year 2010 | Take first year |
| Name contains "20082011" | Year 2008 | Take first year |
| Name contains "20092012" | Year 2009 | Take first year |
| Name contains "20152019" | Year 2015 | Take first year |
| Name contains "20072013" | Year 2007 | Take first year |
| Name contains "19952000" | Year 1995 | Take first year |

## Adding new shows to the database

When the user provides a TVDB ID for a show not in the database, add it before updating:

1. **Check exact name** using `SELECT show_name FROM shows WHERE show_name LIKE ?` (with dots).
2. **If not found**, insert a new row with the show name, TVDB ID, year, bucket, season_count, episode_count, and total_files.
3. **Verify** with a SELECT after insertion.

**Example** (Side Quest, 2025):
```python
cur.execute("INSERT INTO shows (show_name, tvdb_id, year, bucket, season_count, episode_count, total_files) VALUES (?, ?, ?, ?, ?, ?, ?)", ('Side Quest (2025)', 428425, '2025', 'S', 1, 4, 4))
```

### Year correction from user-provided data

When the user supplies corrected year data, update the `year` field:

**Example** (Zomvivor): database had `Zomvivor.2026 (Unknown)`; user said `Zomvivor 2025, Series #468814` → update year to 2025.

```python
cur.execute("UPDATE shows SET year = ? WHERE show_name = ?", ('2025', 'Zomvivor.2026 (Unknown)'))
```
- The database is `tv_tvdb_show_db.db` with table `shows(show_name TEXT PRIMARY KEY, tvdb_id INTEGER, year TEXT, bucket TEXT, season_count INTEGER, episode_count INTEGER, total_files INTEGER)`.