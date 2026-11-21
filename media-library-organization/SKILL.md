---
name: media-library-organization
description: "Use when organizing movie, TV, or anime media folders."
version: 1.5.0
author: Nous Research
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [media, files, organization, movies, windows]
    category: media
---

# Media Library Organization

Naming convention (single source of truth): see the `file-naming-conventions` skill. AG-library-specific observed state lives in `references/` — keep generic rules here.

## When to Use
Use this skill when inspecting, flattening, renaming, or reorganizing a local movie, TV, or anime library, especially when folders contain release variants and sidecars.

- **General rules**:
- Always include BOTH parenthesized groups, even when empty (never `Name (Year)( )`), and keep the dots in `rest` — never drop trailing release tokens.
- SxxExx must render UPPERCASE (`S01E03`, never `s01e03`).
- Unless the user explicitly asks to rename files, keep original file names as-is during folder normalization; only movie/season folder names change to `Title (Year)(Quality)`.
- Rename files and folders in the same pass only when the user asks for both; it multiplies collision risk.

### Active naming convention (this user)
- Target form is parenthesized: `Title(Year)(Quality)` for folders and `Title (Year) (Quality) SxxExx.ext` for TV files. The `[SD]`/`[720p]` bracket form is legacy in the AG/quality-root libraries — but when the user supplies an explicit target (their movie-library organizing prompt uses `Movie Title (Year) [Resolution]`), follow it literally. Canonical rule: `file-naming-conventions`.
- Always include BOTH parenthesized groups. Numeric/title-with-no-year folders keep their title + quality, **never** an empty `( )` (e.g. `02 (SD)`, not `02 ( )`).
- Unless the user explicitly asks to rename files, keep original file names as-is during folder normalization; only the movie/season folder names change to `Title(Year)(Quality)`.
- Rename files and folders in the same pass only when the user asks for both.
- Keep the dots in `rest` — never drop trailing release tokens.
- SxxExx uppercase: `S01E03`, never `s01e03`.
- Keep language tag on subtitles (`S01E03.en.srt`) and keep numeric variant suffix (`2.`, `3.`) so one episode with multiple subs yields distinct destinations.
- Skip `Thumbs.db`, `*.db`, `plexignore`, and `.bat` in all plans.

## Plex naming conventions (referenced guide)
1. **Movie file**: `MovieName (release year).ext` — year required to disambiguate. (Differs from the user's `Title(Year)(Quality).ext` convention — Plex uses parentheses with year only.)
2. **Movie directory**: `MovieName (release year)` as a subdirectory of the library root; one folder per movie (keeps posters, subs, extras with the movie).
3. **Alternative IDs** (Plex 1.20.1+): `{imdb-ttXXXXX}` or `{tmdb-XXXX}` appended to the filename.
4. **Multiple parts**: `MovieName (release year) - ptX.ext` — split names: `cdX`, `discX`, `dvdX`, `partX`, `ptX`. All parts same format, audio/subs in same order; up to 8 parts.
5. **Multiple versions**: `MovieName (release year) - 1080p.ext` — the "some text" helps identify the version client-side. All parts same resolution/encoding format, audio/subs in same order.
6. **Multiple editions**: `MovieName (release year).1080p.h264 {edition-Original Theatrical Release}.mp4` — requires Plex Pass; edition tags can also be set via Plex UI.
7. **Trailers & extras — option 1 (inline)**: `DescriptiveTitle-ExtraType.ext` where ExtraType ∈ {`-behindthescenes`, `-deleted`, `-featurette`, `-interview`, `-scene`, `-short`, `-trailer`, `-other`}.
8. **Trailers & extras — option 2 (subdirectory)**: separate subdirectory per extra type (`Trailers/`, `Behind the Scenes/`) with the content files inside.
9. **Movie posters**: `MovieName (Release Date).ext` or `Movie/MovieName (Release Date)/Custom_Poster_Name.ext` (formats: jpg, jpeg, png, tbn).
10. **Background art / fanart**: `MovieName (Release Date)-fanart.ext` (typically 16:9).
11. **Separation**: Movies, TV, Music must be in separate roots. Plex warns mixing causes wrong matches and ignored files.

**Show ID priority** (per media type; see also `file-naming-conventions` skill):
- **Movies**: TMDB → IMDb → TVDB (TMDB preferred)
- **TV shows**: TVDB → TMDB → IMDb (TVDB preferred)

Note: The priority is per-media-type, not per-file. The first ID found in the NFO (or web) wins. If a show is both a movie and a TV show, use the type that applies.

## Plex-based TV show organization (user custom format)
When the user wants the custom TV show output format:
`<First letter of Show Name>\<Show Name>.<ShowYear>\<Show Name>.<ShowYear>.S<Season>Ep<Episode>`

Example:
`T:\Media\TV\A\Alien Earth (2025)\Alien Earth (2025) S01\Alien.Earth.s01e01.1080p.web.h264-successfulcrab[EZTVx.to].mkv`

Rules:
- **Case-sensitive**: preserve the exact casing of the show name and year.
- **Year**: extract from filename, parent folder, or NFO. If missing, use `Unknown`.
- **Season/episode**: extract from filename or NFO. Pad to 2 digits (S01E01). Use `Unknown` if missing in both.
- **Quality**: ffprobe the first video stream. Map height → tier (2160p ≥ 2160, 1440p ≥ 1440, 1080p ≥ 1080, 720p ≥ 720, SD below).
- **Extra info**: preserve brackets (e.g., [EZTVx.to]) and release tags from original filename.

## TV Library Organizer (user custom format - TV shows)

For TV shows, the organizing format is:

**Show folder** (no quality, single TVDB ID):
`<Show Name> (<Year>) {<TVDB-XXXXX>}`

Example: `A.P. Bio (2018) {TVDB-328534}`

**Season folder** (show name + year + quality + season):
`<Show Name> (<Year>)(<Quality>) Season XX`

Example: `The Young Indiana Jones Chronicles (1992)(SD) Season 01`

**After normalizing all season folders in a bucket, move them into `Show Name (Year)\` parent folders:**
`<Letter>\<Show Name> (<Year>)\<Show Name> (<Year>)(<Quality>) Season XX\`

Example: `T:\Media\TV\A\Arrow (2012)\Arrow (2012)(720p) Season 01\`

This is the final structure. Do not leave season folders directly under the letter bucket.

**Video file** (show name + year + quality + season/episode):
`<Show Name> (<Year>) (<Quality>) S<Season>E<Episode>.<OriginalName>.<ext>`

Example: `A.P. Bio (2018) (720p) S01E01.Catfish (720p).mkv`

**Sidecar file** (show name + year, no quality):
`<Show Name> (<Year>) <OriginalName>.<ext>`

Example: `A.P. Bio (2018) tvshow.nfo`, `A.P. Bio (2018) clearlogo.png`

**Rules:**
1. Show name: preserve dots only for established dot-notation titles (e.g., `A.P. Bio`, `The.Young.Indiana.Jones.Chronicles`); otherwise use spaces. See the `file-naming-conventions` skill for the canonical rule (spaces for folder names).
2. Quality only in season folders and file names, NOT in show folder.
3. Single ID for TV shows: only TVDB (no TMDB/IMDb in the folder).
4. SRT files may use "Chapter XX" format instead of "SXXEXX" format (e.g., `Chapter 01` = S01E01).
5. Year comes from the parent folder name when files use a different year.

**Files without season/episode:**
Files lacking SxxEyy in their name must still be organized into the show folder at the series level. Do NOT skip them, and do NOT add a dummy S00E00. Examples: poster.jpg, fanart.jpg, tvshow.nfo, theme.mp3, seasonXXposter.jpg.

### Files without season/episode pitfall
Files lacking SxxEyy in their name must still be organized into the show folder at the series level. Do NOT skip these files and do NOT add a dummy S00E00. Move them to the series level without an episode code.

## Verification workflow
- **Answer short and direct — no narration.** Report the key numbers and the specific items to act on; do not narrate tool calls, re-explain the request, or dump full lists unprompted. Attach a detail list only when asked. The user's explicit preference is: short, direct, no fluff, answers plainly.
- **Verify every count from disk.** If you are given a count to move (e.g. "the 42") or you compute one, re-derive the exact number from `os.listdir`/`dir` and report the verified count — the stated number may differ.
- Dry-run first, commit only after review. Use a plan CSV (`source,dest,kind`); read its columns before acting.
- Numeric/leading-number collections stay in `#` (do not promote to a letter).
- Artwork and sidecars at series/quality level: `Show.Name(YEAR).<original>` in the series folder; do NOT add an episode code.
- Subtitles keep language tag; keep numeric variant suffix (`2.`, `3.`) so one episode with multiple subs yields distinct destinations.
- Skip `Thumbs.db`, `*.db`, `plexignore`, and `.bat` in all plans.
- See `references/catalog-comparison.md` for the catalog-vs-directory comparison procedure.

## Investigation & verification

Standing rules for every task in this skill:

1. **Debug one thing at a time.** When improving several scripts, complete the read -> reproduce -> fix -> verify loop for one script before touching the next. Never batch a whole file's edits before the first fix is verified.
2. **Never test destructive operations on the live library.** Destructive runs go on an isolated test tree (e.g. `C:\Users\Owner\AppData\Local\Temp\*`); the 9.5 TB library root on M: is inventoried and planned only. A live-library run requires a read-only dry run first plus a totals check afterward.
3. **Verify cmd commands before writing.** Any command you intend to document or embed must be run first, and its behavior confirmed, before it is placed in a file.
4. **Write as a teaching guide.** When rewriting instructions, present the original, the fix, and the reason side by side, in a form a novice can follow. Show the original and the fixed version so the reader sees exactly what changed.
5. **Preserve duplicates; only consolidate on a bug.** Keep multiple copies of a script unless a bug or structural problem forces consolidation. Consolidation is a data-loss risk, not a feature.

## Debugging scripts on large media libraries

### Sequential verification

When a batch of scripts shares a common task (organizing a media library), fix and verify them **one at a time, in a fixed order**, re-running each against the same isolated tree after the fix:

1. `organize.movies.bat` — batch organizer
2. `Flatten.Library.py` — content-aware flattener
3. `defolder.py` — cwd-flattening helper
4. `yty.title.year.rename.py` — title/year/renamer
5. `Dir.To.Text.folder.copy.txt` — cmd command guide
6. `Flatten.Safe.bat` / `Nest.killer.safe.bat` — batch cleanup scripts
7. `FileTreeGen.bat` — tree generator

Re-run the **ACTUAL** script (not a reimplementation) against the same scratch tree; a Python repro can confirm the mechanism but must never be the source of truth. Remove the scratch tree when done.

### Batch-file (cmd) pitfalls

- **Quoted wildcard never expands.** A double-quoted `*` inside `for /f` yields a SINGLE literal string, not a glob expansion. Test a one-line loop before trusting a loop body built on it.
- **`goto` inside a parenthesized block crashes.** `goto :label` inside `for (...) do ( ... )` produces `( was unexpected at this time.`. Move labels outside parenthesized blocks, or use `call :label` (jumps, saves/restores state, returns).
- **A trailing space in `==` always fails.** `if "%x:~-1%"=="\ "` never equals `"\"` (backslash alone). `if "%x:~-1%"=="\"` (no space) is the only form that matches. Drop the space.
- **CRLF leaks into `for /f` variables.** A `
` at end of line can corrupt `for /f` variables and cause intermittent drive-navigation errors. Write batch files with LF (Unix) line endings and verify with `od`/`grep -U`.

### Python file-system pitfalls

- **Anchor to an explicit target, not `os.getcwd()`.** A script that uses `os.getcwd()` runs wherever the shell happens to be, not from its own directory. Pass an explicit target path and verify it.
- **`os.path.exists()` is a blind collision check.** It only tests True/False; it does not arbitrate character-level collisions (e.g. `DUP_` vs `DUP__`). Handle collisions explicitly with a dedup strategy (append `1`, then `2`, ...).
- **`os.listdir`/`has_video` silently return False past MAX_PATH.** A folder that `os.walk` lists (and that visibly contains video) may report `has_video == False` because `os.listdir` raises `FileNotFoundError` (WinError 3) on the long path and the helper swallows it. Counts then undercount and a "remaining untagged" scan can disagree with the fix script's collection. Re-probe from a `subst`-mapped drive or shorten the path; never trust a single `has_video` pass on deep trees.
- **Backslash escaping in TSV/path processing.** When reading a TSV file containing Windows paths (backslashes) and building a lookup dictionary, `rel.replace("\\\\", "/")` does NOT work — in a Python string literal, `"\\\\"` is two backslash characters, but the file content has single backslashes. Use `rel.replace("\\", "/")` (one backslash in the literal) instead. This silently causes zero matches if wrong, making all videos appear as "BROKEN" in the plan. Always verify the map size equals the video count after building it.
- **Use absolute paths in Python rename/move scripts.** Relative paths combined with `os.path.join` and mixed separators (`./foo/bar` + `\\`) raise `WinError 3` even when the file exists. Resolve every source/destination with an explicit absolute base (`os.path.join(base, rel)` with `rel` normalized to backslashes) before calling `os.rename`/`shutil.move`.
- **Handle WinError 3 (path not found / too long) with the `\\\\?\\` extended-path prefix.** When `os.rename` raises `WinError 3` on a path that visibly exists, prepend `\\\\?\\` to both source and destination and retry — this bypasses the 260-char MAX_PATH limit. Fall back to `subst` only if the prefix fails.
- **Never overwrite on collision; append ` (2)` or leave the source.** When the destination already exists (often a leftover from a prior partial run), do not overwrite — append ` (2)` to the new name, or leave the source untouched and report it as a duplicate for manual review.
- **`ctypes.CDLL("name.dll")` does not search PATH on Windows (Python 3.8+).** Loading a native DLL by bare name fails even when the DLL's directory is on PATH; call `os.add_dll_directory(dir)` first (a `sitecustomize.py` in the target venv does it at startup) or load by full path.
- **uv spawns git directly and cannot execute a git living under `C:\Program Files\WindowsApps\...`** (Access denied, and its MSYS `sh.exe` likewise). Copy the portable git tree to an ordinary directory and put its `usr\bin` and `mingw64\bin` on PATH for uv commands.

### Batch-file (cmd) recursive descent pattern

When a batch script must walk an unknown directory tree and act on content at any depth, use a **recursive label + `call`**, not a single-pass loop. The pattern (from `Nest.killer.safe.bat`):

```bat
:peel_loop
    set "found=0"
    for /f "delims=" %%S in ('dir /b /ad') do (
        set "subPath=%%~fS"
        call :check_folder "!subPath!"
        if defined _nest (
            echo   [NEST FOUND] !_nest! - Flattening...
            robocopy "!_nest!" . /E /MOVE /R:0 /W:0 >nul
            rd /s /q "!_nest!" 2>nul
            set "found=1"
            set "_nest="
        )
    )
    if %found% == 1 (
        call :peel_loop
    )
    exit /b

:check_folder
    set "_nest="
    for /f "delims=" %%V in ('dir /b /a-d "%~1\*" 2^>nul') do (
        set "fname=%%~nxV"
        if /i "!fname:~-4!"==".mp4" (
            set "_nest=%~1"
            exit /b
        )
        if /i "!fname:~-4!"==".mkv" (
            set "_nest=%~1"
            exit /b
        )
        if /i "!fname:~-4!"==".avi" (
            set "_nest=%~1"
            exit /b
        )
    )
    for /f "delims=" %%T in ('dir /b /ad "%~1" 2^>nul') do (
        call :check_folder "%~1\\%%T"
        if defined _nest exit /b
    )
    exit /b
```

Rules for this pattern:

- **`call` a label, don't `goto` it.** A `goto :label` inside a parenthesized `for (...) do ( ... )` block crashes with `( was unexpected at this time.` Labels must sit outside any parenthesized block. `call` saves/restores state and returns correctly.
- **Use `!var!` (delayed expansion), not `%var%`, inside `for /f` loop bodies.** A `for /f` body is parsed once when the loop starts; `%var%` is expanded then to whatever the variable held at that instant, so changing `%var%` inside the loop body is invisible to subsequent iterations (often it reads as empty/old). `!var!` expands at execution time and sees the current value.
- **Anchor the recursive function's argument to `%~1`** (pass via `call`), not the script's working directory.
- **Use `2^>nul` to silence `dir` stderr** inside `for /f` command substitutions (the `^` escapes the `>` from the outer batch parser).

### Command substitution pitfalls

- **A literal backslash at the end of a `for /f` command substitution argument is a parse error.** `('dir /b /ad "%~1"')` is fine; `('dir /b /ad "%~1\"')` mishandles escaping. Keep the command argument simple.
- **The `dir /b /ad` output is the set of immediate subdirectories** — `dir /b /ad` lists only directories on the current level; it never recurses. Recurse explicitly with a `call` loop for any depth > 1.
- **A trailing space in `==` always fails.** `if "%x:~-1%"=="\ "` never equals `"\"` (backslash alone). `if "%x:~-1%"=="\"` (no space) is the only form that matches. Drop the space.

### YAML/JSON/LF pitfalls

- **YAML block scalars do not preserve CRLF.** `|` (literal block) preserves newlines; `|-` also preserves newlines but strips the trailing newline. If you write `\r` into a YAML file on Windows, the `\r` is stored as literal CRLF and can corrupt downstream parsers (see `\r` leaks in `for /f` variables above).
- **Batch files must use LF (Unix) line endings** for any file that will be read by `for /f`. CRLF line endings leak `\r` into `for /f` variables and cause intermittent drive-navigation errors (e.g. "The system cannot find the drive specified"). Write with `write_file` or convert with `dos2unix` / `sed -i $'s/\r$//'` before running.

## PowerShell pitfalls (learned the hard way)

- **Never run multi-line PowerShell inline through the terminal.** Backslashes, regex, and quotes get mangled by the shell layer and silently produce wrong probe/count results (e.g., 1 failure instead of 8). Always write the script to a `.ps1` file with the file tool and run it with `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <path>`.
- **Function calls in `if` conditions parse wrong.** `if (Get-EntryCount $dir -eq 0)` is parsed as calling the function with the *expression* `$dir -eq 0` as its argument — it returned a truthy value for every directory and a scan once reported 4,132 "empty" folders when the true count was 0. Always assign first: `$count = Get-EntryCount $dir` then `if ($count -eq 0) { ... }`.
- **Get-ChildItem has MAX_PATH blind spots.** On paths over ~260 characters it silently returns no children, making non-empty directories look empty. For empty-directory detection and deletion, use .NET with the `\\?\\` long-path prefix: `[IO.Directory]::GetFileSystemEntries('\\?\' + $path)` and `[IO.Directory]::Delete('\\?\' + $path, $false)`. Deleting a truly non-empty directory throws `The directory is not empty` — a useful safety net; "Could not find a part of the path" on delete signals a long-path case.
- **Write scripts in one clean pass.** Repeatedly patching a generated script accumulated syntax errors (stray braces, broken try/catch, `-sh 1` artifacts). Write the full corrected script fresh instead of layering patches.
- **Verify with an independent recount.** After any mass move, re-count files/videos/bytes with a fresh read-only scan using a different method than the moving script — never trust the script's own counters. If files leave the scanned root, reconcile source + destination combined.

### Empty-directory cleanup recipe

Deepest-first, multi-pass, until a pass removes nothing:

1. Enumerate all directories with the .NET `\\?\\`-prefixed recursive walk (not Get-ChildItem) and sort by full-path length descending.
2. For each directory: skip the root, skip reparse points, read the entry count with `[IO.Directory]::GetFileSystemEntries('\\?\' + $path)`; only delete when the count is exactly 0, re-checked immediately before deleting.
3. A directory whose children disappear mid-pass becomes deletable next pass — loop until a pass removes 0.
4. Report removed / failed / skipped-nonempty / skipped-reparse / still-empty. Failures are usually long-path cases; handle them with the `\\?\\` prefix pass.

Move commits follow the same discipline: track every move in a log, reverse it on failure, delete source trees only after deletion-time empty verification, and confirm final totals before reporting success.

Subtitles: when flattening a source tree into a per-movie folder, duplicate filenames (e.g., `chi.srt` in `Subs\chi` and `Subs\??(??).chi`) collide. When keeping only English subtitles, treat a subtitle as English if its stem matches the video stem or its name/parent mentions English; delete the rest, and report the deleted count.

## Procedure

0. **Organize into letter folders first, then process by letter.** Before scanning, if the library has flat files or unsorted movie folders at the root, group them into letter folders (A, B, C, ..., # for non-alphabetic). Move top-level files and folders into their corresponding letter folder based on the first letter of the name. Then process one letter at a time (A, B, C, ...). Folders/files starting with a digit or non-alphabetic go into `#`; after organization, move `#` folder contents into the appropriate letter folder based on the movie title (e.g., "1997.Bean..." → B). Do not leave a `#` folder in the final structure. This keeps the plan reviewable and prevents a single failure from blocking the whole library.

   Folders and files whose names start with a digit or non-alphabetic character go into a `#` folder. After letter-based organization, move the `#` folder's contents into the appropriate letter folder based on the movie title (e.g., "1997.Bean..." → B for Bean, "2007.Mr.Beans..." → B for Bean). Do not leave a `#` folder in the final structure.

1. **Confirm scope and target layout.** Work only inside the user's named library root. Prefer one `Title (Year)` folder per film, keeping video, subtitles, NFO metadata, and artwork together. Preserve alternate editions and duplicates as separate releases; never deduplicate or overwrite unless explicitly asked.
2. **Verify the live path before scanning.** Check the drive and every named path component with `Get-PSDrive` and `Test-Path`. Treat an attached tree's path and the live filesystem path as potentially different. If the named path is absent, inspect only its immediate parent for a plausible sibling, then confirm the alternate root matches the supplied listing before using it; ask if uncertain.
3. **Inventory files and directories.** Count files, directories (including empty buckets), media by extension, and total bytes inside the confirmed root. Use NFO metadata to resolve title/year when available; use filenames as a fallback and flag ambiguous mappings rather than guessing. Do not inspect video streams unless the user asks to determine quality from the media itself.
4. **Build a complete dry-run plan before moving anything.** Show source-to-destination examples, candidate files and bytes, existing destinations, case-insensitive collisions, and any existing child buckets. For mixed-resolution folders, plan the parent’s highest-quality label and one subfolder per quality; reuse an existing bucket only when it is empty, and stop on nonempty or conflicting targets. Preserve alternate editions and do not merge distinct releases.

   Save the plan as a CSV (`quality_library_plan.csv`) with columns: kind, source, destination, quality, status, bytes. This makes the plan reviewable, re-runnable, and auditable. After execution, verify by counting files in the destination rather than trusting the script's moved counter (see Windows long-path move pitfall).
5. **Honor dry-run requests as read-only.** When the user asks for a preview, stop after reporting it even if they previously approved the general organization. Do not create directories, remove empty directories, or modify files during preview.
6. **Apply only the reviewed, authorized plan.** Move videos with their matching same-stem subtitles/NFOs. Before any quarantine move, re-check the quarantine target: it must be empty or hold only previously quarantined content, otherwise stop and ask. If quarantining probe failures is requested, do not call a file corrupt solely because probing failed; move its isolated release folder with sidecars/artwork, or only the failed video and matching sidecars if that folder contains unrelated media. Preserve paths beneath the explicitly named quarantine root and never overwrite.
7. **Verify the result.** Confirm every planned destination exists, original sources are absent, and file counts/bytes reconcile. If files moved outside the scanned library root, compare the combined source-root and destination inventories before and after; a source-root-only decrease is expected. Report skipped conflicts and do not claim completion based only on a generated plan.
8. **Reorganize into per-movie folders.** After the flat quality separation, create one folder per movie inside each quality library and move the video plus all matched sidecars into it. Match sidecars by their top-level source directory (not exact parent or stem). Sidecars that were skipped during the initial move (destination collision) can be handled in a second pass by matching their top-level folder to the destination movie folder.
9. **Rename sidecars with title + year prefix.** Prefix every sidecar with `Title (Year) - ` (e.g., `Carry On (2024) - English.srt`). Skip files that already start with the prefix. Watch for Windows MAX_PATH (260 chars) — if `Path.rename()` raises `FileNotFoundError` (WinError 3), the path is too long; shorten the prefix or skip.

## PowerShell pitfalls (learned the hard way)

- **Never run multi-line PowerShell inline through the terminal.** Backslashes, regex, and quotes get mangled by the shell layer and silently produce wrong probe/count results (e.g., 1 failure instead of 8). Always write the script to a `.ps1` file with the file tool and run it with `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <path>`.
- **Function calls in `if` conditions parse wrong.** `if (Get-EntryCount $dir -eq 0)` is parsed as calling the function with the *expression* `$dir -eq 0` as its argument — it returned a truthy value for every directory and a scan once reported 4,132 "empty" folders when the true count was 0. Always assign first: `$count = Get-EntryCount $dir` then `if ($count -eq 0) { ... }`.
- **Get-ChildItem has MAX_PATH blind spots.** On paths over ~260 characters it silently returns no children, making non-empty directories look empty. For empty-directory detection and deletion, use .NET with the `\\?\\` long-path prefix: `[IO.Directory]::GetFileSystemEntries('\\?\' + $path)` and `[IO.Directory]::Delete('\\?\' + $path, $false)`. Deleting a truly non-empty directory throws `The directory is not empty` — a useful safety net; "Could not find a part of the path" on delete signals a long-path case.
- **Write scripts in one clean pass.** Repeatedly patching a generated script accumulated syntax errors (stray braces, broken try/catch, `-sh 1` artifacts). Write the full corrected script fresh instead of layering patches.
- **Verify with an independent recount.** After any mass move, re-count files/videos/bytes with a fresh read-only scan using a different method than the moving script — never trust the script's own counters. If files leave the scanned root, reconcile source + destination combined.

### Empty-directory cleanup recipe

Deepest-first, multi-pass, until a pass removes nothing:

1. Enumerate all directories with the .NET `\\?\\`-prefixed recursive walk (not Get-ChildItem) and sort by full-path length descending.
2. For each directory: skip the root, skip reparse points, read the entry count with `[IO.Directory]::GetFileSystemEntries('\\?\' + $path)`; only delete when the count is exactly 0, re-checked immediately before deleting.
3. A directory whose children disappear mid-pass becomes deletable next pass — loop until a pass removes 0.
4. Report removed / failed / skipped-nonempty / skipped-reparse / still-empty. Failures are usually long-path cases; handle them with the `\\?\\` prefix pass.

Move commits follow the same discipline: track every move in a log, reverse it on failure, delete source trees only after deletion-time empty verification, and confirm final totals before reporting success.

### Commit operation ordering and partial-state retries

- **Rename a parent folder before moving files into it.** A split that renames `Season.5` → `Season.5 [1080p max]` and moves files into `Season.5 [1080p max]\SD` fails if the file moves run first under the old path — the files vanish with the rename. Within a folder, run renparent → create quality subfolders → file moves. Across folders, process deepest path first so a child is finished before its ancestor renames (an ancestor rename invalidates every descendant's cached path, including destinations already validated).
- **Re-resolve paths live during commit; do not trust a frozen plan.** A frozen rename plan that renames a parent first invalidates every descendant source path (WinError 3 "path not found"). Walk each subtree bottom-up, re-checking existence at move time, and skip items whose source no longer exists (already moved with a sibling) instead of failing. Sort by path depth descending is not sufficient across shared ancestors.
- **Use one globally sorted op list, not phased passes.** Sort operations by (full-path depth descending, kind priority: renparent 0, file moves 1, tag renames 2). Phased sequencing (all splits, then all renames) reintroduces the same ancestor/descendant bug between phases.
- **Treat rollback as partial until re-verified.** Rollback restores files to original paths in reverse order, and created quality subfolders are deleted only if empty — a failed commit can leave a half-applied structure (split subfolders without their `[max]` parent label, plus a nested duplicate folder from a rename-into-existing-directory). Before retrying, re-probe and re-classify from disk and rebuild the plan from current state; never reuse expected counts computed before the failure, and replace hard-coded count assertions with drift-tolerant checks.
- **Enumerate sidecars live at move time.** Computing sidecar lists at plan time freezes paths that later operations relocate. Enumerate each video's same-stem, non-video sidecars from the live folder when moving it, and skip any whose source no longer exists (already moved with a same-stem sibling) instead of failing.

Subtitles: when flattening a source tree into a per-movie folder, duplicate filenames (e.g., `chi.srt` in `Subs\chi` and `Subs\??(??).chi`) collide. When keeping only English subtitles, treat a subtitle as English if its stem matches the video stem or its name/parent mentions English; delete the rest, and report the deleted count.

## TV libraries (same workflow, season-shaped)

The movie workflow transfers directly, with the unit of work being the **season folder** (the immediate directory holding episodes) instead of a movie folder:

- Inventory the letter/`#` folder (count series, season folders, videos, bytes) before planning; a `#` TV folder typically holds a handful of series with many episodes each.
- Probe each episode folder with ffprobe and map to tiers exactly as for movies. Tag the **season folder** (append `[SD]`/`[720p]`/`[1080p]`), not the series folder. Uniform → tag; mixed → split into per-quality subfolders under a `[max]` parent (the Aeon.Flux pattern); probe failure → quarantine the isolated release folder with its sidecars. Do not call a file corrupt from a failed probe.
- Series can legitimately contain several encodes of the same season side by side (`Season.1`, `Show.S01.1080p.BluRay`, `Show.S01.x265-RARBG`). These are alternate editions: keep all of them, never merge or dedupe, and never rename shared collection ancestors.

**In-place TV layout preference (T:\\Media\\TV) (user-specified target format):**
`T:\Media\TV\<Letter>\Show Name (Year)\Show Name (Year)(Quality) Season XX\file`

Example: `T:\Media\TV\A\A P Bio (2018)\A P Bio (2018)(720p) Season 01\A P Bio (2018)(720p) S01E01.mkv`

Rules for this format:
- Quality in parens immediately after the year: `(Year)(Quality)`, then ` Season XX`.
- Parent folder is REQUIRED: season folders MUST be inside `Show Name (Year)\` parent folders, never directly under the letter bucket. After normalizing a letter bucket, create parent folders for every show and move all season folders inside them (see references/TV-normalization.md → Pattern 13). Leaving season folders directly under the letter bucket is wrong.
- Keep the existing A-Z letter folders; promote `#` collections by series title's first letter with leading articles stripped.
- After normalizing a letter bucket, move "The X" folders to the letter matching the word after "The" (see references/TV-normalization.md → Pattern 4). The folder name keeps "The" — only the location changes.
- For (Unknown) year recovery, see references/TV-normalization.md → Pattern 7 (web search batch recovery + mislabeled show detection). For duplicate encode handling, see Pattern 8. For extras consolidation, see Pattern 10. For systematic bucket processing, see Patterns 11-12. For year_map matching, see Pattern 14 (substring-matching pitfall). For catch-all extras folders, see Pattern 15. For dotted-to-spaced merging, see Pattern 16. For quality-only folders with long descriptors, see Pattern 17.
- Never leave a `#` folder in the final structure.
- Verify the root before scanning (no root-level media files; only `desktop.ini`, `norm.file.names.py`, `tree.txt`, and A-Z/#/Ongoing containers).
- If the user changes the target layout mid-session, rebuild the plan and re-seek approval before moving.

When the user wants normalization without a separate quality root, keep the existing A–Z letter folders and shape each show as `T:\Media\TV\<Letter>\Series (Year)\Series(Year)(Quality)S0\file`. Keep numeric/leading-number collections in `#` (do not promote them to a letter). Quality comes from the file/folder name when present; otherwise ffprobe (header-only). TV normalization procedure for messy buckets (quality-split pairs, loose episodes, dotted folders): see [references/TV-normalization.md](references/TV-normalization.md).

### Numeric collections stay in `#`

Collections whose names start with a digit (e.g. `11.22`, `12.Monkeys`, `3.Body.Problem`) remain under `#`; do not promote them into A–Z even when a letter can be derived from the title.
- **In-place TV layout preference (T:\\\\Media\\\\TV).** When the user wants organizing inside the existing tree rather than a quality-separated root, use `T:\\\\Media\\\\TV\\\\<Letter>\\\\Series (Year)\\\\Series(Year)(Quality)S0\\\\file`: keep the existing A–Z letter folders, promote any `#` collections into their letter folder by the series title's first letter with leading articles stripped (e.g. `The.100` → T, `12.Monkeys` → M for "Monkeys"), and never leave a `#` folder in the final structure. Verify the root before assuming files exist at top level: on this library the root holds only `desktop.ini`, `norm.file.names.py`, `tree.txt`, and the A–Z / `#` / `Ongoing` containers — there are no root-level media files, so any earlier "N root-level media files" count that disagrees with a fresh scan is wrong. Re-count with `find` before planning moves. If the user later says to leave numeric-leading collections in `#` ("leave numbers as is" / "demote back to numbers"), retain all of them in `#` and do not promote; rebuild the plan accordingly. When the user changes the target layout mid-session, rebuild the plan and re-seek approval before moving; never execute a stale plan.
- **Staging folders.** `M:\move\Media` holds stray TV shows and `M:\move\Media\Done` holds stray movies; move them to `S:\_move` (TV) and the appropriate `M:\Media\Movies {quality}` root (movies), normalizing names on arrival. Treat them like outlier consolidation — inventory, classify, dry-run, approve, then move.
- **In-place filename normalization (rename only, no moves).** When the user asks to normalize file names without moving, apply `Title (Year)(Quality).ext` to movies and `Title (Year)(Quality) S01E01.ext` to TV, with Quality taken from existing tags or ffprobe; rename matching sidecars to the video stem; skip files already in target form; flag collisions. Never touch `.bat`, `Thumbs.db`, `plexignore`, or `*.db` (media-server metadata). Skip them in every plan.
- **In-place rename execution notes.** When executing a normalization rename plan: (a) resolve every source/destination to an absolute path with backslashes before `os.rename` — relative paths raise `WinError 3` even on existing files; (b) on `WinError 3` (path too long or not found), retry with the `\\?\\` extended-path prefix on both sides before falling back to `subst`; (c) never overwrite a destination that already exists (leftover from a prior partial run) — leave the source untouched and report it as a duplicate; (d) probe quality with ffprobe only when no quality token is present in the file or any parent folder name; (e) report progress per folder so the user can track long batches.

- **Year recovery from parent paths.** When a file lacks a year but its parent folder contains one (e.g., `A Discovery Of Witches (2018)/...`), extract the year with `\b(19\d{2}|20\d{2})\b` from the full path and insert ` (year)` into the filename. Do not use `\d{4}` alone — it false-matches quality tags like 1080p.

Dry-run CSVs must carry full destination paths (folder + new filename), not just the new filename — see `references/TV-naming.md` → "Dry-run CSV rule". Show-name vs episode-title parsing is bottom-up (files first, then folders) — see `references/TV-naming.md` → "Bottom-up parsing".
SxxExx must render UPPERCASE (S01E03, never `s01e03`); when a filename carries a lowercase season/episode marker, uppercase the marker in the new name without changing the surrounding release tokens.

### Metadata track pitfall (WMP / My Movies show-name mismatches)
Some .mkv/.mp4 files produced by packagers or downloaders contain an extra `bin_data` stream (codec `bin_data`, duration == video duration) alongside the video and audio streams. This is an embedded-metadata track — it is NOT visible as video/audio. WMP's metadata engine reads the container's `title` tag (not the bin_data stream) for the display name, so a mismatched title tag shows a different show's name (e.g. "Babylon 5 Season 1" for Soul Hunter S01E02).

**Diagnosis:** probe `format_tags=title` first — that's the source of the WMP display name. The bin_data stream is a red herring; do not chase it.

**Fix for WMP display:** strip the data track when extracting and re-encoding a clean copy: `ffmpeg -i in.mkv -map 0:v:0 -map 0:a:0 -c copy out.mkv` (drops the bin_data stream). Verify with `ffprobe -show_entries stream` — only 0:v and 0:a should remain. Do not rename or trim other streams.

### Numeric collections stay in `#`
Collections whose names start with a digit (e.g. `11.22`, `12.Monkeys`, `3.Body.Problem`) remain under `#`; do not promote them into A–Z even when a letter can be derived from the title.

### In-place filename normalization (rename only, no moves)
When the user asks to normalize file names without moving, apply `Title (Year)(Quality).ext` to movies and `Title (Year)(Quality) S01E01.ext` to TV, with Quality taken from existing tags or ffprobe; rename matching sidecars to the video stem; skip files already in target form; flag collisions. Never touch `.bat`, `Thumbs.db`, `plexignore`, or `*.db` (media-server metadata). Skip them in every plan.
- Verify the named TV root before scanning: on this machine the user may shorthand it as `T:\TV`, but the actual library is `T:\Media\TV`; if the named path is absent, check immediate siblings and confirm the alternate root before using it (step 2). Mirror any movie-root example the user gives (e.g. `Movies 720p\AG 720p\A 720p\Æon Flux (2005)(720p)`) when shaping quality-separated TV roots.

NFO-year filename normalization (when asked to add the year from NFO to file names):
- Read the series-level `tvshow.nfo` (walk up from the video's folder) for `<year>`; episode-level NFOs usually carry only `<title>`.
- Format: `Title (Year) S01E01.rest` — insert ` (Year)` right before the season/episode marker (`S\d{1,2}E\d{1,3}`, falling back to `S\d{1,2}`); extras without a marker become `Name (Year).ext`. Keep the library's dotted base name otherwise.
- Skip any file whose name already contains a 4-digit year — do not double-tag.
- Rename each video's same-stem **non-video** sidecars to the new stem in the same step (respecting the sidecar safety rules above); give the plan a collision check on destination names within each directory, and verify file/video/byte totals are unchanged afterward (renames only).

## Anime library organization (AniDB)

Applies to `S:\Media\Anime` and any other anime tree. Tool comparison, install, commands, templates, and UDP rate limits: [references/anime-anidb.md](references/anime-anidb.md).

**Tool**: `anipyrenamer` — ED2K hash -> AniDB UDP API -> rename in place or into a destination tree. Installed at `M:\scripts\Anidb downloads\anipyrenamer` in its own venv (needs Python >=3.13; use the bundled `python3`, not the system 3.12).

**Workflow**: dry-run one show folder, then the whole root; review counts and sample renames with the user; commit with `--on-conflict=skip` (never overwrite an existing destination); verify by re-counting destination files. Config is `%APPDATA%\anipyrenamer\.env` — never ask for or accept the AniDB password in chat; create it blank and have the user fill it in an editor.

**Naming target**: ask the user before planning — Plex/ASS `--plex` (`Title [anidb-AID]\...`) or the TV-library `Show Name (Year){id}\Season XX` shape.

## Collections (e.g. an actor's films in Movie.Collections)

Flat single-folder collections exist (`Tom.Holland`, `RIP.Robin.Williams.Movies` — loose files, no subfolders), but when asked to build a collection the user asked for **one subfolder per movie, sidecars inside it**. Follow that shape unless told otherwise: `M:\Movies\Movie.Collections\<Actor.Name>\<Title.Year>\...`. Keep duplicate copies as separate folders (e.g. `Billy.Madison.1995` and `Billy.Madison`, `Click.2006` and `Click (2006) (720p)`); only collapse into one folder when a name collides.

## Quality tagging existing folders

When the user asks to add quality tags to folder names that lack them, append the library's quality token in brackets to the folder name: `12 Monkeys 1995` → `12 Monkeys 1995 [SD]`. Only tag folders that do not already contain a quality indicator (SD, 720p, 1080p, 2160p, 4K). Skip folders already tagged — do not double-tag. This is a rename, not a move; the folder stays in its current location.

When extracting the year for tagging, prefer NFO metadata (`<year>` tag) over parsing the filename. If neither is available, use the folder name as-is and append only the quality tag. Apply to all folders in the target library, not just the current letter batch. Verify afterward that zero folders remain untagged.

Featurette and extras folders (Deleted Scenes, Trailer, Gallery, etc.) that are nested inside a movie folder should be moved into that movie's quality-library folder as standalone folders, not left in source. They typically contain 1-2 files and do not need their own quality tag if the parent movie folder already has one.

### File-lock handling (WinError 32)

When a file is locked by another process (media player, antivirus scan, indexer), `os.rename` raises `WinError 32` ("The process cannot access the file because it is being used by another process"). Do not retry in a loop — the lock persists.

**Workaround (copy-and-recreate):**
1. Copy the locked file to a temp location with `shutil.copy2(src, tmp)` — reads succeed even when writes are locked.
2. Create the destination folder.
3. Copy the temp file to the destination with the new name: `shutil.copy2(tmp, dst)`.
4. Delete the original file (may succeed now that the copy is done, or may still fail — leave it if locked).
5. Remove the original folder if empty.
6. Clean up the temp file.

This preserves the file and its metadata while bypassing the write lock. Report the locked file to the user so they can close the holding process.

### Windows long-path move pitfall

`os.path.exists()` returns `False` for paths exceeding 260 characters even when the file exists. `shutil.move()` may still succeed (it uses the Windows API which handles long paths better), but the `moved` counter in scripts will be inaccurate because the pre-move `exists()` check returns `False`. After any bulk move, verify by counting files in the destination rather than trusting the script's moved counter. If `shutil.move` raises `WinError 2` (file not found) but the file is actually present, retry with `subst` (see below) or the `\\\\?\\` extended-path prefix via `ctypes.windll.kernel32.MoveFileExW`.

subst pitfall: Python's `os.path` functions cannot see drives mapped with `subst` — they return `False` for all paths on the mapped drive. Only bash/MSYS can access subst'd drives. Use subst only from bash commands, never from Python. When paths exceed MAX_PATH and `shutil.move()` fails with WinError 2, map a drive letter to a parent directory (`subst Z: M:/Movies/AG`), perform the move through the mapped drive from bash, then remove the mapping (`subst /d Z:`). This is the only reliable way to handle files whose full paths exceed 260 characters.

Bash-mv fallback: when Python `shutil.move`/`os.rename` raises `WinError 3` on long paths and the `\\?\` prefix is awkward from Python, generate a bash script from the plan CSV (quoted `mkdir -p` + `mv` per row) and run it with bash. Bash handles these long paths directly; Python only writes the script. Skip rows whose destination already exists so retries are idempotent.

When asked to add quality tags, use explicit resolution tokens in the filename or existing path by default (`2160p`/`4K`/`UHD` → `[2160p]`, `1080p` → `[1080p]`, `720p` → `[720p]`). If the user asks to derive quality from the media, probe only the first video stream with ffprobe (`ffprobe -v error -select_streams v:0 -show_entries stream=width,height`) and map the longest edge to tiers: 2160p ≥ 3000×1800, 1440p ≥ 2400×1300, 1080p ≥ 1800×1000, 720p ≥ 1200×700, SD below; when the stream returns more than one dimension pair, take the first `WxH`. Preview renames of the immediate directory containing a uniform-quality video; do not rename shared collection ancestors or silently mix resolutions.

## Measuring archive size

- **The archive spans several roots and drives — measure them all or the total is wrong by many terabytes.** Known roots: `M:\Movies` plus the sibling quality roots at the `M:\` root (`Movies 1080p`, `Movies SD`, `Movies 720p`, `Movies 2160p`, `Movies Broken`); `S:\Media` (cartoons, anime, kids, educational); `T:\Media` (TV) and `T:\Organized`; `S:\_move` / `T:\_move` (staging); `M:\lottie`, `M:\Doctor.Who.2005`, `M:\z.CAMS`; `E:\_Collection` / `E:\_Other`. `S:\Media` and `T:\Media` are each individually larger than the whole M: movie library, so counting only `M:\Movies` undercounts by well over 20 T. Also sweep the non-media drives (`O:`, `X:`, `Y:`, `D:`, `R:`) — staging, torrent and download folders there hold video too.
- **Snapshot layout and sizes in one pass; the numbers are volatile.** The library is reorganized constantly (quality separation, collection moves), so a size measured an hour earlier can be off by terabytes and a folder's contents can change between two passes. Re-measure in the same pass you report, stamp the snapshot with `date`, and never mix numbers from two passes taken minutes apart.
- **Run exactly one measurement pass at a time.** Two overlapping `du` scans of the same multi-terabyte trees compete for the same slow disk and stretch a 5-minute scan past 20. Kill the superseded process before starting a new one.
- **Show progress on multi-terabyte scans.** Run `du -h -d 1 "/m/Movies"` (git-bash/MSYS paths) as a background terminal process and poll it (`process_manage` wait/poll), reporting each subfolder as it lands; a foreground `du` on this drive takes minutes with no output and looks hung. Quote the space-containing quality-root names (`"/m/Movies 1080p"`). Finish with a `du -sh` total per root, then sum the roots.
- **Count videos with a shell `find`, as a separate pass from sizing.** One invocation per root, run from bash (not a ripgrep-based search — the extension OR-logic and multi-terabyte walk are the point): `find "$d" -type f \( -iname '*.mkv' -o -iname '*.mp4' -o -iname '*.avi' -o -iname '*.m4v' -o -iname '*.mpg' -o -iname '*.mpeg' -o -iname '*.wmv' -o -iname '*.ts' -o -iname '*.flv' -o -iname '*.mov' \) | wc -l`. Append each result to a file as it completes and run it in the background — an 8–16 T tree takes many minutes. Counts are the stable inventory; sizes are the volatile one.
- **Keep the script path and the output path in the same scratch location.** In this git-bash, `$TMPDIR` resolves to `/tmp` (= `C:\Users\Owner\AppData\Local\Temp`), NOT the Hermes scratch dir (`C:\Users\Owner\AppData\Local\hermes\cache\scratch`). A script written to the scratch dir that writes its output to `$TMPDIR/...` puts the output somewhere else, and `bash "$TMPDIR/script.sh"` fails with "No such file". Use an absolute native path for both. Python (a native program) does not understand `/c/...` MSYS paths at all — it raises `FileNotFoundError` — so hard-code `C:/Users/...` style paths inside any script that opens files.
- **Verify a suspiciously small folder before reporting it.** `AG` reported 444 K because it now holds only `Thumbs.db` — check with `ls -la` (and `du -sh -L` to rule out junction/symlink double-counting) instead of trusting memory. Re-verify the layout at scan time; it changes as libraries are reorganized.
- **Sweep every attached drive, not just the known media roots.** Staging and download folders on non-media drives can hold hundreds of GB of video — this library has `O:\move media` (838 videos / 255 G), `X:\Tor` (169 / 153 G) and `X:\DOWNLOADS` (14 / 66 G), plus game-video assets under `Y:\EpicLibrary`. Enumerate the drive letters first (`df -h`, then `ls /<letter>`) and run the video count on each one; even a nearly-empty drive is worth a count, because a single large ISO or archive dominates its footprint.
- **Measure video bytes, not folder bytes, when a folder mixes media with non-media.** `du -sh` on a downloads or game-library folder counts installers and game assets too. Sum only the video file sizes: `find "$d" -type f \( -iname '*.mkv' -o -iname '*.mp4' -o -iname '*.avi' -o -iname '*.m4v' -o -iname '*.mpg' -o -iname '*.mpeg' -o -iname '*.wmv' -o -iname '*.ts' -o -iname '*.flv' -o -iname '*.mov' \) -printf '%s\n' | awk '{s+=$1; n++} END {printf "files=%d size=%.2f GB\n", n, s/1073741824}'`. Use this for the video footprint of mixed folders; use `du -sh` for pure media roots.
- **Exclude disc images from the media count.** `.iso` is not a video — a Linux or game installer ISO otherwise inflates a drive's media total (one pop-os installer ISO reported as "1 video, 3.66 GB"). Drop `-iname '*.iso'` from the count, or count it separately and label it non-media.

### Archive inventory handoff report

When the user asks for a handoff file, write two artifacts into the user's home directory (`C:\Users\Owner\`):

- `media_archive_handoff.md` — totals table (terabytes + video count), per-drive and per-folder breakdown with size and video count, the caveats that make the numbers volatile (reorganization in progress, what is not media), and pointers to the raw scan outputs.
- `media_archive_inventory.csv` — one row per location with columns `drive,path,size,videos,category,notes` so the inventory can be sorted and filtered in a spreadsheet.

Rules:

- Stamp the report with the scan date and the snapshot window; state which roots were measured in the same pass.
- Report size and video count side by side for every location — a folder with a large size and a near-zero video count is not media.
- Reference the raw scan files (`archive_size_fresh.txt`, `archive_counts.txt`, `other_drives.txt`) as source data so the numbers can be re-derived.
- Deliver both files with `MEDIA:<absolute path>` lines.

## Consolidating outliers into the main libraries

When the user asks to consolidate stray/staging/torrent folders into the main library, the sources are roots outside the main library (`O:\move media`, `X:\Tor\done`, `X:\DOWNLOADS`, ...) and the destinations are the main roots (`S:\Media`, `T:\Media\TV`, `M:\Movies`, `E:\_Collection`).

Procedure:

1. **Confirm scope before scanning.** Ask which folders are in and out; the user corrects scope mid-task ("ignore EpicLibrary", "ignore tor/inc"). Scanning an excluded folder wastes a multi-terabyte pass.
2. **Inventory the outliers** — per-folder video count and video-byte total, using the `find` count and byte-sum commands above.
3. **Classify each item** as anime / cartoon / live-action TV / film. Recipe and API details: [references/outlier-consolidation.md](references/outlier-consolidation.md). Route: anime → `S:\Media\Anime`, cartoon → `S:\Media\_Cartoon`, live-action TV → `T:\Media\TV`, film → `M:\Movies`, named collection → `E:\_Collection`.
4. **Deduplicate by content hash** (MD5 with size pre-filter) against the destination library. Report exact duplicates separately; never move them.
5. **Write a dry-run plan** (move table + duplicate-deletion table + open questions) to the home directory and present it. Nothing moves until the user approves.
6. **Execute, then verify** with before/after `du -sh` per destination and a video recount.

Pitfalls:

- **Never hash the whole destination library.** Size pre-filtering turns a 72k-file/40 TB hash job into a few thousand hashes; hashing everything reads the entire archive and takes hours.
- **Filename matching is not duplicate detection.** It reported 0 matches where MD5 found 93/93 duplicates, because release names differ entirely (`1927 - Wings.mp4` vs `Wings(1927)().mp4`). Confirm with content hash before calling something new.
- **A same-named destination folder can be a partial copy.** Compare video counts, not folder names — one library's `BATMAN.Cartoons...` held 64 `.srt` and 0 videos, so the source was new content, not a duplicate.
- **Python cannot open MSYS paths.** A script run under this git-bash that opens `/c/Users/...` raises `FileNotFoundError`; pass native `C:/Users/...` to Python, and reserve `/c/...` for bash builtins and for native Windows programs invoked from bash.
- **Flag ambiguous classifications.** A single API can be wrong (a 2026 Marvel series returned `Scripted`). Surface the uncertainty and ask; do not silently route.
- **Deletion is a separate decision.** Exact duplicates are safe to delete, but the user decides — present the deletion list and wait.

## Quality-based library separation

When the user asks to separate a mixed library by quality into distinct library roots, use the pattern `M:\Movies {quality}\AG {quality}\A {quality}` (e.g., `M:\Movies 1080p\AG 1080p\A 1080p`).

Subtitle filtering: When the user asks to keep only English subtitles, delete all .srt files whose path contains a non-English language name (Spanish, French, German, Italian, Portuguese, Dutch, Polish, Russian, Arabic, Chinese, Japanese, Korean, Turkish, Swedish, Norwegian, Danish, Finnish, Czech, Hungarian, Romanian, Greek, Hebrew, Thai, Vietnamese, Indonesian, Malay, Hindi, Bengali, Tamil, Telugu, Croatian, Serbian, Bulgarian, Ukrainian, Lithuanian, Latvian, Estonian, Slovak, Slovenian, Catalan, Basque, Galician, Welsh, Irish, Icelandic, Persian, Urdu, Punjabi, Tagalog, Swahili, Afrikaans, Latin, Brazilian, Castilian, and their 3-letter codes). Keep files whose path contains English, Eng, or En. Delete the non-English files before building the move plan. This is a destructive step — confirm with the user before deleting.

Sort order: When determining destination letter folders or sorting movie names, strip leading articles (A, An, The) from the title. "The Birds" sorts under B, "A Beautiful Mind" under B (Beautiful), "An American Werewolf" under A (American). Apply this to both folder creation and any alphabetical listing. For existing folders that start with an article, move them to the sub-bucket matching the word after the article (see "Movie article reorganization" above) — do not rename, only relocate. Each quality gets its own root, letter folder, and movie folder. Sidecars (NFO, subtitles, artwork) follow their matching video into the same quality library. Files where ffprobe cannot read dimensions go to `M:\Movies Broken\AG Broken\A Broken` — do not call a file corrupt solely because probing failed. Probe with `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0` (reads header only, no decoding). When matching probe results to files, strip quality tags like `[SD]` or `[720p]` from directory names since they may have been added after the original inventory. Match by basename as a fallback when full-path matching fails.

Path-mismatch pitfall: The probe TSV's path column may list files from a different library root than the one being organized (e.g., A-folder files appearing under a C-folder scan). Always verify that the source path in the plan actually exists on disk before moving; if it does not, search the broader library tree for the basename and re-verify the destination. Do not silently skip or error — report the mismatch and ask which root the file belongs to.

- **Terminal tool (bash) fails on paths containing `#`.** The bash shell mangles paths with `#` (treats as comment). Use `execute_code` (Python) with `os.rename` for file operations on such paths. Python's `os` module handles `#` paths correctly.

- **Live root can move mid-session.** The user may relocate the whole library (e.g. `M:\\Movies` → `M:\\Media\\Movies`) or change the destination layout after a plan is built. Re-verify the root with `ls`/`find` before acting, rebuild the plan from current disk state, and re-seek approval; never execute a stale plan.

Windows pitfall: Running ffprobe via Python's subprocess module fails with `WinError 5 Access is denied` on this system. Use bash (MSYS) to invoke ffprobe instead — the same command works when run directly in the shell. Python's subprocess cannot spawn it even though the binary is on PATH.

Long-path inventory pitfall: `os.walk()` can list files with paths exceeding 260 characters, but `os.path.getsize()` raises `FileNotFoundError` (WinError 3) on those same paths. When building inventories, catch the size error and record 0 or use the `\\?\` extended-path prefix. Do not let a single long-path file abort the entire inventory scan.

Multi-stream output: Some files (especially .mpg/.m4v) return multiple dimension pairs from ffprobe, e.g. `352x288x` or `1280x720 640x480`. Take only the first `WxH` pair — split on `x` and use the first two values. Do not assume a single clean `WxH` output.

- **Resolution tier rule (apply in this order):** (1) height < 720 → **SD**, regardless of width; (2) otherwise take the longest edge — ≥3840 → 2160p, ≥2500 → 1440p, ≥1800 → 1080p, else 720p.

## Unsorted movie folders

When the library root contains individual movie folders (e.g., `The.Birds`, `The.Matrix`) mixed with letter folders (A, B, C, ...), treat the unsorted folders as a separate batch. Probe and plan them together, but assign each movie to its letter folder based on the title with leading articles stripped ("The Birds" → B). Use `M:\Movies {quality}\AG {quality}\{letter} {quality}` as the destination, matching the existing letter-folder structure. Do not create a separate "Unsorted" or "Misc" folder.

## Bulk rename collision handling (duplicate copies)

When a bulk rename maps a non-conforming folder to a name that already exists (a `(2)`/`(3)`/`(4)` copy whose base folder is already conforming), do not overwrite — the two are usually distinct copies (different format/size/rip), not bit-identical duplicates. Verify first:

- Compare file sets (names + sizes) between the two folders. If names and sizes match exactly, hash both (SHA1) to confirm true duplicates before deleting anything.
- If they differ (different extension, size, or extra files), treat them as distinct copies: merge the duplicate's files into the conforming folder, renaming each to append an 8-char SHA1 of its content before the extension (e.g. `Movie(2024)(1080p).a1b2c3d4.mkv`), then remove the now-empty duplicate folder. This keeps both copies while avoiding filename collisions.
- After any move, re-hash every moved file and compare against the hash embedded in its new name; report 0 mismatches before claiming success.
- Audit regexes that count parenthesized groups produce false positives on titles that legitimately contain parentheses (e.g. `(500) Days of Summer`). Treat such folders as conforming and leave them untouched rather than forcing a rename.

## Per-movie folder reorganization

After separating by quality into flat library directories, reorganize each quality library so every movie gets its own folder containing its video and all matched sidecars (subtitles, NFO, artwork, torrent metadata). This avoids flat-directory filename collisions.

Matching sidecars to movies: match by the sidecar's top-level source directory, not by exact parent or stem. Source folders are raw torrent names (e.g. `Caddo.Lake.2024.1080p.AMZN.WEBRip`); destination folders are cleaned `Title (Year) (Quality)`. Extract a normalized key (lowercase, strip quality/codec suffixes, extract title+year) from both sides and match on that. Fall back to substring containment when exact key match fails.

Sidecar safety rules (learned from a failed commit):
- **Sidecars are non-video files only.** Never treat another VIDEO file as a sidecar, even when stems match. One season folder can hold two encodes of one episode sharing a stem (e.g. `...S03E04.Watch.the.Thrones.avi` and `...S03E04.Watch.the.Thrones.mp4`); same-stem matching that includes video extensions renames the second video as a "sidecar" of the first and then fails on its own rename — triggering a full rollback. Filter sidecar candidates by extension (everything not `.mkv/.mp4/.avi/...`) BEFORE comparing stems.
- **Shared sidecars are renamed once.** When two same-stem videos share one `.nfo`/`.jpg`, the sidecar belongs to the folder, not to either video: dedupe sidecar renames by source path so the second video's sidecar step skips an already-renamed source instead of failing.
- **Duplicate filenames inside one source tree collide on flatten.** The same filename can exist in two subfolders (e.g. `Subs\chi\chi.srt` and `Subs\??(??).chi\chi.srt`). Resolve by renaming the duplicate (`name (2).ext`) or, when the user authorizes deleting non-English subtitles, drop it (see Subtitle filtering).

Generic sidecar filenames (English.srt, INFO.nfo, TGx.Downloaded...txt) collide across movies in flat directories. Per-movie folders eliminate this. Files already moved flat can be reorganized in-place by moving each video and its matched sidecars into a new subfolder named after the video stem. Handle remaining source files (skipped due to destination collisions) by matching their top-level folder to the destination movie folder and moving them in.

Collision resolution for duplicate titles: When the same movie exists in multiple encodes (x264 vs x265) or releases, their videos may share a filename. Include the encode/variant in the folder name to keep them separate (e.g. `Encanto (2021) (1080p) x264` and `Encanto (2021) (1080p) x265`). Extract encode from the filename (x264, x265, h264, h265, hevc, avc) or release group (RARBG, YTS) as fallback. For single-version movies, use the clean folder name without encode. For movies with multiple versions, append the encode to distinguish them.

Movies nested under a collection folder: When a top-level folder is a collection name (e.g. `Ernest`) containing subfolders for individual movies, extract the movie title and year from the subfolder name, not the collection folder. The collection folder name alone will not match any destination. Match sidecars by their immediate parent subfolder, not the collection root.

Large collection execution (e.g. Movie.Collections with 4,000+ files): The quality plan will have duplicate destinations for generic-named files (INFO.nfo, Torrent.downloaded.from.*.txt, Darkside.RG.jpg) that appear in every movie folder. These are skipped during the move (destination exists) and cleaned up afterward. After reorganization, delete junk files (INFO.nfo, Torrent.downloaded.*.txt, .jpg/.png artwork, .bat, .sfv) and non-English subtitles from the remaining source tree, then clean empty directories. Do not attempt to move these junk files into per-movie folders.

## NFO-driven folder renaming (title + year + quality)

When renaming folders using NFO metadata, extract `<title>` and `<year>` from the NFO and insert them into the folder name. The target format is `Title (Year)(Quality) [rest of original name]` — the year and quality go immediately after the movie title, before any release/codec info.

Pitfall: NFO titles frequently contain characters that are invalid in Windows filenames — colons (`:`), slashes (`/`, `\`), asterisks, question marks, quotes, angle brackets, pipes. Sanitize these before renaming: replace `:` with ` -`, replace `/` and `\` with spaces, and strip the rest. Failure to sanitize causes `WinError 123` ("The filename, directory name, or volume label syntax is incorrect").

Pitfall: The NFO title may not match the start of the folder name (e.g., NFO title "The 13th Warrior" vs folder "13th.Warrior"). In these cases, skip the release-info split and use just `Title (Year)(Quality)` without the rest. Do not force a match — a slightly shorter name is better than a corrupted one.

Pitfall: Folders that already contain a 4-digit year in their name should be skipped — do not double-tag. Check with `re.search(r"\d{4}", name)` before processing.

Pitfall: Before NFO-driven renaming, strip any existing quality tag (e.g., `[SD]`, `[720p]`) from the folder name with `re.sub(r"\s*\[[^\]]*\]\s*$", "", name)`. Otherwise the quality tag gets duplicated in the new name (e.g., `Title (2006)(SD) [SD]`).

Pitfall: The `1# SD` library folder and featurette/extras folders (Deleted Scenes, Trailer, Gallery, etc.) have no NFO and should be skipped. They are not movies.

## Resolution audit before a quality split

Measure real resolution before splitting a library across drives — folder and
filename tags are routinely wrong. Recipe: `references/resolution-audit.md`.
Runnable helpers: `scripts/probe_resolution.sh` (parallel ffprobe) and
`scripts/resolution_audit.py` (tier summary + normalized dry-run plan).

- Build the file list with **drive-letter paths** (`T:/...`), not MSYS mounts —
  ffprobe is a native program and cannot resolve `/t/...`.
- Probe in parallel, one process per file, each writing its own part file
  (`xargs -P`, per-PID `part.$$`); expect ~20 files/s on a spinning HDD, so run it
  as a background process and report progress.
- Tier rule: height < 720 → SD regardless of width; otherwise the longest edge
  (≥3840 → 2160p, ≥2500 → 1440p, ≥1800 → 1080p, else 720p).
- Probe every file whose extension is neither a known video nor a known
  sidecar/artwork type — mislabeled videos (`..._mkv`, `.arj`, `.exe`, no
  extension) otherwise land in "non-video" and distort the totals.
- Write Python-produced lists with `newline='\n'`; CRLF makes `xargs -d '\n'`
  hand the native tool a trailing `\r`.

### Quality resolution order (when a folder/file has no quality token)

When normalizing a library where quality is not in the folder name, resolve in this order — stop at the first hit:

1. **Parent/root path token** (e.g., `Movies 720p` → 720p, `Movies 1080p` → 1080p, `Movies 2160p` → 2160p, `Movies` or `Movies SD` → SD). Never probe individual files when a parent path carries a quality token.
2. **NFO `<height>` tag** — read the nearest `*.nfo` (walk up from the video's folder); map height → SD/720p/1080p/1440p/2160p.
3. **ffprobe** the first video stream header only (`ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0`); map by **vertical height** to tiers (2160p = height 2160+, 1440p = 1440, 1080p = 1080, 720p = 720, **SD = height below 720**). Take only the first `WxH` pair when multiple are returned.

- **Quality-tagging examples (from the rule above):** 1280×688, 1280×640, 1280×540 and 720×480 → SD (height < 720 wins over the width tag); 1920×800 and 1920×960 → 1080p (long edge ≥1800). Files tagged 720p frequently probe below 720 lines — trust the probe, not the name.

Never leave `Name (Year)()` — an empty quality tag means a resolution step was missed. Probe only leaf folders that contain a video; leave structural/category/letter folders untouched.

Auditing space per resolution tier (probe-based): [references/resolution-audit.md](references/resolution-audit.md).

### In-place sidecar rename (match video stem)

When normalizing file names in place (no moves), rename each video's non-video sidecars to match the video's new normalized stem in the same step:

- Enumerate sidecars live at rename time (do not freeze paths at plan time — ancestor renames invalidate them).
- Filter sidecar candidates by extension first (everything except `.mkv/.mp4/.avi/.m4v/.mpg/.mpeg/.wmv/.ts/.flv/.mov`); never treat a second video sharing a stem as a sidecar.
- Dedupe sidecar renames by source path so a shared `.nfo`/`.jpg` is renamed once even when two same-stem videos share it.
- Skip files already in target form; flag collisions instead of overwriting.
- Never touch `.bat`, `Thumbs.db`, `plexignore`, or `*.db`.
- Report progress per folder for long batches.
When the user asks to normalize names to `Name(Year)(rest)` (keeping original release info inside the second parentheses), apply to both folders and files. Strip the year token; everything after the year becomes `rest`. Keep original filenames only when explicitly asked.

### Movie folder normalization (Title (Year)(quality) folders + Title(Year)(quality).ext files)
When the user asks to normalize an entire movie library to `Title (Year)(quality)` folders with `Title(Year)(quality).ext` files:

1. **Parse title + year from folder name.** Folder names are typically `Title(Year)(release info)` or `Title(Year)()`. Extract title (text before first `(`), year (from `(YYYY)`), quality from parent folder path (Movies 720p → 720p). Replace dots with spaces for folder title; keep dots for file title.
2. **Handle missing year.** When no `(YYYY)` is found in the folder name or file names, use "Unknown" — never leave empty parens `()`. Check file names inside the folder as a fallback before defaulting to "Unknown".

### Unknown-year recovery via web search

When a library contains many `(Unknown)` folders (no year in path), recover years by:

1. **Extract unique titles** from the "Unknown" folders (strip quality tags, normalize spaces).
2. **Match against existing library** — check if the same title appears elsewhere with a `(Year)` in the name. Use normalized title comparison (lowercase, strip quality tags). This typically resolves ~40% of titles.
3. **Web search the rest in batches** — group ~10 titles per search query. Use `web_search` with quoted titles. Extract years from results (IMDb, Wikipedia, TMDB). Save matched titles+years to a file.
4. **Build a dry-run CSV** mapping `(Unknown)` → `(year)` in both folder and file names. Apply to video files and sidecars (nfo, jpg, png, srt). Skip files already containing a 4-digit year.
5. **Handle unresolvable titles.** Some `(Unknown)` entries are extras, featurettes, or bonus content (e.g., "BurnE", "Celebration Reel", "Meet the Cast", Blu-ray special features) that have no standalone release year. Leave these as `(Unknown)` or rename to a generic label (e.g., `(Extras)`) — do not force a year. Flag them in the plan for manual review. Conversely, some titles that LOOK like extras or bonus content may actually be standalone movies with their own release years (e.g., "InuYasha" movies, "Digimon" movies, "The RM", "Snowday") — always verify with a web search before classifying as unresolvable. A user-reviewed subset often contains resolvable titles that the initial automated search missed.
6. **Commit** the rename, then verify totals are unchanged (renames only).
3. **Handle empty parens.** Folder names like `Anna.and.The()()` have empty parens — the year may be in the file name or metadata. Search the full path with `\\b(19\\d{2}|20\\d{2})\\b` (not `\\d{4}` alone, which false-matches 1080p).
4. **Quality from parent path.** Map "Movies" → SD, "Movies 720p" → 720p, "Movies 1080p" → 1080p, "Movies 2160p" → 2160p, "Movies SD" → SD. Never probe individual files unless quality is absent from all parent paths.
5. **Commit bottom-up.** Sort operations by path depth descending. Rename video files first (inside the folder), then rename the folder. Process deepest paths first so ancestor renames don't invalidate descendants.
6. **Handle duplicate folder names.** When two folders map to the same new name (different editions), append ` (2)`, ` (3)`, etc. to the second+.
7. **Handle nested duplicate folders.** Collections like Harry Potter have deeply nested duplicate structures (e.g., `Harry.Potter.3.../Harry.Potter.3.../Harry.Potter.3.../`). When a parent folder is renamed, all descendant paths become invalid (WinError 3). Re-resolve paths live during commit; skip items whose source no longer exists instead of failing.
8. **Skip non-video sidecars that are already moved.** After the main pass, junk files (INFO.nfo, Torrent.downloaded.*.txt, artwork) and non-English subtitles in remaining source trees should be cleaned up separately — do not attempt to move them into per-movie folders.

**File-type rules** (use to classify the path component to normalize):
- **Video file:** `Title (Year)(Quality) SxxExx.ext` inside the quality folder — SxxExx always UPPERCASE.
- **Artwork** (`.jpg/.png` matching backdrop, folder, landscape, logo, poster, thumb, banner): `Show.Name(YEAR).<original>` in the series folder — do NOT add an episode code.
- **NFO with episode:** `Show.Name(Year)(Quality) SxxExx.nfo` in the season folder.
- **NFO / txt / xml – season-level** (`season.nfo`): `Show.Name(YEAR).season.N.nfo` in the series folder, with N taken from the parent folder.
- **Subtitles (`.srt`/`.sub`):** `Show.Name(Year)(Quality) SxxExx.<language>.ext` in the season folder, keeping the language tag.
- **Subtitle numeric variants (2., 3., …):** keep the leading variant suffix so one episode with multiple subs yields distinct destination names (e.g. `…S01E01.2.English.srt`, `…S01E01.3.English.srt`) instead of colliding. Match the episode stem from the name or its parent folder; do not collapse `2.`/ `3.` variants.

**General rules**:
- Always include BOTH parenthesized groups, even when empty (never `Name (Year)( )`), and keep the dots in `rest` — never drop trailing release tokens.
- SxxExx must render uppercase (`S01E03`, never `s01e03`).
- Unless the user explicitly asks to rename files, keep original file names as-is during folder normalization; only movie folder names change to `Title (Year)(Quality)`.
- Rename files and folders in the same pass only when the user asks for both; it multiplies collision risk.

### Ancestor-rename invalidation
A frozen plan goes stale once an ancestor renames (WinError 3). Rebuild from current disk state (skip names containing `(`) or do a live bottom-up walk re-resolving parents.

### Long-path renames
Paths >260 chars fail with WinError 3. Use `subst` to map a drive letter to a parent and rename through it (bash only), then `subst /d`.

Pitfall: When a library root carries no quality token (e.g. legacy `M:\\Movies`), resolve each leaf movie folder's quality from its NFO (`<height>`) first, then ffprobe the first video (height → SD/720p/1080p/1440p/2160p). Never leave `Name (Year)()` — an empty quality tag means the probe/NFO was missed. Probe only leaf folders that contain a video; leave structural/category/letter folders untouched.

Pitfall: Unless the user explicitly asks to rename files, keep original file names as-is during folder normalization; only the movie folder names change to `Title (Year)(Quality)`. Renaming files and folders in the same pass multiplies collision risk.

Pitfall: When the user asks to keep release info in the name, use the compact form `Title(Year)(rest)` for BOTH the folder and the file, where `rest` is the original release/codec info after the year (e.g. `Apollo.13(1995)(720p.BluRay.x264.YIFY)`). Always include both parenthesised groups even when year or rest is missing (empty parens), and keep the dots in `rest`; never drop the trailing release tokens.

Pitfall: Artwork and sidecar files (backdrop.jpg, folder.jpg, logo.png, season posters, .nfo) that sit at the series/quality level should be prefixed with `Show.Name(YEAR).` (e.g. `The.100(2014).logo.png`) and stay with the series folder — do not move them into a season folder or rename them with an episode code.

## Deep-nested and unmatched file recovery

When reorganizing, some files end up in deep-nested subfolders (Subs/, VobSub/, srt/) that the flat sidecar-matching logic misses. After the main move pass:

1. Delete non-English subtitles (see Subtitle filtering) from the remaining tree.
2. Move surviving files to a `_cleanup` folder at the library root.
3. For NFO files in `_cleanup`, read `<title>` and `<year>` and create a folder named `Title (Year)` for each, moving the NFO in. Sanitize colons in folder names (`:` → ` -`).
4. Move all remaining unmatched files (generic-named subs, images, text) into an `Unmatched` subfolder.
5. Move the entire `_cleanup` contents to a `Recovered` folder at the library root for manual review. Do not attempt to auto-match generic-named subs to movies — the filename contains no movie identifier.

This is a best-effort recovery; the user can manually sort the `Recovered` folder later.

When per-movie folders are not used (flat directories) or for extra clarity, prefix every sidecar filename with the movie title and year: `Carry On (2024) - English.srt`. This prevents collisions among generic filenames (English.srt, INFO.nfo, TGx...txt) across movies. Even inside per-movie folders, this makes sidecars identifiable at a glance.

Extract the prefix from the parent movie folder name: use the `Title (Year)` portion (everything up to and including the first `(YYYY)`). For folders without parenthesized years, use the text up to the first 4-digit year. Skip files that already start with the prefix — some sidecars (especially .nfo files) already include the full movie name in their filename (e.g. `Daddys.Little.Girls.2007.16x9.nfo`), so they will be skipped correctly. Do not double-prefix.

Windows MAX_PATH pitfall: Windows has a 260-character path limit. When combining long folder names with long filenames, the full path may exceed this. If `Path.rename()` raises `FileNotFoundError` (WinError 3), the path is likely too long. Check `len(str(full_path))` and skip or shorten the prefix for paths approaching 250 characters. Use a shorter prefix (first 30-40 characters) for deeply nested or long-named folders.

For files that cannot be moved or renamed due to path length even after shortening, map a drive letter to a parent directory using `subst X: "C:\path\to\parent"`, perform the operation through the mapped drive (which shortens the path), then remove the mapping with `subst /d X:`. This is the only reliable way to handle files whose paths exceed MAX_PATH when the `\\?\` extended-path prefix does not work with the tool in use.

- Use the reusable path-validation and read-only repeated-folder preview recipe in [references/powershell-dry-run.md](references/powershell-dry-run.md).
- Naming decision table for TV libraries: see [references/TV-naming.md](references/TV-naming.md).

## Movie article reorganization (existing folders)

When an existing movie folder's name starts with an article ("The", "A", "An"), move it to the sub-bucket whose letter matches the first letter of the word **after** the article. The folder name keeps the article — only the location changes. This applies to all quality roots and all letter-range buckets.

- "The Birds (1963)(SD)" in `Movies SD/AG SD/T SD/` → move to `Movies SD/AG SD/B SD/`.
- "A Beautiful Mind (2001)(1080p)" in `Movies 1080p/AG 1080p/A 1080p/` → move to `Movies 1080p/AG 1080p/B 1080p/`.

**Double check then ignore articles rule (user-specified):** Before treating any "A", "An", or "The" folder as an article and moving it, ALWAYS double-check that it is genuinely an article (i.e., the word following it is a real word/title, not a single-letter initialism or abbreviation). Only after confirming it is a real article should you ignore it and organize by the following word. Do NOT blindly move every folder starting with "A", "An", or "The" — some are titles (e.g., "A P Bio", "A.P", "A.P (2018)"). Verify the following word is a normal title word, not an initialism or proper-noun exception, before treating the leading word as an article. Note: "The 100", "The 4400" and similar where "The" is followed by a number ARE articles — "The" is ignored and the folder is organized by the number (under "#").

**Outlier rule (user-specified):** "A P Bio", "A.P", "A.P (2018)" and similar where "A"/"An" is part of the title (single-letter or initialism) are NOT articles — leave them in A. 99% of the rest: treat "A"/"An" as an article and organize by the following word.

**ALL-CAPS casing rule (user-specified):** ALL-CAPS folder casing is preserved ONLY for shows where ALL-CAPS is the correct/standard form — acronyms (NCIS, NYC, SSGB), Roman numerals (XIII), single-letter titles (V), and stylized titles (NOS4A2). Regular multi-word titles that happen to be stored in ALL-CAPS (e.g., BIONIC.WOMAN, BODY.OF.PROOF, DOMINION, JEREMIAH) are NOT ALL-CAPS shows — convert them to title case (Bionic Woman, Body of Proof, Dominion, Jeremiah). When in doubt, check the web: if the canonical title uses title case, use title case. Do not blindly preserve ALL-CAPS for every folder that appears in all caps.

**TV extras folders may contain standalone movies.** A folder labeled "Deleted.Scenes", "Deleted Scenes [1080p]", or similar in a TV bucket may actually contain standalone movie files (filenames with a 4-digit year and movie title, not short deleted-scene clips). When processing TV buckets, inspect the contents of extras/deleted-scenes folders: if files match movie patterns (`Title (Year).ext` or `Title.Year.ext`), move them to the movie library with proper `Title (Year)(Quality)` naming rather than leaving them in TV/Extras. Quality is derived from the file or folder name (1080p, SD, etc.) or ffprobe. This prevents movie files from being stranded in TV extras folders.

**Movie files in TV buckets.** When processing a TV letter bucket, some folders may contain standalone movie files (e.g., `Demon.Knight.1995.avi` in bucket D). These are not TV shows — identify them by the absence of season/episode markers and the presence of a movie title + year, then move them to the appropriate movie library quality root with `Title (Year)(Quality)` naming. Quality is derived from the file extension or ffprobe (avi → SD, mkv/mp4 → check parent or probe).

**Procedure:**
1. Scan every letter-range bucket for folders starting with `The `, `A `, or `An ` (case-insensitive, word boundary).
2. For each candidate, strip the article and take the first character of the remainder.
   - If the remainder's first token is a single letter or initialism, skip (leave in place).
   - If it's a digit → target `#`.
   - Otherwise → target is that uppercase letter.
3. If target == source letter, skip (already in the right place).
4. Move the folder to the correct sub-bucket within the same letter-range bucket without renaming.
5. Dry-run first: report counts per target letter before applying.

**Pitfalls:**
- Do not strip the article from the folder name — only the location changes.
- A folder whose name is just "The", "A", or "An" (no following word) stays put.
- Verify no real conflicts (same name already in target) before moving.
- Apply to movies the same way as TV (see references/TV-normalization.md → Patterns 4 & 5).

## Movie sub-bucket splitting (>100 movies)

When a single-letter sub-bucket contains more than 100 movie folders, split it into second-letter sub-buckets named `{letter}{second_letter} {quality}` (e.g., `BA SD`, `BB SD`, ..., `BZ SD`). Move each movie folder into the sub-bucket matching the second letter of its title (after stripping leading articles).

- "B SD" with 119 movies → `BA SD`, `BE SD`, `BI SD`, `BL SD`, `BO SD`, `BR SD`, `BU SD`, `BY SD`.
- "S SD" with 148 movies → `SA SD`, `SC SD`, ..., `SY SD`.

**Procedure:**
1. Count movie folders in each single-letter sub-bucket.
2. For any sub-bucket with >100 movies, create second-letter sub-buckets.
3. For each movie folder, determine the second letter of its title (after stripping leading articles like "The", "A", "An").
4. Move the movie folder into the matching second-letter sub-bucket.
5. Remove empty sub-buckets after processing.
6. Verify no sub-bucket exceeds 100 movies after splitting.

**Pitfalls:**
- Do not split sub-buckets that already have ≤100 movies.
- When determining the second letter, strip leading articles first (so "The Birds" → B → BI, not "The Birds" → T → TH).
- After splitting, the single-letter sub-bucket becomes a container for second-letter sub-buckets — do not leave loose movie folders alongside them.
- Verify totals (file count, movie count) are unchanged after splitting.

## Subtitle fetching (OpenSubtitles API)

When the user asks to download subtitles for a library (e.g., "get English + HI subs for every movie missing them"):

- **API**: OpenSubtitles v1, base `https://api.opensubtitles.com/api/v1`. Auth via `Api-Key` header only — no login/OAuth needed for search or download. Also send `User-Agent`.
- **Search**: `GET /subtitles?query=<title>&languages=en&year=<year>` (URL-encode the title). Response `data[]` items have `attributes`: `hearing_impaired` (bool), `download_count` (int), `files[0].file_id`.
- **Download**: `POST /download` with `{"file_id": <id>}` → returns `{"link": ...}`; then `GET` the link and write bytes to disk.
- **Pick best**: among standard (`hearing_impaired=false`) and HI (`hearing_impaired=true`) candidates separately, choose the one with highest `download_count`.
- **Naming**: save next to the video as `<video_base>.en.srt` (standard) and `<video_base>.en.hi.srt` (HI). One subtitle per language/variant per video.
- **Hash-based matching**: for accuracy, compute the OpenSubtitles file hash (file size + sum of first/last 64KB in 8-byte chunks) and search by `moviehash` + `moviebytesize` instead of title. Falls back to title+year search when hash yields no results.
- **Year handling**: send `year` when available; if the year-filtered search returns zero results, automatically retry without year. Also expose a toggle to disable year filtering entirely.
- **Title/year extraction**: regex `\((\d{4})\)` on the folder name; title = text before the first `(`. Find the video file by extension set (mkv/mp4/avi/m4v/wmv/mov/mpg/mpeg/ts/flv/webm).
- **Pacing**: VIP tier allows 100 downloads/day. Cap each run at ~90 successful downloads and stop; resume the next day. Track progress in a JSON checkpoint (set of done folder names) so reruns skip completed folders. **Persist the checkpoint to disk** (e.g. `subs_checkpoint.json` next to the .py) and load it on startup; on scan, mark already-processed folders as done/skipped; on each successful download, append the folder path and save. This survives server restarts and avoids re-searching.
- **Path handling**: use native Windows drive paths with forward slashes in Python; bash/MSYS cannot be relied on for Python file I/O. Paths >260 chars need the `\\?\` prefix or `subst` (see Windows long-path pitfalls above).
- **Path-escaping pitfall (HTML/JS UI)**: in JavaScript string literals, a Windows path written with backslashes gets over-escaped and renders with doubled backslashes in the input field (e.g. `M:\Media` displays as `M:\\Media`). Use forward slashes (`M:/Media`) for all default paths in JS/HTML; Windows accepts them. When changing a default that is cached in `localStorage`, bump the storage key version (e.g. `subs_settings` -> `subs_settings_v2`) so stale cached values don't override the new default.
- **Daily-count display pitfall (HTML/JS UI)**: when a daily counter is persisted server-side, initialize the client display from the server's persisted value on page load (fetch `/daily`), and do NOT reset the display to 0 during `scan()` — preserve the persisted count. Clobbering it makes the status bar show 0 until the next download.
- **Do not** download more than the daily cap in one run; the API returns rate-limit errors beyond it.
- **Pacing pitfall**: 0.3s between requests is too fast and triggers `503 Service Unavailable`. Use ≥1.5s between requests and wrap both search and download in retry/backoff on `429/502/503/504` (exponential: 2s, 4s, 8s, 16s, …). A 503 storm that fails every movie still advances the checkpoint unless guarded — see next.
- **Checkpoint pitfall**: only add a folder to the "done" set when its downloads actually succeed (or the search definitively returns no matching subtitle). On any HTTP/IO error, leave it out so the next run retries it. Marking failed folders done silently skips them forever."

## Folder-name cleanup (strip prefixes/suffixes)

When a set of folders shares a known leading token you want removed — uploader tags, domain prefixes, organization aliases — normalize by renaming the folder name, never moving it. Use when cleaning torrent-uploader tags, phase prefixes, or alias tokens from media-library folder names.

1. **Inventory the target folders first.** `find . -type d -depth` over the named root, then filter by the token pattern; report the count before changing anything.
2. **Build the strip rule.** One anchored regex over the folder name; the matched region may be a literal token (`www.Torrenting.com.`) or a token plus separator (`www.Torrenting.com - `). Greedy so the separator runs with the token and nothing survives it.
3. **Dry-run renames only.** For each match, compute the new name by removing the matched prefix (and nothing else); do NOT move the folder or touch its contents. Report `before -> after` for a sample and the total count.
4. **Commit the renames** with `mv -v` in the same directory (rename, not move). Print each rename so the applied set is visible.
5. **Verify from disk, not the script.** Re-run the same directory scan + regex; assert the remaining-match count is 0, and confirm no new name collides with an existing name in its parent. Report the verified final counts.

### Pitfall: `while read -d ''` swallows multi-line `find` output
`find . -type d` emits one path per line. `while IFS= read -r -d '' d` reads until a NUL byte — `find` never emits NULs, so the whole output is swallowed into `$d` on the first iteration and nothing else is read: zero matches and a false "nothing to do". Always use the default newline delimiter:

```bash
while IFS= read -r d; do
  ...
done < <(find . -type d -depth)
```

### Pitfall: strip only the matched prefix, then confirm uniqueness
After removing the token, two folders can map to the same name (different prefixes, same remainder). `mv` refuses on collision — it does not overwrite. Re-run the scan after committing and confirm the new names are unique within each parent directory; report any collisions as skipped-for-review rather than forcing a rename.

### Pitfall: the strip regex must include the separator
If the separator (spaces, dashes) is not included in the matched group, the new name keeps leading whitespace and the prefix is only half-removed (e.g. `The Way Home` instead of `The Way Home`). Include the token's separators (`[.[:space:]-]*`) after the token, then spot-check a few originals that begin with the token.

## Subtitle UI (self-service)

Two versions exist in `M:\scripts\Movies Hermes Scratch\ui\`: `subtitle_ui.py` (basic, port 8765) and `subtitle_ui_v2.py` (feature-rich, port 8766), plus `subtitle_ui_v2.1.py` (latest, port 8800 default, configurable). Prefer v2.1.

v2.1 features (cumulative over v2): duplicate-merging (movies present in multiple quality folders are downloaded once, then the .srt files are copied into the other folders with the correct video basename); per-row year-search toggle checkbox in the Year column; NFO title/year override during scan; OpenSubtitles.com link in the topbar; Reset and Restart buttons (Restart = reset checkpoint + start); configurable server port (default 8800, avoids Plex on 8787; persisted via port.txt and Settings); intelligent auto-scroll to the row being processed; settings-checkbox alignment fix (width:auto override so checkboxes stay compact on the left). Plus all v2 features: layout selector (1 single-page / 2 dashboard / 3 two-pane, default 1), sortable/reorderable/resizable columns with tooltips, checkbox = skip these, inline edit title/year, filter/search, color-coded status, progress bar + ETA, daily counter + remaining today, pause/resume, retry-failed, dry-run, per-row "Download now", right-click context menu, hash-based matching toggle, year in search + auto-retry without year + year toggle, custom naming template, language + HI toggles, persistent settings in localStorage, toast notifications toggle, watch-folder mode toggle, full row rendering (no 200-row cap) for scroll-to-active. Restart server from UI: "Restart Server" button calls `/restart_server`, which spawns a new detached process (bind retry) and exits the old one after 2s; the page auto-reloads. Persistent checkpoint across restarts (subs_checkpoint.json).

- Location: `M:\scripts\Movies Hermes Scratch\ui\subtitle_ui_v2.1.py` (also mirrored in Hermes scratch).
- Launch: double-click `Start Subtitle Downloader.bat` in the `ui\` folder (auto-starts the .py and opens the browser), or run `python subtitle_ui_v2.1.py --port 8800` manually, then open http://localhost:8800.
- Stop/Restart: `Stop Subtitle Downloader.bat` / `Restart Subtitle Downloader.bat`.
- Flow: enter Api-Key (pre-filled), set library path → **Scan** (lists movies without subtitles) → **Start Download** (downloads standard + HI per movie, 90-download daily cap with auto-stop).
- Progress + daily counter shown in-page; logs to `subs_log.txt`; checkpoint in `subs_checkpoint.json` (resume on next run).
- API calls retry on `429/502/503/504` with exponential backoff (2s→16s); 1.5s pacing between requests. Stop with Ctrl+C in the terminal.
- Daily cap is 90 successful downloads (under the 100/day VIP limit); rerun the next day to continue.

## Installed library tooling

Use the tooling already installed on this machine rather than reimplementing it.

- **AniDB rename / MyList** — `anipyrenamer` (`M:\scripts\Anidb downloads\anipyrenamer`, venv) and `yumemi` (`uv tool`, `%USERPROFILE%\.local\bin\yumemi.exe`). Install, config, commands and the Windows DLL pitfalls: `references/anime-anidb.md`.
- **Plex metadata / collections** — Kometa at `C:\Users\Owner\Kometa` (Plex + TMDb; does not rename files). Install, config and verify: `references/plex-metadata-kometa.md`.

Examining a tool and installing it are separate approvals: when the user supplies tool archives or docs without an explicit instruction, report what each tool does and where it fits — install or configure only after they say so.

Credentials (AniDB username/password, Plex token, TMDb key) are supplied by the user into each tool's own config; never ask for or accept them in chat, and never print a config file after writing a secret into it.