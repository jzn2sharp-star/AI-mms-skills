# TV naming reference

Decision table for normalizing TV filenames and folder names, derived from a live library normalization pass (The.100, 2014). Ship the same rules to any TV library.

## Naming matrix

| Component | Type | Destination | Rule | Example |
|---|---|---|---|---|
| Video | `Title (Year)(Quality) SxxExx.ext` | season folder | SxxExx UPPERCASE; quality from tag/ffprobe | `The.100 (2014)(720p) S01E03.mp4` |
| Subtitle | `Show.Name(Year)(Quality) SxxExx.<language>.ext` | season folder | match episode from filename or parent folder; keep language tag | `The.100 (2014)(720p) S01E03.en.srt` |
| Subtitle numeric variant (2., 3., …) | same as above, keep variant suffix | season folder | do NOT collapse variants — use `…S01E01.2.English.srt` | `The.100 (2014)(720p) S01E01.2.English.srt` |
| NFO with episode | `Show.Name(Year)(Quality) SxxExx.nfo` | season folder | read episode from filename or parent folder | `The.100 (2014)(720p) S01E03.nfo` |
| NFO / txt / xml – season-level | `Show.Name(YEAR).season.N.nfo` | series folder | N taken from parent folder | `The.100(2014).season.1.nfo` |
| Artwork (`.jpg/.png`) | `Show.Name(YEAR).<original>` | series folder | no episode code; backup std/landscape/logo/posters/thumb/banner | `The.100(2014).logo.png` |
| Media-server metadata | `*.db` | skip | leave untouched | — |
| Windows cache | `Thumbs.db` | skip/delete | thumbnail cache, not media | — |

## SxxExx

- Must render UPPERCASE: `S01E03`, never `s01e03`.
- When a filename contains a lowercase `s01e03`, uppercase it in the new name without changing surrounding release tokens.
- If the episode marker is absent, fall back to the parent folder's SxxExx, then to the parent season number (`S01E00`).
- If no episode can be determined, use `S01E00` and leave a review flag.

## Season NFO

`season.nfo` belongs to the parent folder's season, not the series: route it to `Series (Year) Season.N` with `Show.Name(YEAR).season.N.nfo`, and default to `S01E00` when the season is unknown.

## Numeric collections / #, leading numbers

Collections whose names start with a digit stay under `#` (e.g. `11.22`, `12.Monkeys`); do not promote to a letter folder.

### In-place compact naming
When the user asks to keep release info in the name (compact form), use `Title(Year)(rest)` for BOTH folder and file, where `rest` is the original release/codec info after the year (e.g. `Apollo.13(1995)(720p.BluRay.x264.YIFY)`). Always include both parenthesised groups even when year or rest is missing — empty parens allowed (`02 (SD)`, never `02 ( )`). Keep the dots in `rest`; never drop trailing release tokens.

### Media-server metadata pitfall
Some .mkv/.mp4 files produced by packagers or downloaders contain an extra `bin_data` stream (codec `bin_data`) alongside video and audio. WMP/My Movies reads that track and can misidentify the file's title (e.g. "Babylon 5 Season 1" for Soul Hunter S01E02). Fix for WMP display: strip the data track when extracting a clean copy:
`ffmpeg -i in.mkv -map 0:v:0 -map 0:a:0 -c copy out.mkv`
Verify with `ffprobe -show_entries stream` — only 0:v and 0:a should remain. Do not rename or trim other streams.

## Folder structure convention (in-place, T:\Media\TV)

When organizing into the existing tree (no separate quality root):

```
T:\Media\TV\<Letter>\<Show Name> (<year>)\<Show Name> (<year>) (<quality>) Season N\<files>
```

- `<Letter>` = first letter of the show name (uppercase).
- `<Show Name> (<year>)` = series folder (no quality tag, no season number).
- `<Show Name> (<year>) (<quality>) Season N` = season folder (quality from ffprobe or filename, season from SxxExx).
- Empty folders and non-video content (INFO, Torrent) stay in `#` — do not promote.
- Numeric-leading collections stay in `#` (do not promote to a letter).

## Quality-split pair normalization (TV libraries)

Many TV libraries contain pairs of folders for the same show: one named `Show (Unknown)` (often empty or holding loose episodes) and one named `Show(Unknown)Quality` (holding season subdirs and/or loose episodes). Normalize them into `Show (Year)(Quality) Season XX` folders.

### Detection

- Group folders by show name: strip the `(Unknown)` token and quality suffix from the folder name. Folders sharing a show name form a quality-split pair.
- The `(Unknown)` folder is typically empty (0 videos, 0 subdirs) — verify with `os.listdir` before assuming. If it has content, treat its loose videos as an additional quality tier.
- The quality folder's name encodes the quality: `Show(Unknown)SD` → SD, `Show(Unknown)720p` → 720p, etc. Normalize `720` → `720p`, `1080` → `1080p`.

### Procedure

1. **Delete empty (Unknown) folders first.** Check `os.listdir` returns empty; if so, `os.rmdir` (or `.NET [IO.Directory]::Delete` with `\\?\` prefix for long paths). Do not delete non-empty ones without reviewing contents.
2. **Process the quality folder:**
   - **Season subdirs present** (e.g. `Season.1`, `season.4`, `1`, `2`): extract the season number with regex `[Ss]eason\.?(\d+)` or `^(\d+)$`, then `shutil.move` the whole subdir to `Show (Year)(Quality) Season NN` at the bucket level. Merge into an existing destination if it already exists (from loose videos).
   - **Loose videos only**: group by season using regex `S(\d+)E\d+` on the filename; create one `Show (Year)(Quality) Season NN` folder per season and move videos into it. Videos without an SxxExx marker default to Season 01.
   - **Both subdirs and loose videos**: process subdirs first, then loose videos into the corresponding season folders.
3. **Clean leftover non-video files** (Thumbs.db, .jpg, .nfo) from subdirs before removing them — delete junk files, move surviving sidecars into the season folder. Use `os.walk(topdown=False)` to handle nested junk.
4. **Remove empty source folders** after moving all content. Re-check emptiness immediately before deleting; a folder that became empty mid-pass is deletable next pass.
5. **Year resolution**: extract from show name if it contains a 4-digit year; otherwise use `Unknown`. Do not force a year — leave `Unknown` and flag for later lookup. Do not leave empty parens `()`.

### Long-path handling

- Folder names with very long srt filenames (>260 chars total path) raise `WinError 3` (`FileNotFoundError`) from `shutil.move`/`os.rename`. Prepend `\\?\` to both source and destination paths (e.g. `'\\\\?\\' + os.path.abspath(path)`) and retry. This bypasses MAX_PATH for move operations.
- `os.path.exists()` returns `False` for paths over 260 chars even when the file exists. Do not use it as a pre-move check on long paths; attempt the move and catch the exception instead.
- `os.listdir` can list long-path files but `os.path.getsize` raises `WinError 3` on them — catch and record 0.

### Leftover junk in subdirs

- Subdirs may contain `Thumbs.db` (Windows-locked, may fail to delete — skip and leave the subdir), `.jpg` thumbnails, and `.nfo` sidecars. Delete junk files silently; move surviving sidecars into the season folder; leave locked files and report them.
- Some subdirs are not season folders at all (`Subs`, `www.UIndex`, `Season.1` with leftover content) — skip them (no season number parseable) and handle their contents in a separate cleanup pass.

### Batch processing at scale

- Process all quality-split pairs in one script pass, not one show at a time. Group by show name, iterate sorted, and report per-show counts.
- Use `Unknown` as the year for all shows initially; years can be filled in later via web search or NFO. Do not block on year lookup during structural normalization.
- After processing, verify: count remaining non-season Unknown folders (should be 0), and spot-check a few season folders for correct video + srt counts.

## Dry-run CSV rule

A dry-run plan CSV must carry **full destination paths** (folder + new filename), not just the new filename. A destination column that contains only the new filename is unusable for commit — the commit script cannot resolve which folder to move into. Always write `os.path.join(folder, newname)` for the destination column.

## Bottom-up parsing (show name vs episode title)

When parsing a TV filename to derive the show name and episode title:

- If `SxxExx` is the **first** token (nothing before it), the show name is missing — resolve it from the file's container title tag (ffprobe `format_tags.title`), stripping season/disc suffixes (e.g. `BABYLON 5 SEASON 2 DISC 1` → `Babylon 5`).
- If text precedes `SxxExx`, that text is the show name (strip year and release tags).
- Text after `SxxExx` is the episode title (strip release tags and parenthesized quality like `(480p)`).
- Process files first, then apply missing show info to the parent folder — never the reverse, or folder-level info is lost.

## General conventions

- Always include BOTH parenthesized groups (never empty `()`), keep dots in `rest`, never drop trailing release tokens.
- Keep original file names as-is during folder normalization unless the user explicitly asks to rename files.
- Rearrange only when the user asks; it multiplies collision risk, so dry-run the rename plan and get approval first.
