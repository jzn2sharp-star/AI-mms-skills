#!/usr/bin/env bash
# Parallel ffprobe resolution probe (read-only).
#
# Usage: probe_resolution.sh <listfile> <outdir> [parallel]
#   listfile : one Windows-style path per line (T:/...), no CR
#   outdir   : receives dims.tsv  (path<TAB>WxH; empty dims = probe failed)
#   parallel : concurrent ffprobe processes (default 8)
#
# Each worker appends to its own part.$$ so concurrent writes never interleave.
set -u
FF="${FFPROBE:-/c/Program Files/Jellyfin/Server/ffprobe.exe}"
LIST="$1"; OUTDIR="$2"; PAR="${3:-8}"
mkdir -p "$OUTDIR"

probe_one() {
  local f="$1" d
  f="${f%$'\r'}"
  d=$("$FF" -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 -- "$f" 2>/dev/null | head -1)
  printf '%s\t%s\n' "$f" "$d" >> "$OUTDIR/part.$$"
}
export FF OUTDIR
export -f probe_one

xargs -a "$LIST" -d '\n' -P "$PAR" -n 1 bash -c 'probe_one "$0"'
cat "$OUTDIR"/part.* > "$OUTDIR/dims.tsv"
rm -f "$OUTDIR"/part.*
echo "probed lines: $(wc -l < "$OUTDIR/dims.tsv")"
