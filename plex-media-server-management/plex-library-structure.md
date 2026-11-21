# Plex Library Structure Reference

## Root separation (mandatory)

Keep Movies, TV, and Music in separate roots. Plex warns and ignores files when mixed in one library root.

| Content | Library root |
|---|---|
| Movies | `M:\MOVIES\AG` (and movie quality roots) |
| TV shows | `T:\Media\TV` |
| Music | Separate root (not used on this machine) |

## Folder conventions (combined with naming skill)

### Movie library (M:\MOVIES\AG)

- **Movie folder**: `Movie Name (Year) (Quality)` — e.g. `The CROW (1994) (720p)`.
- **Movie file**: `MovieName (release year).ext` — year required to disambiguate.
- **Multiple parts**: `MovieName (year) - ptX.ext`.
- **Multiple versions**: `MovieName (year) - ArbitraryText.ext`.
- **Multiple editions**: `MovieName (year) {edition-Name}.ext` (Plex Pass).
- **Poster**: `MovieName (Release Date).ext` or `Movie/MovieName (Release Date)/Custom_Poster_Name.ext`.
- **Fanart**: `MovieName (Release Date)-fanart.ext`.
- **Trailers/extras**: inline in same movie folder, or subdirectory (`Trailers/`, `Behind the Scenes/`).

### TV library (T:\Media\TV)

- **Show folder** (no quality, single TVDB ID): `#\Show Name (Year) {TVDB-XXXXX}`.
- **Season folder** (show name + year + quality + season): `#\Show Name (Year)\Show Name (Year)(Quality) Season XX`.
- **Episode file**: `#\Show Name (Year)\Show Name (Year)(Quality) Season XX\Show Name (Year)(Quality)S<S>E<E>.<TitleWithSpaces>.<ext>`.
- **Sidecar**: `<Show Name> (<Year>) tvshow.nfo`, `<Show Name> (<Year>) clearlogo.png`.
- **Extras/Specials**: `Extras/`, `Specials/` folders, no ID needed.
- **Probe-failed**: move to `broken/` quarantine subfolder within the library root.
- **Numeric/leading-number collections**: keep in `#`; never promote to a letter bucket.
- **Season count**: number of distinct season folders OR number of distinct seasons in the 4-digit episode map, whichever is present.

## Quality-tag conformance (movie folders)

A movie folder name must match `^.+\s*\(\d{4}\)\s*\((SD|720p|1080p|1440p|2160p)\)\s*$`: title, 4-digit year, valid quality tag, nothing trailing. Failures to audit: brackets, trailing counters `(2)`/`(3)`, empty parens `()`, dotted titles, all-caps titles, missing year, double spaces. Normalize legacy bracket tags `[SD]` to parens, strip release-group junk, collapse dotted titles to spaces, and never force a quality tag onto sidecars (.nfo/.jpg/.png).
