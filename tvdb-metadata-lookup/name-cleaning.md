# name-cleaning (clean_for_search)

Turn a messy library show name into a short canonical query for the TVDB search endpoint.

## Rule
Strip noise, keep the title. Quality tags, parenthetical years, file artifacts, collection and subtitle markers disappear; the actual title stays.

## Apply in order
1. Strip bracketed quality tags: `\[[^\]]*\]`
2. Strip parenthetical years: `[^)]*`
3. Strip quality resolutions: `1080p`, `720p`, `480p`, `3d` (`\b\d{3,4}p\b`)
4. Strip file artifacts: `x264`, `x265`, `x255`, `BluRay`, `Bluray`, `WEBRip`, `WEBDL`, `HDTV`, `Greek Subs`, `DVDRip`, `AAC`, `DTS`, `REPACK`
5. Strip collection markers: `Complete Series`, `Season N`, `S01`, `S12`
6. Strip network keywords: `BBC`, `TV`
7. Replace whole-word `and` with `&`.
8. Convert single letters separated by spaces to dots: `A P Bio` -> `A.P.Bio`.
9. Collapse repeated whitespace, trim.

## Examples

| Library name | Cleaned query |
|---|---|
| `13 Reasons Why [SD]` | `13 Reasons Why` |
| `3 Body Problem 2024 [1080p]` | `3 Body Problem` |
| `Agents of SHIELD Slingshot` | `Agents of SHIELD Slingshot` |
| `A P Bio` | `A.P.Bio` |
| `Castle 2009 (2009)` | `Castle 2009` |
| `Dune 2000 1080p Bluray x255 Greek Subs` | `Dune 2000` |
| `Hitch Hikers Guide to the Galaxy BBC` | `Hitch Hikers Guide to the Galaxy` |
| `DARK MATTER 20152017 Complete TV Series Season 123 S01S03 720p WebDL x264` | `DARK MATTER` |
