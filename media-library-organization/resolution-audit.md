# Resolution audit by probing (space per tier)

Read-only procedure for reporting GB/TB per resolution tier on a library root, and for
emitting a dry-run normalized move plan. Do this before sizing drives or splitting a
library by quality; never sample folder names.

## 1. Enumerate candidates by exclusion, not by video extension

Release files are frequently mislabeled: names ending `_mkv`/`_mp4` with no real
extension, or a wrong suffix (`.arj`, `.exe`, `.divx`). Multi-GB videos hide in that
set, so an extension allow-list undercounts the library badly.

```python
VIDEO_EXTS = {'.mkv','.mp4','.avi','.m4v','.ts','.wmv','.mpg','.mpeg','.mov','.flv','.webm'}
NON_VIDEO  = {'.nfo','.jpg','.jpeg','.png','.txt','.srt','.sub','.idx','.db','.xml','.mp3',
              '.m4a','.ico','.py','.website','.sfv','.ini','.json','.html','.URL','.bat',
              '.md5','.cue','.zip','.rar','.7z','.torrent','.part','.tmp','.log','.pls',
              '.m3u','.dll','.htm'}
# walk the root; probe every file whose extension is in neither set
```

## 2. Probe in parallel from bash

ffprobe is a native program: pass Windows paths (`T:/Media/...`), never MSYS `/t/...`.
Expect ~20 files/s on a spinning HDD — 30k files is ~25 minutes, so run it in the
background and report progress.

```bash
FF="/c/Program Files/Jellyfin/Server/ffprobe.exe"
probe_one() { local f="$1" d
  d=$("$FF" -v error -select_streams v:0 -show_entries stream=width,height \
        -of csv=s=x:p=0 -- "$f" 2>/dev/null | head -1)
  printf '%s\t%s\n' "$f" "$d" >> "$OUTDIR/part.$$"
}
export -f probe_one; export FF OUTDIR
xargs -a list.txt -d '\n' -P 16 -n 1 bash -c 'probe_one "$0"'
cat "$OUTDIR"/part.* > "$OUTDIR/dims.tsv"
```

Per-worker `part.$$` files avoid interleaved appends; concatenate at the end.

## 3. Tier rule

height < 720 → SD; otherwise longest edge ≥3840 → 2160p, ≥2500 → 1440p,
≥1800 → 1080p, else 720p.

## 4. Aggregation

- Match probe rows to walked paths using forward slashes — Windows `os.path.join`
  yields backslashes while the probe list came from `find | sed`.
- Per tier: shows, video count, video bytes.
- Non-video bytes attributed to each directory's majority tier; directories with no
  video reported separately (they hold artwork/quarantine, and sometimes mislabeled
  videos).

## 5. Outputs

- `resolution_summary.csv`: tier, shows, videos, video_bytes, video_GB, other_bytes,
  other_GB, total_GB, pct_of_video.
- Dry-run normalized plan: `<tier>/TV/<bucket>/<show>/Season XX/<Show> - S01E01 [tier].ext`
  (tier placeholder is the drive the user assigns later).
- Files that do not parse to `SxxExx` (extras, `Inside.Episode.1`, leading-`01.` names)
  keep their cleaned stem plus ` [tier]` and are listed separately for review — expect a
  few thousand on a 30k-file TV root.

## 6. Pitfalls

- **A Python-written list carries CRLF.** `open(..., 'w')` on Windows emits `\r\n`;
  `xargs -d '\n'` then hands ffprobe a trailing `\r` and every row fails with "No such
  file or directory". Write with `newline='\n'` and strip `\r` in the probe.
- **Store `None` for failed probes**, not a missing key: `dims.get(k) or (None, None)`.
  A present-but-`None` value unpacks to a `TypeError`.
- **Disk-bound, not CPU-bound.** Raising `-P` past ~8-16 does not help on a spinning
  HDD; measure the rate before promising an ETA.
- Re-runnable helpers: `scripts/probe_resolution.sh` (parallel probe) and
  `scripts/resolution_audit.py` (aggregation + plan).
