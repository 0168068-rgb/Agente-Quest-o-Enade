param([string]$InnoCompiler = "")
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
if ($env:OS -ne "Windows_NT") { throw "Execute este script em Windows 10/11 de 64 bits." }
Set-Location $PSScriptRoot

function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Falha em $Program (código $LASTEXITCODE). Geração interrompida." }
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Instale Python 3.12 de 64 bits, incluindo o Python Launcher (py). Consulte LEIA-ME.md."
}
if (-not $InnoCompiler) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $InnoCompiler = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $InnoCompiler) {
        $command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
        if ($command) { $InnoCompiler = $command.Source }
    }
}
if (-not $InnoCompiler -or -not (Test-Path $InnoCompiler)) {
    throw "Instale Inno Setup 6 ou informe -InnoCompiler 'C:\caminho\ISCC.exe'."
}
Invoke-Checked "py" @("-3.12", "-c", "import struct,sys; assert struct.calcsize('P') == 8 and sys.version_info[:2] == (3,12), 'Use Python 3.12 de 64 bits'")
Invoke-Checked "py" @("-3.12", "-m", "venv", ".venv-windows")
$python = Join-Path $PSScriptRoot ".venv-windows\Scripts\python.exe"
Invoke-Checked $python @("-m", "pip", "install", "--disable-pip-version-check", "-r", "requirements-build.txt")

$previousBrowserPath = $env:PLAYWRIGHT_BROWSERS_PATH
try {
    $env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $PSScriptRoot "build_browsers"
    Invoke-Checked $python @("-m", "playwright", "install", "chromium")
    Invoke-Checked $python @("-m", "unittest", "discover", "-s", "tests", "-v")
    Invoke-Checked $python @("-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", "--windowed",
        "--name", "LancadorNotasSophia", "--collect-all", "playwright", "--hidden-import", "xlrd",
        "--hidden-import", "openpyxl", "--add-data", "build_browsers;browsers", "main.py")
    New-Item -ItemType Directory -Path "dist\LancadorNotasSophia" -Force | Out-Null
    Copy-Item "LEIA-ME.md" "dist\LancadorNotasSophia\LEIA-ME.md"
    Invoke-Checked $InnoCompiler @("instalador.iss")
    & $python -m pip freeze | Set-Content -Encoding UTF8 "dist\dependencias-windows.txt"
    if ($LASTEXITCODE -ne 0) { throw "Não foi possível registrar as versões das dependências." }
    Write-Host ""
    Write-Host "Instalador gerado em: $PSScriptRoot\dist\instalador\LancadorNotasSophia-Setup-1.0.0.exe"
    Write-Host "Teste a instalação em uma conta sem Python, primeiro em simulação."
} finally {
    if ($null -eq $previousBrowserPath) { Remove-Item Env:PLAYWRIGHT_BROWSERS_PATH -ErrorAction SilentlyContinue }
    else { $env:PLAYWRIGHT_BROWSERS_PATH = $previousBrowserPath }
}
