$ErrorActionPreference = 'Stop'
$projectRoot = 'C:\Users\claud\Assignment-3-GroupSHARED'
$destinationRoot = 'C:\Users\claud\PDFs Assignment 3'
$resolvedDestination = (Resolve-Path -LiteralPath $destinationRoot).Path
if ($resolvedDestination -ne $destinationRoot) { throw 'Unexpected destination folder.' }

$draftFolder = Join-Path $projectRoot 'Assignment-3\drafts\draft-A'
$temporaryFolder = Join-Path $projectRoot 'tmp'
$moves = @()
foreach ($file in Get-ChildItem -LiteralPath $draftFolder -File -Filter '*.pdf') {
    $moves += [pscustomobject]@{ Source = $file.FullName; Target = Join-Path $destinationRoot $file.Name }
}
foreach ($file in Get-ChildItem -LiteralPath $temporaryFolder -File) {
    if ($file.Extension -in @('.png', '.py')) {
        $subfolder = if ($file.Extension -eq '.png') { 'previews' } else { 'scripts' }
        $target = if ($file.Name -eq 'update_reports.py') {
            Join-Path $destinationRoot $file.Name
        } else {
            Join-Path (Join-Path $destinationRoot $subfolder) $file.Name
        }
        $moves += [pscustomobject]@{ Source = $file.FullName; Target = $target }
    }
}
$oldReview = Join-Path $temporaryFolder 'ii3_pdf_review'
if (Test-Path -LiteralPath $oldReview) {
    foreach ($file in Get-ChildItem -LiteralPath $oldReview -File -Filter '*.png') {
        $moves += [pscustomobject]@{
            Source = $file.FullName
            Target = Join-Path (Join-Path $destinationRoot 'previews\ii3_pdf_review') $file.Name
        }
    }
}

# Check every move before changing any file. Never overwrite existing files.
foreach ($move in $moves) {
    $resolvedSource = (Resolve-Path -LiteralPath $move.Source).Path
    if (-not $resolvedSource.StartsWith($projectRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Source is outside the project: $resolvedSource"
    }
    if (-not $move.Target.StartsWith($destinationRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Target is outside the destination: $($move.Target)"
    }
    if (Test-Path -LiteralPath $move.Target) { throw "Destination already exists: $($move.Target)" }
}
foreach ($move in $moves) {
    $parent = Split-Path -Parent $move.Target
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    Move-Item -LiteralPath $move.Source -Destination $move.Target
}
Write-Host "Moved $($moves.Count) files to $destinationRoot"
Write-Host 'Future execution-instructions PDF updates: run update_reports.py in the destination folder with a Python environment containing reportlab, pypdf and pdfplumber.'
Write-Host 'Notebooks, project modules, data and models remain in the repository. Earlier scripts are retained in scripts as historical working files.'
