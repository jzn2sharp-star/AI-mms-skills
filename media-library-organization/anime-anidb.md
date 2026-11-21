# Anime library organization with AniDB tooling

Depth for the anime root `S:\Media\Anime` and any other anime tree. Always-on rules and the workflow live in SKILL.md; this file is the tool/command reference.

## Choosing a tool

| Tool | Language / OS | Role | Notes |
|---|---|---|---|
| `anipyrenamer` | Python >=3.13, Windows-tested | ED2K hash -> AniDB UDP lookup -> rename in place or into a destination tree | Best fit for a bulk reorganization: `--dry-run`, ledger, conflict policy, naming templates, SQLite cache, `--offline` reruns |
| `anidb-mv` (`amv`) | Python >=3.10 | Moves files and registers them at AniDB / MyList | MyList and file registration, not a renamer |
| `anidbcli` | Python 3.6+ | ED2K hash + API rename by format string; MyList | Older; no dry-run ledger |
| `adbren` | Perl | In-place rename by format string | Renames in the same directory only |
| `yumemi` | Python >=3.9, Windows | ED2K hash -> MyList add -> optional in-place rename | Explicit file paths only (no recursion, no dry-run); prompts for credentials |

Most other entries on the AniDB software list are Linux/Docker-only (shisho, animanager, aniupdate, anime-helper.sh) or mobile players; `cisqua` is a Ruby+Redis web app whose renamer hardcodes romaji names. Kometa is a Plex metadata/collection tool and is installed on this machine — see `references/plex-metadata-kometa.md`. This host runs both Plex (`127.0.0.1:32400`) and Jellyfin.

## Install (anipyrenamer)

```bash
cd "M:/scripts/Anidb downloads/anipyrenamer"
python3 -m venv .venv                                   # bundled python3 = 3.14; the tool needs >=3.13
./.venv/Scripts/python.exe -m pip install -e .
./.venv/Scripts/anipyrenamer.exe --doctor
```

`--doctor` checks `.env` discovery, credentials, cache dir, and AniDB reachability (`300 PONG`). The system Python on this host is 3.12, below the tool's floor — invoke the bundled 3.14 interpreter, not `python`.

## Configuration

`%APPDATA%\anipyrenamer\.env` (a project-root `.env` is also read):

```
ANIDB_USERNAME=
ANIDB_PASSWORD=
ANIDB_API_KEY=          # optional; enables AES-128 UDP encryption
ANIDB_UDP_CLIENT=anipyrenamer
ANIDB_UDP_CLIENTVER=1
ANIDB_LOCAL_PORT=0
```

The client name/version must be registered on anidb.net (Settings -> Account). Never ask for or accept the password in chat — create the file with blank credentials and have the user fill it in an editor.

## Commands

| Goal | Command |
|---|---|
| Preview | `anipyrenamer "<path>" --dry-run` |
| Apply | `anipyrenamer "<path>" --yes` |
| Plex/ASS folders | `anipyrenamer "<path>" --plex` (implies `--folder`) |
| Into a new tree | `anipyrenamer "<path>" -d "D:/Anime" -t "%title% S01E%epno%%ext%"` |
| Series folder rename | `--folder` / `--folder-template` |
| Cache only | `--offline` |
| Conflict policy | `--on-conflict skip\|suffix\|fail` (default `skip`) |
| Plan as JSON | `--preview-format json` |

Default file template: `%title% %epno%%fileversion% - %eptitle% [%group%]%ext%`.
Default folder template: `%title% [%group%]%ext%`.

## yumemi (MyList add + in-place rename)

```bash
uv tool install yumemi          # -> %USERPROFILE%\.local\bin\yumemi.exe
```

`yumemi` needs LibRHash. On Windows the MSYS2 package `mingw-w64-x86_64-rhash` provides `librhash.dll`; put it (with `libintl-8.dll` and `libasprintf-0.dll` from `mingw-w64-x86_64-gettext-runtime`) in one folder, e.g. `C:\Users\Owner\tools\libs`.

**Pitfall — CPython 3.8+ does not search PATH for a bare DLL name.** `ctypes.CDLL("librhash.dll")` raises `Could not find module ... (or one of its dependencies)` even with the DLL's folder on PATH, and even with the DLL sitting next to `python.exe`; loading by full path works. Register the folder at interpreter startup instead — drop a `sitecustomize.py` into the tool env's `Lib/site-packages`:

```python
import os
os.add_dll_directory(r"C:\Users\Owner\tools\libs")
```

Verify: `yumemi --ping` (AniDB reachable) and cross-check one ED2K against anipyrenamer's `compute_ed2k` — they must match exactly.

Commands: `yumemi -u USER -p PASS FILE [FILE...]` (prompts for credentials; never type them for the user). `-R/--rename-format` (default `$aname - $epno`), `-w`/`-W` watched state, `-d` deleted, `-e` edit existing MyList entries. The CLI takes no directories — build the file list yourself (`find ... -print0 | xargs -0 ...`).

## Naming target

Decide with the user before planning a bulk run:

- `--plex`: `Title [anidb-<aid>]\Title - 01 - Episode Name [Group].ext` — no season-based numbering.
- TV-library shape: `Show Name (Year){id}\Season XX\` to match `T:\Media\TV`.

## Rate limits

AniDB UDP enforces flood protection: one packet per 2 s after the first five, ~1 per 4 s sustained. Large libraries are long runs. A `555 BANNED` means stop sending (including LOGOUT); a bare timeout is ambiguous — retry with backoff, never treat it as a ban. Rerun with `--offline` once the cache is warm.

## Pitfalls

- `--plex` does not support season-based numbering — do not combine it with a season layout.
- Files absent from AniDB become SKIP rows; warm the cache with one online run before reading a large skip count as a failure.
- `--folder` renames the direct parent folder; never point it at an A-Z bucket or a `.Collections` folder.
- Never overwrite on conflict; default `--on-conflict=skip` and review the skipped set.
