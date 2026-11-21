# Plex Edition vs Version Reference

## Edition vs Version

| Concept | Definition | Plex handling |
|---|---|---|
| Version | Same release, different resolution/encoding (1080p vs 2160p, HEVC vs H.264) | Merged automatically into one item with "Other Versions" section |
| Edition | Different releases/cuts (Theatrical, Director's Cut, Extended, Unrated, 2D vs 3D) | Each edition is its own item, tracked separately for watched status, ratings, metadata |

## Requires

- **Versions**: no Plex Pass required (auto-merged).
- **Editions**: Plex Pass required for Server admin account.

## File naming

### Versions (file naming)

`MovieName (year) - ArbitraryText.ext` — e.g. `Pulp Fiction (1994) - 1080p.mkv` and `Pulp Fiction (1994) - SD.m4v` collapse to one item. All parts share resolution/encoding format and audio/subs in same order.

### Editions (file naming)

- Movie: append `{edition-Name}` to the movie file: `Blade Runner (1982) {edition-Director's Cut}.mp4`.
- TV: add `{edition-Edition Title}` to the end of the show folder name: `/TV Shows /Babylon 5 (1994) /Season 01 /Babylon 5 (1994) {edition-Bluray Remaster} /Season 01`.

## Movie editions

1. Requires Plex Pass for Server admin account.
2. Editions = different cuts of the same movie (Theatrical, Director's Cut, Extended, Unrated, etc.).
3. Each edition tracked separately — watched status, ratings, and metadata per-edition.
4. View in Plex Web (Admin → Library → …).

## TV editions

1. Requires Plex Pass for Server admin account.
2. Editions = different releases of a TV show as a whole (color vs B&W, different episode counts/orders, aspect ratios).
3. Each edition tracked separately — watched status, ratings, and metadata per-edition.
4. Watch state syncing: editions are NOT included in syncing of watch state/ratings.
5. Client support: Plex Web (4.160), iOS/Android (2026.13.0); Roku support coming.

## Renaming warning

- Renaming an existing file/folder creates a new library item after the next scan.
- Watched status and custom metadata are NOT carried over.
- Prefer the "Edit" method for existing items.
