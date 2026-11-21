# matching-decisions

Score thresholds and ambiguous-match handling for TVDB lookups.

## Score thresholds
| Score | Meaning | Action |
|---|---|---|
| >= 0.85 | High confidence | Mark `ok`, use the TVDB id directly. |
| 0.60--0.84 | Good enough for bulk use | Mark `ok`; the id is stable. |
| 0.40--0.59 | Ambiguous | Mark `low`. Keep the candidate row, flagged for manual review. |
| < 0.40 or no hits | Unresolvable | Mark `unresolved`. Do not write an id. |

## Ambiguous-match handling
- Multiple candidate hits at similar score -> prefer the shortest canonical title and the hit with a present `first_air_date`.
- The query matched a collection/multipart name (e.g. `DARK MATTER 20152017 Complete TV Series` -> `Dark Matter` 12720) -> re-clean (drop year/collection suffix), re-search; if still multipart, keep the shortest match.
- The query is a subtitle or season marker (e.g. `Citadel S01 COMPLETE`) -> not the show; the parent is the show (`Citadel` 10954).
- The query is a misspelling or alias -> match `name` and `aliases` (`PEN15` -> 348127 exact; `A P Bio` -> `A.P. Bio` 328534 via alias).
- **No hits at all** -> insert spaces between letters and digits (e.g. `earth21994` -> `earth 21994`), drop a trailing year, search the first **two** words only (e.g. `The 4400`, `Winter 2026`), **never the first word alone** (a one-word fallback returns an unrelated record). If still nothing, mark `unresolved` and report it; do not invent an id.
- A one-word fallback finds the wrong show (see SKILL.md key pitfalls).

## Decision recipe
1. Clean the name (see name-cleaning skill).
2. Search the cleaned name.
3. Collect top 8 hits.
4. Score every hit's `name` and `aliases` (difflib ratio) against the cleaned query.
5. Take the highest score.
6. Apply the threshold table above.
