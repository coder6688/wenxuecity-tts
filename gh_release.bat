@echo off
setlocal enabledelayedexpansion

echo [DEBUG] Starting release process...
echo [DEBUG] Working directory: %cd%

:: Windows version of gh_release.sh

:: Parse command-line arguments with defaults
set VERSION=%1
if "%VERSION%"=="" (
    echo [INFO] No version specified, using default v0.0.4
    set VERSION=v0.0.4
) else (
    echo [INFO] Using specified version: %1
)

set BUILD_DATE=%2
if "%BUILD_DATE%"=="" (
    echo [INFO] Getting current date from system...
    for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value ^| more /e ^| find "LocalDateTime"') do (
        set datetime=%%a
        :: Remove non-digit characters
        set datetime=!datetime:~0,14!
        set datetime=!datetime: =!
    )
    set BUILD_DATE=!datetime:~0,8!
    echo [DEBUG] Raw datetime from WMIC: !datetime!
) else (
    echo [INFO] Using specified build date: %2
)

:: Clean and validate date
set BUILD_DATE=!BUILD_DATE: =!
echo [DEBUG] After cleaning: BUILD_DATE=!BUILD_DATE!

:: Validate date format
echo|set /p="!BUILD_DATE!" > temp_date.txt
findstr /r "^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$" temp_date.txt >nul
del temp_date.txt
if errorlevel 1 (
    echo [ERROR] Invalid date format. Got: '!BUILD_DATE!'
    exit /b 1
)

:: Validate executable exists
set "exe_file=dist\WenxuecityTTS_!BUILD_DATE!.exe"
echo [INFO] Checking for executable: %cd%\!exe_file!
if not exist "!exe_file!" (
    echo [ERROR] Executable not found at: %cd%\!exe_file!
    echo [HELP] Verify these match:
    echo        - Build date in filename: !BUILD_DATE!
    echo        - Actual files in dist:
    dir /b dist\
    echo [ACTION] Try rebuilding with: python build_win.py
    exit /b 1
)

echo [INFO] Checking for GitHub CLI...
:: Validate GH CLI installed
where gh >nul 2>&1
if errorlevel 1 (
    echo [ERROR] GitHub CLI not found. Install from:
    echo         https://cli.github.com/
    exit /b 1
)

echo [INFO] GitHub CLI found.
:: Create GitHub release
echo [INFO] Creating release !VERSION! with date !BUILD_DATE!
echo [DEBUG] Full command:
echo gh release create !VERSION! ^
  --title "Version !VERSION!" ^
  --notes "Release !VERSION! ^(!BUILD_DATE^!)" ^
  "!exe_file!"

gh release create !VERSION! ^
  --title "Version !VERSION!" ^
  --notes "Release !VERSION! ^(!BUILD_DATE^!)" ^
  "!exe_file!"

if errorlevel 1 (
    echo [ERROR] Failed to create release
    exit /b 1
)

echo [SUCCESS] Release !VERSION! created successfully!

:: Usage examples:
:: gh_release.bat                  :: Uses v0.0.4 and current date
:: gh_release.bat v0.1.0           :: Uses v0.1.0 and current date
:: gh_release.bat v0.1.0 20250202  :: Uses specified version and date 