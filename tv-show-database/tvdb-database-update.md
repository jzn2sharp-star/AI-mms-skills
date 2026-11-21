---
description: TVDB database update workflow
name: tvdb-database-update
version: 1.0.0
---

# TVDB Database Update Workflow

This reference covers the workflow for applying gathered TVDB IDs to the `tv_tvdb_show_db.db` SQLite database.

## Database schema

The database `tv_tvdb_show_db.db` has a table:

```sql
CREATE TABLE shows (
    show_name TEXT PRIMARY KEY,
    tvdb_id INTEGER,
    year TEXT,
    bucket TEXT,
    season_count INTEGER,
    episode_count INTEGER,
    total_files INTEGER
);
```

## Update script template

Each batch update uses a script `update_tvdb_idsN.py`:

```python
import sqlite3

DB_PATH = r"C:/Users/Owner/AppData/Local/hermes/cache/scratch/tv_tvdb_show_db.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

updates = [
    ('Show.Name (2019)', 362696, 4, 32),
    ('The.Boys (2019)', 299154, 6, 60),
]

applied = 0
unmatched = []
for show_name, tvdb_id, seasons, episodes in updates:
    cur.execute("SELECT show_name FROM shows WHERE show_name = ?", (show_name,))
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE shows
            SET tvdb_id = ?, season_count = ?, episode_count = ?
            WHERE show_name = ?
        """, (tvdb_id, seasons, episodes, show_name))
        applied += 1
    else:
        unmatched.append(show_name)

conn.commit()
print(f"Applied: {applied} updates")
print(f"Unmatched: {unmatched}")
```

## Verification after each batch

```python
cur.execute("SELECT COUNT(*) FROM shows WHERE tvdb_id IS NOT NULL")
with_tvdb = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM shows")
total = cur.fetchone()[0]
cur.execute("SELECT SUM(season_count) FROM shows")
total_seasons = cur.fetchone()[0] or 0
cur.execute("SELECT SUM(episode_count) FROM shows")
total_episodes = cur.fetchone()[0] or 0
print(f"Shows with TVDB: {with_tvdb} / {total} ({with_tvdb/total*100:.1f}%)")
print(f"Shows missing TVDB: {total - with_tvdb}")
print(f"Total seasons: {total_seasons}")
print(f"Total episodes: {total_episodes}")
```

## Key rules

- Use exact `show_name` matches (with dots). Do not use LIKE patterns.
- After each batch, print the new totals.
- If a show name is not found, investigate before adding a new record — the show may be a file/alias.
- The database is at `C:/Users/Owner/AppData/Local/hermes/cache/scratch/tv_tvdb_show_db.db`.
