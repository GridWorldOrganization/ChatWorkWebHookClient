# ChatWork Webhook Client

ChatWork のメッセージを SQS 経由で受信し、Claude Code を使って AI が自動返信するシステムです。

## 構成

```
ChatWorkWebHookClient/
├── windows_poller.py       # SQSポーリング + Claude Code 実行 + Chatwork返信
├── start_poller.bat        # 起動スクリプト（ダブルクリックで起動）
├── setup_windows.bat       # 初回セットアップスクリプト
├── config.env.example      # 環境変数テンプレート
├── clients/
│   ├── 00_common_rules.md  # 全メンバー共通ルール
│   ├── 01_yokota/          # メンバー個別フォルダ（.gitignore対象）
│   │   └── 01_persona.md
│   └── 02_fujino/          # メンバー個別フォルダ（.gitignore対象）
│       └── 01_persona.md
└── .gitignore
```

## セットアップ（新しいPCで使う場合）

### 1. リポジトリを取得

```
git clone https://github.com/GridWorldOrganization/ChatWorkWebHookClient
cd ChatWorkWebHookClient
```

### 2. setup_windows.bat を編集

`setup_windows.bat` を開き、AWSキーを実際の値に書き換えます。

```bat
aws configure set aws_access_key_id YOUR_AWS_ACCESS_KEY_ID ...
aws configure set aws_secret_access_key YOUR_AWS_SECRET_ACCESS_KEY ...
```

### 3. config.env を作成

`config.env.example` をコピーして `config.env` を作成し、実際の値を設定します。

```
FOLLOWUP_WAIT_SECONDS=30
```

### 4. setup_windows.bat を実行

ダブルクリックで実行します。以下が自動でセットアップされます。

- boto3 インストール
- AWS プロファイル `chatwork-webhook` の設定
- 環境変数の設定

### 5. メンバーフォルダを作成

`clients/` 直下に各メンバーのフォルダを作成し、ペルソナファイルを配置します。

```
clients/
├── 01_yokota/
│   └── 01_persona.md   ← 横田百恵のキャラクター設定
└── 02_fujino/
    └── 01_persona.md   ← 藤野楓のキャラクター設定
```

> `clients/01_*/` と `clients/02_*/` は `.gitignore` 対象です。
> トークンや個人情報が含まれるため、Git には含まれません。

### 6. 起動

`start_poller.bat` をダブルクリックします。

## 動作の仕組み

1. SQS キューから Chatwork Webhook イベントを受信
2. 宛先メンバー（`[To:ACCOUNT_ID]` または `[rp aid=ACCOUNT_ID` のメンション）を特定
3. `sender_account_id` が空の場合、Chatwork API からメッセージ情報を取得して補完
4. `clients/00_common_rules.md` + メンバー個別の `.md` をプロンプトに組み込む
5. Claude Code を実行して返信文を生成
6. Chatwork API 経由でルームに返信（`[rp]` タグ自動付与）
7. 返信に「確認します」等のキーワードが含まれる場合、フォローアップ処理を実行
   - `FOLLOWUP_WAIT_SECONDS` 秒待機
   - ルーム情報（メンバー一覧・直近メッセージ）を収集
   - 収集した情報を元に再度 Claude Code を実行してフォローアップ返信
   - 完了後「おやすみなさい」を発言

## 設定パラメータ（config.env）

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `FOLLOWUP_WAIT_SECONDS` | 30 | フォローアップ返信までの待機秒数 |

## 前提条件

- Python 3.x
- AWS CLI v2
- Claude Code（`claude` コマンドが使えること）
- AWS SQS キューおよび Chatwork Webhook の設定が完了していること

## 変更履歴

### v0.6.0 (2026-03-25)
- **feat**: フォローアップ自動返信機能
  - 「確認します」「調べます」等のキーワードを検出し、待機後に情報収集→再返信
  - 待機秒数を `FOLLOWUP_WAIT_SECONDS` で設定可能
  - フォローアップ完了後「おやすみなさい」を発言
  - 発生経緯: 藤野が「少し確認します！」と返信したが、claude -p はワンショット実行のため後続のフォローアップができなかった

### v0.5.0 (2026-03-25)
- **fix**: `00_common_rules.md` から `[rp]` タグ組み立て指示を削除
  - コード側で `[rp]` タグを自動付与するため、AI に組み立てさせる指示を除去
  - 発生経緯: AI が `[rp]` タグを出力 + コード側でも付与 → 名前が二重に表示された

### v0.4.0 (2026-03-25)
- **fix**: `find_target_member` で `[rp aid=ACCOUNT_ID` パターンも検出
  - `[To:]` のみチェックしていたため、`[rp]` でメンションされたメンバーが特定できずデフォルトの横田にフォールバックしていた
  - 発生経緯: 飛峪が藤野に `[rp]` で話しかけると、横田が代わりに返答していた

### v0.3.0 (2026-03-25)
- **feat**: Chatwork API で sender 情報を補完（`get_message_info` 関数）
  - SQS メッセージの `sender_account_id` が空の場合、Chatwork API からメッセージ情報を取得
  - 発生経緯: Lambda 側の問題で `sender_account_id` が空文字で渡されていた
- **fix**: 共通ルール読み込みを `00_*.md` に限定
  - `SCRIPT_DIR` 直下の `*.md` を全て読んでいたため、`log.md` 等が指示ファイルとして誤読み込みされていた

### v0.2.0 (2026-03-25)
- **feat**: 共通ルール + `[rp]` タグ自動付与
  - `clients/00_common_rules.md` で全メンバー共通ルールを管理
  - コード側で `[rp]` タグを自動構築し、AI には返信本文のみ出力させる
  - `sender_name` と `message_id` をプロンプトに追加
  - 発生経緯: 横田の返信で `[rp]` タグが壊れていた（aid 空、名前抜け、メッセージID間違い）

### v0.1.0 (2026-03-25)
- **feat**: 初版リリース
  - SQS キューからメッセージを直列処理
  - Claude Code バッチ実行（`claude -p`）
  - 複数メンバー対応（横田百恵・藤野楓）
  - `config.env` による AWS クレデンシャル管理
  - エラー時はグリ姉アカウントで報告ルームに通知
