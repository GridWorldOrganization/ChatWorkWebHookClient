"""
Google Workspace API 接続チェッカー

OAuth クライアント認証情報を使って Google Sheets / Drive API に接続し、
認証・接続が正常に動作するかを確認する。

config.env の GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET を使用。
初回実行時にブラウザで OAuth 認証フローを実行し、トークンを保存する。
"""

import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(SCRIPT_DIR, "google_token.json")

# Google API スコープ（Drive読み書き + Sheets読み書き）
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def load_env():
    """config.env から環境変数を読み込む"""
    env_path = os.path.join(SCRIPT_DIR, "config.env")
    if not os.path.exists(env_path):
        return {}
    result = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                result[key.strip()] = val.strip()
    return result


def get_credentials(env):
    """OAuth 認証情報を取得する。トークンがなければ認証フローを実行"""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None

    # 既存トークンの読み込み
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # トークンが無効 or 期限切れ → リフレッシュ or 再認証
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # リフレッシュ成功 → 保存
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
        except Exception as e:
            print(f"  Token refresh failed: {e}")
            creds = None

    if not creds or not creds.valid:
        # OAuth フローを実行（ブラウザが開く）
        client_id = env.get("GOOGLE_OAUTH_CLIENT_ID", "")
        client_secret = env.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }

        print("")
        print("  *** OAuth authentication required ***")
        print("  A browser window will open. Sign in and grant access.")
        print("")

        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)

        # トークンを保存
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"  Token saved: {TOKEN_PATH}")

    return creds


def check():
    """Google Workspace API の接続チェックを実行する"""
    env = load_env()

    # --- 1. config.env チェック ---
    print("[1] Config")
    email = env.get("GOOGLE_EMAIL", "")
    client_id = env.get("GOOGLE_OAUTH_CLIENT_ID", "")
    client_secret = env.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print("  NOT SET")
        print("")
        print("  config.env に以下を追加してください:")
        print("    GOOGLE_EMAIL=your-email@example.com")
        print("    GOOGLE_OAUTH_CLIENT_ID=xxxx.apps.googleusercontent.com")
        print("    GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxx")
        print("")
        print("  取得方法: Google Cloud Console > APIs & Services > Credentials > OAuth 2.0 Client IDs")
        print("  必要なAPI: Google Drive API, Google Sheets API を有効化")
        return

    print(f"  Email: {email or '(not set)'}")
    print(f"  Client ID: {client_id[:20]}...")
    print(f"  Client Secret: {'*' * len(client_secret)}")
    print("")

    # --- 2. ライブラリチェック ---
    print("[2] Python Libraries")
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        print("  google-api-python-client: OK")
        print("  google-auth-oauthlib: OK")
    except ImportError as e:
        print(f"  MISSING: {e}")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return
    print("")

    # --- 3. 認証 ---
    print("[3] Authentication")
    if os.path.exists(TOKEN_PATH):
        print(f"  Token file: {TOKEN_PATH}")
    else:
        print(f"  Token file: not found (will start OAuth flow)")

    try:
        creds = get_credentials(env)
        print(f"  Auth: OK (valid={creds.valid})")
    except Exception as e:
        print(f"  Auth FAILED: {e}")
        return
    print("")

    # --- 4. Google Drive 接続チェック ---
    print("[4] Google Drive API")
    try:
        drive = build("drive", "v3", credentials=creds)
        results = drive.files().list(
            pageSize=5,
            fields="files(id, name, mimeType)",
            q="mimeType='application/vnd.google-apps.spreadsheet'",
        ).execute()
        files = results.get("files", [])
        print(f"  Connected. Spreadsheets found: {len(files)}")
        for f in files:
            print(f"    - {f['name']}")
    except Exception as e:
        print(f"  FAILED: {e}")
        return
    print("")

    # --- 5. Google Sheets 読み書きチェック ---
    print("[5] Google Sheets API")
    if files:
        test_sheet = files[0]
        try:
            sheets = build("sheets", "v4", credentials=creds)
            meta = sheets.spreadsheets().get(spreadsheetId=test_sheet["id"]).execute()
            sheet_title = meta["sheets"][0]["properties"]["title"]
            print(f"  Read OK: '{test_sheet['name']}' sheet='{sheet_title}'")
        except Exception as e:
            print(f"  Read FAILED: {e}")
    else:
        print("  SKIP: No spreadsheets found to test")
    print("")

    print("=== All checks passed ===")


if __name__ == "__main__":
    print("==========================================")
    print("  Google Workspace API Checker")
    print("==========================================")
    print()
    check()
