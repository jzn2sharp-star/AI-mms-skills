# Batch media quality probe (parallel ffprobe)

Use this procedure to extract quality metadata (container, duration, size, bitrate, stream details) from every video file in a media root.

## When to Use

- Extracting quality metadata from every video file in a media root (e.g., `T:\Media\TV`)
- After probing, assembling per-file JSON with quality tags

## Procedure

1. **Inventory the root** with NUL-delimited `find` (spaces in names survive):
   `find <root> -type f \\( -iname '*.mp4' -o -iname '*.mpeg' \\) -print0 > video_files.txt`

2. **Write the per-file probe script** `ffprobe_one.sh`:
   - Invokes `C:/Program Files/Jellyfin/Server/ffprobe.exe` via bash (not Python subprocess)
   - Prints one compact JSON object per file on stdout: `path, container, duration, size_bytes, bitrate, num_streams, video, audio, subs, error`
   - On rc≠0, emit `{"path": "...", "error": "probe_failed", "rc": <rc>}` instead of aborting

3. **Parallelize** across cores: `xargs -0 -P 24 -n 1 probe_one.sh < video_files.txt > probe.jsonl`

4. **Assemble** `probe.jsonl` into the final JSON sorted by `path`; keep the JSONL as the source of truth.

5. **Report progress at the top of each minute** during the run.

## Per-file probe script `ffprobe_one.sh`

```bash
#!/usr/bin/env bash
# ffprobe one file, emit NDJSON, handle rc≠0 as probe_failed
IN="${1}"

if [ ! -f "$IN" ]; then
  echo "{\"path\": \"$IN\", \"error\": \"file_not_found\", \"rc\": -1}"
  exit 0
fi

OUT=$(C:/Program\ Files/Jellyfin/Server/ffprobe.exe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,width,height,bit_rate,codec_type -of json "$IN" 2>&1)
RC=$?

if [ $RC -ne 0 ]; then
  echo "{\"path\": \"$IN\", \"error\": \"probe_failed\", \"rc\": $RC}"
  exit 0
fi

# Build JSON with path field
python3 -c "
import json, os, sys
data = json.load(sys.stdin)
data['path'] = '$IN'
print(json.dumps(data))
" <<< "$OUT"
```

## Key pitfalls

- **ffprobe via bash**: on this Windows host, Python `subprocess` on `C:/Program Files/Jellyfin/Server/ffprobe.exe` raises `WinError 5`. Call it from a bash script with forward slashes.
- **Missing `import sys`**: a per-file `-c` snippet that reads `sys.stdin` but only imports `json, os` raised `NameError` and aborted the run. Import every name you use.
- **NUL-delimited counting**: `wc -l` reports `0` for `-print0` output (no newlines). Use `tr -cd '\0' | wc -c` or count entries instead.
- **Output location**: write big outputs to the Hermes scratch dir, not the home directory, or they are pruned/locked.

## Error handling

- On probe failure, emit `{"path": "...", "error": "probe_failed", "rc": <rc>}` instead of aborting the batch.
- Verify all lines parse as valid JSON (exit 0, "all lines parse OK").
- Total probe failures = count of lines with `error: probe_failed`.

## Quality extraction from probe results

After assembling `probe.jsonl` into `all_quality.json`:

- `container` = `format.format_name`
- `duration` = `format.duration`
- `size_bytes` = `format.size`
- `bitrate` = `format.bit_rate`
- Per-stream: `codec_name`, `width`, `height`, `bit_rate`, `codec_type` (video/audio/subtitle)

## Background

- **24 CPUs**: `xargs -0 -P 24`
- **Probes report**: `C:/Program Files/Jellyfin/Server/ffprobe.exe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,width,height,bit_rate,codec_type -of json`
- **Output format**: NDJSON (`probe.jsonl`), one JSON object per file
- **Probe failure fallback**: emit `{"path": "...", "error": "probe_failed", "rc": <rc>}` instead of aborting
