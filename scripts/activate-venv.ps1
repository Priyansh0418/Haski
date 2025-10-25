<#
PowerShell helper to activate the project's virtual environment (.venv).

Important: To activate the venv in your CURRENT PowerShell session, dot-source this script:

    . .\scripts\activate-venv.ps1

If you simply run the script (for example `./scripts/activate-venv.ps1`) it executes in a child process
and will not keep the virtual environment activated after the script exits.
#>

[CmdletBinding()]
param()

$venvPath = Join-Path -Path (Get-Location) -ChildPath ".venv\Scripts\Activate.ps1"

if (-not (Test-Path -Path $venvPath)) {
    Write-Host "Virtual environment not found at .venv. Create it with:`n  python -m venv .venv" -ForegroundColor Yellow
    return
}

try {
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force -ErrorAction Stop | Out-Null
} catch {
    Write-Verbose "Unable to set execution policy: $($_.Exception.Message)"
}

. $venvPath

Write-Host "Activated virtualenv at .venv" -ForegroundColor Green
