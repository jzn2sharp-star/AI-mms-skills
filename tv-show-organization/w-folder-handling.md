# W-folder handling (www.UIndex.org.* torrent folders)

Use this procedure when the TV library contains torrent download folders named with the `www.UIndex.org.` prefix (e.g., `www.UIndex.org.The.Bear.S05E04.1080p.HEVC`). These folders need to be renamed and classified, then TVDB IDs assigned.

## When to Use

- Rescanning `T:\Media\TV\W` (or whatever letter bucket contains UIndex torrent folders)
- Renaming `www.UIndex.org.*` folders to a clean show-name convention
- Extracting show name, SXX, EXX, quality from renamed folder names
- Assigning TVDB IDs to the renamed folders

## Procedure

1. **Scan for UIndex folders**: Use `os.listdir` or `os.walk` to find all folders starting with `www.UIndex.org.`. Count them.

2. **Dry-run naming**: For each folder, produce a table with:
   - Original folder name
   - Renamed folder name (after applying the rules below)
   - Extracted show name
   - SXX
   - EXX
   - Quality

3. **Apply rename rules** in this order:
   a. **Remove the `www.UIndex.org.` prefix entirely** (the dots in the prefix are NOT kept — the prefix is gone).
   b. **Remove ALL dots** from the remainder of the name.
   c. **Replace every space** (created by dot removal) with a space. Wait — no: the user's correction is "remove all dots replace with spaces". This means: remove all dots, and replace with spaces.
   d. **Preserve the year.** The year (e.g., `2023`, `2015`) must appear in the final show name. Do NOT remove the year.
   e. **Extract show name**, SXX, EXX, quality.

4. **Verification**: After renaming all folders on disk, rescan with `os.listdir` to confirm:
   - 0 folders still start with `www.UIndex.org.`
   - 0 remaining dots in any folder name
   - Year present in every show name

## Rename Rules (user corrections)

The following rules are user-mandated and non-negotiable:

- **DO NOT REMOVE THE YEAR!** — The year (e.g., `2023`, `2015`) must appear in the final folder name.
- **remove all dots replace with spaces** — All dots (except the UIndex.org. prefix which is removed entirely) are removed and replaced with spaces.

### Example transformations

| Original folder | Renamed folder |
|---|---|
| `www.UIndex.org.The.Bear.S05E04.1080p.HEVC` | `The Bear S05E04 1080p HEVC` |
| `www.UIndex.org.Doctor.Who.2023.S02E01.1080p.WEB` | `Doctor Who 2023 S02E01 1080p WEB` |
| `www.UIndex.org.The.Bear.S05E04.1080p.HEVC` | `The Bear S05E04 1080p HEVC` |

## Extraction

After renaming, extract:
- **Show name**: from the folder name (spaces replacing dots after the UIndex.org. prefix is removed)
- **SXX**: `S\d{2}E\d{2}` pattern (e.g., `S05E04`)
- **EXX**: `E\d{2}` pattern (e.g., `E04`)
- **Quality**: `NNNp` pattern (e.g., `1080p`, `720p`, `480p`, `2160p`, `HEVC`, `WEB`)

## TVDB ID assignment

1. Fuzzy-match the extracted show name against the TVDB search index (`api4.thetvdb.com/web/search/queries`).
2. Flag ambiguous matches for manual review (see `tvdb-metadata-lookup` skill).
3. Write TVDB IDs into the xlsx correction workbook.

## Verification Checklist

- [ ] Count of UIndex folders matches the dry-run count
- [ ] 0 folders still start with `www.UIndex.org.`
- [ ] 0 remaining dots in any folder name
- [ ] Year present in every renamed folder
- [ ] Show name, SXX, EXX, quality all extracted for each folder
- [ ] TVDB IDs written and verified
