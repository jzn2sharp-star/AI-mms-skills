# Quality extraction (resolution tagging)

Use this procedure when deriving quality (resolution) tags from folder names and video files.

## Quality tokens

Match quality tokens in this order (case-insensitive, word boundaries):

1. **Parenthetical form**: `(SD)`, `(720p)`, `(1080p)`, `(1440p)`, `(2160p)`, `(480p)` — regex: `\\((SD\\|720p\\|1080p\\|1440p\\|2160p\\|480p)\\s*\\)`
2. **Trailing unparenthesized token**: `720p`, `1080p`, `480p`, etc. at end of string
3. **Embedded token**: `.720p.BluRay.` → `720p` via `\\b720p\\b`

## Normalization rules

- Numeric tiers to lowercase: `1080P` → `1080p`
- `SD`/`480p` keep their spelling
- If no token matches, quality is **Unknown**

## Per-folder quality extraction

1. Take the last path component of the file (the folder name).
2. Match quality tokens in the order above.
3. If no token matches, probe the first video stream (height → tier).

## Forum folders

For UIndex.org torrent folders (e.g., `The.Bear.S05E04.1080p.HEVC`):
- Quality = first `NNNp` token in the name
- Default `SD` if no quality token found

## Per-file quality extraction

From `probe.jsonl`, derive quality from the `video` object:
- `height >= 2160` → 2160p
- `height >= 1440` → 1440p
- `height >= 1080` → 1080p
- `height >= 720` → 720p
- `height >= 480` → 480p
- `height < 480` → SD

## Pitfalls

- **480p is tracked as a tier** (not folded into SD) in this user's library.
- **Embedded tokens**: `...720p.BluRay.` resolves to 720p even though not in parentheses.
- **Trailing-token rule**: `...1080p` at end of string resolves to 1080p.
- **SD is a word boundary**: `\\bSD\\b` catches `(SD)` and trailing `SD` but not `SomethingSDXYZ`.
