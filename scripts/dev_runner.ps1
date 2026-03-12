param(
    [switch]$Watch = $true
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "Virtual environment not found at .venv" -ForegroundColor Red
    exit 1
}

$watchTargets = @(
    (Join-Path $repoRoot "src"),
    (Join-Path $repoRoot "content"),
    (Join-Path $repoRoot "docs"),
    (Join-Path $repoRoot "main.py"),
    (Join-Path $repoRoot ".env"),
    (Join-Path $repoRoot "pyproject.toml"),
    (Join-Path $repoRoot "README.md")
)

$script:restartRequested = $false

function Start-BotProcess {
    Write-Host ""
    Write-Host "Starting Lia & Yuna persona simulator..." -ForegroundColor Cyan
    return Start-Process -FilePath $pythonExe -ArgumentList "main.py" -WorkingDirectory $repoRoot -PassThru -NoNewWindow
}

function Stop-BotProcess {
    param([System.Diagnostics.Process]$Process)

    if ($null -eq $Process) {
        return
    }

    if (-not $Process.HasExited) {
        Write-Host "Stopping bot process..." -ForegroundColor Yellow
        Stop-Process -Id $Process.Id -Force
        $Process.WaitForExit()
    }
}

function New-Watcher {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return $null
    }

    $isDirectory = (Get-Item $Path) -is [System.IO.DirectoryInfo]
    $watchPath = if ($isDirectory) { $Path } else { Split-Path -Parent $Path }
    $filter = if ($isDirectory) { "*.*" } else { Split-Path -Leaf $Path }

    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $watchPath
    $watcher.Filter = $filter
    $watcher.IncludeSubdirectories = $isDirectory
    $watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, CreationTime, DirectoryName'
    $watcher.EnableRaisingEvents = $true
    return $watcher
}

if (-not $Watch) {
    & $pythonExe "main.py"
    exit $LASTEXITCODE
}

$watchers = @()
$events = @()

foreach ($target in $watchTargets) {
    $watcher = New-Watcher -Path $target
    if ($null -eq $watcher) {
        continue
    }
    $watchers += $watcher
    $events += Register-ObjectEvent -InputObject $watcher -EventName Changed -Action { $script:restartRequested = $true }
    $events += Register-ObjectEvent -InputObject $watcher -EventName Created -Action { $script:restartRequested = $true }
    $events += Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action { $script:restartRequested = $true }
    $events += Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action { $script:restartRequested = $true }
}

$process = $null

try {
    $process = Start-BotProcess
    while ($true) {
        Start-Sleep -Milliseconds 400

        if ($process.HasExited) {
            Write-Host "Bot exited with code $($process.ExitCode)." -ForegroundColor DarkYellow
            if ($process.ExitCode -ne 0) {
                Write-Host "Startup failed. Read the traceback above. Watching for changes before restarting..." -ForegroundColor Red
            }
            Write-Host "Restarting in watch mode..." -ForegroundColor DarkYellow
            Start-Sleep -Seconds 1
            $process = Start-BotProcess
            continue
        }

        if ($script:restartRequested) {
            $script:restartRequested = $false
            Write-Host "Change detected. Restarting bot..." -ForegroundColor Green
            Start-Sleep -Milliseconds 500
            Stop-BotProcess -Process $process
            $process = Start-BotProcess
        }
    }
}
finally {
    Stop-BotProcess -Process $process
    foreach ($event in $events) {
        Unregister-Event -SourceIdentifier $event.Name -ErrorAction SilentlyContinue
        Remove-Job -Id $event.Id -Force -ErrorAction SilentlyContinue
    }
    foreach ($watcher in $watchers) {
        $watcher.EnableRaisingEvents = $false
        $watcher.Dispose()
    }
}
