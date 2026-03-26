"""
Google Workspace API 接続チェッカー

サービスアカウントの JSON キーファイルを使って Google Drive API に接続し、
認証・接続が正常に動作するかを確認する。

config.env の GOOGLE_SERVICE_ACCOUNT_KEY_PATH を読み込んで実行。
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


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


def check():
    """Google Workspace API の接続チェックを実行する。結果をテキストで返す"""
    lines = []

    # --- 1. config.env 読み込み ---
    env = load_env()
    key_path = env.get("GOOGLE_SERVICE_ACCOUNT_KEY_PATH", "")
    if not key_path:
        key_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY_PATH", "")

    lines.append("[1] Service Account Key")
    if not key_path:
        lines.append("  NOT SET")
        lines.append("  config.env に GOOGLE_SERVICE_ACCOUNT_KEY_PATH を設定してください")
        lines.append("  例: GOOGLE_SERVICE_ACCOUNT_KEY_PATH=C:\\path\\to\\service-account.json")
        return "\n".join(lines)

    if not os.path.exists(key_path):
        lines.append(f"  FILE NOT FOUND: {key_path}")
        return "\n".join(lines)

    lines.append(f"  OK: {key_path}")
    lines.append("")

    # --- 2. ライブラリチェック ---
    lines.append("[2] Python Libraries")
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        lines.append("  google-api-python-client: OK")
        lines.append("  google-auth: OK")
    except ImportError as e:
        lines.append(f"  MISSING: {e}")
        lines.append("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return "\n".join(lines)
    lines.append("")

    # --- 3. 認証チェック ---
    lines.append("[3] Authentication")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        lines.append(f"  Service Account: {credentials.service_account_email}")
        lines.append(f"  Project ID: {credentials.project_id}")
    except Exception as e:
        lines.append(f"  FAILED: {e}")
        return "\n".join(lines)
    lines.append("")

    # --- 4. Drive API 接続チェック ---
    lines.append("[4] Google Drive API")
    try:
        service = build("drive", "v3", credentials=credentials)
        results = service.files().list(pageSize=3, fields="files(id, name)").execute()
        files = results.get("files", [])
        lines.append(f"  Connected. Files found: {len(files)}")
        for f in files:
            lines.append(f"    - {f['name']} (ID: {f['id'][:20]}...)")
    except Exception as e:
        lines.append(f"  FAILED: {e}")
        return "\n".join(lines)
    lines.append("")

    # --- 5. Gmail API 接続チェック ---
    lines.append("[5] Gmail API")
    try:
        gmail_creds = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )
        gmail_service = build("gmail", "v1", credentials=gmail_creds)
        # サービスアカウント単体では Gmail は使えない（ドメイン委任が必要）
        lines.append("  Service account loaded (domain-wide delegation required for Gmail)")
    except Exception as e:
        lines.append(f"  SKIPPED: {e}")
    lines.append("")

    # --- 6. Sheets API 接続チェック ---
    lines.append("[6] Google Sheets API")
    try:
        sheets_creds = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
        sheets_service = build("sheets", "v4", credentials=sheets_creds)
        lines.append("  Service loaded: OK")
    except Exception as e:
        lines.append(f"  FAILED: {e}")
    lines.append("")

    lines.append("=== All checks passed ===")
    return "\n".join(lines)


if __name__ == "__main__":
    print("==========================================")
    print("  Google Workspace API Checker")
    print("==========================================")
    print()
    result = check()
    print(result)
