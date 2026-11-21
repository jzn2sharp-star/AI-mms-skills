# Plex Library Refresh Reference

## When to refresh

Trigger a Plex library rescan/refresh after:

- Any batch of moves, renames, NFO writes, or `.plexmatch` changes.
- After clearing the `broken/` quarantine folder.
- After applying the phase2/phase3 plan workflow (tv-show-organization skill).
- After major library changes (show additions, quality retags, TVDB ID updates).

## Refresh process

1. Apply the planned changes on disk (moves, renames, NFO writes, `.plexmatch` writes).
2. Open Plex Web UI (Settings → System → Server Health → Refresh library, or Admin → Library → Scan now).
3. Monitor the scan progress; confirm the directory changes are picked up.
4. Verify in Plex: shows, seasons, episodes appear correctly with matching metadata.
5. Do NOT skip this step — directory changes are NOT picked up by Plex until you rescan.

## Scan vs. refresh

- **Scan**: Plex rescans the entire library from scratch.
- **Refresh**: Plex rescans a specific library or item.
- For directory changes (moves, renames), use the library-wide scan/refresh.
- For individual item edits, use the item's Edit UI.

## Performance notes

- Scanning large libraries (30,000+ files) takes several minutes.
- Report progress at the top of each minute during long scans.
- After a move/rename batch, always verify totals (per-folder counts) before and after the refresh.
