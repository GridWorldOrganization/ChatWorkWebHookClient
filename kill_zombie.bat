@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ==========================================
echo   Zombie Process Killer
echo ==========================================
echo.

set COUNT=0

REM --- windows_poller.py を実行中の python.exe を検出 ---
echo [1] Poller processes (python + windows_poller.py)
echo.
for /f "tokens=2 delims=," %%P in ('wmic process where "name='python.exe'" get ProcessId /FORMAT:CSV 2^>nul ^| findstr /r "[0-9]"') do (
    set "PID=%%P"
    wmic process where "ProcessId=!PID!" get CommandLine /FORMAT:LIST 2>nul | findstr /i "windows_poller" >nul
    if not errorlevel 1 (
        set /a COUNT+=1
        set "PID_!COUNT!=!PID!"
        echo   !COUNT!. python.exe  PID=!PID!  [windows_poller.py]
    )
)

REM --- claude.exe (Native) ---
echo.
echo [2] Claude processes (Native)
echo.
for /f "tokens=1,2 delims=," %%A in ('tasklist /FO CSV /NH 2^>nul ^| findstr /i "claude.exe"') do (
    set /a COUNT+=1
    set "PID_!COUNT!=%%~B"
    echo   !COUNT!. %%~A  PID=%%~B  [Native]
)

REM --- node.exe (npm claude) ---
echo.
echo [3] Claude processes (npm/node)
echo.
for /f "tokens=2 delims=," %%P in ('wmic process where "name='node.exe'" get ProcessId /FORMAT:CSV 2^>nul ^| findstr /r "[0-9]"') do (
    set "PID=%%P"
    wmic process where "ProcessId=!PID!" get CommandLine /FORMAT:LIST 2>nul | findstr /i "claude" >nul
    if not errorlevel 1 (
        set /a COUNT+=1
        set "PID_!COUNT!=!PID!"
        echo   !COUNT!. node.exe  PID=!PID!  [npm]
    )
)

echo.
echo ------------------------------------------

if !COUNT!==0 (
    echo   No zombie processes found.
    echo.
    if exist ".claude_pids" (
        echo   .claude_pids found. Cleaning up...
        del ".claude_pids"
        echo   .claude_pids deleted.
    )
    goto :END
)

echo   Total: !COUNT! process(es) found.
echo.
echo   [a] Kill ALL
echo   [q] Quit
echo.
set /p CHOICE="Select: "

if /i "!CHOICE!"=="q" goto :END

if /i "!CHOICE!"=="a" (
    echo.
    echo Killing all...
    for /L %%i in (1,1,!COUNT!) do (
        call set "KILL_PID=%%PID_%%i%%"
        taskkill /F /PID !KILL_PID! >nul 2>&1
        echo   Killed PID=!KILL_PID!
    )
    if exist ".claude_pids" del ".claude_pids"
    echo.
    echo Done. All zombie processes killed.
)

:END
echo.
pause
