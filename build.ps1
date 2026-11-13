param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & $Python -m PyInstaller --clean --noconfirm LightControl.spec
    if ($LASTEXITCODE -ne 0) { throw 'Falló PyInstaller.' }
    Write-Host 'Build sin firma: dist/LightControl. Puede ser bloqueado por Smart App Control.'
} finally { Pop-Location }
