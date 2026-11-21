---

name: tv-show-organization

description: "TV library organization: naming, TVDB mapping, quality."

version: 1.0.0

author: Nous Research

license: MIT

platforms: [windows]

metadata:

  hermes:

    tags: [media, tv, organization, tvdb, quality]

    category: media

---



# TV Show Organization



This skill covers organizing a TV show library according to the user's specified conventions:

- Per-movie folders tagged with quality in parentheses: `Title(Year)(Quality)`

- Numeric/leading-number collections kept in `#` (not promoted to a letter)

- Dry-run first, then commit only after reviewing counts

- Verify totals after every change

- **Repair-and-place for damaged names**: when media is playable but its name is damaged (dot lost from the extension, `_mkv`-style suffixes, stray release tokens), fix the name and route the file to its proper show/season folder. Do not quarantine or delete it; quarantine is only for unreadable/probe-failed files.



## When to Use



Use this skill when:

- Organizing a TV library tree (e.g., `T:\Media\TV`)

- Creating a new TV show organization plan

- Applying quality tags to existing folders

- Assigning TVDB IDs to show folders

- Resolving probe-failed folders (move to `broken/`)



## Procedure



1. **Scan** the library root recursively; inventory all folders and files.

2. **Classify** each folder: main show, season, extras, specials, broken (probe-failed).

3. **Resolve quality**: if not in the folder name, ffprobe the first video stream and map height → tier.

4b. **Verify the mapping CSV**: parse the CSV (e.g., `mapping_fixes.csv`), check row count, buckets, unique TVDB IDs, and any null fields. Flag rows where the year is marked 'not verified' or the TVDB ID is unclear.

4c. **Verify via websearch**: for each flagged row, run `websearch "Show Name" "TVDB" "year"` to confirm the correct TVDB ID and first-air year before writing it into the CSV. Treat low-confidence hits as verify-needed.

4d. **Update the CSV**: write the confirmed TVDB ID into the `tvdb_id` column; update the note column with the verification source (e.g., 'websearch verified'). Do not leave ambiguous rows unchanged.

5. **Build the dry-run plan** as a CSV (`source,dest,kind,action,tvdb_id`); read its columns before acting.

6. **Dry-run**: review counts and the full plan. **ASK the user to commit** — do not move files automatically.

7. **Verify**: re-count all destinations, report skipped conflicts.



> **Standing rule**: `Dry run first, then ask to commit.` Always present the plan, get explicit approval, then act.

> **User style**: short, direct, no fluff. Lead with the summary and the concrete corrections, then a compact table. Put the full table in a separate output file — never paste large tables into prose.

### Pre-flight audit of an existing library

Run this before proposing any consolidation, merge, or rename plan.

1. **Inventory from disk, never from a paste.** A `tree /f` dump or "strategy" document supplied by the user is unverified input. Windows `tree` output carries CRLF endings that break indentation-based parsers (phantom nesting silently inflates file counts), and strategy documents routinely describe a folder layout the library does not have. Take one authoritative scan — `find <root> -type f -printf '%s\t%P\n'` — and reconcile any pasted inventory against it before planning. Compare the proposed target layout against the library's actual confirmed convention, not against the document's example tree.
2. **Classify duplicate families by content, not by folder name.** Same-named folders are not duplicates until each is shown to hold video. Count videos and subtitles per folder, normalise the show name (strip `{TVDB-…}`, `(Year)`, quality tags, `Season N`, `SXXEYY`, dots), group, and bucket each family: `REAL_DUP` (>=2 folders holding video), `MIXED` (one video folder plus metadata-only leftovers), `SUB_ONLY_LEFTOVER` (no video anywhere — e.g. per-episode folders holding only `.srt`). Only `REAL_DUP` families belong in a merge plan; leftovers get their own cleanup pass.
3. **Inventory outside the library root too.** Stray quarantine/broken/"to sort" folders commonly sit one level above the root being organised (e.g. `T:\MEDIA\Broken Fix or Replace\` beside `T:\MEDIA\TV\`). Scan the parent root, or the audit silently omits them.
4. **Cost every proposed delete against real content.** Intersect the delete list with the file inventory and report files affected **and** GB before asking for approval. Generic cleanup lists naming Extras/Bonus/Featurettes/podcast folders usually select real media, while genuine junk (`.HERE`/screenshot marker stubs, empty placeholder folders) is a tiny fraction of the matched volume.
5. **Scan the bucket roots themselves, not only the show folders.** The planner descends into `<bucket>\<show>\…` and skips `_`-prefixed trees, so files sitting loose directly under a letter bucket never enter the plan at all. Diff a live `find <root> -type f` against the plan's `src` set and read `not in plan` as "unhandled", not "newly added": the expected residue is the archived `_TO_SORT` tree plus a handful of bucket-root strays — anything else needs explaining.

### Pre-apply validation of any move/rename plan

Before presenting a plan for approval — whether you generated it, another tool did, or the user supplied it — re-validate it against the current disk state. A plan is a snapshot; the library and the mapping keep changing underneath it.

1. **Check destination naming against the generator's own format string.** Do not apply a generic "IDs belong in the mapping CSV, never in paths" test: the live `.4` planner emits `{tvdb-<ID>}` into show/season/file names by design (its format string documents that layout as user-confirmed), so such paths are correctly shaped. Validate against the format the plan was actually generated with, and flag only genuine deviations — ask before changing the token itself.
2. **Sample source existence.** Take ~300 random `src` rows and test them; report the hit rate. Sources deleted or moved since generation make row-by-row application unsafe.
3. **Confirm every touched show has a mapping row.** A show absent from `mapping_fixes.csv` silently inherits whatever ID sits in the master mapping, and that stale ID propagates into thousands of plan rows. Trace any suspicious ID to its source row, not to the plan.
4. **Regenerate after any mapping edit.** Changing an ID or show name invalidates every plan row derived from it; either regenerate the whole plan or patch the affected rows explicitly and name them.
5. **Report the shape, not just the totals**: action counts (MOVE / LEAVE / WRITE), status counts (OK / REVIEW / BLOCKED), and what the non-MOVE actions do.
6. **Verify the identity of a damaged/mislabeled batch before filing it under a show.** A batch rename can stamp one show's episode numbers onto another show's content. Check the episode numbers against the series' real season range and the title tokens against the show name (e.g. "deleted scenes" titles belonging to a different series, or an S09 on a seven-season show), and quarantine anything that does not belong instead of letting it inherit a season folder.

See `references/tv-pipeline.md` for the pipeline file map, the mapping-correction recipe and the archive convention.

## Batch media quality probe

Use when asked to extract quality (resolution, codec, bitrate, duration, size) from every video file in a media root.



1. **Inventory** the root with NUL-delimited `find` (spaces in names survive):

   `find <root> -type f \( -iname '*.mp4' -o -iname '*.mkv' -o -iname '*.avi' -o -iname '*.mpv' -o -iname '*.mov' -o -iname '*.m4v' -o -iname '*.ts' -o -iname '*.wmv' -o -iname '*.flv' -o -iname '*.webm' -o -iname '*.mpg' -o -iname '*.mpeg' \) -print0 > files.txt`

2. **Per-file script** `probe_one.sh` that invokes `C:/Program Files/Jellyfin/Server/ffprobe.exe` via **bash** (not Python subprocess) and prints one compact JSON object per file on stdout: `path, container, duration, size_bytes, bitrate, num_streams, video, audio, subs, error`.

3. **Parallelize** across cores: `xargs -0 -P 24 -n 1 probe_one.sh < files.txt > probe.jsonl`. 24 cores on this host; ffprobe ≈ 0.25 s/file serially, so 24-way is ≈ 5–6 min for 31.5k files.

4. **Assemble** `probe.jsonl` into the final JSON sorted by `path`; keep the JSONL as the source of truth. Each line is read with a brace-counting extractor that pulls every complete `{"path": ...}` object — a probe run can emit **two JSON objects on one line** when the NUL-delimited file list mangles a path, and a line-level `json.loads` undercounts (it saw 31,515 of 31,519 files; the merged lines hid 5 extra probes).

5. **Report progress at the top of each minute** during the run.

### Dedicated resolution probe: probe_missing.py

When the task is specifically to determine actual video resolution (quality), use the `probe_missing.py` script — it probes only files not already in `all_quality.json`, making it incremental and resumable:

1. **Run the script**:
   `python3 probe_missing.py --root "T:\Media\TV" --existing all_quality.json --out all_quality_merged.json --workers 2`

2. **Read the merged JSON** (`all_quality_merged.json`) — it contains `width`, `height`, `codec`, `field_order`, `sample_aspect_ratio`, `resolution` per file.

3. **Use the `resolution` field** for quality tagging — never derive quality from folder names or filename tokens.

4. **If full-drive probing times out** (~31,000 files), use `--plan` to probe only files flagged `"reason": "quality not found"` in the planner CSV. This is targeted and fast.

5. **Re-run as needed**: finished files are skipped automatically; corrupt files are listed as failures without aborting.
6. **Success criteria**: a completed run produces `all_quality_merged.json` with 31,519 files, 0 failures (2026-11-19 run).

### QUALITY EXTRACTION (CORRECTED)
**CRITICAL**: When a task asks for the quality (resolution) of each file, derive it from the **actual video stream resolution via ffprobe**, NOT from folder name tags.

The user's correction: "the point is to ascertain the actual quality of the video file and then organize it according to the file's attributes."

Steps:
1. Probe every file (see Batch media quality probe or probe_missing.py) and parse `video.width` / `video.height` from the ffprobe JSON output.
2. Map resolution to quality tier (width-first):
   - width ≥ 3600 → 2160p
   - width ≥ 1800 → 1080p
   - width ≥ 1200 → 720p
   - width ≥ 700 → 480p
   - below → SD
3. Report a `quality_counts` summary alongside the per-file table. Do NOT derive quality from folder names.

### Filename-vs-actual resolution pitfall

**Filenames claiming "720p" / "1080p" often contain 480p SD content.** The 100 (2014) title is a classic example: ~30 files named `...720p...` or `...1080p...` were probed and found to be 480p (720x404, 624x350, 640x360, 854x480). Only the truly 1080p files (1920x1080 video) were correctly labeled; the `...1080p...` files containing 1920x872 or 1920x816 were 480p widescreen crops. Always trust ffprobe pixel dimensions over filename tokens.

### Non-video file handling

A file with no `video` stream (or no `width`/`height`) is **not a video file**. It may be:
- An audio-only file (e.g., The.Boys...Silence.mkv with eac3 audio only)
- A corrupted/truncated file (no streams at all)
- A 0-byte file

**Treat these as non-video.** Do NOT classify them into SD/720p/1080p. Mark `Not a video`. When the user asks for "the quality of the video library," report video files only, and list the non-video files separately.

### ffprobe is part of the probe batch, not the quality-extraction step

`ffprobe` runs inside the parallel batch (`xargs -0 -P 24`), and the per-file JSON output is parsed for `video.width` / `video.height` to classify quality. Do not run a second ffprobe pass for quality classification.

- **ffprobe via bash**: on this Windows host, Python `subprocess` on `C:/Program Files/Jellyfin/Server/ffprobe.exe` raises `WinError 5`. Call it from a bash script with forward slashes.

- **Missing `import sys`**: a per-file `-c` snippet that reads `sys.stdin` but only imports `json, os` raised `NameError` and aborted the run. Import every name you use.

- **NUL-delimited counting**: `wc -l < files.txt` reports `0` for `-print0` output (no newlines). Use `tr -cd '\0' | wc -c` or count entries instead.

- **Output location**: write big outputs to the Hermes scratch dir, not the home directory, or they are pruned/locked.



- **Merged JSONL lines**: a parallel probe run can emit two JSON objects on a single line (the NUL-delimited source list mangled a path boundary, so one script invocation produced two probe results). A `for line in f: json.loads(line)` pass then undercounts — json.loads then reports `Extra data`, and the regex fallback finds zero matches. Before assembling, read each line with a brace-counting extractor that pulls every complete `{"path": ...}` object, and reconcile the total against the on-disk video count (the probe run saw 31,515 lines for 31,519 files; a strict per-line parse reported 31,508 probed until the merged lines were split out).



## Audit review (TVDB mapping exports)

Run this when the user drops a TVDB mapping audit export (JSON/CSV) and wants a correction plan.



1. **Parse** the export. JSON imports fine; the file reader prefixes each line with `N|` — strip those prefixes and blank lines before `json.loads`, or it fails on "Extra data".

2. **Classify** each row: real show, subtitle/metadata/season-stub, torrent/channel/collection, or generic `?` folder. Only real shows get a TVDB ID.

3. **Group** rows by actual show. Dedupe same-series entries (e.g., `Xena Warrior Princess` + `Xena Warrior Princess S01` → one family).

4. **Fill corrections**: use the TVDB IDs you verified; mark anything unverified as `verify` — never invent an ID. Treat `Probably OK - confirm` as a confirm-with-no-change.

5. **Separate the non-mapping issues** into their own buckets: `no-id` (no series TVDB ID — do not invent), `year_conflicts` (labeling issue — do not rewrite IDs), `tag_conflicts` (ID must match the folder's existing tag).

6. **Verify totals**: the sum of grouped folder counts must equal the wrong-show folder total; list skipped/conflicts.

7. **Emit**: a short summary (counts + confirmed IDs) first, then the full table in a report file. Do not paste large tables into prose.

### CSV audit and bug check

Run this when the user drops a CSV mapping (e.g., `mapping_fixes.csv`) and wants a bug review before committing.

1. **Parse** the CSV (strip BOM, validate all required columns present).

2. **Check 1 — TVDB ID consistency**: group by `tvdb_id`; ensure each ID maps to exactly one distinct show name. A TVDB ID should not map to two different show names.

3. **Check 2 — Folder conflict**: group by `folder`; each folder must map to exactly one TVDB ID. (Same folder, same ID is fine for repeated entries.)

4. **Check 3 — Show name vs folder extraction**: extract a candidate show name from the folder (strip quality tags, season info, SXXEXX, year, file artifacts) and compare to `show_name`. Flag only where the candidate does not share at least 50% of words with the show name. Note that crude extraction produces many false positives — e.g. `Charmed (1998) vs Charmed.1998 (1998)` is consistent; the folder has not one token that the show name lacks.

5. **Check 4 — Non-ASCII characters**: list any non-ASCII characters found. Some are legitimate (e.g. `ë` in `The Law According to Lidia Poët (2023)`); do not flag as a bug without verification.

6. **Check 5 — Missing values**: any field (folder, tvdb_id, show_name, note) empty is a bug — list and resolve.

7. **Check 6 — Duplicate TVDB IDs within buckets**: every bucket must have unique TVDB IDs. If two rows in bucket `B` share TVDB `12345`, that is a bug (same ID mapped twice to different shows).

8. **Check 7 — Folder name length**: list folders > 80 characters. Long is acceptable but note it.

9. **Check 8 — Year discrepancies**: folder year (19xx/20xx in the name) vs show year (in `show_name`). Some are explainable: `Doctor Who (2005)` folders dated 2023 (current season of the 2005 series). Do not rewrite IDs for explainable year mismatches.

10. **Report**: a short summary (counts + confirmed IDs) first, then the full table in a report file. Do not paste large tables into prose.

### Examples

```text
=== Bug check passed ===
Total rows: 237
TVDB IDs to multiple shows: none
Folder conflicts: none
Missing values: none
Duplicate TVDB within buckets: none
Non-ASCII: 1 (ë — legitimate, "Poët")
Long folders (>80): 2
Year mismatches: 4 (3 explainable: Doctor Who 2005 in 2023 folders; 1: Young Indiana Jones Chronicles 1992 vs folder 1993)
```

## DB/index build and correction rules

### Show-year vs folder-year disambiguation

When extracting a show year from folder names, **the folder year and the show year are often different**:

- `American Horror Story (2016)(SD) Season 01` → show year is **2011**, folder year 2016 is the season/year (season 06 of the 2011 series).
- `Killjoys 20152019 S01S05 COMPLETE` → `20152019` is a date range (2015–2019); show year is **2015**.
- `NIKITA 20102013 Complete TV Series Seasons 1234 S01S04 and Movies` → `20102013` is a date range; show year is **2010**. The folder `La.Femme.Nikita.1990.720p.BluRay.mp4` is a **movie** (La Femme Nikita 1990), not part of the NIKITA (2010) series.
- `Grimm 2011 Season 16 S01S06 1080p BluRay x265 HEVC 10bit AAC 5 (2011)(1080p) Season 01` → folder name says "Season 16" but contains **seasons 1–6** (S01–S06). Fix folder names like `Seasons 01-06`.
- `game.of.thrones.the.story.so.far.2017.hdtv.x264plutonium.mkv` → **recap/extra**, not a regular episode.

Applied to: database building, quality classification, and any script that maps folder names to show metadata.

### 4-digit episode-number parsing (CORRECTED)

Some files use a 4-digit code where the first 2 digits are the season and the last 2 are the episode:

- **0101** → S01E01, **0102** → S01E02, …, **0836** → S08E36
- **11213** in `burn.notice.11213.avi` → two episodes **S01E12** and **S01E13** (the original parse treated it as season 11, episode 213 — wrong). When the 4-digit token ends in a pattern that looks like S##E## (e.g., `11` + `213` → S01E12/S01E13), split into multiple episodes.
- Rule: extract the first `S##E##` pattern, then fall back to the 4-digit pattern `(\d{2})(\d{2})` where group 1 = season, group 2 = episode.

### Movie-vs-series separation

A file that looks like `La.Femme.Nikita.1990.720p.BluRay.mp4` or `game.of.thrones.the.story.so.far.2017.hdtv.x264plutonium.mkv` is a **movie** or **recap**, not a TV series episode. When building a series database, exclude these files from episode counts. Handle by:
1. Checking the filename for movie/recap keywords (`The Story So Far`, `La Femme Nikita`, etc.)
2. Verifying the show name/year matches the file's year marker
3. Skipping the file from series episode counts

### Season counting from 4-digit episode map

For shows where all episodes are in one folder (e.g., `The Golden Girls`), count seasons from the 4-digit episode map:

```python
# after parsing all files into data[show]['season_episode_map'] (dict: season -> set of episodes)
data[show]['season_count'] = len(data[show]['season_episode_map'])
```

The map is built by:

```python
m = re.match(r'^(\d{2})(\d{2})', base)  # 0101 -> season 1, episode 1
if m:
    s, e = int(m.group(1)), int(m.group(2))
    data[show]['season_episode_map'].setdefault(s, set()).add(e)
```

### Folder-name bug correction (Grimm 2011)

A folder named `Grimm 2011 Season 16 S01S06 1080p BluRay x265 HEVC 10bit AAC 5 (2011)(1080p) Season 01` contains seasons 1–6, not season 16. When scanning, **extract the actual season folders** (Season.1, Season.2, …, Season.6) inside the folder, not the folder name's "Season 16". Corrected on disk: `Grimm 2011 Seasons 01-06 1080p BluRay x265 HEVC 10bit AAC 5 (2011)(1080p) Season 01`.

### Episode title verification against files present

After building the database with show entries, verify episode counts against the actual files present in the directory tree. This catches discrepancies like missing episodes, extra episodes, or mismatched counts.

**Procedure:**

1. **Extract TVDB episode titles** from the paste file or TheTVDB export for each show.
2. **Scan the directory tree** for files matching the show's folder path.
3. **Match by episode number** using the numeric folder pattern: `S01E09` → `09` (or `009` in some trees).
4. **Compare counts**: DB season count / episode count vs actual files on disk.
5. **Report discrepancies**:
   - `Missing episodes`: TVDB episodes not found in directory tree
   - `Extra episodes`: Directory tree files not in TVDB
   - `Count mismatch`: DB count ≠ file count

**Example:**

```text
Show: Japan Sinks: 2020 (2020) - TVDB 370768
DB: 1 season, 10 episodes
Directory tree: 0 files found
Result: Show is MISSING from the library

Show: The Coroner (2015) - TVDB 302973
DB: 1 season, 6 episodes
Directory tree: 7 files found (S01E01, S01E02, S01E03, S01E04, S01E06, S01E07, S01E08)
Result: 1 extra file (S01E06 counted in DB but 6 files found), 1 missing (S01E05)
```

**Rule:** Always verify episode counts against the actual directory tree after adding new shows to the database. Do not assume the DB count matches the file system.

### Similar-name conflict detection

When adding shows from paste files or TVDB lookups, check for similar show names that may be DIFFERENT shows:

1. **Search for similar names** in the database before adding a new show.
2. **Compare the full title** — not just the first word or key phrase.
3. **Flag potential conflicts** for manual review.

**Example:**

- `Japan Sinks: 2020` (2020, TVDB 370768) vs `Japan (2018)` (2018, TVDB 85409) — different shows, similar names. Do NOT confuse these.

**Rule:** Before adding a show, search the database for all shows containing the same key words. Verify the year and full title match before applying the TVDB ID.

### Database-building rule

After the TV show organization workflow, build a structured database:

1. **Scan** the TV library and parse each show folder.
2. **Cross-reference** with `mapping_fixes.csv` (or a similar master mapping) to get TVDB IDs, years, and quality tags.
3. **Merge** show metadata:
   - For each show, find the best match in the mapping (exact name match, then partial match, then keyword match).
   - For unmatched shows, mark `tvdb_id = NULL` and leave `year` as the folder year.
4. **Verify corrections**: manually review ambiguous shows (e.g., American Horror Story 2016→2011, Killjoys 20152019→2015, NIKITA 2010 movie vs series, Grimm 2011 S01-S06, Game of Thrones recap).
5. **Output** a database (SQLite/JSON/CSV) with: show_name, year, tvdb_id, bucket, season_count, episode_count, total_files.

**Key rules for the database:**
- Season count = number of distinct season folders OR number of distinct seasons in the 4-digit episode map (whichever is present).
- Episode count = number of video files in season folders (excluding movies/recaps/extras).
- TVDB ID comes from the mapping CSV; if missing, leave NULL.
- Bucket = first letter of show name (or `#` for numeric-leading collections, `T` for "The "-prefixed).

**Output files:** `tv_db.db` (SQLite), `show_database.json`, `show_database.csv`.

## Merlin (2008) reorganization workflow

Execute after creating the target folder structure (`Series.0`–`Series.5`, Series.N = Season N). This covers the complete Merlin (2008) reorganization:

1. **Inventory** all files across the target folders (`find <Merlin folder> -type f | wc -l`).
2. **Probe** every video file (see probe-batch skill) to confirm readability before committing.
3. **Rename on disk**: normalize filenames (remove duplicate SXXEXX patterns, remove dots, remove `(2008)(SD)` duplicates, extract episode, keep title).
4. **Move files** from source folders into the target `Series.N` folders.
5. **Verify**: ffprobe reorganized files; confirm no data loss; check for collisions.
6. **Handle alternate versions**: never delete alternate-version files. If a collision would occur, rename to avoid it (append `-alt` suffix, or insert episode title). Leave files in place.
7. **Delete empty folders** after all files are moved.

### Merlin target structure

| Folder | Contents |
|--------|----------|
| `Merlin (2008)(SD) Series.0` | 3 files (S00E20 children in need) |
| `Merlin (2008)(SD) Series.1` | 39 files (S01E01–S01E13) |
| `Merlin (2008)(SD) Series.2` | 39 files (S02E01–S02E13) |
| `Merlin (2008)(SD) Series.3` | 40 files (S03E01–S03E13) |
| `Merlin (2008)(SD) Series.4` | 43 files (S04E01–S04E13) |
| `Merlin (2008)(SD) Series.5` | 27 files (S05E01–S05E13) |

### Merlin filename normalization rules

- Remove duplicate `SXXEXX.SXXEXX.` patterns (collapse to single `SXXEXX`)
- Remove extra dots and extra spaces
- Remove ` (2008)(SD)` duplicates
- Extract episode: first `S\d{2}E\d{2}` matches
- Keep Part 1 / Part 2 in titles (do not treat as duplicates)
- Target filename pattern: `Merlin (2008)(SD) SXXEXX.TitleWithSpaces.ext`

### User corrections on Merlin naming
- **Preserve the year**: DO NOT REMOVE THE YEAR from folder names.
- **Remove ALL dots, replace with spaces**: remove all dots, replace with spaces.
- **Keep alternate versions**: never delete alternate-version files; if a collision occurs, rename to avoid it.

## Communication style

- User communicates in short, direct, no-fluff responses (answers like "1", "yes", "continue").
- Always lead with the summary and concrete corrections; put full tables in a separate output file — never paste large tables into prose.
- Do not narrate tool calls the user cannot see.
- Do not mention skills, skills_list, or skill management in responses.
- Respond at the level of detail the user requests — short for yes/no, detailed only for substantive questions.



## Naming Convention

**Show folder** (no quality, single TVDB ID):
`Title (Year) {TVDB-XXXXX}`

**Season folder** (show name + year + quality + series number):
`Title (Year)(Quality) Series X` — user accepts "Series" as a synonym for "Season"; numbering uses "Series.X" (e.g., Series.5), NOT "Season XX"

**Example**: `The 100 (2014)(SD) Series.5\`**

**After normalizing, move season folders into `Show Name (Year)\` parent folders:**
`<Letter>\<Show Name> (<Year>)\<Show Name> (<Year>)(<Quality>) Season XX\`

### Video file (show name + year + quality + season/episode):
`Title (Year)(Quality)S<Season>E<Episode>.<TitleWithSpaces>.<ext>`

**Example**: `The 100 (2014)(SD)S06E01.Sanctum.avi`

**Rules:**
- Show name: spaces for folder names; preserve dots only for established dot-notation titles (e.g., `A.P. Bio`).
- Quality only in season folders and file names, **NOT** in the show folder.
- Single ID for TV shows: only TVDB (no TMDB/IMDb in the folder).
- Year comes from the parent folder name when files use a different year.
- Move season folders into `Show Name (Year)\` parent folders — never leave season folders directly under the letter bucket.

### User corrections on naming
- **Preserve the year**: When normalizing folder names, DO NOT remove the year. (User correction: "DO NOT REMOVE THE YEAR!!")
- **Remove ALL dots, replace with spaces**: When normalizing folder names, remove all dots and replace them with spaces. (User correction: "remove all dots replace with spaces")
- These corrections apply to the W-folder rescan and any other folder renaming.

### W-folder rescan and renaming
When you find `www.UIndex.org.` prefixed folders in the TV library `W` folder:
1. Remove the `www.UIndex.org.` prefix from the folder name.
2. Remove ALL dots from the remaining name.
3. Replace dots with spaces.
4. Preserve the year (user correction: "DO NOT REMOVE THE YEAR!!").
5. Extract show name, SXX, EXX, quality from the resulting name.

### User naming corrections
- **Preserve the year**: When normalizing folder names, DO NOT remove the year. (User correction: "DO NOT REMOVE THE YEAR!!")
- **Remove ALL dots, replace with spaces**: When normalizing folder names, remove all dots and replace them with spaces. (User correction: "remove all dots replace with spaces")
- **Merlin (2008) reorganization — keep alternate versions**: Never delete alternate-version files, even if they look like duplicates. Left in place. If a collision would occur, rename to avoid it (e.g., append `-alt` suffix, or insert the episode title). The target structure is `Merlin (2008)(SD) Series.N` (Series.N = Season N).

**Example**: `www.UIndex.org.Doctor.Who.2023.S02E01.1080p.WEB` → `Doctor Who 2023 S02E01 1080p WEB`

**Example**: `The.Bear.S05E04.1080p.HEVC` → `The Bear S05E04 1080p HEVC`

**Rule**: Never leave dots in folder names after normalization. Remove the `www.UIndex.org.` prefix, remove ALL dots, replace with spaces, preserve the year.

### TV library path conventions (user-confirmed)
The user's target path format:

- **Show folder**: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\`
- **Episode file**: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`
- **Movie library**: `M:\Media\Movies\The CROW(1994)(720p)\The CROW JAPANESE Remaster(1994)(720p).mp4`
- **"Series" is an acceptable synonym for "Season"** — both forms are valid.

### Extras and specials (user-confirmed)

- **All extras go to one place**: `<Letter>\<Show> ({year}){{tvdb-<id>}}\Extras\`. Deleted scenes, gag reels, audition tapes, making-of, featurettes, webisodes and other unnumbered behind-the-scenes material are moved out of release/season subfolders into it. Never leave extras sitting in `Season.N` release folders, and never let an extra inherit a season folder name.
- **Specials that exist on TVDB are named by their special number**: `<Show> ({year}) - S00E## - <TVDB title>.<ext>`, kept inside `Extras\` so they cannot be mistaken for season episodes. Drive this from `specials_map.csv` (`tvdb_id,special,title,match`) rather than hand-renaming — the first matching row wins, so list specific patterns before generic ones, and re-check the map when a show's extras change.
- **Multi-version is the default**: keep every resolution/release of an episode (`--keep-both`); do not auto-delete lower-quality duplicates. SD/720p/1080p copies are kept deliberately.
- Unnumbered videos that match no episode and no extra pattern are still routed to `Extras\` as REVIEW — placed, not dropped, and flagged for manual naming.

See `references/tv-pipeline.md` for the specials-map lookup order, the `--keep-both` guard for rows without an episode number, and the packaged `scripts/generate_tree.py` inventory walker.

### Dashboard / GUI of a plan

When asked for a GUI, web view or "better looking" front-end over the plan or library state, ship one of
two forms — the user does not require HTML and accepts a native desktop app:

- **Browser page**: one self-contained `index.html` (compressed data embedded, no server or CDN) with
  search, status/action/reason filters, sortable columns, paging and filtered-CSV export.
- **Native app**: a stdlib-tkinter window (`gui_app.py`) that additionally *runs* the pipeline — refresh
  plan, apply marked/filtered rows through `phase3_apply.py`, undo last run — with a live subprocess log.
  Tkinter is present on this host (Tk 9.x); use `sys.executable` as the interpreter and `--self-test` for
  a headless smoke check.

Rebuild either whenever the plan regenerates, and verify in a real browser/window before reporting.
Recipe, serving and verification: `references/gui-dashboard.md`.

### Regenerating the live `.7` plan

The live planner rebuilds its own inputs; treat it as the source of truth rather than hand-editing derived CSVs.

1. **Fix mapping at the source** — the map export, `mapping_fixes.csv`, `show_master.csv` and `tvdb_collected.db`. `--prep` regenerates the master from the map plus fixes and preserves prior edits only where the TVDB ID is unchanged, so a correction that changes an ID is silently lost unless it also lives in the map/fixes.
2. **Run the planner without `--prep`** once the inputs are correct, passing the quality/pixel JSON files the library already has.
3. **Move the generated `_plan_phase2*.csv` out of the library root** and re-verify the root loose-file count; refresh the consolidated views in the working set.
4. **Report action/status counts plus the top blocker reasons**, not just a row total.

See `references/tv-pipeline.md` for the exact command line, provenance rules, wholesale adoption of user-supplied mapping/master exports (diff for removed/reverted IDs before overwriting), folding probed resolutions back into the quality file, applying one folder/show batch safely, registering applied destination folders in the map, and the undo-log/CRLF gotchas. It also covers the enriched research DB (pick one canonical copy, adopt `resolved_proposals` as a reviewed batch, work around a write-locked legacy DB) and the scratch-pruning rule for probe/quality inputs.

### Archived Phase 2/3 workflow (reference only)

The live pipeline is `O:\Scripts\TV organization .7\` — phase 2 planner, phase 3 applier (with sha256 duplicate detection) and phase 4 quality-split in one folder; `.4`/`.5` are the earlier working set/mirror and `.6` the snapshot it was merged from. Superseded pipelines are archived under `O:\Scripts\_archive\` and never deleted. See `references/tv-pipeline.md` for the file map, mapping-provenance rules and the archive convention.

- **`plan_all_files.csv`** (`.4`) — the full dry-run plan covering every file: `action` (MOVE / LEAVE / WRITE), `status` (OK / REVIEW / BLOCKED), `src`, `dst`, `tvdb_id`, show/year/season/episode/quality, plus `dup_group` and `follows` (multi-episode chain) columns. Read-only; regenerate after any mapping edit.
- **`mapping_fixes.csv`, `show_master.csv`, `extras_map.csv`, `tvdb_collected.db`** (`.4`) — the mapping inputs the plan is generated from.
- The older `.3` scripts (`phase2_plan.py`, `phase3_apply.py`) survive only as archived reference.

### Execution workflow

1. **Run phase2_plan.py** (dry-run): `python3 phase2_plan.py`. Read its output CSVs.
2. **Review the plan**:
   - `plan_summary_by_show.csv` — summary of planned moves by show
   - `plan_blocked.csv` — shows with BLOCKED entries (reasons: `no S##E## found`, `LOW_SIMILARITY`, `YEAR_MISMATCH`)
   - `plan_ready_OK.csv` — shows with ready-to-move episodes
   - `plan_episodes_preview.csv` — detailed episode preview
3. **Ask the user to commit** — present the counts and the BLOCKED items. Do not move files automatically.
4. **Run phase3_apply.py** only after user approval: `python3 phase3_apply.py --apply`.
5. **Optional — split qualities across drives**: `python3 phase4_split.py --src "T:/Media/TV" --tier 1080p="U:/Media/TV" --tier SD="V:/Media/TV"` (dry run unless `--apply`; `--reserve-gb` guards free space). Only files inside `(Quality) Sxx`/`Season xx` season folders move — loose untagged episodes, show-level artwork and untagged folders stay on the source drive. Each destination's TV folder must be added to Plex/Jellyfin for the moved seasons to appear.
6. **Verify totals after every change:** re-scan the destination root and confirm counts match the plan. Report skipped conflicts.

### Websearch TVDB ID verification workflow

After reviewing `mapping_fixes.csv`, verify `not verified` years (and any flagged IDs) via websearch before writing them into the CSV:

1. **Identify flags**: rows with year `not verified` or unclear TVDB ID. (This session: 78 rows across 20 shows.)
2. **Run websearch** for each: `websearch "Show Name" "TVDB" "year"`. Check the first result field for the TVDB ID and first-air year.
3. **Confirm matches**: if the websearch returns a TVDB ID + year that match the row, mark as verified. (This session: 78 rows all verified via websearch.)
4. **Update the CSV**: write the confirmed TVDB ID into `tvdb_id`; update the note column with the verification source. Do not leave ambiguous rows unchanged.
5. **Re-count**: CSV now has 237 rows; 0 duplicate folders; 0 duplicate TVDB IDs within buckets.

### Example websearch queries (this session)
- `The Eternaut TVDB 420039 2025` → matched
- `The Unit TVDB 75707 2006` → matched
- `Upload TVDB 368211 2020` → matched
- `Unstable TVDB 418721 2023` → matched
- `Doctor Who TVDB 76107 1963` → matched

### Paste file processing workflow (NEW - this session)

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

### Jellyfin CSV cross-reference (NEW - this session)

When cross-referencing a Jellyfin TV show export (any `Library - TV Shows - All [N].csv` or `.json` zip), the file has a **hierarchical structure** with three levels of entries:

1. **Show-level**: `ratingKey == parentRatingKey` (same value), has `title` and `year`.
2. **Season-level**: `parentRatingKey != ratingKey`, has `seasons.title` (e.g., "Season 1").
3. **Episode-level**: `ratingKey != parentRatingKey`, has `seasons.episodes.episodeNumber`, no `seasons.title`.

**Correct extraction of top-level shows**:

```python
if rating_key and rating_key != 'None' and parent_rating_key and rating_key == parent_rating_key and title and title != 'None':
    top_level_shows.add(title)
```

**CRITICAL**: The wrong filter `if not parent_rating_key` returns 0 top-level shows because every row has a parentRatingKey. The correct filter is `rating_key == parent_rating_key and title != 'None'`.

**Why "Containment" appeared multiple times**: The CSV contains one top-level entry per show, plus one season entry per season, plus one episode entry per episode. "Containment" had 1 season and 8 episodes, so it appeared 1 (show) + 1 (season) + 8 (episodes) = 10 times. Cross-reference by **unique top-level title**, not by total entries.

**Workflow for CSV cross-reference**:

1. **Parse the CSV/JSON**: extract all rows, categorize by level.
2. **Extract unique top-level shows**: use `rating_key == parent_rating_key` filter.
3. **Cross-reference with DB**: compare unique titles against `shows` table.
4. **Count missing shows**: unique titles in file but not in DB.
5. **Report**: total shows in file, total in DB, in-file-but-not-DB count, and the list of missing shows.
6. **Apply TVDB IDs**: for shows with known IDs, add to database.
7. **Re-run plan**: after adding shows, re-run the Phase 2/3 plan workflow.

### Subtitle cleanup (non-English only) and pairing rule

- Scan `T:\Media\TV` recursively for subtitle files: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`.
- **Delete only non-English** subtitles. **English subtitles (~900 files) left untouched** — they contain `english`, `eng`, `enhi`, or `en-` markers in the filename.
- **24 files failed deletion** due to Windows path length limits (WinError 3) — these remain in place.
- **Delete verification**: after the deletion, **re-scan the source root with a different method** (e.g., `find -type f | wc -l` vs `delete_subs.py` counter). Confirm: source totals decreased by exactly the number deleted; 924 remain (900 English + 24 path-length failures).
- Do not re-scan with the same method that produced the deletion count — use a second independent method.

### Subtitle pairing during rename/move operations (CRITICAL)

**Rule**: Subtitles must accompany their video file. Whenever a video file is renamed and moved, its subtitle file(s) must also be renamed and moved with it. This applies to ALL rename/move operations.

1. **Enumerate subtitles before renaming**: for each video file being renamed/moved, list all sibling subtitle files (extensions: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`).
2. **Pair by stem**: a subtitle `X.S01E01.en.srt` pairs with video `X.S01E01.mp4` (same stem before the extension).
3. **Rename subtitles together with the video**: if the video moves from `Source/Season 01/` to `Dest/Series.1/`, the subtitle moves to the same destination folder with the same transformation applied to its name.
4. **Never leave orphan subtitles**: after every rename/move batch, verify each video folder contains its subtitle pair. User directive: "whenever a video file is renamed and moved the subtitle file(s) should also be renamed and moved".
5. **Keep original subtitles in place only if they fail to pair**: if a subtitle cannot be paired (no matching video stem), flag it for manual review rather than deleting it.

### Subtitle co-movement checklist

- [ ] Before renaming/moving a video file, list all sibling subtitle files (srt/ssa/ass/sub/idx/vtt/smi/sup/psb)
- [ ] Pair subtitles by stem (same base name, different extension)
- [ ] Apply the same target path to subtitle files as to the video
- [ ] After the move, verify each video folder contains its subtitle pair
- [ ] Any orphan subtitles (no matching video) → flag for manual review, do not delete

### Example

Video move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`
- Subtitle to move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.en.srt`
- Subtitle must be renamed/moved with the video to the same destination

### # folder organization target structure

After organizing into letter buckets (A-Z, `#`), the `#` folder is organized with this target structure:

- **Show folder** (no quality, single TVDB ID): `#\Show Name (Year) {TVDB-XXXXX}`
- **Season folder** (show name + year + quality + series number): `#\Show Name (Year)\Show Name (Year)(Quality) Series X`
- **Episode file**: `#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`

**Rules:**
- Show name: spaces for folder names; preserve dots only for established dot-notation titles (e.g., `A.P. Bio`).
- Quality only in season folders and file names, **NOT** in the show folder.
- Single ID for TV shows: TVDB (no TMDB/IMDb in the folder).
- Year comes from the parent folder name when files use a different year.
- Move season folders into `Show Name (Year)\` parent folders — never leave season folders directly under the `#` bucket.
- **TVDB IDs are remembered and preserved** in this structure — the season folder paths carry the show name, year, and quality exactly as specified.
- The user's exact target format: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`
- **\"Series\" is an acceptable synonym for "Season"** — both forms are valid.

### Quarantine consolidation workflow (new in this session)

After a reorganization that affects `T:\Media\TV\Quarantine`, consolidate the folders to reduce clutter (target: 9–15 folders). The consolidation pattern:

1. **Identify mergeable folders** — folders that represent the same series split by season, quality, or sub-collection should be merged into a single parent folder.
2. **Merge season folders into parent**: e.g., `Universe.History.Channel (Unknown)(720P) Season 01` + `Season 02` + ... `Season 07` → `Universe.History.Channel (Unknown)(720P) Season 01 (All)` (33 files). Merge all season subfolders into one parent folder.
3. **Merge single season folders into parent**: e.g., `Chronicles.of.Narnia.TV.miniseries (Unknown)(SD) Season 01` → `Chronicles.of.Narnia.TV.miniseries (Unknown)(SD)` (6 files).
4. **Keep subtitle-only folders separate**: `english.subtitles`, `Subtitles.SRTMicroDVD` (these are metadata, not videos).
5. **Preserve folder names that encode critical info**: do not lose TVDB IDs, years, or quality tags during merge; the parent folder's name should carry the essential info.
6. **Verify after consolidation**: re-count video files in Quarantine, confirm total files unchanged after merge (files moved, not deleted).

### Re-run rule (new in this session)

**After any major library change** (Quarantine rework, mapping additions, show additions from user-provided TVDB IDs), re-run the plan workflow:

1. **Add the new shows/changes to `mapping_fixes.csv`** (if not already present).
2. **Re-run `phase2_plan.py`** (dry-run): `python3 phase2_plan.py`. Read its output CSVs.
3. **Review the plan**:
   - `plan_summary_by_show.csv` — summary of planned moves by show
   - `plan_blocked.csv` — shows with BLOCKED entries (reasons: `no S##E## found`, `LOW_SIMILARITY`, `YEAR_MISMATCH`)
   - `plan_ready_OK.csv` — shows with ready-to-move episodes
   - `plan_episodes_preview.csv` — detailed episode preview
4. **Check for newly added shows**: verify each show in `mapping_fixes.csv` that was recently added has an entry in the plan. If not, add it to `mapping_fixes.csv` and re-run the plan.
5. **Check for review queues**: shows with many REVIEW episodes (e.g., Unstable 213, Upload 182) need triage before the plan can be committed.
6. **Ask the user to commit** — present the counts and the BLOCKED items. Do not move files automatically.
7. **Run `phase3_apply.py` only after user approval**: `python3 phase3_apply.py --apply`.
8. **Verify totals after every change:** re-scan the destination root and confirm counts match the plan. Report skipped conflicts.

### Websearch TVDB ID verification workflow

After reviewing `mapping_fixes.csv`, verify `not verified` years (and any flagged IDs) via websearch before writing them into the CSV:

1. **Identify flags**: rows with year `not verified` or unclear TVDB ID. (This session: 78 rows across 20 shows.)
2. **Run websearch** for each: `websearch "Show Name" "TVDB" "year"`. Check the first result field for the TVDB ID and first-air year.
3. **Confirm matches**: if the websearch returns a TVDB ID + year that match the row, mark as verified. (This session: 78 rows all verified via websearch.)
4. **Update the CSV**: write the confirmed TVDB ID into `tvdb_id`; update the note column with the verification source. Do not leave ambiguous rows unchanged.
5. **Re-count**: CSV now has 237 rows; 0 duplicate folders; 0 duplicate TVDB IDs within buckets.

### Example websearch queries

- `The Eternaut TVDB 420039 2025` → matched
- `The Unit TVDB 75707 2006` → matched
- `Upload TVDB 368211 2020` → matched
- `Unstable TVDB 418721 2023` → matched
- `Doctor Who TVDB 76107 1963` → matched

### Subtitle cleanup (non-English only) and pairing rule

- Scan `T:\Media\TV` recursively for subtitle files: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`.
- **Delete only non-English** subtitles. **English subtitles (~900 files) left untouched** — they contain `english`, `eng`, `enhi`, or `en-` markers in the filename.
- **24 files failed deletion** due to Windows path length limits (WinError 3) — these remain in place.
- **Delete verification**: after the deletion, **re-scan the source root with a different method** (e.g., `find -type f | wc -l` vs `delete_subs.py` counter). Confirm: source totals decreased by exactly the number deleted; 924 remain (900 English + 24 path-length failures).
- Do not re-scan with the same method that produced the deletion count — use a second independent method.

### Subtitle pairing during rename/move operations (CRITICAL)

**Rule**: Subtitles must accompany their video file. Whenever a video file is renamed and moved, its subtitle file(s) must also be renamed and moved with it. This applies to ALL rename/move operations.

1. **Enumerate subtitles before renaming**: for each video file being renamed/moved, list all sibling subtitle files (extensions: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`).
2. **Pair by stem**: a subtitle `X.S01E01.en.srt` pairs with video `X.S01E01.mp4` (same stem before the extension).
3. **Rename subtitles together with the video**: if the video moves from `Source/Season 01/` to `Dest/Series.1/`, the subtitle moves to the same destination folder with the same transformation applied to its name.
4. **Never leave orphan subtitles**: after every rename/move batch, verify each video folder contains its subtitle pair. User directive: "whenever a video file is renamed and moved the subtitle file(s) should also be renamed and moved".
5. **Keep original subtitles in place only if they fail to pair**: if a subtitle cannot be paired (no matching video stem), flag it for manual review rather than deleting it.

### Subtitle co-movement checklist

- [ ] Before renaming/moving a video file, list all sibling subtitle files (srt/ssa/ass/sub/idx/vtt/smi/sup/psb)
- [ ] Pair subtitles by stem (same base name, different extension)
- [ ] Apply the same target path to subtitle files as to the video
- [ ] After the move, verify each video folder contains its subtitle pair
- [ ] Any orphan subtitles (no matching video) → flag for manual review, do not delete

### Example

Video move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`
- Subtitle to move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.en.srt`
- Subtitle must be renamed/moved with the video to the same destination

### Plan review (Phase 2 + Phase 3)

After adding shows to `mapping_fixes.csv` (or after any major library change), follow this review workflow:

1. **Run phase2_plan.py** (dry-run): `python3 phase2_plan.py`. Read its output CSVs.
2. **Review the plan**:
   - `plan_summary_by_show.csv` — summary of planned moves by show
   - `plan_blocked.csv` — shows with BLOCKED entries (reasons: `no S##E## found`, `LOW_SIMILARITY`, `YEAR_MISMATCH`)
   - `plan_ready_OK.csv` — shows with ready-to-move episodes
   - `plan_episodes_preview.csv` — detailed episode preview
3. **Check for newly added shows**: verify each show in `mapping_fixes.csv` that was recently added has an entry in the plan. If not, add it to `mapping_fixes.csv` and re-run the plan.
4. **Check for review queues**: shows with many REVIEW episodes (e.g., Unstable 213, Upload 182) need triage before the plan can be committed.
5. **Ask the user to commit** — present the counts and the BLOCKED items. Do not move files automatically.
6. **Run phase3_apply.py only after user approval**: `python3 phase3_apply.py --apply`.
7. **Verify totals after every change:** re-scan the destination root and confirm counts match the plan. Report skipped conflicts.

When you find `www.UIndex.org.` prefixed folders in the TV library `W` folder:
1. Remove the `www.UIndex.org.` prefix from the folder name.
2. Remove ALL dots from the remaining name.
3. Replace dots with spaces.
4. Preserve the year (user correction: "DO NOT REMOVE THE YEAR!!").
5. Extract show name, SXX, EXX, quality from the resulting name.

Example: `www.UIndex.org.Doctor.Who.2023.S02E01.1080p.WEB` → `Doctor Who 2023 S02E01 1080p WEB`

### Renaming on disk

When committing folder renames:
1. Apply the same normalization to the disk folder names.
2. Verify the new names on disk after the move.
3. Report the final naming: `Show Name (Year) (Quality) SXXEXX` or `Show Name (Year)` for show folders.


## Quality Tags



| Tag | Meaning |

|---|---|

| `[480p]` | 480p (SD-tier, tracked separately) |

| `[SD]` | Standard Definition (≤ 480p) |

| `[720p]` | 720p |

| `[1080p]` | 1080p |

| `[1440p]` | 1440p |

| `[2160p]` | 2160p (Ultra HD) |



## Special Cases



| Folder | Purpose | TVDB |

|---|---|---|

| `Extras/` | Deleted scenes, bloopers, bonus content | No ID needed |

| `Specials/` | Promos, behind-the-scenes | No ID needed |

| `broken/` | Probe-failed folders (quarantine) | No ID needed |

| `#` | Numeric/leading-number collections | Keep in `#`; do not promote |



**Files without season/episode** (poster.jpg, fanart.jpg, tvshow.nfo, theme.mp3, seasonXXposter.jpg):

- Still organized into the series folder at series level.

- Do NOT skip them, and do NOT add a dummy `S00E00`.



## Verification Checklist



After every change:

- [ ] Per-folder item counts match expectations.

- [ ] No orphaned files (files not in any folder).

- [ ] `broken/` is empty or all items logged.

- [ ] TVDB mapping covers all main shows.

- [ ] Totals match the source audit CSV.



## Output Files & Paths



- Write all project outputs under `O:\Scripts\` — the dedicated artifacts folder has moved (now `O:\Scripts\Movie scripts\Hermes Artifacts\`; it used to be `O:\Scripts\Hermes Artifacts\`). `ls` the parent before writing: the `O:` drive is the persistent workspace for this task, and pipeline folders are renumbered, so confirm the live path rather than trusting either name. Never leave output files in the home directory.

- Dry-run plan CSV columns: `source, dest, kind, action, tvdb_id`.

- Show folder (no quality, single TVDB ID): `Title (Year) {TVDB-XXXXX}`

- Season folder (show name + year + quality + season): `Title (Year)(Quality) Season XX`

- After normalizing, move season folders into `Show Name (Year)\` parent folders: `<Letter>\<Show Name> (<Year>)\<Show Name> (<Year>)(<Quality>) Season XX\`

- Video file (show name + year + quality + season/episode): `Title (Year) (Quality) S<Season>E<Episode>.<OriginalName>.<ext>`



**Rules:**

- Show name: spaces for folder names; preserve dots only for established dot-notation titles (e.g., `A.P. Bio`).

- Quality only in season folders and file names, **NOT** in the show folder.

- Single ID for TV shows: only TVDB (no TMDB/IMDb in the folder).

- Year comes from the parent folder name when files use a different year.

- Move season folders into `Show Name (Year)\` parent folders — never leave season folders directly under the letter bucket.



## Common pitfalls



- **Path mismatch — Python Windows interpreter vs git-bash MSYS**: Python (the Windows Python at `C:\Users\Owner\AppData\Local\hermes\tools\python-3.14.9+...`), including via `subprocess`, CANNOT resolve git-bash MSYS mount points like `/m/` or `/t/`. Commands that succeed in the bash terminal (`ls /m/Media/Movies`, `find /t/Media/TV`) return "file not found" or "Access is denied" when run from Python. Use native Windows drive paths with forward slashes (e.g., `M:/Media/Movies SD/AG SD`) in Python. Bash can use `/m/...`. For file scanning on this host, call a bash script from Python, or run the scan entirely via `bash script.sh` — verify the command works from the terminal before encoding it in a Python caller.

- **ffprobe via bash**: on this Windows host, never call `C:/Program Files/Jellyfin/Server/ffprobe.exe` from Python `subprocess` (WinError 5). A native bash command or bash script is the correct path.

- **Import every name**: if a `-c` one-liner reads `sys.stdin`, `import sys` is mandatory; a missing import aborts the run.

- **Status reporting**: for long batch runs, report progress at the top of each minute so the user can steer.

- **Large tables → files**: never paste large tables into prose; write the full table to an output file and lead with counts.

- **NUL-delimited counting**: `-print0` output has no line breaks, so `wc -l` reads `0`. Count entries another way.

- **ffprobe CSV column order is not the order you requested.** `-show_entries stream=width,height,codec_name -of csv=p=0` can return `codec,width,height`; ffprobe does not honour the listing order in CSV mode. Parse by key (`-of json`, read `stream.width`/`stream.height`) or verify the emitted columns on one sample before slicing positionally — reading height as width silently flips files between SD/720p/1080p buckets while still producing plausible-looking numbers.

- **Never classify media by `os.path.splitext` alone.** A name containing an earlier dot (e.g. `Show.S01E01.12_Monkeys..._RCVR_mkv`) yields a bogus extension, so files whose dot was lost by an older renamer (`_mkv`, `_mp4`, `_avi`, `_srt`) fall through as "not a video" and are silently dropped from the plan. Normalise damaged `_ext` endings to `.ext` first, then re-derive the extension, regenerate, and confirm those files moved from LEAVE to MOVE. Probe one with ffprobe before assuming such a file is junk. Apply the normalised value by **comparison**, not by testing whether an extension was found: `if norm != ext.lower(): ext, stem = norm, fn[:-len(norm)]`. Gating on a missing extension (`if norm and not ext:`) silently no-ops — `splitext` hands back the bogus dotted tail as a non-empty extension, so the totals come out byte-identical and it looks like the repair changed nothing.

- **Mapping corrections written only into a derived file are overwritten on the next `--prep`.** Rebuild-from-source steps keep prior edits only when the key (TVDB ID) is unchanged; write ID-changing fixes into the map export and `mapping_fixes.csv` too, or they vanish along with every plan row derived from them.

- **Check for duplicate folder keys in `mapping_fixes.csv`** before believing a correction applied — the lookup keeps the last matching row, so a stale row later in the file silently wins.

- **A freshly regenerated tree export is still not ground truth.** Even a brand-new `tree /f` / `Media tree.txt` can omit real files: whole episodes inside very long or deeply nested folder names, non-Latin filenames, and OS files like `desktop.ini`. The mechanism is MAX_PATH (260 chars): `tree.exe` and other MAX_PATH-bound enumerators silently skip anything longer, which is why one episode of a season appears while its siblings do not. Generate inventories with a long-path-safe walker (`\\?\`-prefixed paths, see `scripts/generate_tree.py`) instead, and reconcile filename tokens against a live `find` before trusting either. When recursing with the extended prefix, pass the already-prefixed path through unchanged — re-applying the prefix yields `\\?\?\...` and every subdirectory is skipped silently. Read a mismatch as "the tree is incomplete", not "the disk is wrong"; strip leading whitespace from parsed tokens first, since names that legitimately begin with a space produce phantom mismatches.



## Related Skills



- `media-library-organization` — general media folder organization

- `tvdb-metadata-lookup` — TVDB ID lookup (already loaded)



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

### Subtitle cleanup (non-English only) and pairing rule

- Scan `T:\Media\TV` recursively for subtitle files: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`.
- **Delete only non-English** subtitles. **English subtitles (~900 files) left untouched** — they contain `english`, `eng`, `enhi`, or `en-` markers in the filename.
- **24 files failed deletion** due to Windows path length limits (WinError 3) — these remain in place.
- **Delete verification**: after the deletion, **re-scan the source root with a different method** (e.g., `find -type f | wc -l` vs `delete_subs.py` counter). Confirm: source totals decreased by exactly the number deleted; 924 remain (900 English + 24 path-length failures).
- Do not re-scan with the same method that produced the deletion count — use a second independent method.

### Subtitle pairing during rename/move operations (CRITICAL)

**Rule**: Whenever a video file is renamed and moved, its subtitle file(s) must also be renamed and moved so they stay paired. This applies to ALL rename/move operations.

1. **Enumerate subtitles before renaming**: for each video file being renamed/moved, list all sibling subtitle files (extensions: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`).
2. **Pair by stem**: a subtitle `X.S01E01.en.srt` pairs with video `X.S01E01.mp4` (same stem before the extension).
3. **Rename subtitles together with the video**: if the video moves from `Source/Season 01/` to `Dest/Series.1/`, the subtitle moves to the same destination folder with the same transformation applied to its name.
4. **Never leave orphan subtitles**: after every rename/move batch, verify each video folder contains its subtitle pair. User directive: "whenever a video file is renamed and moved the subtitle file(s) should also be renamed and moved".
5. **Keep original subtitles in place only if they fail to pair**: if a subtitle cannot be paired (no matching video stem), flag it for manual review rather than deleting it.

### Subtitle co-movement checklist

- [ ] Before renaming/moving a video file, list all sibling subtitle files (srt/ssa/ass/sub/idx/vtt/smi/sup/psb)
- [ ] Pair subtitles by stem (same base name, different extension)
- [ ] Apply the same target path to subtitle files as to the video
- [ ] After the move, verify each video folder contains its subtitle pair
- [ ] Any orphan subtitles (no matching video) → flag for manual review, do not delete

### Example

Video move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`
- Subtitle to move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.en.srt`
- Subtitle must be renamed/moved with the video to the same destination

### # folder organization target structure

After organizing into letter buckets (A-Z, `#`), the `#` folder is organized with this target structure:

- **Show folder** (no quality, single TVDB ID): `#\Show Name (Year) {TVDB-XXXXX}`
- **Season folder** (show name + year + quality + series number): `#\Show Name (Year)\Show Name (Year)(Quality) Series X`
- **Episode file**: `#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`

**Rules:**
- Show name: spaces for folder names; preserve dots only for established dot-notation titles (e.g., `A.P. Bio`).
- Quality only in season folders and file names, **NOT** in the show folder.
- Single ID for TV shows: TVDB (no TMDB/IMDb in the folder).
- Year comes from the parent folder name when files use a different year.
- Move season folders into `Show Name (Year)\` parent folders — never leave season folders directly under the `#` bucket.
- **TVDB IDs are remembered and preserved** in this structure — the season folder paths carry the show name, year, and quality exactly as specified.
- The user's exact target format: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`
- **\"Series\" is an acceptable synonym for \"Season\"** — both forms are valid.

### Quarantine consolidation workflow (new in this session)

After a reorganization that affects `T:\Media\TV\Quarantine`, consolidate the folders to reduce clutter (target: 9–15 folders). The consolidation pattern:

1. **Identify mergeable folders** — folders that represent the same series split by season, quality, or sub-collection should be merged into a single parent folder.
2. **Merge season folders into parent**: e.g., `Universe.History.Channel (Unknown)(720P) Season 01` + `Season 02` + ... `Season 07` → `Universe.History.Channel (Unknown)(720P) Season 01 (All)` (33 files). Merge all season subfolders into one parent folder.
3. **Merge single season folders into parent**: e.g., `Chronicles.of.Narnia.TV.miniseries (Unknown)(SD) Season 01` → `Chronicles.of.Narnia.TV.miniseries (Unknown)(SD)` (6 files).
4. **Keep subtitle-only folders separate**: `english.subtitles`, `Subtitles.SRTMicroDVD` (these are metadata, not videos).
5. **Preserve folder names that encode critical info**: do not lose TVDB IDs, years, or quality tags during merge; the parent folder's name should carry the essential info.
6. **Verify after consolidation**: re-count video files in Quarantine, confirm total files unchanged after merge (files moved, not deleted).

### Archived Phase 2/3 workflow (reference only)

Two scripts exist in `O:\Scripts\TV organization .3\`:
- **phase2_plan.py** — DRY-RUN planner. Reads `mapping_fixes.csv`, scans the library, writes `_plan_phase2.csv` and `_plan_phase2_episodes.csv` with MOVE/LEAVE/BLOCKED actions. **Read-only** — does not move files.
- **phase3_apply.py** — APPLY script. Reads the Phase 2 plan, moves files with `--apply`, keeps an undo log. **Dry-run by default**; add `--apply` to commit.

### Re-run rule (new in this session)

**After any major library change** (Quarantine rework, mapping additions, show additions from user-provided TVDB IDs), re-run the plan workflow:

1. **Add the new shows/changes to `mapping_fixes.csv`** (if not already present).
2. **Re-run `phase2_plan.py`** (dry-run): `python3 phase2_plan.py`. Read its output CSVs.
3. **Review the plan**:
   - `plan_summary_by_show.csv` — summary of planned moves by show
   - `plan_blocked.csv` — shows with BLOCKED entries (reasons: `no S##E## found`, `LOW_SIMILARITY`, `YEAR_MISMATCH`)
   - `plan_ready_OK.csv` — shows with ready-to-move episodes
   - `plan_episodes_preview.csv` — detailed episode preview
4. **Check for newly added shows**: verify each show in `mapping_fixes.csv` that was recently added has an entry in the plan. If not, add it to `mapping_fixes.csv` and re-run the plan.
5. **Check for review queues**: shows with many REVIEW episodes (e.g., Unstable 213, Upload 182) need triage before the plan can be committed.
6. **Ask the user to commit** — present the counts and the BLOCKED items. Do not move files automatically.
7. **Run `phase3_apply.py` only after user approval**: `python3 phase3_apply.py --apply`.
8. **Verify totals after every change:** re-scan the destination root and confirm counts match the plan. Report skipped conflicts.

### Websearch TVDB ID verification workflow

After reviewing `mapping_fixes.csv`, verify `not verified` years (and any flagged IDs) via websearch before writing them into the CSV:

1. **Identify flags**: rows with year `not verified` or unclear TVDB ID.
2. **Run websearch** for each: `websearch "Show Name" "TVDB" "year"`. Check the first result field for the TVDB ID and first-air year.
3. **Confirm matches**: if the websearch returns a TVDB ID + year that match the row, mark as verified.
4. **Update the CSV**: write the confirmed TVDB ID into `tvdb_id`; update the note column with the verification source. Do not leave ambiguous rows unchanged.
5. **Re-count**: CSV now has 237 rows; 0 duplicate folders; 0 duplicate TVDB IDs within buckets.

### Example websearch queries
- `The Eternaut TVDB 420039 2025` → matched
- `The Unit TVDB 75707 2006` → matched
- `Upload TVDB 368211 2020` → matched
- `Unstable TVDB 418721 2023` → matched
- `Doctor Who TVDB 76107 1963` → matched

### Subtitle cleanup (non-English only) and pairing rule

- Scan `T:\Media\TV` recursively for subtitle files: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`.
- **Delete only non-English** subtitles. **English subtitles (~900 files) left untouched** — they contain `english`, `eng`, `enhi`, or `en-` markers in the filename.
- **24 files failed deletion** due to Windows path length limits (WinError 3) — these remain in place.
- **Delete verification**: after the deletion, **re-scan the source root with a different method** (e.g., `find -type f | wc -l` vs `delete_subs.py` counter). Confirm: source totals decreased by exactly the number deleted; 924 remain (900 English + 24 path-length failures).
- Do not re-scan with the same method that produced the deletion count — use a second independent method.

### Subtitle pairing during rename/move operations (CRITICAL)

**Rule**: Subtitles must accompany their video file. Whenever a video file is renamed and moved, its subtitle file(s) must also be renamed and moved with it. This applies to ALL rename/move operations.

1. **Enumerate subtitles before renaming**: for each video file being renamed/moved, list all sibling subtitle files (extensions: `.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`).
2. **Pair by stem**: a subtitle `X.S01E01.en.srt` pairs with video `X.S01E01.mp4` (same stem before the extension).
3. **Rename subtitles together with the video**: if the video moves from `Source/Season 01/` to `Dest/Series.1/`, the subtitle moves to the same destination folder with the same transformation applied to its name.
4. **Never leave orphan subtitles**: after every rename/move batch, verify each video folder contains its subtitle pair. User directive: "whenever a video file is renamed and moved the subtitle file(s) should also be renamed and moved".
5. **Keep original subtitles in place only if they fail to pair**: if a subtitle cannot be paired (no matching video stem), flag it for manual review rather than deleting it.

### Subtitle co-movement checklist

- [ ] Before renaming/moving a video file, list all sibling subtitle files (srt/ssa/ass/sub/idx/vtt/smi/sup/psb)
- [ ] Pair subtitles by stem (same base name, different extension)
- [ ] Apply the same target path to subtitle files as to the video
- [ ] After the move, verify each video folder contains its subtitle pair
- [ ] Any orphan subtitles (no matching video) → flag for manual review, do not delete

### Example

Video move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.Sanctum.ext`
- Subtitle to move: `T:\Media\TV\#\The 100 (2014)\The 100 (2014)(SD) Season 06\The 100 (2014)(SD)S06E01.en.srt`
- Subtitle must be renamed/moved with the video to the same destination

### Plan review (Phase 2 + Phase 3)

After adding shows to `mapping_fixes.csv` (or after any major library change), follow this review workflow:

1. **Run phase2_plan.py** (dry-run): `python3 phase2_plan.py`. Read its output CSVs.
2. **Review the plan**:
   - `plan_summary_by_show.csv` — summary of planned moves by show
   - `plan_blocked.csv` — shows with BLOCKED entries (reasons: `no S##E## found`, `LOW_SIMILARITY`, `YEAR_MISMATCH`)
   - `plan_ready_OK.csv` — shows with ready-to-move episodes
   - `plan_episodes_preview.csv` — detailed episode preview
3. **Check for newly added shows**: verify each show in `mapping_fixes.csv` that was recently added has an entry in the plan. If not, add it to `mapping_fixes.csv` and re-run the plan.
4. **Check for review queues**: shows with many REVIEW episodes (e.g., Unstable 213, Upload 182) need triage before the plan can be committed.
5. **Ask the user to commit** — present the counts and the BLOCKED items. Do not move files automatically.
6. **Run phase3_apply.py only after user approval**: `python3 phase3_apply.py --apply`.
7. **Verify totals after every change:** re-scan the destination root and confirm counts match the plan. Report skipped conflicts.

When you find `www.UIndex.org.` prefixed folders in the TV library `W` folder:
1. Remove the `www.UIndex.org.` prefix from the folder name.
2. Remove ALL dots from the remaining name.
3. Replace dots with spaces.
4. Preserve the year (user correction: "DO NOT REMOVE THE YEAR!!").
5. Extract show name, SXX, EXX, quality from the resulting name.

Example: `www.UIndex.org.Doctor.Who.2023.S02E01.1080p.WEB` → `Doctor Who 2023 S02E01 1080p WEB`

### Renaming on disk
When committing folder renames:
1. Apply the same normalization to the disk folder names.
2. Verify the new names on disk after the move.
3. Report the final naming: `Show Name (Year) (Quality) SXXEXX` or `Show Name (Year)` for show folders.


## Quality Tags



| Tag | Meaning |

|---|---|

| `[480p]` | 480p (SD-tier, tracked separately) |

| `[SD]` | Standard Definition (≤ 480p) |

| `[720p]` | 720p |

| `[1080p]` | 1080p |

| `[1440p]` | 1440p |

| `[2160p]` | 2160p (Ultra HD) |



## Special Cases



| Folder | Purpose | TVDB |

|---|---|---|

| `Extras/` | Deleted scenes, bloopers, bonus content | No ID needed |

| `Specials/` | Promos, behind-the-scenes | No ID needed |

| `broken/` | Probe-failed folders (quarantine) | No ID needed |

| `#` | Numeric/leading-number collections | Keep in `#`; do not promote |



**Files without season/episode** (poster.jpg, fanart.jpg, tvshow.nfo, theme.mp3, seasonXXposter.jpg):

- Still organized into the series folder at series level.

- Do NOT skip them, and do NOT add a dummy `S00E00`.



## Verification Checklist



After every change:

- [ ] Per-folder item counts match expectations.

- [ ] No orphaned files (files not in any folder).

- [ ] `broken/` is empty or all items logged.

- [ ] TVDB mapping covers all main shows.

- [ ] Totals match the source audit CSV.



## Output Files & Paths



- Write all project outputs under `O:\Scripts\` — the dedicated artifacts folder has moved (now `O:\Scripts\Movie scripts\Hermes Artifacts\`; it used to be `O:\Scripts\Hermes Artifacts\`). `ls` the parent before writing: the `O:` drive is the persistent workspace for this task, and pipeline folders are renumbered, so confirm the live path rather than trusting either name. Never leave output files in the home directory.

- Dry-run plan CSV columns: `source, dest, kind, action, tvdb_id`.

- Show folder (no quality, single TVDB ID): `Title (Year) {TVDB-XXXXX}`

- Season folder (show name + year + quality + season): `Title (Year)(Quality) Season XX`

- After normalizing, move season folders into `Show Name (Year)\` parent folders: `<Letter>\<Show Name> (<Year>)\<Show Name> (<Year>)(<Quality>) Season XX\`

- Video file (show name + year + quality + season/episode): `Title (Year) (Quality) S<Season>E<Episode>.<OriginalName>.<ext>`



**Rules:**

- Show name: spaces for folder names; preserve dots only for established dot-notation titles (e.g., `A.P. Bio`).

- Quality only in season folders and file names, **NOT** in the show folder.

- Single ID for TV shows: only TVDB (no TMDB/IMDb in the folder).

- Year comes from the parent folder name when files use a different year.

- Move season folders into `Show Name (Year)\` parent folders — never leave season folders directly under the letter bucket.



## Common pitfalls



- **Path mismatch — Python Windows interpreter vs git-bash MSYS**: Python (the Windows Python at `C:\Users\Owner\AppData\Local\hermes\tools\python-3.14.9+...`), including via `subprocess`, CANNOT resolve git-bash MSYS mount points like `/m/` or `/t/`. Commands that succeed in the bash terminal (`ls /m/Media/Movies`, `find /t/Media/TV`) return "file not found" or "Access is denied" when run from Python. Use native Windows drive paths with forward slashes (e.g., `M:/Media/Movies SD/AG SD`) in Python. Bash can use `/m/...`. For file scanning on this host, call a bash script from Python, or run the scan entirely via `bash script.sh` — verify the command works from the terminal before encoding it in a Python caller.

- **ffprobe via bash**: on this Windows host, never call `C:/Program Files/Jellyfin/Server/ffprobe.exe` from Python `subprocess` (WinError 5). A native bash command or bash script is the correct path.

- **Import every name**: if a `-c` one-liner reads `sys.stdin`, `import sys` is mandatory; a missing import aborts the run.

- **Status reporting**: for long batch runs, report progress at the top of each minute so the user can steer.

- **Large tables → files**: never paste large tables into prose; write the full table to an output file and lead with counts.

- **NUL-delimited counting**: `-print0` output has no line breaks, so `wc -l` reads `0`. Count entries another way.

- **ffprobe CSV column order is not the order you requested.** `-show_entries stream=width,height,codec_name -of csv=p=0` can return `codec,width,height`; ffprobe does not honour the listing order in CSV mode. Parse by key (`-of json`, read `stream.width`/`stream.height`) or verify the emitted columns on one sample before slicing positionally — reading height as width silently flips files between SD/720p/1080p buckets while still producing plausible-looking numbers.

- **Never classify media by `os.path.splitext` alone.** A name containing an earlier dot (e.g. `Show.S01E01.12_Monkeys..._RCVR_mkv`) yields a bogus extension, so files whose dot was lost by an older renamer (`_mkv`, `_mp4`, `_avi`, `_srt`) fall through as "not a video" and are silently dropped from the plan. Normalise damaged `_ext` endings to `.ext` first, then re-derive the extension, regenerate, and confirm those files moved from LEAVE to MOVE. Probe one with ffprobe before assuming such a file is junk. Apply the normalised value by **comparison**, not by testing whether an extension was found: `if norm != ext.lower(): ext, stem = norm, fn[:-len(norm)]`. Gating on a missing extension (`if norm and not ext:`) silently no-ops — `splitext` hands back the bogus dotted tail as a non-empty extension, so the totals come out byte-identical and it looks like the repair changed nothing.

- **Mapping corrections written only into a derived file are overwritten on the next `--prep`.** Rebuild-from-source steps keep prior edits only when the key (TVDB ID) is unchanged; write ID-changing fixes into the map export and `mapping_fixes.csv` too, or they vanish along with every plan row derived from them.

- **Check for duplicate folder keys in `mapping_fixes.csv`** before believing a correction applied — the lookup keeps the last matching row, so a stale row later in the file silently wins.

- **A freshly regenerated tree export is still not ground truth.** Even a brand-new `tree /f` / `Media tree.txt` can omit real files: whole episodes inside very long or deeply nested folder names, non-Latin filenames, and OS files like `desktop.ini`. The mechanism is MAX_PATH (260 chars): `tree.exe` and other MAX_PATH-bound enumerators silently skip anything longer, which is why one episode of a season appears while its siblings do not. Generate inventories with a long-path-safe walker (`\\?\`-prefixed paths, see `scripts/generate_tree.py`) instead, and reconcile filename tokens against a live `find` before trusting either. When recursing with the extended prefix, pass the already-prefixed path through unchanged — re-applying the prefix yields `\\?\?\...` and every subdirectory is skipped silently. Read a mismatch as "the tree is incomplete", not "the disk is wrong"; strip leading whitespace from parsed tokens first, since names that legitimately begin with a space produce phantom mismatches.



## Related Skills



- `media-library-organization` — general media folder organization

- `tvdb-metadata-lookup` — TVDB ID lookup (already loaded)

