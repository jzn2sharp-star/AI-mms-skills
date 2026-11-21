# Outlier consolidation: classification + content-hash dedup

Class of task: moving stray/staging/torrent video folders into the main library roots (`S:\Media`, `T:\Media\TV`, `M:\Movies`, `E:\_Collection`) and deleting the ones that are already there.

## 1. Classify anime / cartoon / live action

Two free APIs, no key required. Run both; do not rely on one.

**AniList GraphQL** (anime only, no auth):
```
POST https://graphql.anilist.co
{"query": "{Media(search:\"<title>\",type:ANIME){id title{english} format countryOfOrigin}}"}
```
A non-null `Media` means anime. It correctly returns null/404 for western animation and live action (e.g. Avatar: The Last Airbender is not in AniList).

**TVMaze** (Animation vs live action, no auth):
```
GET https://api.tvmaze.com/search/shows?q=<urlencoded title>
```
Read `show.type`: `Animation` → cartoon; anything else (`Scripted`, `Talk Show`, …) → live action. The search returns a `score`; take the top hit but verify the name/year is plausible.

Decision order that works:
1. Name keyword: `anime` → anime; `cartoon`/`animated`/`animation` → cartoon; `live action`/`live-action` → live action.
2. AniList match → anime.
3. TVMaze `type == Animation` → cartoon, else live action.

### Normalizing the query
Folder names carry release metadata that breaks search. Strip bracketed/parenthesized blocks, standalone 4-digit years, runs of 5+ digits, and release tokens (`complete`, `collection`, `season`, `series`, `1080p`, `720p`, `480p`, `webdl`, `bluray`, `x264`, `x265`, `hevc`, `hd`, `hdtv`, `amzn`, `nf`, `web`, `remastered`, `pack`, `vol`, `part`, `s\d+`, `e\d+`), then collapse non-alphanumerics to spaces.

Long multi-word queries return nothing (`batman cartoons the five animated` → empty). When a query returns no hits, retry with the first 3 significant words, and fall back to a curated short title for the specific item. Curated titles beat normalization for a fixed, known list of folders.

### Known traps
- `DC.collection` normalizes to `dc`, which AniList resolves to the anime *Cleopatra D.C.* — a false positive. Never let a bare acronym/initialism query hit AniList; skip container names.
- TVMaze is TV-only: a film query (`baron munchausen`) returns nothing. Classify films from the name/year or a film source, not TVMaze.
- TVMaze can be wrong for a new or obscure title (a 2026 Marvel series returned `Scripted`). Flag the uncertainty in the plan and ask; do not silently route.

## 2. Content-hash dedup (MD5 with size pre-filter)

Name matching is not enough: the same film can be named `1927 - Wings.mp4` in the source and `Wings(1927)().mp4` in the library. Content hashing is the reliable test.

Do NOT hash the destination library (tens of thousands of files, tens of TB). Filter by size first:

```python
# 1. walk the destination roots once; index size -> [paths]
size_idx = {}
for root in DEST:
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.lower().endswith(VIDEO_EXT):
                p = os.path.join(dp, f)
                size_idx.setdefault(os.path.getsize(p), []).append(p)

# 2. for each outlier file, hash it and only the same-size candidates
for x, sz, p in outliers:
    h = md5(p)
    hit = next((c for c in size_idx.get(sz, []) if md5(c) == h), None)
    dup = bool(hit)
```

Video sizes are usually unique, so each outlier file triggers one or two hashes instead of thousands.

### Reading the result
- Report `content-dup` and `new` counts per folder, plus a sample of the duplicate destination paths. The user reviews these counts before anything moves.
- Distinguish an exact duplicate from a partial copy: compare **video counts**, not folder names. A same-named destination folder can hold only sidecars (one library's `BATMAN.Cartoons...` folder held 64 `.srt` and 0 videos), so the source is new content, not a duplicate.
- Exact duplicates are the deletion list; ask before deleting. Never delete on the strength of a name match alone.

## 3. Dry-run plan format

Write a markdown plan to the user's home directory (`C:\Users\Owner\<name>_dryrun.md`) containing:

1. **Classification table** — item, class, and the evidence (which API returned what).
2. **Move plan table** — source → destination, video count, size. One row per item.
3. **Duplicate deletion table** — source, count, size, and the exact destination path it already exists at.
4. **Open questions** — anything ambiguous, plus the merge-vs-new-folder and naming-convention choices.
5. **Verification steps** — before/after `du -sh` per destination, video counts, spot checks.

State plainly at the top that nothing has been moved or deleted. Present the numbers and wait for approval; the user's standing rule is dry run first, commit only after review.
