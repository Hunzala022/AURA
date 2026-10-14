$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($PSScriptRoot)
$project = 'D:\Project AURA'
$private = Join-Path $root '.aura-private'
$active = Join-Path $private 'encryption-cutover-20261014'
$recovery = Join-Path $private 'fyp1-sealed-recovery'
$verify = Join-Path $private 'disposition-verification'
$reportPath = Join-Path $root 'reports/legacy_disposition.json'
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if (-not $report.verified -or $report.phase -ne 'verified-not-retired') { throw 'Verified archives required' }
$allowed = @(
    (Join-Path $root 'aura_memory.db'), (Join-Path $root 'aura_chroma'), (Join-Path $root '.keys'),
    (Join-Path $private 'communication_limits.db'),
    (Join-Path $project 'aura_memory.db'), (Join-Path $project 'aura_chroma'), (Join-Path $project '.keys'),
    (Join-Path $project '.aura-private/containment-20261010/aura_memory.db'),
    (Join-Path $project '.aura-private/containment-20261010/aura_chroma'),
    (Join-Path $project '.aura-private/containment-20261010/.keys'),
    (Join-Path $project '.aura-private/post-rotation-backup-20261010/aura_memory.db'),
    (Join-Path $project '.aura-private/post-rotation-backup-20261010/aura_chroma'),
    (Join-Path $project '.aura-private/post-rotation-backup-20261010/.keys'),
    (Join-Path $private 'encryption-preparation-20261014'),
    (Join-Path $private 'encryption-preparation-20261014-final'),
    (Join-Path $active 'legacy-backup'), (Join-Path $active 'legacy-read-copy'),
    (Join-Path $active 'postcutover-recovery'), (Join-Path $active 'tamper-probes'),
    (Join-Path $project '.aura-private/containment-20261010/staged')
) | ForEach-Object { [IO.Path]::GetFullPath($_) }
function Assert-SafePath([string]$path) {
    $full = [IO.Path]::GetFullPath($path)
    if (-not $full.StartsWith($project+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Outside project' }
    $item = Get-Item -LiteralPath $full -Force
    $cursor = $item
    while ($null -ne $cursor -and $cursor.FullName.StartsWith($project,[StringComparison]::OrdinalIgnoreCase)) {
        if ($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point rejected' }
        $cursor = if ($cursor.PSIsContainer) { $cursor.Parent } else { $cursor.Directory }
    }
    if ($item.PSIsContainer) {
        foreach ($entry in Get-ChildItem -LiteralPath $full -Force -Recurse) {
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Nested reparse point rejected' }
        }
    }
    return $full
}
foreach ($archive in $report.archives) {
    $path = [IO.Path]::GetFullPath((Join-Path $root $archive.archive))
    if (-not $path.StartsWith($recovery+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Archive outside recovery area' }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $archive.sha256) { throw 'Archive checksum changed' }
}
if ($report.retirement_candidates.Count -ne $allowed.Count) { throw 'Target count mismatch' }
# Validate all targets and hashes before removing any target.
foreach ($candidate in $report.retirement_candidates) {
    $path = Assert-SafePath $candidate.path
    if ($allowed -notcontains $path) { throw 'Target not explicitly approved' }
    $item = Get-Item -LiteralPath $path -Force
    $files = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $path -Recurse -Force -File) } else { @($item) }
    $properties = @($candidate.files.PSObject.Properties)
    if ($files.Count -ne $properties.Count) { throw 'Source file inventory changed' }
    foreach ($file in $files) {
        $relative = if ($item.PSIsContainer) { $file.FullName.Substring($path.Length+1) } else { $file.Name }
        $expected = $candidate.files.PSObject.Properties[$relative].Value
        if (-not $expected -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'Source file hash changed' }
    }
}
$verifiedExtraction = Assert-SafePath $verify
if ($verifiedExtraction -ne [IO.Path]::GetFullPath($report.verification_extraction)) { throw 'Extraction target mismatch' }
Remove-Item -LiteralPath $verifiedExtraction -Recurse -Force
foreach ($candidate in $report.retirement_candidates) {
    $path = Assert-SafePath $candidate.path
    Remove-Item -LiteralPath $path -Recurse -Force
}
$report.phase = 'retired'
$report | Add-Member -NotePropertyName retired_target_count -NotePropertyValue $allowed.Count
$report | Add-Member -NotePropertyName verification_extraction_removed -NotePropertyValue (-not (Test-Path -LiteralPath $verify))
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding utf8
Write-Output ('Retired verified runtime targets: '+$allowed.Count)
Write-Output ('Verification extraction removed: '+(-not (Test-Path -LiteralPath $verify)))
