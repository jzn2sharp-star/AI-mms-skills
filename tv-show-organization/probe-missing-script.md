# Probe missing.py — video resolution probe script

A Python script that probes video files with ffprobe to determine their actual resolution,
codec, and other metadata. It probes ONLY files not already in an existing quality JSON,
making it incremental and resumable. It never modifies media files.

## Usage

```bash
# Probe only files flagged as "quality not found" in a plan
python3 probe_missing.py --root "T:\Media\TV" --existing all_quality.json --plan plan_all_files.csv --out all_quality_merged.json

# Probe every video not already in the JSON (catches moved folders)
python3 probe_missing.py --root "T:\Media\TV" --existing all_quality.json --out all_quality_merged.json

# With fewer workers for slow/network drives
python3 probe_missing.py --root "T:\Media\TV" --existing all_quality.json --out all_quality_merged.json --workers 2
```

## Key behavior

- **Probe command**: `C:/Program Files/Jellyfin/Server/ffprobe.exe -v error -select_streams v:0 -show_entries stream=width,height,codec_name,field_order,sample_aspect_ratio -of json`
- **Only probes files not in `all_quality.json`** (moved folders mean many files lack entries)
- **Handles broken names**: files ending in `_mkv`, `_mp4`, `_avi`, `_m4v` (missing-dot extensions) are included
- **Skips folders starting with `_`** (e.g., `_TO_SORT`)
- **Corrupt files**: listed as failures, run continues (no abort)
- **Progress**: saved every 200 files; finished files skipped on re-run
- **Resume**: if `--out` exists, already-probed files are skipped on re-run
- **Resolution classification** (width-first):
  - width ≥ 3600 → 2160p
  - width ≥ 1800 → 1080p
  - width ≥ 1200 → 720p
  - width ≥ 700 → 480p
  - below → SD

## Why filename claims are unreliable

The 100 (2014) title is a classic case: files named `...720p...` or `...1080p...` often contain
**480p SD content** cropped to 16:9 (e.g., 720x404, 624x350, 640x360). Only ~11 of ~38 files are
actually 1080p; all remaining files are 480p. Always derive quality from actual ffprobe pixel
dimensions, never from filename tokens.

## Successful run results (2026-11-19)

The full-drive probe (31,519 files) was completed after two background process runs:

- **31,371 files probed, 0 failures**
- **Resolution distribution** (from `all_quality_merged.json`):
  - 1080p: 7,385 files
  - 2160p: 3 files
  - 480p: 4,969 files
  - 720p: 5,935 files
  - SD: 13,079 files
  - **Total: 31,519 files**

## UNKNOWN files (20 files, 3 shows)

The audit report's UNKNOWN tier (12 shows, 20 videos, 6.80 GB) resolved to:

- **Persons Unknown (2010)**: 13 files, all 624x352 SD 4:3 (folder: `P\Persons Unknown (2010)`)
- **Unknown Serial Killers of America (2025)**: 6 files (folder: `U\Unknown.Serial.Killers.of.America.2025...`)
- **The Unknown (2012)**: folder NOT found in `T:\Media\TV` tree (TVDB 269030)

## Known limitations

- Full-drive scan is slow (~31,000 files, timed out at ~300s). Use `--plan` for targeted probing.
- ffprobe via Python `subprocess` on `C:/Program Files/Jellyfin/Server/ffprobe.exe` raises
  `WinError 5` on this host; the script uses `subprocess.run` and handles the fallback.
- The script is now proven to work: full-drive probe completed after two background
  process runs with `--workers 2` (processes proc_a1ee508bbd94, proc_4e6e245252cf).
