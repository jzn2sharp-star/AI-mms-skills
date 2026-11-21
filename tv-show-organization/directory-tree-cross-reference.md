# Directory Tree Cross-Referencing

## Overview

When the user provides a directory tree file (e.g., `T:\Media\Media tree.txt`) and a TVDB data source (e.g., a paste file from TheTVDB), both must be cross-referenced to:
1. Verify physical files exist for database entries
2. Match episode titles (TVDB) to folder names (filesystem) using episode numbers
3. Identify missing or extra episodes

## Naming Convention Differences

### TVDB Paste Data (from TheTVDB.com export)
- Episode folders use **title format**: `S01E17 Masks Of Evil`
- Files use descriptive names with quality tags
- Format: `S01E17 Title (SD/FHD/1080p).ext`
- Example: `S01E17 Masks Of Evil (SD).avi`

### Directory Tree (filesystem)
- Episode folders use **numeric format**: `17.Masks.Of.Evil`
- Files follow same numeric pattern: `17.Masks.Of.Evil.avi`
- Format: `<season_episode_number>.<Title>.<ext>`
- Example: `17.Masks.Of.Evil.avi`

### Mapping Rule
```
TVDB S01E17 → Directory Tree 17
```

## Cross-Reference Procedure

### Step 1: List TVDB-Listed Episodes
From the paste file, extract all episodes with their titles:
- `S01E16 Tales Of Innocence`
- `S01E17 Masks Of Evil`
- `S01E18 Treasure Of The Peacocks Eye`

### Step 2: List Directory Tree Episodes
From the directory tree, extract all folders/files:
- `16.Tales.Of.Innocence.`
- `17.Masks.Of.Evil`
- `18.Treasure.Of.The.Peacocks.Eye`

### Step 3: Match by Episode Number
| TVDB Episode | Tree Folder | Status |
|--------------|-------------|--------|
| S01E16 | 16.Tales.Of.Innocence | ✅ Match |
| S01E17 | 17.Masks.Of.Evil | ✅ Match |
| S01E18 | 18.Treasure.Of.The.Peacocks.Eye | ✅ Match |

### Step 4: Identify Discrepancies
- **Missing episodes**: Episodes in TVDB but not in directory tree
- **Extra episodes**: Episodes in directory tree but not in TVDB
- **Duplicate episodes**: Same episode number appearing multiple times

## Episode Count Verification

### Database State
| Show | TVDB ID | Year | DB Season Count | DB Episode Count | Tree Season Count | Tree Episode Count |
|------|---------|------|-----------------|------------------|-------------------|-------------------|
| The Young Indiana Jones Chronicles (1992) | 72452 | 1992 | None | None | 1 | 22 |
| The Adventures of Young Indiana Jones (1999) | 82643 | 1999 | None | None | 1 | 22 |

### Tree Episode Count Source
- Directory tree shows 22 episodes in `S01E01` through `S01E22`
- Episodes S01E17 and S01E20 were found under numeric folder names (17, 20)

## Verification Checklist

- [ ] **List all TVDB episodes** from the paste file (S01E01-S01E22)
- [ ] **List all directory tree episodes** (numeric folder names)
- [ ] **Match by episode number** (17 → S01E17, 20 → S01E20)
- [ ] **Confirm presence** of each episode in both sources
- [ ] **Flag missing**: TVDB episodes not in directory tree
- [ ] **Flag extra**: Directory tree episodes not in TVDB

## Example Verification

```
TVDB Paste File: S01E09 Demons Of Deception
Directory Tree:   09.Demons.Of.Deception
Status: ✅ Match (episode 9)

TVDB Paste File: S01E17 Masks Of Evil
Directory Tree:   17.Masks.Of.Evil
Status: ✅ Match (episode 17)

TVDB Paste File: S01E20 Mystery Of The Blues
Directory Tree:   20.Mystery.Of.The.Blues
Status: ✅ Match (episode 20)
```

## Notes

- **Do not delete** episodes that exist in either source
- **Flag inconsistencies** to the user, not silently fix them
- **Preserve alternate versions** (user directive): If a tree has multiple files for one episode, keep all
- **Verify after changes**: Re-scan both sources after any modification
