# AI-mms-skills

Reusable skills for organizing, naming, and managing a personal media library
(movies, TV shows) that feeds a Plex or Jellyfin server. It also covers
TVDB metadata lookup.

## Skills

| Skill | What it covers |
| --- | --- |
| `plex-media-server-management` | Administering a Plex server: library roots, NFO files, `.plexmatch` match hinting, ID priority (TVDB/TMDB/IMDb), edition-vs-version, renaming warnings, the scan/refresh cycle. |
| `media-library-organization` | Organizing movie, TV, and anime media folders: naming rules, dry-run moves first, quality tagging from actual ffprobe streams, flattening/from-variant. |
| `tv-show-organization` | TV library organization: naming conventions, TVDB mapping, quality tags, batching, probe-failed quarantining, subtitle pairing, the plan/apply workflow. |
| `tv-show-database` | Building a structured TV-show database (SQLite/JSON/CSV) from a TV library: name/year/TVDB ID/season/episode counts, content-type classification, batch TVDB updates, conflict detection. |
| `tvdb-metadata-lookup` | Look up TheTVDB series IDs by show name when you do not have a registered API key (web_search method, plus fallback API). |

## Conventions the skills assume

- **Naming** is a single source of truth in `file-naming-conventions`.
- **Movie library root:** `M:\MOVIES\AG` (with `A` and `B` sub-trees).
- **TV library root:** `T:\Media\TV` (shorthand `T:\TV`).
- **Movie folders:** `Movie Name (Year) (Quality)` with quality tags `[SD]`, `[720p]`, `[1080p]`, `[1440p]`, `[2160p]`.
- **TV shows:** `Title (Year) {TVDB-XXXXX}` at show level; season folders carry the quality tag; episodes carry `S<S>E<E>`.
- **Probe-failed** folders go to `broken/` under the library root; they get no quality tag and no TVDB ID.
- **Numeric/leading-number collections** stay in the `#` bucket; they are never promoted to a letter.

## How to use these skills

Skills are used by the Hermes Agent. Place them under the Hermes skills tree:

```
~/.hermes/skills/<category>/<skill-name>/SKILL.md
```

Categories used here: `media`, `tv-show-organization`, `tvdb-metadata-lookup`.

## Requirements

- Windows 11 (host of the library).
- `ffprobe` (Jellyfin's `C:\Program Files\Jellyfin\Server\ffprobe.exe`) for quality probing.
- `Plex Media Server` (for the Plex-management skill) or `Jellyfin`.
- git (to clone this repo).

## Repository layout

```
.
├── README.md
├── plex-media-server-management/   # SKILL.md + references (edition/version, id-priority, nfo, plexmatch, refresh, structure)
├── media-library-organization/     # SKILL.md + references + probe scripts
├── tv-show-database/               # SKILL.md + references
├── tv-show-organization/           # SKILL.md + references + scripts
└── tvdb-metadata-lookup/           # SKILL.md + references
```
