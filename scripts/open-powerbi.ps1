$ErrorActionPreference = 'Stop'

function Assert-ExitCode([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed (exit code $LASTEXITCODE)."
    }
}

Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $changes = git status --porcelain
    Assert-ExitCode 'Git status'
    if ($changes) { throw 'Commit or set aside workspace changes before updating this project.' }

    git switch build/commercial-intelligence-platform
    Assert-ExitCode 'Branch switch'
    git pull --ff-only origin build/commercial-intelligence-platform
    Assert-ExitCode 'Git pull'

    $python = '.\.venv\Scripts\python.exe'
    & $python -m beauty.demo
    Assert-ExitCode 'Synthetic demo generation'
    & $python -m scripts.validate_powerbi
    Assert-ExitCode 'Power BI validation'

    Write-Host "DemoRoot = $((Resolve-Path 'output/demo').Path)"
    Start-Process (Resolve-Path 'dashboard/powerbi/Luxury_Beauty_Commercial_Intelligence.pbip').Path
}
finally {
    Pop-Location
}
