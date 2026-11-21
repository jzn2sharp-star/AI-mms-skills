# TV organization pipeline — file map and validation

## Where things live
- Live pipeline: `O:\Scripts\TV organization .7\` — phase2 planner, phase3 applier (sha256 dedupe, `--hash full|quick`, `--keep-identical`) and phase4 drive splitter in one folder. `.4` (working set) and `.5` (mirror) plus `.6` (pre-merge snapshot) remain as history; confirm by modification time before assuming a number.
- Hermes working set / dry-runs: the next numbered folder and `O:\Scripts\Movie scripts\Hermes Artifacts\` (moved from `O:\Scripts\Hermes Artifacts\` — re-check with `ls` before assuming either).
- Superseded pipelines: `O:\Scripts\_archive\<pipeline name>\` — moved, never deleted.

## What each pipeline file is for

| File | Role |
|---|---|
| `plan_all_files.csv` | Full dry-run plan: every file with `action` (MOVE / LEAVE / WRITE), `status` (OK / REVIEW / BLOCKED), `src`, `dst`, `tvdb_id`, show/year/season/episode/quality, plus `dup_group` and `follows` (multi-episode chains). Regenerate after any mapping edit. |
| `mapping_fixes.csv` | Master mapping: `bucket,folder,tvdb_id,show_name,note`. Authoritative per folder. A folder with no row falls back to `show_master.csv` and inherits whatever ID that holds. |
| `show_master.csv` | Per-show master: id, mapped/clean names, year, bucket, review flags. Only as current as the last mapping correction. |
| `extras_map.csv` | Maps loose `Extras\` subfolders to a parent show + TVDB ID (alternate pilots, intended endings, webisodes, etc.). |
| `tvdb_collected.db` | SQLite: `series`, `movies`, `folder_map`, `id_corrections`, `episodes`, `unresolved`. `id_corrections` is the audit trail for ID changes. |
| `plan_blocked.csv`, `plan_review.csv`, `plan_ready_OK.csv`, `plan_summary_by_show.csv` | Review queues sliced out of the full plan. |
| `missing_tvdb_triage.csv`, `show_mismatch.csv`, `episode_disagreements_real.csv` | Triage exports: folders with no ID, Plex-vs-plan title mismatches (with a `direction` verdict), episode-numbering disagreements. |

## Applying a mapping correction

1. Copy `tvdb_collected.db` to a backup name before writing.
2. Update `mapping_fixes.csv`, then propagate the same values to `show_master.csv` and the DB (`series`, `folder_map`), and record the change as a row in `id_corrections`.
3. **Also fix the map export** (e.g. `TVTV_Shows_with_path.csv`) — see "Regeneration provenance" below; otherwise the next `--prep` resurrects the old ID.
4. Regenerate the affected plan rows — a mapping edit invalidates everything derived from the old ID or name.

## Adopting externally supplied mapping/master data

When the user hands over a zip/export of `show_master.csv`, `mapping_fixes.csv`, `episode_titles.csv` (their own pipeline generation, a corrected dump), treat it as a candidate replacement, not a drop-in:

1. **Diff before overwriting.** Compare TVDB-id sets and shared-row values: print added ids, removed ids, and changed rows with old/new side by side. A removed id is how a previously corrected show silently comes back — e.g. a master rebuilt from a stale export drops the corrected ID and reintroduces the old one plus its old year.
2. **Re-assert every ID correction in all four places** — map export, `mapping_fixes.csv`, `show_master.csv`, and the DB (`series`, `folder_map`, `id_corrections`). Then regenerate and confirm the show's plan destination carries the intended `{tvdb-<id>}` and that episode titles come out right (titles drive file names; a missing `episode_titles.csv` block leaves release-token garbage in names).
3. **Expect a large blocker swing and attribute it.** User-supplied fixes usually clear whole blocker classes (e.g. every `NO_YEAR`); if counts jump the other way, diff again instead of hand-patching plan rows.
4. Supplied masters can also drop fields the planner relies on (`accept_years`, review flags). Re-check those columns after adoption, and keep a copy of the pre-adoption files (`applied/previous_data/`) so the change is reversible.

## Merging pipeline generations

Pipeline folders get renumbered (`.4` -> `.5` -> `.6` -> `.7`). To consolidate instead of running several in parallel:

1. Extract the newer snapshot into the new numbered folder, then overlay the planner that has the most fixes — features are additive, so a smaller file size does not mean older.
2. Copy in the newest data files (master, fixes, titles, extras/specials maps, DB) and the probe tooling/TSVs; keep applied-batch history and undo logs in an `applied/` subfolder.
3. Patch known gaps in the adopted scripts (e.g. a quality-tier matcher that only knows `(1080p) S01` and misses `(1080p) Season 01`).
4. Re-run the planner in the new folder and require the same row count / status totals as the donor run before calling the merge done; then write a PLAN.md recording lineage, run order and current state.

## Regeneration provenance (why corrections get lost)

`phase2_plan.py --map <export> --prep` rebuilds `show_master.csv`/`mapping_review.csv` from the export plus `mapping_fixes.csv`. Two consequences:

- **Edits survive only when the key is unchanged.** The merge step preserves prior user edits for IDs already present; a correction that changes the ID (e.g. 85409 -> 370768) creates a new key, so the hand-edited master row is discarded on the next prep. Write ID-changing fixes into the export and `mapping_fixes.csv`.
- **`mapping_fixes.csv` is keyed by `(bucket, folder)` with last-row-wins.** A stale duplicate row for the same folder silently overrides the newer correction — grep the folder before concluding a fix did not apply.

Year flags can also need a second pass: after a correct prep, re-apply `year`/`accept_years` in `show_master.csv` (the merge preserves them), then run the planner without `--prep`.

## Regeneration command line

```
python3 phase2_plan.py --map "O:/Scripts/Movie scripts/Hermes Artifacts/TVTV_Shows_with_path.csv" \
  --master show_master.csv --root T:/Media/TV \
  --episodes episode_titles.csv --extras-map extras_map.csv \
  --specials-map specials_map.csv \
  --quality-file quality_for_phase2.json --pixel-quality-file all_quality.json \
  --keep-both
```

- Pass native Windows paths (`C:/...`) to flags read by Python; MSYS `/c/...` forms raise FileNotFoundError inside the script even though bash accepts them.
- `--keep-both` turns destination collisions into "duplicate kept as a second version" instead of BLOCKED; omit it to keep every collision visible for review.
- Outputs are written into the scanned root (`T:\Media\TV\_plan_phase2.csv` and `_plan_phase2_episodes.csv`). Move them into the working set afterwards and re-check the root loose-file count — never leave generated CSVs in the library root.
- Regenerate the review views (`plan_ready_OK.csv`, `plan_review.csv`, `plan_blocked.csv`, `plan_summary_by_show.csv`) from the full plan so they match the run you are reporting.
- Re-check counts against the previous run: unchanged totals after a code or input change usually means the change did not reach the executed path.
- Attribute every row-count delta instead of reporting a bare total. Join the old and new plan on lowercased `src` and print only-in-old / only-in-new / changed-destination rows; a one-row drop is normally a file deleted off disk between runs, not a regeneration bug. Confirm zero changed destinations among the surviving rows before calling the run reproducible.

## Damaged extensions

An older renamer wrote filenames ending in `_mkv`/`_mp4`/`_avi` (dot lost). Classify with a normaliser that maps those endings back to `.ext` **before** the video/subtitle membership test; deriving the extension with `os.path.splitext` alone fails because an earlier dot in the name (e.g. `S01E01.12_Monkeys...`) produces a bogus extension and the file is dropped as "not a video/subtitle". ffprobe a sample to confirm such files are real media before repairing names.

Apply the normaliser by comparison (`if norm != ext.lower(): ext, stem = norm, fn[:-len(norm)]`), never by testing for a missing extension. Gating on `not ext` silently no-ops when `splitext` returns a dotted tail, and the run's totals stay byte-identical — the tell that the fix never reached the executed path.

The same normalised `stem + ext_l` must be used when building the **extras destination name**; reusing the raw filename there moves the damaged extension along with the file and leaves `_mkv`-style names sitting in `Extras\` after the apply.

## Merging probed resolutions into the quality file

A file the planner calls `quality not found` is only unblocked once it has an entry in the quality file. Fold ffprobe results back in instead of hand-tagging rows:

1. Probe from bash (ffprobe cannot be spawned from Python on this host) into a TSV: `<native path>\t<codec>,<width>,<height>`. Build the file list with drive-letter paths (`T:/...`) — ffprobe is native and rejects `/t/...`. Write the list with `newline=''` (or binary mode): text-mode writes on Windows emit CRLF, and the trailing `\r` then makes ffprobe fail to open every path while the loop still reports success.
2. `python3 update_probed_quality.py <tsv> [...] [--overwrite] [--quality-out PATH]` — adds missing entries to `quality_for_phase2.json`, keeps existing ones unless `--overwrite`, and labels each row with the planner's own thresholds so plan and probe agree.
3. Regenerate the plan and attribute the delta: blockers should drop by roughly the number of newly labelled videos, MOVE OK should rise.

## Loose files at bucket roots

Files sitting directly under a letter bucket (`<bucket>\dune.2000.cd1.avi`, `<bucket>\Show.S01E01.Eden.mp4`) never appear in the plan: the walker only descends into `<bucket>\<show>\…` and skips `_`-prefixed trees. Find them by diffing a live scan against the plan's `src` set; expect exactly two residue classes — the archived `_TO_SORT` tree and a few bucket-root strays.

Placement rules for those strays:

1. **Resolve the show first** (existing tagged show folder wins; a second candidate folder means the ID mapping decides, not the filename).
2. **Hash before filing.** Compare md5/size against the episode already in the target folder: an identical stray is a redundant copy — place it under a distinct name (`<stem>.copy1.<ext>`) so nothing is overwritten, log the hop, and tell the user it is a duplicate they may want to drop. Never overwrite a same-named target.
3. **Do not invent episode numbers.** Disc splits and other unverifiable chunks keep neutral names (`Dune.2000.CD1.avi`) inside the show's `(Quality) Sss` folder; with no `SxxEyy` the planner routes them to `Extras\` as REVIEW, which is the honest outcome. Only assign episode numbers you can prove from the source metadata.
4. **Register the destination** in the map export afterwards (see "After the apply") so the filed files become NOOP instead of `NOT_IN_MAPPING`.

## Applying one folder or show batch

`phase3_apply.py --tvdb <id>` selects **every folder of that show across the library** — fine for a one-show pilot, wrong when the task is one mislabeled folder. Build a scoped plan instead: filter the full plan on a lowercased `src` prefix and write `_plan_<name>.csv`, then `python3 phase3_apply.py --plan _plan_<name>.csv --apply` (dry run first; the script defaults to dry).

- The script writes an undo log (`_phase3_undo.csv`, `time,src,dst`). It records where files were put, so it goes stale the moment a file is moved again: if you rename destinations after the apply (e.g. repairing extensions) **or quarantine a subset out of the destination folder**, rewrite those `dst` values to the file's real current path — join on the lowercased path with `\` normalised to `/`, keep a copy of the pre-edit log, then dry-run `--undo` and expect every row to resolve. Otherwise `--undo` restores quarantined files into season folders.
- After the apply, read the destination file names once more and group them by title-token provenance. A botched batch rename can stamp one show's episode numbers onto another show's content (a seven-season show carrying S09 "deleted scenes" whose titles belong to a different series; files named for a different franchise entirely). Quarantine those before the media server scans them, rather than letting them inherit episode slots. Give the quarantine folder a self-describing name plus a date — `T:\Media\TV\Quarantine\<Show> - mislabeled content <YYYY-MM-DD>\` — and drop a `_manifest.csv` (`src,dst,bytes`) inside it so the hop is reversible and auditable; update the phase-3 undo rows to point at the quarantine path, or undo returns the wrong-show files to season folders.
- Verify with independent counts afterwards: source folder files == 0, destination files == moved count, total library file count unchanged.

### After the apply

- **Register the destination folder in the map export.** Applied destinations (`<bucket>\<Show> ({year}){{tvdb-<id>}\...`) are not in the export the planner reads, so the next regeneration reports every moved file as `NOT_IN_MAPPING` (BLOCKED). Add one top-level row for the new show folder — `<root path>,<folder name>,<show name>,<tvdb_id>` — and expect those rows to become NOOP (already at target) instead of BLOCKED.
- **REVIEW rows stay behind on purpose.** `phase3_apply.py` moves only `status: OK` unless `--include-review` is passed, so a batch that looks half-applied normally means the remainder was REVIEW (ambiguous episode/extra naming), not that the move failed. Report the split.
- Re-run the applier after any partial failure instead of switching tools: `robocopy /MOVE` semantics (copy first, then remove the source) are what finish a cross-drive batch safely.

## Destination length ceiling (long show titles)

The tag is repeated three times (`<bucket>\<tag>\<tag>(Quality) Sss\<tag>(Quality) SssEee.<release>.<ext>`),
so any title longer than roughly 45 characters pushes the computed path past the 259-char cap. The planner
reacts by truncating the release text and marking every episode REVIEW — a naming problem, not a mapping bug.
Watch for rows whose `reason` is `release truncated to fit 259-character limit` and for `len(dst)` pinned at
the cap.

Settle the policy before bulk-applying:

1. accept the truncated release text (files land, title tails are lost);
2. shorten the folder name (deviates from the TVDB title);
3. **recommended general rule** — when the computed path would exceed the cap, drop the repeated tag inside
   season folders and files (`(Quality) SssEee.<release>.<ext>`), which saves one full repetition.

The `S01`-vs-`Season 01` choice only buys ~6 characters per level; it cannot rescue a genuinely long title.

## Phase 4 — split by quality across drives

`phase4_split.py` runs after phase 3 has normalized the library. It reads the quality tier from the season folder's own name (`(1080p) S01`, and with the widened pattern `(1080p) Season 01`) — no re-probing — and moves each such folder's contents to the same relative path under the drive chosen for that tier.

```
python3 phase4_split.py --src "T:/Media/TV" --show Grimm \
  --tier 1080p="U:/Media/TV" --tier 2160p="U:/Media/TV" --tier 720p="V:/Media/TV" --tier SD="V:/Media/TV"
python3 phase4_split.py --undo _phase4_undo.csv --apply
```

- Dry run writes `split_plan.csv` and prints per-tier/per-destination GiB plus a free-space check against `--reserve-gb` (default 50 GiB).
- Cross-drive moves copy to `<dst>.part`, size-check, rename, then remove the source; an interrupted run leaves at most one `.part`. A rerun does NOT resume a finished-but-unremoved file: if the destination exists while the source remains, the row is skipped and both copies stay — clean those up deliberately.
- Show-level files (`poster.jpg`, `tvshow.nfo`, `Extras\…`) and any folder without a quality tag stay where they are, and `_`-prefixed trees are skipped.
- Add each destination's TV folder to the media server; Plex/Jellyfin will not see the moved seasons otherwise.

## Extras and specials

Extras are moved out of release/season subfolders into `<bucket>\<show tag>\Extras\`; a file-level pattern list (`EXTRAS_FILE`: deleted scenes, gag reel, audition tape, featurettes, making-of, highlight reel, webisodes, VFX...) plus the directory-level `EXTRAS_DIR` decide what counts. Two behaviours worth knowing before changing them:

- **The specials map is consulted first.** A row whose `match` regex hits the file stem turns the file into `<Show> ({year}) - S00E## - <TVDB title>.<ext>` inside `Extras\`. Rows are tried in file order, first hit wins; a specials entry therefore also acts as an extras detector for names that carry no keyword at all.
- **`--keep-both` needs a guard for rows without an episode number.** Collision handling rebuilds names from `S{int(season):02d}{episode}`; extras/specials have neither, which raises before the guard. Route those rows through their own suffix path (`<stem>.<suffix><ext>`), and note `season`/`episode` may arrive as int or str — coerce with `str(...)` before `.isdigit()`.
- Bundled extras (one local file holding several webisodes) cannot take one TVDB special number honestly; name it after the first part and mark the bundle in the title, then let the user adjust the map.

## Inventory exports vs MAX_PATH

`tree.exe` silently skips entries whose full path exceeds MAX_PATH (260 chars), so a `Media tree.txt` can be short by hundreds of real files while looking complete. Generate inventories with the packaged walker (`scripts/generate_tree.py`, which uses `\\?\`-prefixed paths) or an equivalent long-path-safe script, and pass the already-prefixed path to recursion unchanged — prefixing twice produces `\\?\?\...` and every subdirectory is skipped without an error. Reconcile the export's filename tokens against a live scan (`find <root> -type f`) before treating either as ground truth; strip leading whitespace from parsed tokens to avoid phantom mismatches from names that legitimately start with a space.

## Enriched research DB and proposal exports

The user's own research pipeline emits incremental SQLite dumps next to the working set (`*_enriched*.db`, then `plex_catalog_resolved.db`). They share a schema (`series`, `folder_map`, `id_corrections`, `episodes`, `unresolved`, `research_log`, and in the newest, `resolved_proposals`) and differ only in how far the research got.

1. **Pick exactly one canonical copy.** Compare `research_log` row counts and timestamps; the newest supersedes the others. Rename it to something stable (`tvdb_enriched.db`), move the superseded dumps to `applied/enriched_history/`, and keep the legacy `tvdb_collected.db` untouched.
2. **Adopt `resolved_proposals` as a reviewed batch, not automatically.** Rows carry a `confidence`; apply high-confidence rows and show medium/low ones separately for the user. A proposal names a folder that currently has no mapping — verify the folder exists on disk before writing a fix row for it.
3. **Apply proposals the same way as any ID correction**: map export + `mapping_fixes.csv` + `show_master.csv` + DB (`series`, `folder_map`, `id_corrections`). Then regenerate and attribute the blocker delta (a good proposal batch drops `NOT_IN_MAPPING`/`LOW_SIMILARITY` sharply).
4. **Write locks happen.** A stale Hermes kernel process can hold an open transaction on the legacy DB and every write returns "database is locked" while reads still work. Don't force-kill it: write the corrections into the canonical enriched DB instead (nothing in the pipeline reads the legacy DB at plan time) and note the lock. Retrying the same statement in a loop does not help.

## Probe/quality inputs do not live forever in scratch

Large ffprobe outputs written under `%LOCALAPPDATA%\hermes\cache\scratch` are pruned once idle (roughly a day), and the pipeline silently loses its pixel fallback when they go. Two rules:

1. **Persist the quality inputs in the pipeline folder** (`quality_for_phase2.json`, optionally a fresh `all_quality.json` dump) so a regeneration never depends on scratch survival; keep using absolute paths to whichever copy is current.
2. **If the pixel file is missing, run without `--pixel-quality-file`** — name/folder quality plus `quality_for_phase2.json` still covers nearly everything; expect the `quality taken from the file itself` count to shift, not the blocker count. Re-probe only what is still `quality not found`.

## Rules of thumb

- Plans inherit mapping errors silently: a missing `mapping_fixes.csv` row means the stale master ID wins. Always trace a suspicious ID back to its source row.
- Destination paths must match the generator's own format string (the live `.4` planner embeds `{tvdb-<id>}` in show/season/file names by design). Ask before changing the token; do not "strip IDs" as a blanket fix.
- Never apply a plan whose sampled sources are partly missing; re-scan and regenerate first.
- Similar-name shows are a distinct hazard: verify year and full title before assigning an ID, and check for an existing folder carrying the near-miss name.
- Archive, don't delete: superseded pipelines keep scripts and plans for reference, and any copies other folders depend on get refreshed.
- Confirm the inputs actually changed before spending a regeneration cycle: compare modification times under the pipeline folder and `cmp` the key CSVs/DB against the working-set copies. Nothing newer than your own last run means the user's edit did not land (check for `.~lock.*` files from a spreadsheet holding the folder open).
- Keep the live pipeline folder and its mirror byte-identical after each regeneration: copy the union both ways (never overwrite an existing file with an older one), then verify md5 over the shared set and report which side was missing what. Pipeline folders get renumbered/renamed without notice, so answer "where is the plan?" with the concrete current paths.
- **Review user-supplied organizer/sorter scripts; don't run them.** Three disqualifiers: delete-by-extension cleanup (unlinking `.nfo`/`.jpg`/`.png`/`.txt` plus empty-dir sweeps destroys artwork and episode metadata), no dry-run or undo log, and target paths that contradict this library's confirmed conventions (letter bucket, `(Year){tvdb-id}` tag, `(Quality)` in season folder and file name, `S01` not `Season 01`). Check that the source and destination drives actually exist. Report a compact verdict table; if rejected, archive the script with a short README stating why, and port any useful ideas (edition maps, subtitle language tags, resolution routing) into `phase2_plan.py`.
- A freshly generated tree export is not ground truth either: it can omit real episodes in very long/deep folder paths, non-Latin filenames and OS files. Reconcile filename tokens against a live scan; expect leading-space artifacts when diffing parsed tokens.
