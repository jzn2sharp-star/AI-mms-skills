# Turning plan/library CSVs into a self-contained HTML dashboard

Use when the user asks for "an HTML GUI", a web view of the plan, or any browseable front-end over the
plan CSVs. Deliver one static file — no framework, no CDN, no backend — because the machine has no
web stack installed and the page must open straight from disk.

Canonical instance: `O:\Scripts\TV organization .7\build_gui.py` -> `index.html`.

## Build

1. **Slim the rows.** Read `plan_all_files.csv` and keep only the columns the UI shows (`action, status,
   reason, src, dst, tvdb_id, show, year, season, episode, quality`). Dropping `release`, `dup_group`
   and `follows` roughly halves the payload; 37k rows then compress to ~1 MB.
2. **Embed, don't fetch.** `fetch()` on `file://` is blocked by CORS, so the data must live inside the
   HTML. Compress then base64: `zlib.compress(json.dumps(payload, separators=(',', ':')).encode(), 9)`
   -> `base64.b64encode(...)` -> inject into a `__DATA__` placeholder in the template string.
3. **Decode in-page with platform APIs only** (no pako/JSZip):
   `atob` -> `Uint8Array` -> `new DecompressionStream('deflate')` -> write/close the writable side ->
   `await new Response(ds.readable).text()` -> `JSON.parse`. Wrap it in try/catch and render an
   explicit "decompress failed" message; a silent empty page is worse than an error.
4. **UI worth shipping**: stat cards per status, one search box matching src/dst/show, dropdowns for
   status/action/reason (reason values derived from the data at load), sortable column headers, ~200-row
   paging, an "export filtered set to CSV" button, plus tabs for the per-show summary and for the
   applied/undo history. Keep it keyboard-light and dependency-free.
5. **Rebuild on every plan regeneration** — the HTML is a snapshot of the CSVs at build time, so stale
   dashboards silently disagree with the plan. Print the payload size and row count so the run is
   self-evidencing.
6. **Icon**: any image dropped next to `build_gui.py` (`.ico` preferred, else png/jpg/webp/avif/svg) is
   embedded as a data URI and used twice — `<link rel="icon">` for the tab and an `<img>` beside the title.
   Detect it by scanning the folder rather than hard-coding a filename, and rebuild after swapping the file.

## Serving and verification

- A double-clicked `index.html` works in an ordinary browser, but the sandboxed/automation browser may
  refuse `file://` outright. Serve it instead:
  `python3 -m http.server 8777` from the pipeline folder, then open `http://localhost:8777/index.html`.
- **Verify in a real browser before reporting it as done**: confirm the header row count, the status
  card totals, that a status filter returns exactly its count, that a text search narrows the table,
  and that each tab populates (shows / undo / quarantine). Report those observed numbers, not
  "built successfully".
- `localhost` servers are session-scoped; tell the user the URL and the one-line command to restart it.

## Native desktop app (tkinter)

When the user wants a GUI "that doesn't have to be HTML", or wants to *run* batches rather than browse them,
ship a stdlib tkinter window (`gui_app.py`). Recipe that works on this host:

- Tkinter/Tk is already present — no install. Set the window icon from an `.ico` sitting next to the script
  (`iconbitmap`), ignoring `TclError` if it fails.
- Load the CSVs once; on filter change re-render at most a few thousand rows into a `Treeview`. Never insert the
  whole 37k-row plan into the widget.
- Colour rows with tags (`OK`/`REVIEW`/`BLOCKED`), mark/unmark with `space`, select-all with Ctrl-A.
- Run pipeline steps with `subprocess.Popen([sys.executable, script, ...], cwd=<pipeline dir>)` on a worker
  thread; stream stdout through a `queue` drained from the UI thread via `after(200, ...)`.
- Gate every mutating action behind a `messagebox.askyesno` that states the exact count ("Apply 144 planned
  move(s)?" / "Reverse ALL 249 logged moves?"). Apply writes through `phase3_apply.py`, so the undo log is
  the safety net.
- Ship a `--self-test` mode: build the window, update once, print row/filtered counts, destroy — it validates
  data loading headlessly before the real run.
- **Dark theme**: `ttk.Style.theme_use('clam')` is what makes full colour control possible; then configure
  the root background plus `TFrame/TLabel/TLabelframe/TNotebook/TButton/TEntry/TCombobox/TCheckbutton/
  Treeview/Treeview.Heading/scrollbars` (page background `#0f1115`, panel `#161a22`, accent selection).
  Map `Treeview` selection explicitly and keep the status tags for row text colour — configuring only the
  default `.` style leaves tree rows and tabs light.

Verify like the browser page: load counts, a filter result, and that a dry-run reports the expected number.

## Pitfalls

- Do not embed uncompressed JSON for a full plan: 37k rows are several MB of markup and every filter
  re-renders sluggishly. Compress + page.
- Never `document.write` the payload or interpolate it into inline JS strings — paths contain
  backslashes and quotes; keep it as a base64 blob decoded at runtime.
- If the page is ever moved to a real server, keep the same single-file build; splitting data into a
  sibling `.json` only works over HTTP and breaks the double-click case.
