# TV Show Organization — Bug Check & Audit

## CSV Audit and Bug Check

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

## Examples

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
