@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal enabledelayedexpansion
set AWS_DEFAULT_REGION=ap-northeast-1

REM 多重起動チェック（windows_poller.py が既に実行中なら起動禁止）
tasklist /FI "IMAGENAME eq python.exe" /FO CSV /NH 2>nul | findstr /i "python" >nul
if not errorlevel 1 (
    wmic process where "name='python.exe'" get CommandLine /FORMAT:LIST 2>nul | findstr /i "windows_poller" >nul
    if not errorlevel 1 (
        echo [ERROR] windows_poller.py is already running.
        echo         Stop the existing instance first.
        echo.
        pause
        exit /b 1
    )
)

REM config.env から環境変数を読み込み（コメント行・空行をスキップ）
if exist config.env (
    for /f "usebackq eol=# tokens=1,* delims==" %%A in ("config.env") do (
        if not "%%A"=="" if not "%%B"=="" set "%%A=%%B"
    )
    echo config.env loaded.
) else (
    echo [WARN] config.env not found. Using defaults.
)

REM AWS認証: プロファイルが存在するか確認、なければ直接キー認証にフォールバック
if defined AWS_PROFILE (
    aws configure get aws_access_key_id --profile %AWS_PROFILE% >nul 2>&1
    if errorlevel 1 (
        echo [INFO] AWS_PROFILE=%AWS_PROFILE% が未作成のため直接キー認証を使用
        set "AWS_PROFILE="
        if not defined AWS_ACCESS_KEY_ID (
            echo [ERROR] AWS_ACCESS_KEY_ID も未設定です。setup_windows.bat を実行してください
            pause
            exit /b 1
        )
    )
)
if not defined AWS_PROFILE (
    if not defined AWS_ACCESS_KEY_ID (
        echo [ERROR] AWS認証情報がありません。config.env を確認してください
        pause
        exit /b 1
    )
)

python windows_poller.py
pause
