# Plex metadata & collections with Kometa

Kometa edits Plex metadata, collections, playlists and overlays. It does NOT rename or move files — it is not a file organizer. This host runs Plex Media Server (listening on `127.0.0.1:32400`) alongside Jellyfin, and the Plex libraries point at the same media roots as the file libraries.

## Install

`uv` is the package manager (`%USERPROFILE%\.local\bin\uv.exe`). Checkout and sync:

```bash
cd C:/Users/Owner
git clone --depth 1 https://github.com/Kometa-Team/Kometa
cd Kometa
uv sync
uv run python kometa.py --run      # first run writes config/config.yml
```

**Pitfall — uv cannot spawn the git that ships inside the Hermes app payload.** Paths under `C:\Program Files\WindowsApps\NousResearchInc.HermesAgent_*\` are denied to a native `CreateProcess`, so `uv sync` fails with `Access is denied (os error 5)` while cloning a git dependency (e.g. `serializd-py`). Copy the portable git tree to a normal directory (`C:\Users\Owner\tools\git-portable`) and run uv with BOTH `usr\bin` and `mingw64\bin` on PATH — `usr\bin` is required because git spawns `sh.exe` from it.

## Configure

`config/config.yml` must use the exact Plex library names. List them from the running server:

```bash
curl -s "http://127.0.0.1:32400/library/sections?X-Plex-Token=$TOK"
```

The token lives in `%LOCALAPPDATA%\Plex\Plex Media Server\Preferences.xml` as `PlexOnlineToken` — note the extra `Plex\` path level. `tmdb.apikey` must hold a TMDb **v3** key; Kometa checks TMDb before Plex, so a blank key stops the run before any Plex call.

Write the token into the config by substitution and verify the field length — do not `cat` the file afterwards, the secret lands in the transcript.

## Verify

```bash
uv run python kometa.py --validate --no-source-integrity
```

`--validate` reports one structure warning per empty library, which is expected.

## Notes

- Defaults are enabled one line at a time (`collection_files: - default: universe`). Overlays render an image per movie/show/season/episode into `asset_directory` — slow and image-heavy; prefer a collections-only first pass.
- `collection_mode: hide` (used in the wiki sample) hides collections from the Plex library tab.
- Kometa's AniDB module can build anime collections; the file renamers in `references/anime-anidb.md` are separate tools.
