@echo off
cd /d "%~dp0"
set AWS_PROFILE=chatwork-webhook
set AWS_DEFAULT_REGION=ap-northeast-1

REM config.env から環境変数を読み込み
if exist config.env (
    for /f "usebackq tokens=1,* delims==" %%A in ("config.env") do (
        REM #で始まるコメント行と空行をスキップ
        echo %%A | findstr /r "^#" >nul || (
            if not "%%A"=="" set "%%A=%%B"
        )
    )
    echo config.env loaded.
) else (
    echo [WARN] config.env not found. Using defaults.
)

python windows_poller.py
pause
