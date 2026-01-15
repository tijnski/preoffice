@echo off
REM =============================================================================
REM PreOffice Windows MSI Build Script (Batch wrapper)
REM =============================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set COMMAND=%1

if "%COMMAND%"=="" set COMMAND=build

REM Check for PowerShell
where powershell >nul 2>&1
if errorlevel 1 (
    echo PowerShell is required but not found.
    exit /b 1
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%build-msi.ps1" %COMMAND%

exit /b %ERRORLEVEL%
