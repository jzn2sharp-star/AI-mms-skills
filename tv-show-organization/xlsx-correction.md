# XLSX correction workflow

Use this procedure when auditing and correcting a TVDB mapping workbook (`shows_needing_correction.xlsx`) that contains show/folder mismatch entries.

## Sheets in the workbook

| Sheet | Rows | Purpose |
|---|---|---|
| `shows_to_fix` | 88 | Shows that need TVDB ID correction |
| `Wrong show (fix ID)` | 300 | Wrong-show-folder entries needing correct TVDB ID |
| `Year conflicts` | 24 | Shows with year labeling conflicts |
| `No ID` | 9 | Shows with no TVDB ID |
| `Tag conflict` | 1 | Show with conflicting tag and mapping |

## Procedure

1. **Load the workbook** with openpyxl (read with `read_only=False` for write access).

2. **Classify**: Parse the export. Classify each row as:
   - Real show (needs TVDB ID)
   - Subtitle/metadata/season-stub (skip)
   - Torrent/channel/collection (skip)
   - Generic `?` folder (skip)

3. **Group rows by actual show.** Dedupe same-series entries (e.g., `Xena Warrior Princess` + `Xena Warrior Princess S01` → one family).

4. **Fill TVDB IDs**: Use the IDs you verified; never invent an ID. Mark unverified rows as `verify`.

5. **Write TVDB IDs** into the appropriate column:
   - `shows_to_fix` → column I (Correct TVDB ID)
   - `Wrong show (fix ID)` → column F (Correct TVDB ID / Mapped)

6. **Separate non-mapping issues** into their own buckets:
   - `no-id`: no series TVDB ID — do not invent
   - `year_conflicts`: labeling issue — do not rewrite IDs
   - `tag_conflicts`: ID must match the folder's existing tag

7. **Verify totals**: the count of filled rows should match the number of shows you resolved via TVDB lookup.

8. **Re-read the file** to confirm the write succeeded. Check that the written values are correct.

## Comprehensive audit
Use when the user says "check for all errors missing info", "work all corrections", or similar audit requests.

1. **Load the workbook** with openpyxl (read with `read_only=False` for write access).
2. **Classify each row** in every sheet: real show, subtitle/metadata/season-stub, torrent/channel/collection, generic `?` folder.
3. **Group rows by actual show.** Dedupe same-series entries (e.g., `Xena Warrior Princess` + `Xena Warrior Princess S01` → one family).
4. **Fill TVDB IDs**: use the IDs you verified; never invent an ID. Mark unverified rows as `verify`.
5. **Write TVDB IDs** into the appropriate column:
   - `shows_to_fix` → column I (Correct TVDB ID)
   - `Wrong show (fix ID)` → column F (Correct TVDB ID / Mapped)
6. **Separate non-mapping issues** into their own buckets:
   - `no-id`: no series TVDB ID — do not invent
   - `year_conflicts`: labeling issue — do not rewrite IDs
   - `tag_conflicts`: ID must match the folder's existing tag
7. **Verify totals**: the count of filled rows should match the number of shows you resolved via TVDB lookup.
8. **Re-read the file** to confirm the write succeeded. Check that the written values are correct.

## User corrections on naming (verbatim)
- **Preserve the year**: "DO NOT REMOVE THE YEAR!!" — never remove the year.
- **Remove all dots, replace with spaces**: "remove all dots replace with spaces" — remove all dots, replace with spaces.

## Show name corrections
When the mapping provides a correct show name:
- Use the mapped show name (e.g., `WW` → `What We Do in the Shadows`).
- Write the correct show name into the `Correct show name` column.
- User may correct show names (e.g., `SSGB` → `SS-GB`). Apply the correction.
- User may correct TVDB IDs (e.g., `A.P. Bio` → `A P Bio (2018) {TVDB-328534}`). Apply the correction.

## Show name corrections (verified from audit)
When the mapping provides a correct show name or TVDB ID:
- Use the mapped show name (e.g., `WW` → `What We Do in the Shadows`).
- Write the correct show name into the `Correct show name` column.
- User may correct show names (e.g., `SSGB` → `SS-GB`). Apply the correction.
- User may correct TVDB IDs (e.g., `A.P. Bio` → `A P Bio (2018) {TVDB-328534}`). Apply the correction.
