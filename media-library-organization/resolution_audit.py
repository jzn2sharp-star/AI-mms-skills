"""Per-resolution storage audit + normalized dry-run plan (read-only).

Usage: resolution_audit.py <root> <dims.tsv> [more dims.tsv ...] --out <outdir>
  root     : Windows path, e.g. T:/Media/TV
  dims.tsv : path<TAB>WxH rows from probe_resolution.sh (repeatable)
  --out    : directory for resolution_summary.csv, normalized_plan.csv, audit_report.txt

Tier rule: height < 720 -> SD; else longest edge (>=3840 2160p, >=2500 1440p,
>=1800 1080p, else 720p). Probe failures are UNKNOWN.
"""
import csv
import os
import re
import sys
from collections import defaultdict

VIDEO_EXTS = {'.mkv', '.mp4', '.avi', '.m4v', '.ts', '.wmv',
              '.mpg', '.mpeg', '.mov', '.flv', '.webm'}
TIER_ORDER = ['2160p', '1440p', '1080p', '720p', 'SD', 'UNKNOWN']
GB = 1024 ** 3


def parse_dims(text):
    m = re.match(r'\s*(\d+)\s*x\s*(\d+)', text or '')
    return (int(m.group(1)), int(m.group(2))) if m else None


def tier_of(w, h):
    if w is None or h is None:
        return 'UNKNOWN'
    if h < 720:
        return 'SD'
    edge = max(w, h)
    if edge >= 3840:
        return '2160p'
    if edge >= 2500:
        return '1440p'
    if edge >= 1800:
        return '1080p'
    return '720p'


def parse_season_episode(folder_name, file_name):
    m = re.search(r'[Ss](\d{1,2})[Ee](\d{1,3})', file_name)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r'(?<!\d)(\d{1,2})x(\d{1,3})(?!\d)', file_name)
    if m:
        return int(m.group(1)), int(m.group(2))
    season = 1
    sm = re.search(r'[Ss]eason[\s._-]*(\d{1,2})', folder_name)
    if sm:
        season = int(sm.group(1))
    em = re.match(r'^(\d{1,3})[\s._-]+', file_name)
    return season, (int(em.group(1)) if em else None)


def normalized_name(show, season, episode, orig_stem, tier, ext):
    if episode is not None:
        stem = f"{show} - S{season:02d}E{episode:02d} [{tier}]"
    else:
        stem = re.sub(r'\s*\[(2160p|1440p|1080p|720p|SD)\]', '', orig_stem,
                      flags=re.I).strip() + f" [{tier}]"
    return stem + ext.lower()


def main():
    args = sys.argv[1:]
    outdir = None
    if '--out' in args:
        i = args.index('--out')
        outdir = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) < 2:
        sys.exit(__doc__)
    root, dims_files = args[0], args[1:]
    os.makedirs(outdir, exist_ok=True)

    dims = {}
    for path in dims_files:
        with open(path, encoding='utf-8', errors='replace') as f:
            for line in f:
                parts = line.rstrip('\n').split('\t')
                if len(parts) >= 2:
                    dims[parts[0]] = parse_dims(parts[1])

    videos = []
    dir_nonvideo = defaultdict(int)
    dir_tiers = defaultdict(lambda: defaultdict(int))
    file_count = 0

    for dp, dn, fn in os.walk(root):
        for name in fn:
            p = os.path.join(dp, name)
            key = p.replace('\\', '/')
            try:
                size = os.path.getsize(p)
            except OSError:
                size = 0
            file_count += 1
            ext = os.path.splitext(name)[1].lower()
            if ext in VIDEO_EXTS or key in dims:
                w, h = dims.get(key) or (None, None)
                t = tier_of(w, h)
                videos.append((p, size, t))
                dir_tiers[dp][t] += 1
            else:
                dir_nonvideo[dp] += size

    tier_bytes = defaultdict(int)
    tier_count = defaultdict(int)
    tier_shows = defaultdict(set)
    for p, size, t in videos:
        tier_bytes[t] += size
        tier_count[t] += 1
        rel = os.path.relpath(p, root).replace('\\', '/')
        parts = rel.split('/')
        tier_shows[t].add(parts[1] if len(parts) > 2 else '(loose)')

    tier_other = defaultdict(int)
    unattributed = 0
    for d, size in dir_nonvideo.items():
        tiers = dir_tiers.get(d)
        if not tiers:
            unattributed += size
            continue
        tier_other[max(tiers.items(), key=lambda kv: kv[1])[0]] += size

    total_v = sum(tier_bytes.values())
    lines = [f"Root: {root}", f"Files walked: {file_count}", f"Videos found: {len(videos)}", ""]
    lines.append(f"{'Tier':<8}{'Shows':>7}{'Videos':>8}{'Video GB':>12}{'Other GB':>11}{'Total GB':>12}{'Pct':>7}")
    for t in TIER_ORDER:
        if not tier_count[t] and not tier_bytes[t]:
            continue
        vgb, ogb = tier_bytes[t] / GB, tier_other[t] / GB
        pct = (tier_bytes[t] / total_v * 100) if total_v else 0
        lines.append(f"{t:<8}{len(tier_shows[t]):>7}{tier_count[t]:>8}{vgb:>12.2f}"
                     f"{ogb:>11.2f}{vgb + ogb:>12.2f}{pct:>6.1f}%")
    lines.append('-' * 70)
    lines.append(f"{'TOTAL':<8}{'':>7}{len(videos):>8}{total_v / GB:>12.2f}"
                 f"{(sum(tier_other.values()) + unattributed) / GB:>11.2f}")
    if unattributed:
        lines.append(f"\nNon-video bytes in directories with no video: {unattributed / GB:.2f} GB")
    report = "\n".join(lines)
    print(report)

    with open(os.path.join(outdir, 'audit_report.txt'), 'w', encoding='utf-8') as f:
        f.write(report + '\n')

    with open(os.path.join(outdir, 'resolution_summary.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['tier', 'shows', 'videos', 'video_bytes', 'video_GB',
                    'other_bytes', 'other_GB', 'total_GB', 'pct_of_video'])
        for t in TIER_ORDER:
            if not tier_count[t] and not tier_bytes[t]:
                continue
            vgb, ogb = tier_bytes[t] / GB, tier_other[t] / GB
            pct = (tier_bytes[t] / total_v * 100) if total_v else 0
            w.writerow([t, len(tier_shows[t]), tier_count[t], tier_bytes[t],
                        f'{vgb:.2f}', tier_other[t], f'{ogb:.2f}',
                        f'{vgb + ogb:.2f}', f'{pct:.1f}'])

    rows = []
    unparsed = 0
    for p, size, t in videos:
        rel = os.path.relpath(p, root).replace('\\', '/')
        parts = rel.split('/')
        bucket = parts[0]
        show = parts[1] if len(parts) > 2 else '(loose)'
        parent = os.path.basename(os.path.dirname(p))
        season, ep = parse_season_episode(parent, os.path.basename(p))
        ext = os.path.splitext(p)[1]
        name = normalized_name(show, season, ep,
                             os.path.splitext(os.path.basename(p))[0], t, ext)
        if ep is None:
            unparsed += 1
        rows.append([t, size, 'VIDEO', p, f"<{t}>/TV/{bucket}/{show}/Season {season:02d}/{name}"])

    with open(os.path.join(outdir, 'normalized_plan.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['tier', 'bytes', 'type', 'source', 'dest_relative'])
        w.writerows(rows)

    print(f"\nPlan rows: {len(rows)} (no parseable SxxExx: {unparsed})")


if __name__ == '__main__':
    main()
