# Plex Media Server — ID Priority Reference

## ID Priority (per media type)

| Media type | Priority | Preferred |
|---|---|---|
| TV shows | TVDB → TMDB → IMDb | TVDB |
| Movies | TMDB → IMDb → TVDB | TMDB |

## Rules

- The first ID found in the NFO (or web) wins.
- A show that is both a movie and a TV show uses the type that applies to the item.
- TV shows use only TVDB in the folder name; movies use TMDB/IMDb.
- Do not invent an ID — verify ambiguous rows via websearch first.
- Reference confirmed IDs in the dry-run plan (column: `tvdb_id`). For movies, store the chosen TMDB/IMDb ID in the plan's note column.

## Verification workflow

1. Determine media type: TV show → TVDB preferred; movie → TMDB preferred.
2. Write the ID into `mapping_fixes.csv` via `tvdb-metadata-lookup` (TV) or a TMDB/IMDb lookup (movie), verifying ambiguous rows via websearch first.
3. Reference the confirmed ID in the dry-run plan (column: `tvdb_id`).
4. Output the final structure using the quality/tag conventions in `SKILL.md`.

## Common mistakes

- Using TMDB/IMDb in a TV show folder → TV shows use only TVDB.
- Inventing an ID → always verify.
- Not verifying ambiguous rows → verify via websearch before writing.