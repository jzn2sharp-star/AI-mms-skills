# Plex .plexmatch Files Reference

## File format

A `.plexmatch` file is a line-delimited text file named exactly `.plexmatch`, placed in a series or season directory. It overrides Plex's matching for that directory.

### Comment and blank lines

- Blank lines, whitespace-only lines, and lines starting with `#` (after whitespace) are ignored.
- Whitespace around hint names/values is ignored; hint names are case-insensitive.

### Hint types

| Hint | Scope | Description |
|---|---|---|
| `title` / `show` | series | Override the series title for matching (not the directory name) |
| `season` | season | Set the season number (used in a season directory; overrides directory name) |
| `year` | series | Set the series release year |
| `tvdbid` | series | Override the TVDB numeric ID |
| `tmdbid` | series | Override the TMDB numeric ID |
| `imdbid` | series | Override the IMDb ID |
| `guid` | series | Plex URI-style GUID (`[source]://[id]`) |
| `pattern` / `pt` | episode | Glob-style pattern with `*` wildcards and `{curly braces}` match tokens |
| `episode` / `ep` | episode | Individual episode hint: `simpleEpisodeNumber: filename`; formats `SP[X]`, `E[X]`, `[X]` |

### Pattern matching

- Plex 1.30.0+ supports `pattern` / `pt` with `*` wildcards and `{curly braces}` match tokens.
- Match tokens: `s`/`se`/`season` (season), `e`/`ep`/`episode` (episode), `sp`/`special` (special in season 0), `see` (combined season-episode).
- Supports validity ranges `[start]-[end]`, offsets `+[offset]` / `-[offset]`, and maximum lengths `l[length]`.
- At least one episode token is required per pattern; the earliest matching pattern wins.

### Example

```
# Directory contains season 2 of Cool Show
Title: Cool Show
Year: 2018
Season: 2
```

## Placement

- Top-level `.plexmatch` in a series directory affects all subdirectories.
- Season-level `.plexmatch` in a season directory affects only that season.
- Most libraries do not need `.plexmatch`; use it to fix mis-matches.
