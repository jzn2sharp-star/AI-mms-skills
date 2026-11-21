# TV Library Normalization (Messy → Conforming)

Use when a TV letter bucket contains quality-split pairs, loose episode folders, or dotted show folders that need normalizing to `Show (Year)(Quality) Season XX`.

## Pattern 1: Quality-split pairs

A show appears as two folders: `Show (Unknown)` (empty) + `Show(Unknown)Quality` (has content). The `(Unknown)` folder is always empty — delete it. The quality folder needs normalizing.

**Procedure:**
1. Delete all empty `(Unknown)` folders (verify empty first with `os.listdir`).
2. For each quality folder, extract show name + quality from the folder name: regex `^(.+?)\(?Unknown\)?(\w+)$`.
3. Quality: uppercase the extracted token; append `p` if it's a bare number (720 → 720p).
4. Year: extract from show name if a 4-digit year is present; otherwise look up in a known-shows dict; otherwise `Unknown`.
5. If the quality folder has **season subdirs** (Season.1, season.4, 1, 2, etc.):
   - Extract season number from subdir name (`Season.N`, `SNN`, or bare `N`).
   - Rename/move each subdir to `Show (Year)(Quality) Season NN`.
   - Move the entire subdir (not just files) to the bucket root with the new name.
6. If the quality folder has **loose videos** (no subdirs):
   - Group videos by season extracted from filename (`S(\d+)E\d+`).
   - Create `Show (Year)(Quality) Season NN` for each season.
   - Move videos + non-video sidecars into the season folder.
   - Delete junk files (`.exe`, `.db`, `.txt`, `.nfo` if orphaned).
7. If the quality folder has **both** subdirs and loose videos: handle subdirs first, then loose videos.
8. Remove the quality folder if empty after processing.

**Known-shows year lookup:** maintain a dict of ~90+ show names → years. Covers most common shows. For unmatched, use `Unknown`.

**Case-insensitive matching:** when matching folder names to show names, lowercase both and use `startswith`.

## Pattern 2: Loose episode folders

Folders like `Show.S01E01.1080p.BluRay` that contain only sidecar files (srt, nfo, txt) and sometimes videos. These are orphaned sidecar folders.

**Procedure:**
1. Parse show, season, episode, quality from folder name: `^(.+?)\.S(\d+)E(\d+)\.(.+)$`.
2. Quality = first `NNNp` token in the `rest` part; default `SD`.
3. Create/find season folder: `Show (Unknown)(Quality) Season NN`.
4. Move video files (`.mkv/.mp4/.avi/...`) and `.srt` files to the season folder.
5. Delete junk (`.exe`, `.db`, `.txt`, `.nfo`).
6. Remove the now-empty folder.

**Pitfall — subtitle filename collision:** Multiple loose episode folders for the same show/season often contain `.srt` files with identical names (e.g., `8.English.srt` appears in both `S01E01` and `S01E02` folders, numbered by language index, not episode). Moving them all into one season folder causes `os.path.exists(dst)` to skip the duplicates, leaving source files behind and producing incomplete season folders. **Fix:** prefix each `.srt` with the episode code before moving: `S01E02.8.English.srt`. Video files rarely collide (they include the episode in the name), but `.srt` files numbered by language index always will.

**Pitfall — leftover sidecar-only folders:** After the main loose-episode consolidation pass, some folders may remain that contain only `.srt` files (no video). These are orphaned sidecar folders that the initial pass missed (often because their video was already moved in a prior run). Handle them in a second pass: parse show/season/episode from the folder name, create/find the season folder, prefix each `.srt` with the episode code, move, then remove the empty folder. Verify 0 leftover folders after this pass.

**Note:** many loose episode folders are completely empty (just placeholders). Handle them the same way — they'll be removed as empty.

## Pattern 3: Dotted show / season folders

Folders like `Show.Season.1`, `Show.S01.1080p.BluRay`, `Show (2014) Season.1 [720p]` that need renaming to `Show (Year)(Quality) Season XX`.

**Procedure:**
1. Match show name against known-shows dict (case-insensitive, `startswith`).
2. Year: from folder name (4-digit) → known-shows dict → `Unknown`.
3. Quality: first `NNNp` in name → `[SD]`/`(SD)` tag → `SD` default.
4. Season: `Season.N` → `.SNN.` → `.SNN` → bare number in name → scan video files inside for `S(\d+)E\d+` → default 1.
5. Rename the folder (or merge if destination exists).

## Pattern 4: "The X" article reorganization

After normalizing a letter bucket, folders whose names start with "The " (the article) should be moved to the letter bucket matching the first letter of the word **after** "The". The folder name keeps the "The" prefix — only the location changes.

Examples: `The Big Bang Theory (2007)(SD) Season 01` → move to `B/`; `The 100 (2014)` → move to `#/` (numbers); `The Umbrella Academy (...)` → move to `U/`.

**Procedure:**
1. Scan the source letter bucket (typically `T/` since most "The X" shows end up there).
2. For each folder starting with `The ` or `The.`:
   - Strip the "The " / "The." prefix (case-insensitive).
   - Take the first character of the remainder.
   - If it's a digit → target is `#`.
   - If it's `(` (e.g., `The (Unknown)(SD) Season 01`) → skip (the show name is just "The").
   - Otherwise → target is that uppercase letter.
3. If the target letter equals the source letter (e.g., "The Terminal List" → T), skip (already in the right place).
4. Move the folder to `TV/<target_letter>/`. No renaming — the folder name keeps "The".
5. Verify: 0 real conflicts (a folder with the same name should not already exist in the target).

**Pitfalls:**
- Do NOT strip "The" from the folder name — only the location changes. The user's convention keeps the article in the display name.
- Folders where the word after "The" starts with the same letter as the source bucket (e.g., "The Terminal List" in T) stay put — no move needed.
- Always dry-run first: report how many folders would move to each target letter before applying.

**Double check then ignore articles (user-specified):** Before treating any "The" folder as an article, verify the word after "The" is a real title word. "The 100", "The 4400" — "The" IS an article (organize under "#"). "The Terminal List" — "The" is an article but Terminal starts with T, so it stays in T. Only move when the target letter differs from the source. "The Whispers" → W (move out of T). Do NOT blindly move all "The X" folders.

## Pattern 5: "A"/"An" article reorganization

Same as Pattern 4, but for folders starting with the article "A " or "An " (case-insensitive). Move them to the letter bucket matching the first letter of the word after the article. Keep the article in the folder name — only the location changes.

**Outlier rule (user-specified):** "A P Bio", "A.P", "A.P (2018)" and similar where "A"/"An" is part of the title (single-letter or initialism) are NOT articles — leave them in A. 99% of the rest: treat "A"/"An" as an article and organize by the following word.

**Procedure:**
1. Scan every letter bucket (not just A) for folders starting with `A ` or `An ` (case-insensitive, word boundary).
2. For each candidate, strip the article and take the first character of the remainder.
   - If the remainder's first token is a single letter or initialism (e.g. "P", "P.", "P Bio"), or the folder is a known outlier (A P Bio, A.P), skip — leave in A.
   - If it's a digit → target `#`.
   - Otherwise → target is that uppercase letter.
3. If target == source letter, skip.
4. Move the folder to `TV/<target_letter>/` without renaming.
5. Dry-run first: report counts per target letter before applying.

**Pitfalls:**
- Do not strip the article from the folder name — only the location changes.
- A folder whose name is just "A" or "An" (no following word) stays put.
- Verify no real conflicts (same name already in target) before moving.

## Pattern 6: "New folder" recovery

When a bucket contains a folder named `New folder` (or similar generic name) that holds video files, it is usually a mislabeled show folder. Identify the show from the video filenames, create a proper show folder with the correct name, and move all files there.

**Procedure:**
1. List the contents of the `New folder`.
2. Extract the show name from video filenames (strip episode/quality markers).
3. Look up the show in the known-shows dict for the year.
4. Create `Show (Year)(Quality) Season NN` and move all files (videos + sidecars) there.
5. Remove the now-empty `New folder`.

**Pitfalls:**
- Do not assume the folder is junk — it may contain a full season of episodes.
- Quality comes from the filenames or the known-shows dict, not from the folder name.

## Pattern 7: Year recovery via web search for (Unknown) folders

When a TV bucket contains folders with `(Unknown)` year tags, recover years before normalizing. The known-shows dict covers common shows, but many will be missing.

**Procedure:**
1. List all `(Unknown)` folders and group by show name (strip `(Unknown)` and quality tag).
2. For each unique show, check if it exists elsewhere in the library with a `(Year)` — exact normalized match first, then fuzzy (substring).
3. For shows not found in the library, search the web (web_search) in batches of ~5-10 shows per query. Use quoted show names with "TV series year".
4. Extract the year from search results (Wikipedia, IMDb, TMDB all list it prominently).
5. Apply year fixes: rename `(Unknown)` → `(YEAR)` in all matching folders. Use the show name with spaces (convert dots to spaces per file-naming-conventions).
6. For shows that are actually mislabeled (e.g., "The (Unknown)" is really "The Whispers"), apply a name replacement in addition to the year fix.
7. For shows where the year is in the folder name but the show name includes release info (e.g., "Tales.From.The.Void.2024.Season.1.Complete..."), extract just the show name and year, discarding release info.

**Pitfalls:**
- Some `(Unknown)` folders are actually different shows than their name suggests — verify by checking video filenames inside (e.g., "The (Unknown)" folder contained "The.Whispers" episodes).
- When merging renamed folders into existing ones (same show+year already exists), use merge (move files, then remove empty source) not rename (which fails on collision).
- Dot-notation folders (e.g., `Teen.Wolf`) that were created from `(Unknown)` renames should use spaces per convention, but pre-existing dotted folders in the library are left as-is (the user's library predominantly uses dots; converting all would be a massive operation not yet requested).
- Season numbers can be wrong in folder names (e.g., "Season 123" when files are S01-S03). Always verify season numbers from the video filenames inside, not the folder name.
**Per-bucket year_map approach:** When processing a bucket, build a dictionary mapping show names to years for all shows in that bucket. Use this to resolve (Unknown) years without web searching for every show. Steps: (1) List all (Unknown) folders. (2) For each, check if the same show exists elsewhere in the library with a (Year) — exact normalized match first, then fuzzy (substring). This typically resolves 60-80% of years from the library alone. (3) For remaining shows, web search in batches of ~10. (4) Save the year_map to a file for reuse across buckets. (5) Apply year fixes using the year_map. (6) After applying, verify 0 (Unknown) folders remain; any that couldn't be resolved are flagged for manual review.

- **Mislabeled show names:** Show folders may use abbreviated or truncated names that cause confusion. Examples: a folder named "Mental (2009)" actually contained Mentalist seasons (The Mentalist, 2008); a folder named "Mr" actually contained Mr. Robot (2015). Always verify the show name against the video filenames inside, not just the folder name. When renaming, add a distinguishing suffix to avoid collision with the canonical name.
- **Distributor-named folders:** Some folders are named after the distributor/source rather than the show (e.g., "Amazon." prefix containing "Just Add Magic" episodes). These get misfiled under the wrong letter bucket. Identify the actual show from video filenames and move to the correct letter bucket.

## Pattern 8: Duplicate encode handling

When the same show/season exists in multiple folders (different encodes, e.g., dot-notation `The.Terminal.List` and spaced `The Terminal List`), these are different releases, NOT duplicates to merge. Keep them separate.

**Pitfall:** Do not automatically merge folders with the same show name — verify they have the same file count and content first. Different file counts = different encodes = keep separate. If renaming one to match the other's naming convention (e.g., dots→spaces), add a distinguishing suffix like ` (2)` to avoid collision.

## Pattern 9: Junk-only and misplaced folders in TV buckets

TV letter buckets often contain folders that are not TV shows at all. These should be identified and handled separately from the main normalization.

**Junk-only folders:** Folders containing only `.txt`, `.nfo`, `.exe`, `.db` files (no video files). These are orphaned sidecar folders from deleted or moved content. **Action:** delete all files and remove the folder. Verify by checking for video extensions (`.mkv/.mp4/.avi/.m4v/.wmv/.mov/.mpg/.mpeg/.ts/.flv/.webm`) — if none present, the folder is junk.

**Misplaced movie folders:** Single-file folders containing a movie file (e.g., `Demon.Knight.1995/Demon.Knight.1995.avi`). These belong in the movie library, not TV. **Action:** leave in place and flag for manual review — do not auto-move to movies (the user may want to verify first).

**Misplaced show folders:** Folders whose name doesn't match the content (e.g., a folder named `2d` containing Nikita episodes). **Action:** identify the actual show from video filenames, note the correct target bucket, and flag for manual review. Do not auto-move across letter buckets without user confirmation.

**Extras folders:** Folders named `Deleted.Scenes`, `Deleted Scenes`, `Featurettes`, `Behind the Scenes`, etc. containing video files. These are bonus content for a show in the same bucket. **Action:** leave in place during normalization; the user can decide whether to merge them into the show's folder or keep separate. Do not delete them.

**Pitfall:** Do not assume every folder in a TV bucket is a TV show. Always check the actual video filenames inside before deciding how to process. A folder named `2d` might contain Nikita episodes; a folder named `Deleted.Scenes` might contain Breaking Bad extras.

## Pattern 10: Extras/trailers consolidation

When the user asks to consolidate all extras/trailers/deleted-scenes/featurettes/bonus folders into a single location under TV, collect them from all letter buckets and move them into `T:\Media\TV\Extras\`.

**Procedure:**
1. Scan every letter bucket (A-Z, #) for folders whose name (case-insensitive) contains: `deleted`, `featurette`, `behind`, `trailer`, `bonus`, `extra`, `scene`, `gag`, `bloopers`, `cut scene`, `alternate ending`.
2. For each candidate, verify it actually contains video files and is NOT a TV show with a similar name (e.g., "Extraordinary 2023" is a TV show, not extras; "Zoeys Extraordinary Playlist" is a TV show). Use the "double check then ignore articles" principle — verify the folder is genuinely extras, not a show.
3. List all candidates with their source bucket and file count. Report before moving.
4. Create `T:\Media\TV\Extras\` if it doesn't exist.
5. Move each extras folder into `Extras\` without renaming. Handle collisions (same name from different buckets) by appending ` (2)`, etc.
6. Verify: count folders in Extras, verify no extras remain in source buckets (except known TV shows with "extra" in the name).

**Pitfalls:**
- Do not move folders that are actually TV shows with "extra" in the title (e.g., "Extraordinary 2023", "Zoeys Extraordinary Playlist"). Verify by checking if the folder has a year tag and season structure.
- The user may explicitly request moving a specific show that happens to be a TV show (e.g., "Behind the Scenes (2024)") — comply even if it's technically a show.
- After moving, check all remaining buckets for any extras that were missed in the first pass.
- Extras folders may contain nested subfolders (e.g., "Deleted.Scenes [1080p]/Featurettes/") — move the entire top-level folder.
- **Generic-named extras:** Some extras folders have generic names like "Soundtrack", "english.subtitles", "Behind the Scenes" that don't clearly indicate they're extras. Verify by checking contents — if the folder contains only .srt files, .mp3 soundtracks, or featurette videos without a show's season structure, it's extras. Check file sizes and types before moving.

## Pattern 11: Bucket processing workflow (systematic)

When processing a TV letter bucket from messy to normalized, follow this order:

1. **Categorize** all folders into: clean (has year + season), quality-only (has year, no season), Unknown (has (Unknown)), other (no year), empty.
2. **Delete empty folders** first (verify empty with `os.listdir`).
3. **Process quality-only folders** (Pattern 1) — split into season folders.
4. **Process Unknown folders** (Pattern 7) — recover years via web search, then normalize.
5. **Process season/dotted folders** (Pattern 3) — rename to convention.
6. **Process loose episode folders** (Pattern 2) — group by season.
7. **Process junk/misplaced folders** (Pattern 9) — delete junk, flag misplacements.
8. **Handle "New folder"** (Pattern 6) — identify and normalize.
9. **Process extras** (Pattern 10) — move to Extras folder.
10. **Create parent show folders** (Pattern 13) — move ALL season folders into `Show (Year)\` parent folders. THIS STEP IS MANDATORY — do not skip it. Leaving season folders directly under the letter bucket violates the naming convention and will be caught by the user. After this step, verify 0 loose season folders remain at the letter-bucket level. If any remain, they are stray season folders — see Pattern 13 → "Stray season folders at bucket level."
11. **Verify** — 0 remaining without (year) or (Unknown), 0 loose season folders at bucket level, file counts unchanged.

**Pitfalls:**
- Always dry-run first for each category.
- Process deepest paths first within each category.
- After processing each category, re-scan to update counts before proceeding to the next.
- Some folders may need multiple passes (e.g., a folder that was "quality-only" becomes "clean" after splitting).
- Quality folders with subfolders named "Season.1", "Season.2", etc. need to be split into individual season folders — do not rename the whole quality folder as one season.
- Folders like "Eureka.Season.1.to.5.Mp4.1080p" have subfolders "Season.1" through "Season.5" that each need to become separate `Show (Year)(Quality) Season NN` folders.

## Pattern 12: Quality-folder sub-splitting

When a quality-only folder contains multiple season subfolders (e.g., "Season.1", "Season.2", ..., "Season.5"), each subfolder must become its own normalized season folder. Do not rename the quality folder as a single season.

**Procedure:**
1. For each subfolder, extract the season number.
2. Create `Show (Year)(Quality) Season NN` at the bucket root.
3. Move all contents (videos + sidecars) from the subfolder into the season folder.
4. Remove the now-empty subfolder.
5. Remove the quality folder if empty.

**Pitfalls:**
- Subfolder names may use various formats: "Season.1", "Season 1", "S01", "1", "season.1". Handle all.
- If a season folder already exists at the bucket root, merge contents instead of creating a duplicate.
- Verify file counts after moving — subfolders may contain nested directories that need recursive handling.

- **MAX_PATH (260 chars):** Python `os.rename`/`shutil.move` raise `WinError 3` on long paths. Use the `\\?\\` extended-path prefix on both source and destination. If that fails, use `subst` to map a drive letter (bash only — Python can't see subst'd drives).
- **Locked files (Thumbs.db):** `WinError 32` (file locked). Use copy-and-recreate: `shutil.copy2` to temp, copy to destination, delete original (may still fail — leave it), remove folder if empty.
- **Empty folder detection:** `os.listdir` can return `[]` for non-empty folders on long paths. Use `.NET` `[IO.Directory]::GetFileSystemEntries('\\\\?\\' + path)` for reliable counts. For Python, catch `FileNotFoundError` and retry with `\\\\?\\\\` prefix.
- **Verify from disk, not counters:** script counters (`moved_files`) are unreliable for long paths. Re-count files in destination after processing.
- **Catch-all sub-bucket misnaming:** A catch-all sub-bucket may have a malformed name like "1080p (1080)(1080p)" — this is a catch-all that was incorrectly given a quality tag in its name. The correct catch-all name is just the quality indicator ("1080p", "720p", "SD") with no parenthesized quality. Rename to the clean form before splitting into letter sub-buckets.

## Pattern 13: Parent show folder creation

After all season folders in a bucket are normalized to `Show (Year)(Quality) Season XX`, they must be moved into `Show (Year)\` parent folders to match the convention: `Letter\Show (Year)\Show (Year)(Quality) Season XX\`.

**Procedure:**
1. For each season folder matching `^(.+?)\s*\((\d{4})\)\s*\([^)]*\)\s*Season\s*\d+`:
   - Extract show name and year.
   - Create `Show (Year)\` parent folder if it doesn't exist.
   - Move the season folder into the parent.
2. Skip show-only folders (no season in name), Unknown folders, extras, and outliers — these ARE show folders and stay at the letter-bucket level.
3. After moving, verify 0 loose season folders remain at the letter-bucket level.

**Stray season folders at bucket level:** When a bucket has season folders sitting at the top level (not inside a parent), these are "stray" season folders that need to be moved into their parent. Common causes: (1) a show folder was renamed but its season folders weren't moved, (2) a previous normalization pass created season folders at the bucket level without creating parents, (3) quality-split folders were split into season folders but parents weren't created. **Procedure:** For each stray season folder matching `Show (Year)(Quality) Season XX`, extract show+year, create/find the parent, move the season folder inside. Verify 0 stray season folders remain.

**Pitfalls:**
- **Duplicate parent folders:** The `clean_show_name` function may include extra words from release info (e.g., "5" from x265, "i c" from i.c, "Atmos 5" from audio tags). This creates duplicate parent folders like "Foundation 2021 5 (2021)" alongside "Foundation (2021)". After creating parent folders, scan for duplicate show names and merge them — move season subfolders from the duplicate into the canonical parent, then remove the empty duplicate.
- **Double-nested folders:** Some parent folders may have season info in their name (e.g., "Fresh Off the Boat Season 01 1080p Phr0stY (2015)" containing "Fresh Off the Boat Season 01 1080p Phr0stY (2015)(1080p) Season 01"). These need to be flattened: rename the parent to "Fresh Off the Boat (2015)" and move the season folder inside.
- **Subtitle-only loose folders:** Folders containing only `.srt` files (no video) that are duplicates of files already in the season folder. These appear after loose-episode consolidation when the merge script reported success but didn't remove the source (because `os.path.exists(dst)` was True for all files). **Action:** delete these folders entirely — their contents are duplicates. Verify by checking if the destination season folder has the same or more srt files.
- **Locked files (Thumbs.db, Arrow.jpg):** `WinError 32` or `WinError 5` (access denied). These are held by Windows Explorer or thumbnail cache. Use copy-and-recreate workaround, or leave them and report to the user. Do not retry in a loop.

## Pattern 14: year_map substring-matching pitfall

When matching show names against a year_map dictionary, using substring matching (`k.lower() in show_norm.lower()`) causes false positives — e.g., \"Origin\" matches \"Originals\" because \"origin\" is a substring of \"originals\". This results in incorrect year assignment (Originals gets 2018 instead of 2013).

**Fix:** Always try exact normalized match first (lowercase, strip spaces and dots, compare equality). Only fall back to substring matching when exact match fails, and when doing so, prefer the LONGEST matching key to avoid shorter keys shadowing longer ones. After applying, verify by spot-checking a few folders whose names are substrings of other show names.

**Procedure:**
1. Build year_map with canonical show names as keys.
2. For each folder, normalize both the folder show name and each key (lowercase, remove spaces and dots).
3. First pass: exact equality match.
4. Second pass: substring match, preferring longest key first (sort keys by length descending).
5. After applying, verify folders with substring-prone names (Originals, Origin, The Mentalist, Mental, etc.) got correct years.

## Pattern 15: Catch-all extras folders (OTHER./Other. prefix and broader)

TV letter buckets may contain catch-all folders that are not TV shows — they are dumping grounds for miscellaneous content. These fall into several categories:

**Category A — OTHER./Other. prefix folders:** Names start with `OTHER.` or `Other.` followed by a description (e.g., `OTHER.Shows.about.MONEY.and.POWER`, `Other.SciFi.ANIME.HERE`). These are not TV shows.

**Category B — Bare quality folders:** Folders named only a quality indicator with no show name: `SD`, `1080p`, `720p`. These are dumping grounds where content was placed without proper letter-bucket assignment. Move to Extras or split into proper letter sub-buckets if they contain >100 items.

**Category C — Loose season collections:** Folders named `SEASON1`, `SEASON2`, `Season.01`, `Season.1`, `Season.1 [720p max]`, etc. These contain episodes from a single show (e.g., Dinosaurs) or mixed shows. Extract the show name from video filenames, group by show, and move into proper season folders. If no show can be identified, move to Extras.

**Category D — Subtitle/supplement folders:** `Screens`, `Screens.Cap`, `suba`, `Soundtrack`, `Subtitles`, `Specials`, `Subs`. These contain subtitle files, soundtracks, or special features. Move to Extras.

**Category E — Mixed-show dumps:** Folders containing episodes from multiple unrelated shows (e.g., `Season.1.1080p.Mixed` with Black Mirror episodes). Extract show name from each filename, group by show, move into proper season folders.

**Procedure:**
1. Scan every letter bucket for folders matching any of the above categories.
2. For Category A, B, D: move the entire folder to `T:\\Media\\TV\\Extras\\` without renaming. Handle collisions by appending ` (2)`, etc.
3. For Category C, E: extract show name from video filenames, group by show, move into proper season folders. Move any remaining non-video files to Extras.
4. Verify: count folders in Extras, verify no catch-all folders remain in source buckets.

**Pitfalls:**
- Do not move folders that are actually TV shows with \"extra\" in the title (e.g., \"Extraordinary 2023\", \"Zoeys Extraordinary Playlist\"). Verify by checking if the folder has a year tag and season structure.
- The user may explicitly request moving a specific show that happens to be a TV show (e.g., \"Behind the Scenes (2024)\") — comply even if it's technically a show.
- Catch-all folders may contain video files mixed with non-video junk. For Category A/B/D, move the entire folder. For Category C/E, sort by show first.
- After moving, check all remaining buckets for any catch-all folders that were missed in the first pass.
- Catch-all folders may contain nested subfolders (e.g., \"Deleted.Scenes [1080p]/Featurettes/\") — move the entire top-level folder.
- **Generic-named extras:** Some extras folders have generic names like \"Soundtrack\", \"english.subtitles\", \"Behind the Scenes\" that don't clearly indicate they're extras. Verify by checking contents — if the folder contains only .srt files, .mp3 soundtracks, or featurette videos without a show's season structure, it's extras. Check file sizes and types before moving.

## Pattern 16: Dotted-to-spaced folder merging

During normalization, a folder may exist in both dotted (`The.Orville (2017)`) and spaced (`The Orville (2017)`) forms. The dotted form is a leftover from an earlier naming convention; the spaced form is the current convention.

**Procedure:**
1. Identify dotted show folders that have a spaced counterpart with the same show name and year.
2. Merge: move all contents from the dotted folder into the spaced folder's season folders.
3. Remove the empty dotted folder.
4. If the dotted folder has different content (different encodes), add a distinguishing suffix like ` (2)` to the parent name before merging.

**Pitfall:** Do not blindly delete the dotted folder — verify its contents were moved first. Some dotted folders may contain unique encodes not present in the spaced version.

## Pattern 17: Quality-only folders with long descriptors

Some quality-only folders have extremely long names encoding release info: `Orphan.Black.Echoes.2023.Season.1.S01.1080p.STAN.WEBDL.x265.HEVC.10bit.EAC3.5(2023)1080p`. The show name and year are embedded but buried in release tokens.

**Procedure:**
1. Extract the year from the last `(YYYY)` in the folder name.
2. Extract the show name from the text before the first season/quality token: split on `.Season`, `.S0`, or the year paren.
3. Convert dots to spaces for the show name.
4. Quality = last quality token in the name (1080p, 720p, etc.).
5. Normalize to `Show (Year)(Quality) Season NN` and move contents.

**Pitfall:** These folders often contain only 1-2 files. Verify file count before and after.

## Dry-run first

Always show a dry-run plan before applying. Report:
- Number of folders to process by category
- Sample source → destination mappings
- Total files to move
- Any folders that can't be parsed (flag for manual review)

## Verification
After processing, verify:
- 0 remaining folders without `(year)` or `(Unknown)` in their name
- File/video counts unchanged (renames only, no data loss)
- No empty source folders left behind
