# Plex NFO Files Reference

## tvshow.nfo structure (TV shows)

Place `tvshow.nfo` in the show folder. It carries Plex's advanced metadata (genres, ratings, tags, the show's ID). XML must be well-formed.

### Required elements

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tvshow>
  <title>Show Name</title>
  <year>2024</year>
  <season>1</season>
  <episode>1</episode>
  <tvshow-title>Show Name</tvshow-title>
  <network>Network</network>
  <premiered>2024-01-01</premiered>
  <rating>8.5</rating>
  <genre>Drama</genre>
  <studio>Studio</studio>
  <tag>tag1</tag>
  <tag>tag2</tag>
  <tvdbid>123456</tvdbid>
  <imdbid>tt1234567</imdbid>
  <plot>Description</plot>
  <plot>Extended description</plot>
  <duration>3600</duration>
  <mpaa>TV-14</mpaa>
  <originallyavailable>2024-01-01</originallyavailable>
  <season>0</season>
  <episode>0</episode>
</tvshow>
```

## Placement

- Show-level NFO: `Show Name (Year)/tvshow.nfo` (TV library) or `Movie Name (Year)/tvshow.nfo` (movie library, optional).
- Season-level NFO: `Show Name (Year)/Season 01/tvshow.nfo` (optional, for season-specific metadata).

## NFO rules

- NFOs are sidecars: they carry no quality tag and must not be forced into a quality tier.
- On rescan, Plex merges NFO metadata with its own library item.
- NFOs are read by Plex on library scan; after writing/editing, trigger a library rescan/refresh.
- Well-formed XML is required. `<tvshow>` root with child elements as above.
- `tvdbid` and `imdbid` override ID hints and directory name.
