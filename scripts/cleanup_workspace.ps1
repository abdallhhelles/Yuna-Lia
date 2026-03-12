Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Cleaning generated Python artifacts..." -ForegroundColor Cyan

# Remove local cache folders outside virtual environments.
Get-ChildItem -Path . -Directory -Recurse |
    Where-Object { $_.Name -eq "__pycache__" -and $_.FullName -notmatch "\\.venv\\" } |
    Remove-Item -Recurse -Force

if (Test-Path ".pytest_cache") {
    Remove-Item -Recurse -Force ".pytest_cache"
}

Get-ChildItem -Path . -Directory -Recurse |
    Where-Object { $_.Name -like "*.egg-info" } |
    Remove-Item -Recurse -Force

Write-Host "Workspace cleanup complete." -ForegroundColor Green
