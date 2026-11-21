"""Merge ffprobe results into the phase-2 quality file.

Input TSV (one per line):  <path>\t<codec>,<width>,<height>
Lines without a usable width/height are skipped. Existing rows are replaced only
with --overwrite; by default only missing paths are added.

Usage:
    python update_probed_quality.py probed.tsv [--quality-out PATH] [--overwrite]
"""
import json
import sys

# Thresholds mirror phase2_plan.pixel_label so probe labels and plan labels agree.
THRESH = [(3000, 1600, '2160p'), (1700, 1000, '1080p'), (1100, 650, '720p'), (800, 460, '480p')]


def pixel_label(w, h):
    for wt, ht, label in THRESH:
        if w >= wt or h >= ht:
            return label
    return 'SD'


def norm(p):
    p = p.replace('\\', '/')
    if p.lower().startswith('t:/media/tv/'):
        p = 'T:/Media/TV/' + p[len('t:/media/tv/'):]
    return p


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    overwrite = '--overwrite' in sys.argv
    qout = 'C:/Users/Owner/AppData/Local/hermes/cache/scratch/quality_for_phase2.json'
    if '--quality-out' in sys.argv:
        qout = sys.argv[sys.argv.index('--quality-out') + 1]
    if not args:
        print(__doc__)
        return 1

    added = updated = skipped = bad = 0
    rows = {}
    for tsv in args:
        for line in open(tsv, encoding='utf-8', errors='replace'):
            line = line.rstrip('\n')
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                bad += 1
                continue
            path = norm(parts[0])
            bits = parts[1].split(',')
            try:
                w, h = int(bits[-2]), int(bits[-1])
            except (ValueError, IndexError):
                bad += 1
                continue
            rows[path] = pixel_label(w, h)

    d = json.load(open(qout, encoding='utf-8-sig'))
    have = {norm(f['path']): f for f in d['files']}
    for path, label in rows.items():
        if path in have:
            if overwrite and have[path]['quality'] != label:
                have[path]['quality'] = label
                updated += 1
            else:
                skipped += 1
        else:
            d['files'].append({'path': path, 'quality': label})
            added += 1
    d['files'].sort(key=lambda f: f['path'])
    json.dump(d, open(qout, 'w', encoding='utf-8'), indent=1)
    print(f'probed rows: {len(rows)}  added: {added}  updated: {updated}  kept: {skipped}  unparsable lines: {bad}')
    print(f'wrote {qout} ({len(d["files"])} entries)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
