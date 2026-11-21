# PowerShell path checks and dry-run previews

Use this recipe when examining a Windows media library or previewing a narrow repeated-folder cleanup. It never moves files.

## Validate the target root

```powershell
$root = 'M:\MOVIES\AG\A'
Get-PSDrive -Name M -ErrorAction SilentlyContinue | Select-Object Name,Root,Provider
@('M:\MOVIES', 'M:\MOVIES\AG', $root) | ForEach-Object {
    [pscustomobject]@{ Path = $_; Exists = Test-Path -LiteralPath $_ }
}
```

If the exact path is missing, check only the immediate parent for a likely directory-name variation. Do not silently substitute a nearby path; verify its contents match the user's supplied inventory first.

## Inventory without reading media contents

```powershell
$files = Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction Stop
$dirs = Get-ChildItem -LiteralPath $root -Recurse -Directory -ErrorAction Stop
$videoExt = '.mkv','.mp4','.avi','.mov','.wmv','.m4v','.mpg','.mpeg','.ts','.webm'
$videos = @($files | Where-Object { $videoExt -contains $_.Extension.ToLowerInvariant() })
[pscustomobject]@{
    Folders = $dirs.Count
    Files = $files.Count
    Videos = $videos.Count
    TotalBytes = ($files | Measure-Object Length -Sum).Sum
}
```

## Preview collapse of adjacent repeated folder names only

This is appropriate only when the user wants repeated nesting flattened. It is not a title/year normalizer and must not be described as one.

```powershell
$moves = foreach ($file in $files) {
    $relative = $file.FullName.Substring($root.Length).TrimStart([char]'\')
    $parts = $relative.Split([char]'\')
    $clean = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $parts.Length - 1; $i++) {
        if ($clean.Count -eq 0 -or $clean[$clean.Count - 1] -ine $parts[$i]) {
            [void]$clean.Add($parts[$i])
        }
    }
    if ($clean.Count -lt $parts.Length - 1) {
        $relativeDestination = (@($clean.ToArray()) + $parts[-1]) -join '\'
        [pscustomobject]@{
            Source = $file.FullName
            Destination = Join-Path $root $relativeDestination
            Bytes = $file.Length
        }
    }
}

$targetCollisions = @($moves | Group-Object { $_.Destination.ToLowerInvariant() } | Where-Object Count -gt 1)
$existingTargets = @($moves | Where-Object {
    (Test-Path -LiteralPath $_.Destination) -and $_.Source -ine $_.Destination
})
[pscustomobject]@{
    FilesScanned = $files.Count
    CandidateMoves = @($moves).Count
    CandidateBytes = ($moves | Measure-Object Bytes -Sum).Sum
    TargetCollisions = $targetCollisions.Count
    ExistingTargets = $existingTargets.Count
}
$moves | Select-Object -First 20 Source,Destination
```

Windows path comparisons should be case-insensitive. Treat every existing target and every collision as a stop/skip condition; never overwrite automatically. Before applying any move plan, regenerate and review the full plan, then verify destinations after the move.

PowerShell execution notes

- The terminal tool’s shell is Git Bash on this machine, which mangles backslashes in inline `powershell.exe -Command '...'` scripts (the paths inside the probe arrive corrupted, so ffprobe reports false failures). Write the script to a `.ps1` file with `write_file`, then run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <C:/Users/... path>`. If inline quoting is unavoidable, wrap the script in a single-quoted heredoc (`<<-'PS1'`) so Bash does not expand `$()` or quotes.
- Execution policy is disabled here; run scripts with `-ExecutionPolicy Bypass`
- Move files in-place with `Move-Item -LiteralPath` using a direct path string reconstructed in PowerShell; using `Join-Path` to append a filename containing brackets onto the source path silently re-roots on Windows and can produce nonsensical destinations.
- Keep plan and apply in one script when the user commits: generate the plan, validate counts, then execute — stale counts from an earlier dry run block the commit.
- After the commit, verify counts inside the source root plus the destination root separately; a source-root-only total is expected to shrink.

## Failure-quarantine dry run

1. Probe every video; collect the directories of failures. A directory of failures is moved as a whole when it holds no unrelated media; otherwise move only the failed video and its matching sidecars.
2. Quarantine target may already hold previously quarantined content — preserve it and add only the new failures beneath the explicitly named quarantine root.
3. Preserve the relative path under the quarantine root. Exclude any candidate whose source is an ancestor of a quarantined folder or vice versa.
4. Count files and bytes under each failed folder explicitly; a deeply nested folder that visually repeats the same name is one folder, not many.

## Metadata-based resolution plans and quarantine moves

Use this workflow only when the user asks to derive quality from the video stream or to quarantine probe failures. Filename/path tokens remain the default when they are sufficient.

Probe only the first video stream's dimensions; do not decode the full video:

```powershell
$raw = & $ffprobe -v error -select_streams v:0 `
    -show_entries stream=width,height -of json $video.FullName 2>$null
if ($LASTEXITCODE -ne 0) {
    # Record as unprobed; this alone does not establish corruption.
} else {
    $stream = @(($raw | ConvertFrom-Json).streams)[0]
    if (-not $stream.width -or -not $stream.height) {
        # Record as unclassified.
    } else {
        $longEdge = [Math]::Max([int]$stream.width,[int]$stream.height)
        # Use common tiers only when supported; retain width x height in the plan.
        if ($longEdge -ge 3000) { $tag = '2160p' }
        elseif ($longEdge -ge 2300) { $tag = '1440p' }
        elseif ($longEdge -ge 1750) { $tag = '1080p' }
        elseif ($longEdge -ge 1200) { $tag = '720p' }
        else { $tag = 'SD' }
    }
}
```

Group probe results by the immediate directory containing each video. If a folder has multiple quality classes and the user wants separation, add the highest class to the parent name and route each video into a class subfolder. Inventory directories as well as files: reuse a matching empty child folder, create only a missing one, and stop if a target is nonempty or collides. Move a video with same-stem NFO/subtitle files; leave shared artwork and folder-level metadata at the parent unless the user requests otherwise.

For requested quarantine moves, list probe-failure paths and inspect all videos in each containing release folder. Move the whole release folder with its sidecars/artwork only when it is isolated to the failed release; otherwise move only the failed video and matching same-stem sidecars. Preserve the source-relative directory path beneath the explicitly named quarantine root, and never describe a probe failure as proven corruption.

If quarantine is outside the scanned library root, capture source and destination inventories before the move. Afterward, verify destinations and reconcile combined file counts, media counts, and bytes across both roots; do not expect the source-root totals alone to remain unchanged.