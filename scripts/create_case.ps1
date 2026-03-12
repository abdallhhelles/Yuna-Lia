param(
    [Parameter(Mandatory = $true)]
    [string]$CaseFolder,
    [string]$CaseId = "",
    [int]$Order = 1,
    [string]$Title = "Working Title"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$templatePath = Join-Path $repoRoot "src/yuna_lia/cases/_template"
$destinationPath = Join-Path $repoRoot ("src/yuna_lia/cases/" + $CaseFolder)

if (-not (Test-Path $templatePath)) {
    throw "Template folder not found: $templatePath"
}

if (Test-Path $destinationPath) {
    throw "Target case folder already exists: $destinationPath"
}

Copy-Item -Path $templatePath -Destination $destinationPath -Recurse

if ([string]::IsNullOrWhiteSpace($CaseId)) {
    if ($CaseFolder -match "(\d{3})") {
        $CaseId = "VEL-$($matches[1])"
    }
    else {
        $CaseId = $CaseFolder
    }
}

if ($Title -eq "Working Title") {
    $Title = "$CaseId - Working Title"
}

$configPath = Join-Path $destinationPath "config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$config.is_template = $false
$config.case_id = $CaseId
$config.order = $Order
$config.title = $Title
$config | ConvertTo-Json -Depth 8 | Set-Content -Path $configPath -Encoding UTF8

Write-Host "Created new case folder: $destinationPath"
Write-Host "Next: update dialogue.json, evidence.json, suspects.json, and board_truth/timeline in config.json."
