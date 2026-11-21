---
name: plex-media-server-management
description: Use when administering a Plex media server: organizing movie/TV library folders for Plex's scanner, writing NFO/.plexmatch metadata, managing collections and quality tags, and refreshing library indexes after changes.
version: 1.0.0
author: Nous Research
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [media, plex, movies, tv, organization, metadata, server]
    category: media
---

# Plex Media Server Management

## Overview

This skill administers Plex media server libraries on disk. Plex's scanner reads the filesystem directly: folder structure, file names, NFO files, and .plexmatch hint files determine what appears in Plex and how it is matched. This skill applies your existing media-organizing conventions (tv-show-organization, media-library-organization, file-naming-conventions) to the Plex-specific layer: library root separation, metadata files, match hinting, ID priority, edition-vs-version, renaming warnings, and the scan/refresh cycle.

## When to Use

- Setting up or retagging a Plex movie or TV library on this machine.
- Organizing folders in M:\MOVIES\AG (movies) or T:\Media\TV (TV shows) so Plex indexes them correctly.
- Writing/updating tvshow.nfo, poster, fanart, and .plexmatch hint files.
- Choosing TMDB vs TVDB vs IMDb IDs and applying them to files/folders.
- Adding/removing Plex collections and playlists.
- Refreshing a Plex library after a batch of moves/renames (do NOT skip this step).
- Administering the Plex server (scanning, reindexing, metadata agent settings) via the Plex Web UI or API.

## Plex-specific rules

1. Separate roots: Plex warns and ignores files when Movies, TV, and Music are mixed in one library root. Keep movie content under M:\MOVIES\AG (and movie quality roots), TV content under T:\Media\TV. Do NOT combine them in a single Plex library path.
2. Structure drives indexing: Plex creates one library item per folder (movies) or per show/season/episode (TV). The folder layout is the source of truth for what Plex shows.
3. NFO files: tvshow.nfo carries Plex's advanced metadata (genres, ratings, tags, the show's ID). Write/update these by hand or via a scraper, then the library picks them up on rescan. Movies use individual NFOs only when you want custom metadata.
4. .plexmatch files: a line-delimited text file named exactly .plexmatch in a series/season directory overrides Plex's matching for that directory. See .plexmatch rules below. Most libraries do not need it; use it to fix mis-matches.
5. Renaming warns: renaming an existing movie/episode folder or file creates a new Plex library item on the next scan — watched status and custom metadata are NOT carried over. For existing items, prefer editing the item in Plex Web (Admin — Library — …) rather than renaming on disk.
6. Refreshing is mandatory: after any batch of moves, renames, NFO writes, or .plexmatch changes, trigger a Plex library rescan/refresh before reporting success.
7. ID priority (independent of naming, applied per media type): TV shows: TVDB → TMDB → IMDb (TVDB preferred); Movies: TMDB → IMDb → TVDB (TMDB preferred). The first ID found in the NFO (or web) wins. A show that is both a movie and a TV show uses the type that applies to the item.
8. Edition vs version (Plex Pass required for Server admin):
   - Versions = same release, different resolution/encoding (1080p vs 2160p, HEVC vs H.264). Plex merges these automatically (one item with an Other Versions section).
   - Editions = different releases/cuts (Theatrical, Director's Cut, Extended, Unrated, 2D vs 3D). Each edition is its own item, tracked separately for watched status, ratings, and metadata. Requires Plex Pass.
9. Multiple versions (file naming): MovieName (year) - ArbitraryText.ext — e.g. Pulp Fiction (1994) - 1080p.mkv and Pulp Fiction (1994) - SD.m4v collapse to one item. All parts share resolution/encoding format and audio/subs in same order.
10. Multiple parts: MovieName (year) - ptX.ext — split names: cdX, discX, dvdX, partX, ptX. All parts same format; up to 8 parts; audio/subs in same order.
11. Multiple editions (file naming): append {edition-Name} to the movie file: Blade Runner (1982) {edition-Director's Cut}.mp4.
12. TV editions (file naming): add {edition-Edition Title} to the end of the show folder name: Babylon 5 (1994) {edition-Bluray Remaster}. Each edition tracked separately.
13. Posters/fanart: posters in MovieName (Release Date).ext or Movie/MovieName (Release Date)/Custom_Poster_Name.ext (jpg, jpeg, png, tbn); fanart in MovieName (Release Date)-fanart.ext (16:9).
14. Local trailers/extras (TV): inline in the same season directory, or a subdirectory per type (Trailers/, Behind the Scenes/). Only when the TV agent is Plex Series.

## Quality tiers (shared with library skills)

Map ffprobe video stream resolution → tier:

| Resolution | Tier |
|---|---|
| 3840x2160 | 2160p |
| 1920x1080 | 1080p |
| 1280x720 | 720p |
| 853x480 / 640x480 | 480p |
| height < 480 | SD |
| no video stream | Not a video (exclude from quality counts) |

Derive quality from the actual video stream via ffprobe (not from folder-name tags). Probe via bash, never via Python subprocess to C:/Program Files/Jellyfin/Server/ffprobe.exe (WinError 5).

## Workflow

1. Scan the relevant library root recursively; inventory all folders and files (NUL-delimited find so spaces in names survive).
2. Classify each item: movie, TV show, season, extras, specials, sidecar (nfo/jpg/png), probe-failed/broken.
3. Resolve quality: ffprobe the first video stream of each video file; map resolution → tier.
4. Resolve IDs (TV shows only): look up TVDB IDs; verify ambiguous ones via websearch before writing.
5. Build the dry-run plan as a CSV (source, dest, kind, action, tvdb_id).
6. Dry-run: review counts and the full plan. ASK the user to commit — do not move files automatically.
7. Apply (move/rename files and folders).
8. Verify: re-count destinations, confirm no orphans; report skipped conflicts.
9. Write metadata: NFO files (if any) and .plexmatch hint files at the correct directory levels.
10. Refresh Plex: trigger a library rescan/scan in the Plex Web UI so the directory changes are picked up. Do not skip this step.

## NFO files (TV shows)

Plex's tvshow.nfo carries structured metadata. When writing one by hand, include at minimum:

- <tvshow … title="…" .../> with the show title, year, TVDB ID (tvdbid="…"), and key attributes.
- <set> elements for genres, ratings, studio, tags.
- Encoded XML; well-formed is required.

Place tvshow.nfo in the show folder (e.g. T:\Media\TV\#\The 100 (2014)\The 100 (2014) tvshow.nfo). NFOs are sidecars: they carry no quality tag and must not be forced into a quality tier. On rescan, Plex merges NFO metadata with its own library item.

## .plexmatch match hinting

A .plexmatch file in a series or season directory overrides Plex's matching for that directory:

- title / show: override the series title for matching (not the directory name).
- season: set the season number (used in a season directory; overrides the directory name).
- year: set the series release year.
- tvdbid, tmdbid, imdbid: override the numeric ID from TheTVDB, TMDB, or IMDb (overrides title/year hints and the directory name).
- guid: Plex URI-style GUID ([source]://[id]).
- pattern / pt: glob-style pattern with * wildcards and {curly braces} match tokens; at least one episode token required; earliest matching pattern wins.
- Episode hints: episode or ep — value simpleEpisodeNumber: filename; formats SP[X], E[X], [X].
- Blank lines, whitespace-only lines, and # comment lines are ignored.

Example in a directory named CoolShowSecondSeason that actually contains season 2 of Cool Show:

Title: Cool Show
Year: 2018
Season: 2

## ID application order

1. Determine media type: TV show → TVDB preferred; movie → TMDB preferred.
2. Write the ID into mapping_fixes.csv via tvdb-metadata-lookup (TV) or a TMDB/IMDb lookup (movie), verifying ambiguous rows via websearch first.
3. Reference the confirmed ID in the dry-run plan (column: tvdb_id). For movies, store the chosen TMDB/IMDb ID in the plan's note column.
4. Output the Plex library's final structure using the quality/tag conventions below.

## Output conventions (combined with naming skill)

### Movie library (M:\MOVIES\AG)

- Movie folder: Movie Name (Year) (Quality) — e.g. The CROW (1994) (720p).
- Movie file: MovieName (release year).ext — year required to disambiguate.
- Multiple parts: MovieName (year) - ptX.ext.
- Multiple versions: MovieName (year) - ArbitraryText.ext.
- Multiple editions: MovieName (year) {edition-Name}.ext (Plex Pass).
- Poster: MovieName (Release Date).ext or Movie/MovieName (Release Date)/Custom_Poster_Name.ext.
- Fanart: MovieName (Release Date)-fanart.ext.
- Trailers/extras: inline in same movie folder, or subdirectory (Trailers/, Behind the Scenes/).

### TV library (T:\Media\TV)

- Show folder (no quality, single TVDB ID): #\Show Name (Year) {TVDB-XXXXX}.
- Season folder (show name + year + quality + season): #\Show Name (Year)\Show Name (Year)(Quality) Season XX.
- Episode file: #\Show Name (Year)\Show Name (Year)(Quality) Season XX\Show Name (Year)(Quality)S<S>E<E>.<TitleWithSpaces>.<ext>.
- Sidecar: <Show Name> (<Year>) tvshow.nfo, <Show Name> (<Year>) clearlogo.png.
- Extras/Specials: Extras/, Specials/ folders, no ID needed.
- Probe-failed: move to the broken/ quarantine subfolder within the library root; these get no quality tag and no TVDB ID.
- Numeric/leading-number collections: keep in #; never promote to a letter bucket.
- Season count = number of distinct season folders OR number of distinct seasons in the 4-digit episode map, whichever is present.

## Quality-tag conformance (movie folders)

A movie folder name must match ^.+s*(SD|720p|1080p|1440p|2160p)s*$: title, 4-digit year, valid quality tag, nothing trailing. Failures to audit: brackets, trailing counters (2)/(3), empty parens (), dotted titles, all-caps titles, missing year, double spaces. Normalize legacy bracket tags [SD] to parens, strip release-group junk, collapse dotted titles to spaces, and never force a quality tag onto sidecars (.nfo/.jpg/.png).

## Archive and reconcile

- Verify totals after every change: re-scan the destination root and confirm per-folder counts match the plan; report skipped conflicts.
- Probe-failed quarantine: probe-failure folders move to a broken/ subfolder within the library root; they are not normal content and are not reorganized normally.
- After any major library change (show additions, quality retags, TVDB ID updates): re-run the plan workflow — rebuild the dry-run CSV, re-run the dry-run, review the plan, ask to commit, apply, then verify, then write metadata, then refresh Plex.

## Common pitfalls

- Mixing Movies/TV/Music in one Plex root → Plex warns and ignores files. Keep roots separate.
- Renaming instead of editing → creates new library items, losing watched status and metadata. Use Plex Web Edit UI for existing items.
- Skipping the refresh → directory changes are NOT picked up by Plex until you rescan the library.
- Deriving quality from folder tags instead of ffprobe → the user's correction: quality comes from the actual video stream resolution.
- Using TMDB/IMDb in a TV show folder → TV shows use only TVDB in the folder name; movies use TMDB/IMDb.
- Forcing a quality tag on sidecars → NFO, JPG, PNG, nfo files may legitimately lack a quality tag.
- Deleting alternate versions on collision → never delete; rename to avoid collision (append -alt or insert episode title).
- Path issues: native Windows tools need forward-slash paths; git-bash/MSYS can use /m/, /t/. Python cannot resolve MSYS mount points — use native Windows drive paths with forward slashes.
- Missing import sys in per-file scripts that read sys.stdin.
- NUL-delimited counting: -print0 output has no newlines; wc -l reads 0. Count entries another way.

## Related skills

- tv-show-organization — TV library organization, quality tags, TVDB mapping, scan-classify-probe-match-rename.
- media-library-organization — general media folder organization, dry-run moves first.
- file-naming-conventions — single source of truth for naming conventions.
- tvdb-metadata-lookup — TVDB IDs for show names.
- tv-show-database — building a show database.
