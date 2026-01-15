# Presearch Office Edition - Windows Installer
# Installs LibreOffice + Presearch customizations

param(
    [switch]$SkipLibreOffice,
    [switch]$Silent
)

$ErrorActionPreference = "Stop"

# Configuration
$LO_VERSION = "24.8.4"
$LO_MSI_URL = "https://download.documentfoundation.org/libreoffice/stable/$LO_VERSION/win/x86_64/LibreOffice_${LO_VERSION}_Win_x86-64.msi"
$LO_INSTALL_PATH = "$env:ProgramFiles\LibreOffice"
$USER_PROFILE = "$env:APPDATA\LibreOffice\4\user"

Write-Host "=========================================="
Write-Host "  Presearch Office Edition Installer"
Write-Host "  Windows"
Write-Host "=========================================="
Write-Host ""

function Test-LibreOffice {
    if (Test-Path $LO_INSTALL_PATH) {
        Write-Host "LibreOffice is already installed at: $LO_INSTALL_PATH"
        if (-not $Silent) {
            $skip = Read-Host "Skip LibreOffice installation? (Y/n)"
            if ($skip -ne "n" -and $skip -ne "N") {
                return $true
            }
        }
        return $true
    }
    return $false
}

function Install-LibreOffice {
    Write-Host "Downloading LibreOffice $LO_VERSION..."

    $tempDir = [System.IO.Path]::GetTempPath()
    $msiPath = Join-Path $tempDir "LibreOffice.msi"

    Invoke-WebRequest -Uri $LO_MSI_URL -OutFile $msiPath

    Write-Host "Installing LibreOffice..."

    $installArgs = "/i `"$msiPath`" /qn ALLUSERS=1"
    Start-Process msiexec.exe -ArgumentList $installArgs -Wait -NoNewWindow

    Write-Host "Cleaning up..."
    Remove-Item $msiPath -Force

    Write-Host "LibreOffice installed successfully!"
}

function Install-Extension {
    Write-Host ""
    Write-Host "Installing Presearch Tools extension..."

    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $presearchDir = Split-Path -Parent (Split-Path -Parent $scriptDir)
    $extensionPath = Join-Path $presearchDir "extension\dist\presearch-tools.oxt"

    if (-not (Test-Path $extensionPath)) {
        Write-Host "Warning: Extension not found at $extensionPath"
        Write-Host "Please build the extension first using build.sh"
        return
    }

    # Find unopkg
    $unopkg = Join-Path $LO_INSTALL_PATH "program\unopkg.exe"

    if (Test-Path $unopkg) {
        & $unopkg add $extensionPath
        Write-Host "Extension installed successfully!"
    } else {
        Write-Host "Warning: unopkg not found. Please install extension manually."
        Write-Host "Extension path: $extensionPath"
    }
}

function Install-IconTheme {
    Write-Host ""
    Write-Host "Installing Presearch icon theme..."

    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $presearchDir = Split-Path -Parent (Split-Path -Parent $scriptDir)
    $themePath = Join-Path $presearchDir "icon-theme\dist\images_presearch.zip"

    if (-not (Test-Path $themePath)) {
        Write-Host "Warning: Icon theme not found at $themePath"
        Write-Host "Please build the icon theme first using build.sh"
        return
    }

    # Create user config directory
    $configDir = Join-Path $USER_PROFILE "config"
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }

    # Copy theme
    Copy-Item $themePath -Destination $configDir -Force
    Write-Host "Icon theme installed successfully!"
}

function Set-Defaults {
    Write-Host ""
    Write-Host "Configuring defaults..."

    # Create user profile directory if needed
    if (-not (Test-Path $USER_PROFILE)) {
        New-Item -ItemType Directory -Path $USER_PROFILE -Force | Out-Null
    }

    Write-Host "Default configuration applied."
    Write-Host "Note: To set Presearch icon theme, go to:"
    Write-Host "  Tools -> Options -> View -> Icon Theme -> Presearch"
}

# Main
function Main {
    if (-not $Silent) {
        Write-Host "This installer will:"
        Write-Host "  1. Install LibreOffice (if not present)"
        Write-Host "  2. Install Presearch Tools extension"
        Write-Host "  3. Install Presearch icon theme"
        Write-Host "  4. Configure defaults"
        Write-Host ""
        $confirm = Read-Host "Continue? (Y/n)"

        if ($confirm -eq "n" -or $confirm -eq "N") {
            Write-Host "Installation cancelled."
            exit 0
        }
    }

    # Step 1: LibreOffice
    if (-not $SkipLibreOffice -and -not (Test-LibreOffice)) {
        Install-LibreOffice
    }

    # Step 2: Extension
    Install-Extension

    # Step 3: Icon Theme
    Install-IconTheme

    # Step 4: Defaults
    Set-Defaults

    Write-Host ""
    Write-Host "=========================================="
    Write-Host "  Installation Complete!"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "To start Presearch Office Edition:"
    Write-Host "  Start Menu -> LibreOffice"
    Write-Host ""
    Write-Host "You'll find Presearch tools in the menu bar."
}

Main
