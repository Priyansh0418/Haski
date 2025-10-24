<#
PowerShell helper to activate the project's virtual environment (.venv).

Important: To activate the venv in your CURRENT PowerShell session, dot-source this script:

    . .\scripts\activate-venv.ps1

If you simply run the script (e.g. `./scripts/activate-venv.ps1`) it runs in a child process and will NOT leave the venv activated in your current shell.
#>

param()

$venvPath = Join-Path -Path (Get-Location) -ChildPath '.venv\Scripts\Activate.ps1'

if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found at .venv. Create it with:`n  python -m venv .venv`" -ForegroundColor Yellow
    return
}

# Try to bypass execution policy for this process if needed (does not change system policy)
try {
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null
} catch {
    # non-critical on some systems
}

# Dot-source the real Activate script so the activation persists in the current session
# When this file is dot-sourced, the below invocation will activate the venv in the caller session.
. $venvPath

Write-Host "Activated virtualenv at .venv" -ForegroundColor Green
