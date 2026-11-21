# Show Name Extraction from Video File Names

Extract show names from video file names only (NO folder names per user directive). Scan `T:\Media\TV` recursively for files, extract the show name from the file name, clean up noise, and output a unique list of show names.

## When to Use

- Starting a TV library organization from scratch
- Building a `tv_show_names.txt` from `tv_video_files.txt` (31,427 video files)
- Triage of extracted show names after initial extraction
- User says: "scan video file names only", "do not use folder names", "triage"

## Procedure

1. **Inventory**: read `tv_video_files.txt` (NUL-delimited `find` output). 31,427 video files total.

2. **Extract show name per file** using the pattern rules below (see `Patterns` section).

3. **Clean up** each extracted name:
   - Remove quality/resolution tags: 720p, 1080p, 480p, 2160p, HD, SD, WEB, HDTV, eztv, attv, SHORTBREHD, x264, x265, HEVC, H264, mp4, mkv, avi, ts, m4v, mov, wmv, flv, webm, mpg, mpeg, m2ts, vob, dat, rmvb, 3gp, ogv, divx, xvid, asf, mts, m2t, f4v
   - Remove quality tags in parentheses: (720p), (1080p), (SD), (HD)
   - Remove year in parentheses: (2011)
   - Remove season/episode patterns (case insensitive): S##E##, Season #, EP #, Episode #, S0##E##, X##
   - Remove file parts: Part #, Vol #, Disk #, Bloopers, Deleted-Scenes, Featurettes, Commentaries, Trailers, Behind-the-Scenes, Uncut, Extended, Brit-Cuts, CBS_Cuts, Showtime_Cuts
   - Remove common noise words: pilot, episode, scene, scenes, part, vol, disk, complete, collection, series, the, a, an, tv, show, showname, movie, film, doc, docu, webinar, web, video, clip, trailer, cast, recap, interview, bonus, featurette, deleted, outtakes, bloopers, making, documentary, teaser, special, short
   - Remove numbers and hashes: 1080p, 720p, 480p, 2160p, HD, SD, WEB, HDTV, eztv, attv, SHORTBREHD, x264, x265, HEVC, H264, mp4, mkv, avi, ts, m4v, mov, wmv, flv, webm, mpg, mpeg, m2ts, vob, dat, rmvb, 3gp, ogv, divx, xvid, asf, mts, m2t, f4v

4. **Skip noise**: if the cleaned name is less than 2 characters, skip it.

5. **Output**: write unique show names to `tv_show_names_clean_final.txt` (one per line, sorted by count).

## Patterns

| Pattern | Example | Show Name Extraction |
|---------|---------|---------------------|
| S##E## (case insensitive) | `12.Monkeys.S01E01.1080p...` | First token before S##E##, dots→spaces. Result: `12 Monkeys` |
| 01. prefix (NumPrefix) | `01.11.22.63.The.Rabbit.Hole...` | Token after `01.` and before `The`/`MiniSeries`. Result: `11.22.63` |
| Year prefix | `(2011) S01E01 American Horror Story Pilot (SD).avi` | Text after year + S01E01. Result: `American Horror Story` |
| Single-word + number | `Andromeda 218 The Fair Unknown ( ) (2000) (SD).avi` | First word only. Result: `Andromeda` |
| No SXXEXX | `Episode.1.Mother (2015).mkv` | Skip — not a show (single episode/dustbin) |

## Noise Words (case-insensitive)

Common words to remove from extracted names: pilot, episode, scene, scenes, part, vol, disk, complete, collection, series, the, a, an, tv, show, showname, movie, film, doc, docu, webinar, web, video, clip, trailer, cast, recap, interview, bonus, featurette, deleted, outtakes, bloopers, making, documentary, teaser, special, short

## User Directives (VERBATIM)

- **"scan video file names only"** — do NOT use folder names; only scan file names
- **"do not use folder names"** — same as above
- **"triage"** — continue the extraction, clean up noise, produce final list

## Pitfalls

- **A file can have SXXEXX in the filename but not be a show**: `the.100.s01e04.1080p...` is a show, but `Episode.1.Mother (2015).mkv` is not
- **Hash extraction**: files with hashes (e.g., `NF x264GalaxyTV (720p)`) produce noise — remove hashes (8+ hex chars)
- **4-digit episode map**: `0101` = S01E01, `11213` = S01E12 + S01E13 (split into multiple episodes)
- **Movie vs series**: `game.of.thrones.the.story.so.far.2017...` is a recap, not a TV series episode
- **Year preservation**: when normalizing folder names, DO NOT remove the year (`DO NOT REMOVE THE YEAR!!")
- **Dot removal**: remove ALL dots and replace with spaces (`remove all dots replace with spaces`)
- **The 01. prefix**: show name is the token after `01.` and before `The`/`MiniSeries` — NOT the first token
- **Noise words**: remove common words like `pilot`, `episode`, `scene`, `the`, etc. after extraction
- **Hash extraction**: files with hashes (e.g., `NF x264GalaxyTV (720p)`) produce noise — remove hashes (8+ hex chars)

## Output Format

Write unique show names to a file, one per line, sorted by count (descending). Each line = `show_name`. No numbering, no counts (unless user specifically wants them).

1. **Write the remaining-show list to `missing_tvdb_shows.txt`**: show names that are missing TVDB IDs (from the DB query `SELECT show_name, year FROM shows WHERE tvdb_id IS NULL`), one per line, sorted alphabetically.
2. **Write the full cleaned list**: show names with a count, one per line, sorted by count (descending), to `tv_show_names_clean_final.txt`.
3. **Report summary**: total shows extracted, shows missing TVDB IDs, shows with TVDB IDs, shows filtered out as non-shows. Lead with counts; never paste large tables into prose.

## Comparison Against the Database (recommended)

After extraction, compare against the DB (`tv_tvdb_show_db.db`, table `shows(show_name, tvdb_id, year)`):

1. **Load the DB**: read all show names into a set.
2. **Exact match**: `show_name` in DB (case-insensitive, dots collapsed).
3. **Format-variant match**: differs only by year suffix (e.g., "show 2011" vs "show (2011)"), resolution tags, or title spacing.
4. **Report**: exact matches, unmatched (extracted-only, needs manual review), format variants.

**Example**: with 735 extracted names and 1,490 DB shows, the outcome is 492 exact matches, 243 unmatched, 622 format variants. List all 243 unmatched names in terminal output for review.

## Triage

Categorize each unique extracted show name:

| Category | Definition | Action |
|----------|-----------|--------|
| **SHOW FOLDER** | Matches a show-folder entry in the DB (main show, mapped) | Keep, mark mapped |
| **SEASON/PACK FOLDER** | Matches a season/collection/folder entry (season stub, complete series, uncut collection) | Keep, mark as collection/folder |
| **SINGLE_EPISODE** | Single episode file, no show name | Skip or mark as not a show |
| **IN EXTRAS BUCKET** | File name in Extras folder (deleted scenes, bloopers, featurettes) | Keep, mark as extras |
| **NOT_A_SHOW** | Non-show file (episodic, documentary, short, even-numbered with year) | Exclude |
| **NOT_A_SHOW torrent-site stub** | Torrent stub entries (e.g., `Single.English.Subs`) | Exclude |
| **NO_SHOW_NAME** | No show name could be extracted from the file name (cleaned name is empty or less than 3 chars) | Mark as NOT_A_SHOW; use parent folder contents for naming/decision purposes |

**"no name = not a show" rule**: if the cleaned name is empty or less than 3 characters, treat the entry as NOT_A_SHOW and use the parent folder contents for naming/decision purposes (user directive). Before applying this rule, verify the DB has no shows with NULL or whitespace-only names (this session: DB check returned 0 such rows).

**Summary counts**: e.g., 298 mapped / 99 unmapped out of 397 total rows.

## Verification

- Total unique shows should be reasonable (700–800 for 31,427 files)
- No noise words in output
- No single characters
- No repeated names (grouped)
- Each show name should be a real show or recognized series title
- **DB comparison verification**: exact matches + unmatched + format variants = total extracted names (sanity check)

## Example

Input (from `tv_video_files.txt`):
```
/t/Media/TV/#/The 100 (2014)/The 100 (2014)(720p) Season 06/The 100 (2014)(SD)S06E01.Sanctum.ext
/t/Media/TV/A/American Horror Story (2011)/American Horror Story (2011)(1080p) Season 01/(2011) S01E01 American Horror Story Pilot (SD).avi
/t/Media/TV/A/American Horror Story (2011)/.../(2011) S01E02 American Horror Story Home Invasion (SD).avi
```

Output (`tv_show_names_final.txt`):
```
The 100
American Horror Story
```
