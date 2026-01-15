@echo off
REM PreOffice Customization Installer for Windows
REM Applies PreOffice UI customizations to LibreOffice

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   PreOffice Customization Installer
echo   Part of the Pre-suite
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "UI_DIR=%SCRIPT_DIR%ui"

REM Detect LibreOffice installation
set "LO_PATH="
if exist "C:\Program Files\LibreOffice" (
    set "LO_PATH=C:\Program Files\LibreOffice"
) else if exist "C:\Program Files (x86)\LibreOffice" (
    set "LO_PATH=C:\Program Files (x86)\LibreOffice"
)

if "%LO_PATH%"=="" (
    echo [ERROR] LibreOffice installation not found
    echo Please install LibreOffice first
    pause
    exit /b 1
)

echo [INFO] LibreOffice found at: %LO_PATH%

REM Set user profile path
set "USER_PROFILE=%APPDATA%\LibreOffice\4\user"
echo [INFO] User profile at: %USER_PROFILE%

REM Create directories
if not exist "%USER_PROFILE%" mkdir "%USER_PROFILE%"
if not exist "%USER_PROFILE%\config" mkdir "%USER_PROFILE%\config"
if not exist "%USER_PROFILE%\template" mkdir "%USER_PROFILE%\template"

REM Install color schemes
echo.
echo [INFO] Installing color schemes...
if not exist "%USER_PROFILE%\registrymodifications" mkdir "%USER_PROFILE%\registrymodifications"
if exist "%UI_DIR%\color-scheme\*.xcu" (
    copy /Y "%UI_DIR%\color-scheme\*.xcu" "%USER_PROFILE%\registrymodifications\" >nul
    echo [SUCCESS] Installed color schemes
)

REM Install icon theme
echo [INFO] Installing icon theme...
if not exist "%USER_PROFILE%\config\images_presearch\cmd" mkdir "%USER_PROFILE%\config\images_presearch\cmd"
if exist "%UI_DIR%\icon-theme\cmd\*.svg" (
    copy /Y "%UI_DIR%\icon-theme\cmd\*.svg" "%USER_PROFILE%\config\images_presearch\cmd\" >nul
    echo [SUCCESS] Installed light theme icons
)

if not exist "%USER_PROFILE%\config\images_presearch_dark\cmd" mkdir "%USER_PROFILE%\config\images_presearch_dark\cmd"
if exist "%UI_DIR%\icon-theme-dark\cmd\*.svg" (
    copy /Y "%UI_DIR%\icon-theme-dark\cmd\*.svg" "%USER_PROFILE%\config\images_presearch_dark\cmd\" >nul
    echo [SUCCESS] Installed dark theme icons
)

REM Install templates
echo [INFO] Installing templates...

if not exist "%USER_PROFILE%\template\PreOffice\Writer" mkdir "%USER_PROFILE%\template\PreOffice\Writer"
if exist "%UI_DIR%\templates\writer\*.fodt" (
    copy /Y "%UI_DIR%\templates\writer\*.fodt" "%USER_PROFILE%\template\PreOffice\Writer\" >nul
    echo [SUCCESS] Installed Writer templates
)

if not exist "%USER_PROFILE%\template\PreOffice\Calc" mkdir "%USER_PROFILE%\template\PreOffice\Calc"
if exist "%UI_DIR%\templates\calc\*.fods" (
    copy /Y "%UI_DIR%\templates\calc\*.fods" "%USER_PROFILE%\template\PreOffice\Calc\" >nul
    echo [SUCCESS] Installed Calc templates
)

if not exist "%USER_PROFILE%\template\PreOffice\Impress" mkdir "%USER_PROFILE%\template\PreOffice\Impress"
if exist "%UI_DIR%\templates\impress\*.fodp" (
    copy /Y "%UI_DIR%\templates\impress\*.fodp" "%USER_PROFILE%\template\PreOffice\Impress\" >nul
    echo [SUCCESS] Installed Impress templates
)

REM Install Start Center branding
echo [INFO] Installing Start Center branding...
if not exist "%USER_PROFILE%\config\startcenter" mkdir "%USER_PROFILE%\config\startcenter"
if exist "%UI_DIR%\startcenter\*.svg" (
    copy /Y "%UI_DIR%\startcenter\*.svg" "%USER_PROFILE%\config\startcenter\" >nul
)
if exist "%UI_DIR%\startcenter\*.xcu" (
    copy /Y "%UI_DIR%\startcenter\*.xcu" "%USER_PROFILE%\config\startcenter\" >nul
)
echo [SUCCESS] Installed Start Center branding

REM Install default settings
echo [INFO] Installing default settings...
if exist "%UI_DIR%\defaults\*.xcu" (
    copy /Y "%UI_DIR%\defaults\*.xcu" "%USER_PROFILE%\registrymodifications\" >nul
    echo [SUCCESS] Installed default settings
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Restart LibreOffice
echo   2. Go to Tools ^> Options ^> View
echo   3. Select 'Presearch' icon theme
echo   4. Access templates via File ^> New ^> Templates
echo.
pause
