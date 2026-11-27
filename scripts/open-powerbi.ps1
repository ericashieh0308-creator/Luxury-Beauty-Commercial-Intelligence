param(
    [ValidateSet('optimized', 'fallback')]
    [string]$Candidate = 'optimized',
    [switch]$Update
)

$ErrorActionPreference = 'Stop'

function Assert-ExitCode([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed (exit code $LASTEXITCODE)."
    }
}

Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    if ($Update) {
        $changes = git status --porcelain
        Assert-ExitCode 'Git status'
        if ($changes) { throw 'Set aside workspace changes before updating.' }
        git switch build/commercial-intelligence-platform
        Assert-ExitCode 'Branch switch'
        git pull --ff-only origin build/commercial-intelligence-platform
        Assert-ExitCode 'Git pull'
    }

    $python = '.\.venv\Scripts\python.exe'
    $result = & $python -m scripts.prepare_powerbi --candidate $Candidate
    Assert-ExitCode 'Demo generation and candidate validation'
    $session = $result | ConvertFrom-Json
    Write-Host "Validated $Candidate ($($session.pages) pages, $($session.visuals) visuals)."
    Write-Host "DemoRoot = $($session.demo_root)"
    Start-Process -FilePath $session.pbip
}
finally {
    Pop-Location
}
