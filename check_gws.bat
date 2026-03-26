@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo   Google Workspace CLI Checker
echo ==========================================
echo.

REM --- Command check ---
echo [1] Command...
gws --version >nul 2>&1
if errorlevel 1 (
    echo   NOT FOUND
    echo.
    echo   Install:
    echo     go install github.com/googleworkspace/cli/cmd/gws@latest
    echo     https://github.com/googleworkspace/cli
    echo.
    echo   Go is required. Install from:
    echo     https://go.dev/dl/
    goto :END
)
echo   OK
echo.

REM --- Version ---
echo [2] Version...
gws --version
echo.

REM --- Path ---
echo [3] Path...
where gws 2>nul
if errorlevel 1 echo   path not found
echo.

REM --- Go version ---
echo [4] Go runtime...
go version >nul 2>&1
if errorlevel 1 (
    echo   Go not found
) else (
    go version
)
echo.

REM --- Auth status ---
echo [5] Auth status...
gws auth status 2>&1
echo.

REM --- Available services ---
echo [6] Available services...
gws help 2>&1
echo.

:END
echo.
pause
