# scripts/installation/windows/build_exe.ps1
param(
    [switch]$Clean  # Pass -Clean to clear all caches and rebuild from scratch
)

Write-Host "========================================"
Write-Host "  Personal Guru - Executable Builder"
Write-Host "========================================"

$ErrorActionPreference = "Stop"

# Determine Project Root (Go up 3 levels from this script: scripts/installation/windows -> root)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..")
Set-Location $ProjectRoot

Write-Host "Project Root: $ProjectRoot"

# Ensure we are in the project root
if (-not (Test-Path "pyproject.toml")) {
    Write-Error "Could not find pyproject.toml in project root. Check paths."
    exit 1
}

# 1. Setup/Activate Virtual Environment
Write-Host "`n[1/4] Setting up Build Environment..."

if ($Clean) {
    Write-Host "Mode: CLEAN BUILD (clearing all caches)"
}
else {
    Write-Host "Mode: INCREMENTAL BUILD (reusing cache)"
}

# Function to remove directory if exists
function Remove-Directory-Force ($path) {
    if (Test-Path $path) {
        Write-Host "Removing existing $path..."
        Remove-Item -Recurse -Force $path
    }
}

# Only clear build environment if -Clean is specified
if ($Clean) {
    Remove-Directory-Force ".build_venv"
}

# Detect Python Executable (Strictly Conda Python 3.11)
$TargetVersion = "3.11"
$PythonExe = $null

Write-Host "Searching for Conda Python $TargetVersion..."

# Helper to check version
function Get-PythonVersion ($exe) {
    if (-not (Test-Path $exe)) { return $null }
    try {
        $ver = & $exe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        return $ver
    } catch {
        return $null
    }
}

# 1. Check Active Conda Env
if ($Env:CONDA_PREFIX) {
    Write-Host "Checking active Conda env: $Env:CONDA_PREFIX"
    $Candidate = Join-Path $Env:CONDA_PREFIX "python.exe"
    $Ver = Get-PythonVersion $Candidate
    if ($Ver -eq $TargetVersion) {
        $PythonExe = $Candidate
        Write-Host "  -> Match found in active env!"
    } else {
        Write-Host "  -> Version mismatch: Found '$Ver', required '$TargetVersion'"
    }
}

# 2. If not found, scan all Conda environments via 'conda info'
if (-not $PythonExe) {
    if (Get-Command "conda" -ErrorAction SilentlyContinue) {
        Write-Host "Scanning local Conda environments..."
        try {
            $JsonOutput = conda info --json 2>$null | Out-String
            $CondaInfo = $JsonOutput | ConvertFrom-Json
            
            foreach ($EnvPath in $CondaInfo.envs) {
                if ($Env:CONDA_PREFIX -and ($EnvPath -eq $Env:CONDA_PREFIX)) { continue }
                
                $Candidate = Join-Path $EnvPath "python.exe"
                $Ver = Get-PythonVersion $Candidate
                if ($Ver -eq $TargetVersion) {
                    $PythonExe = $Candidate
                    Write-Host "  -> Found suitable environment: $EnvPath"
                    break 
                }
            }
        } catch {
            Write-Host "  -> Warning: Failed to query/parse 'conda info'. Is Conda installed?"
        }
    } else {
        Write-Host "  -> 'conda' command not found in PATH."
    }
}

if (-not $PythonExe) {
    Write-Error "BUILD FAILED: Strictly Conda Python $TargetVersion required.`nCould not find a Conda environment with Python $TargetVersion.`nPlease activate one or create one: conda create -n py311 python=3.11"
    exit 1
}

Write-Host "Using Python Executable: $PythonExe"

Write-Host "Creating virtual environment (.build_venv)..."
# Print python version for debugging
& $PythonExe --version
& $PythonExe -m venv .build_venv

# Activate venv
if (Test-Path ".build_venv\Scripts\Activate.ps1") {
    . .build_venv\Scripts\Activate.ps1
}
else {
    Write-Error "Could not find virtual environment activation script."
    exit 1
}

# 2. Install Dependencies
Write-Host "`n[2/4] Installing dependencies..."
python -m pip install --upgrade pip

# Install requirements including local-only libs
# We use the [local] optional dependency group defined in pyproject.toml
Write-Host "Installing project dependencies (this may take a while)..."
python -m pip install ".[local]"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install project dependencies. Please check the error messages above."
    exit $LASTEXITCODE
}

python -m pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install PyInstaller."
    exit $LASTEXITCODE
}

# 3. Clean previous builds (only if -Clean specified)
if ($Clean) {
    Write-Host "`n[3/4] Cleaning previous builds..."
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "PersonalGuru.spec") { Remove-Item -Force "PersonalGuru.spec" }
}
else {
    Write-Host "`n[3/4] Skipping clean (use -Clean flag to clear previous builds)"
}

# 4. Run PyInstaller
Write-Host "`n[4/4] Building Executable..."

# Note: --collect-all ensures hidden imports and data files for complex packages are included
# --add-data "app;app" includes the source code/templates as data for the frozen app to read
# scripts/installation/windows/entry_point.py is the new location

pyinstaller --clean --noconfirm --onefile --console `
    --name "PersonalGuru" `
    --add-data "app;app" `
    --add-data "config.py;." `
    --add-data "migrations;migrations" `
    --collect-all "kokoro_onnx" `
    --collect-all "faster_whisper" `
    --collect-all "misaki" `
    --collect-all "soundfile" `
    --collect-all "flask_session" `
    --collect-all "flask_migrate" `
    --collect-all "flask_login" `
    --collect-all "flask_sqlalchemy" `
    --collect-all "flasgger" `
    --collect-all "weasyprint" `
    --collect-all "markdown_it" `
    --collect-all "cssselect2" `
    --collect-all "tinycss2" `
    --collect-all "tinyhtml5" `
    --collect-all "pyphen" `
    --collect-all "fonttools" `
    --collect-all "pydyf" `
    --collect-all "brotli" `
    --collect-all "zopfli" `
    --collect-all "openai" `
    --collect-all "httpx" `
    --collect-all "authlib" `
    --collect-all "googleapiclient" `
    --collect-all "google_auth_oauthlib" `
    --hidden-import "markdown_it" `
    --hidden-import "googleapiclient" `
    --hidden-import "googleapiclient.discovery" `
    --hidden-import "google_auth_oauthlib" `
    --hidden-import "cssselect2" `
    --hidden-import "tinycss2" `
    --hidden-import "tinyhtml5" `
    --hidden-import "pyphen" `
    --hidden-import "fonttools" `
    --hidden-import "pydyf" `
    --hidden-import "brotli" `
    --hidden-import "zopfli" `
    --hidden-import "openai" `
    --hidden-import "httpx" `
    --hidden-import "authlib" `
    --hidden-import "flask_session" `
    --hidden-import "flask_migrate" `
    --hidden-import "flask_login" `
    --hidden-import "flask_sqlalchemy" `
    --hidden-import "faster_whisper.assets" `
    --hidden-import "misaki.cutlet" `
    --hidden-import "misaki.he" `
    --hidden-import "misaki.ja" `
    --hidden-import "misaki.ko" `
    --hidden-import "misaki.tone_sandhi" `
    --hidden-import "misaki.transcription" `
    --hidden-import "misaki.vi" `
    --hidden-import "misaki.zh" `
    --icon "app/static/favicon.ico" `
    scripts/installation/windows/entry_point.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

if (Test-Path "dist/PersonalGuru.exe") {
    Write-Host "`n========================================"
    Write-Host "SUCCESS! Executable created at: dist/PersonalGuru.exe"
    Write-Host "========================================"
    Write-Host "Note: When running the exe, it will generate data/sandbox and site.db in the same directory."
}
else {
    Write-Error "Build failed. checking logs..."
}
