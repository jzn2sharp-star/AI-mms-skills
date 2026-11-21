# Non-English subtitle cleanup

Use this procedure when the user asks to delete non-English subtitle files from a media library.

## When to Use

- User says "delete non-English subtitles" or "remove non-English subtitle files"
- The TV library contains subtitle files in multiple languages

## File extensions to scan

`.srt`, `.ssa`, `.ass`, `.sub`, `.idx`, `.vtt`, `.smi`, `.sup`, `.psb`

**Do NOT include** `.txt` files (these are torrent descriptions, readme files, etc., not subtitles).

## Language classification

A subtitle is classified as **English** if its filename contains:
- `english` (case-insensitive)
- `eng` (e.g., `S06E04.en.srt`)
- `enhi` (English High Importance)
- `en-` or `en_` prefixes (e.g., `en-US`, `en_GB`, `en-AU`)
- Or the extracted language code is `en`

A subtitle is classified as **non-English** if:
- Its language code is a known non-English code (`fi`, `sv`, `de`, `fr`, `es`, `it`, `pt`, `ru`, `zh`, `ja`, `ko`, `ar`, `he`, `nl`, `pl`, `tr`, `cs`, `da`, `el`, `hu`, `no`, `ro`, `th`, `vi`, `id`, `ms`, `be`, `hr`, `uk`, etc.)

A subtitle is **unknown** (needs manual review) if:
- No language code is present in the filename
- The filename doesn't contain English markers

## Procedure

1. **Scan** the library root recursively for subtitle files (use `find . -type f -iname '*.srt' -o ...` or Python `os.walk`).
2. **Classify** each file by extracting the language code from the filename (the last dot-delimited part). Non-English language codes are: `fi sv de fr es it pt ru zh ja ko ar he nl pl tr cs da el hu no ro th vi id ms be hr uk`.
3. **Decide** which files to delete:
   - Delete all files classified as non-English per the rules above.
   - For "unknown" files (no language code), ask the user or apply a conservative rule (delete only if the filename contains a non-English language name like `Finnish`, `Spanish`, `Arabic`, etc.).
4. **Delete** the selected files using `os.remove()`.
5. **Verify** by rescanning: count original files (5,601), count remaining (924), verify deleted = 4,677.

## Pitfalls

- **Do not include `.txt` files** — these are torrent descriptions and readme files, not subtitles.
- **Language codes vary**: some files use 2-letter codes (fi=Finnish, sv=Swedish), some use full names (Finnish, Spanish). Extract both forms.
- **English markers vary**: `en`, `eng`, `english` all indicate English. `enhi` = English High Importance.
- **Path length errors**: Windows path length limit (260 chars) can cause `WinError 3` on delete. Files in folders with very long names may fail.
- **Verify counts**: original count = remaining + deleted. The sum must equal the original on-disk total.
