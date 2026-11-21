## Catalog comparison (folder vs. a years_found.txt-style catalog)

Use this procedure when you are asked to compare a directory's contents against a catalog file (e.g. `years_found.txt`) and decide what to keep or move.

### Procedure

1. **Inventory both sides.** Count folders and files in the directory; count entries in the catalog. Print both counts.
2. **Normalize titles.** For each catalog entry, take the text before `|` (year). For each folder, take the text before the first `(`. Lowercase, collapse whitespace, strip quality tokens (`[SD]`, `(SD)`, `(720p)`, etc.).
3. **Match.** A catalog title matches a folder when the normalized titles are equal, OR one is a substring of the other (record both). Do NOT substring-match substrings of different lengths unless the shorter title is clearly a core title (e.g. "The Empire" ⊂ "The Empire (Unknown)(1080p)").
4. **Classify.** A catalog entry with a matching folder = KEEP (it is cataloged). A catalog entry with no matching folder = move to quarantine (e.g. `doublebroken`). A folder with no matching catalog entry = the item stays in the folder unless the user says otherwise.
5. **Report.** Give the exact counts: total folders, total catalog entries, matched count, unmatched (keep) count, unmatched (move) count. State which specific folders to move and which to keep. Do not guess; re-query disk for the final list.
6. **Commit only after user approval.** Present the move list; do not move until the user says so (consistent with dry-run discipline).

### Pitfalls

- The user's stated number of items to move may not match the verified folder count on disk. Always re-derive the exact count from `os.listdir` (or `dir`) and report the verified number, not the user's estimate.
- Titles with bracket quality suffixes (`[SD]`) in the catalog must still match folders with parenthesized quality (`(SD)`) after normalization — do not let the bracket/paren difference break the match.
- A title that is a substring of a folder name is not always a true match. E.g. "Orpheus" ⊂ "Orpheus and Eurydice" — confirm the shorter title is a real core title before counting it as a match.
- Digimon/Movie featurettes and similar screens may have no folder in the directory at all — report them, do not invent a move.
