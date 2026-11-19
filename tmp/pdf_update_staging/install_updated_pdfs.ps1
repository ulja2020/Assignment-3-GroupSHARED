$ErrorActionPreference = 'Stop'
$staging = $PSScriptRoot
$destination = 'C:\Users\claud\PDFs Assignment 3'
if ((Resolve-Path -LiteralPath $destination).Path -ne $destination) { throw 'Unexpected destination.' }
$reports = @('Part_I_SVM_framed.pdf', 'Part_II_CNN.pdf')
foreach ($name in $reports) {
    if (-not (Test-Path -LiteralPath (Join-Path $staging $name))) { throw "Missing report: $name" }
}
foreach ($name in $reports) {
    $source = Join-Path $staging $name
    $expectedHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    $target = Join-Path $destination $name
    Copy-Item -LiteralPath $source -Destination $target -Force
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $expectedHash) { throw "Copy verification failed: $name" }
    Remove-Item -LiteralPath $source
}
$previewFolder = Join-Path $destination 'previews\in_memory_update'
New-Item -ItemType Directory -Path $previewFolder -Force | Out-Null
foreach ($file in Get-ChildItem -LiteralPath $staging -File -Filter '*.png') {
    Move-Item -LiteralPath $file.FullName -Destination (Join-Path $previewFolder $file.Name) -Force
}
Move-Item -LiteralPath (Join-Path $staging 'update_model_reports.py') -Destination (Join-Path $destination 'update_model_reports.py') -Force
$installedScript = Join-Path $destination 'scripts\install_updated_pdfs.ps1'
Write-Host 'Updated both PDFs and verified SHA-256 hashes. PDF scripts and previews are outside the repository.'
Move-Item -LiteralPath $PSCommandPath -Destination $installedScript -Force
