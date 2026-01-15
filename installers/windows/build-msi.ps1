# =============================================================================
# PreOffice Windows MSI Installer Build Script (PowerShell)
# Creates an MSI installer for Windows using WiX Toolset
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "clean", "harvest", "help")]
    [string]$Command = "build"
)

$ErrorActionPreference = "Stop"

# Configuration
$ProductName = "PreOffice"
$ProductVersion = "1.0.0"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$BuildDir = Join-Path $ProjectRoot "build\windows"
$DistDir = Join-Path $ProjectRoot "dist"
$SourceDir = Join-Path $ProjectRoot "instdir"

# WiX Toolset paths (adjust as needed)
$WixPath = "C:\Program Files (x86)\WiX Toolset v3.11\bin"
if (!(Test-Path $WixPath)) {
    $WixPath = "C:\Program Files\WiX Toolset v3.14\bin"
}

# Colors
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Write-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# =============================================================================
# Functions
# =============================================================================

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."

    # Check for WiX Toolset
    if (!(Test-Path "$WixPath\candle.exe")) {
        Write-Error "WiX Toolset not found at $WixPath"
        Write-Info "Download WiX Toolset from: https://wixtoolset.org/releases/"
        exit 1
    }

    # Check for LibreOffice build
    if (!(Test-Path $SourceDir)) {
        Write-Error "LibreOffice build not found at $SourceDir"
        Write-Info "Please build LibreOffice first"
        exit 1
    }

    Write-Success "Prerequisites check complete"
}

function New-Directories {
    Write-Info "Creating build directories..."

    New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
    New-Item -ItemType Directory -Force -Path $DistDir | Out-Null
    New-Item -ItemType Directory -Force -Path "$BuildDir\icons" | Out-Null
    New-Item -ItemType Directory -Force -Path "$BuildDir\images" | Out-Null
    New-Item -ItemType Directory -Force -Path "$BuildDir\license" | Out-Null
    New-Item -ItemType Directory -Force -Path "$BuildDir\extensions" | Out-Null

    Write-Success "Directories created"
}

function Copy-Resources {
    Write-Info "Copying resources..."

    # Copy WiX source
    Copy-Item "$ScriptDir\PreOffice.wxs" "$BuildDir\" -Force

    # Copy license
    if (Test-Path "$ProjectRoot\presearch\extension\license\MIT.txt") {
        # Convert to RTF for WiX
        $license = Get-Content "$ProjectRoot\presearch\extension\license\MIT.txt" -Raw
        $rtf = "{\rtf1\ansi\deff0 {\fonttbl {\f0 Courier New;}}`r`n\f0\fs18 $license`r`n}"
        $rtf | Out-File "$BuildDir\license\MIT.rtf" -Encoding ASCII
    }

    # Copy extension
    if (Test-Path "$ProjectRoot\presearch\extension\PreOffice-1.0.0.oxt") {
        Copy-Item "$ProjectRoot\presearch\extension\PreOffice-1.0.0.oxt" "$BuildDir\extensions\" -Force
    }

    # Create placeholder icons if not exist
    if (!(Test-Path "$ScriptDir\icons\preoffice.ico")) {
        Write-Warning "Icon file not found - creating placeholder"
        # In production, you'd have a proper .ico file
    }

    Write-Success "Resources copied"
}

function Invoke-Harvest {
    Write-Info "Harvesting files from LibreOffice build..."

    $heat = "$WixPath\heat.exe"
    $harvestOutput = "$BuildDir\HarvestedFiles.wxs"

    # Harvest the program directory
    & $heat dir "$SourceDir\program" `
        -cg ProgramFilesGroup `
        -dr INSTALLFOLDER `
        -srd `
        -ag `
        -sfrag `
        -sreg `
        -var var.SourceDir `
        -out $harvestOutput

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Harvest failed"
        exit 1
    }

    Write-Success "Files harvested to $harvestOutput"
}

function Build-MSI {
    Write-Info "Building MSI installer..."

    $candle = "$WixPath\candle.exe"
    $light = "$WixPath\light.exe"

    Push-Location $BuildDir
    try {
        # Compile WiX sources
        Write-Info "Compiling WiX sources..."
        & $candle PreOffice.wxs `
            -dSourceDir="$SourceDir" `
            -dProductVersion="$ProductVersion" `
            -ext WixUIExtension `
            -arch x64 `
            -out PreOffice.wixobj

        if ($LASTEXITCODE -ne 0) {
            Write-Error "Candle (compile) failed"
            exit 1
        }

        # Link to create MSI
        Write-Info "Linking MSI..."
        $msiOutput = Join-Path $DistDir "$ProductName-$ProductVersion-x64.msi"

        & $light PreOffice.wixobj `
            -ext WixUIExtension `
            -cultures:en-us `
            -out $msiOutput

        if ($LASTEXITCODE -ne 0) {
            Write-Error "Light (link) failed"
            exit 1
        }

        Write-Success "MSI created: $msiOutput"
        Write-Info "Size: $([math]::Round((Get-Item $msiOutput).Length / 1MB, 2)) MB"

    } finally {
        Pop-Location
    }
}

function Clean-Build {
    Write-Info "Cleaning build artifacts..."

    if (Test-Path $BuildDir) {
        Remove-Item -Recurse -Force $BuildDir
    }

    Write-Success "Clean complete"
}

function Show-Help {
    @"
PreOffice Windows MSI Installer Build Script

Usage: .\build-msi.ps1 [command]

Commands:
    build    Build the MSI installer (default)
    clean    Remove build artifacts
    harvest  Harvest files from LibreOffice build
    help     Show this help message

Prerequisites:
    - WiX Toolset 3.11+ (https://wixtoolset.org/releases/)
    - LibreOffice built in $ProjectRoot\instdir

Examples:
    .\build-msi.ps1 build    # Build the MSI
    .\build-msi.ps1 clean    # Clean build artifacts

"@
}

# =============================================================================
# Main
# =============================================================================

switch ($Command) {
    "build" {
        Test-Prerequisites
        New-Directories
        Copy-Resources
        # Invoke-Harvest  # Uncomment when ready to harvest all files
        Build-MSI
    }
    "clean" {
        Clean-Build
    }
    "harvest" {
        Test-Prerequisites
        Invoke-Harvest
    }
    "help" {
        Show-Help
    }
}
