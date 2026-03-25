# ChatWork Webhook Client

ChatWork のメッセージを SQS 経由で受信し、Claude Code を使って AI が自動返信するシステムです。
Windows PC 上で動作します。

> **注意: ポーラーは必ず1台のPCでのみ起動してください。** 2台同時に動くと同じメッセージを二重処理します。

## 構成

```
ChatWorkWebHookClient/
├── windows_poller.py          # メイン: SQSポーリング + Claude Code 実行 + Chatwork返信
├── start_poller.bat           # 起動スクリプト（ダブルクリックで起動）
├── setup_windows.bat          # 初回セットアップ（AWS CLI設定等）
├── config.env                 # 環境変数（※自分で作成。Gitに含まれない）
├── config.env.example         # ↑のテンプレート
├── members/
│   ├── 00_common_rules.md     # 全メンバー共通ルール（Gitに含まれる）
│   ├── templates/             # テンプレート（Gitに含まれる）
│   │   ├── 01_persona.md.example
│   │   ├── mode.env.example
│   │   └── setup_member.bat
│   ├── 01_yokota/             # 横田百恵の設定（※Gitに含まれない）
│   │   ├── 01_persona.md      # ペルソナ設定
│   │   ├── mode.env           # 会話モード設定
│   │   ├── CLAUDE.md          # Claude Code が自動読み込みする記憶（任意）
│   │   ├── room_426936385.md  # ルーム別口調設定（任意）
│   │   ├── chat_history_*.md  # 会話記録（自動生成）
│   │   └── rejected_rooms.log # 拒否ログ（自動生成）
│   └── 02_fujino/             # 藤野楓の設定（同上）
└── .gitignore
```

## セットアップ手順

### 1. リポジトリを取得

```
git clone https://github.com/GridWorldOrganization/ChatWorkWebHookClient
cd ChatWorkWebHookClient
```

### 2. config.env を作成

`config.env.example` をコピーして `config.env` を作成し、**実際の値** を設定します。

```
copy config.env.example config.env
```

> **config.env にはAPIトークン等の機密情報が入ります。絶対にGitにコミットしないでください。**（.gitignore で除外済み）

### 3. 初回セットアップ

`setup_windows.bat` をダブルクリックで実行します。以下を自動チェック・セットアップします：

1. Python 確認
2. pip パッケージインストール（boto3, requests）
3. Claude Code 確認
4. AWS CLI 確認
5. AWS プロファイル設定

### 4. メンバーフォルダを作成

```
cd members\templates
setup_member.bat
```

メンバーフォルダ名（例: `01_yokota`）を入力するとフォルダが作成され、テンプレートがコピーされます。

### 5. ペルソナを設定

`members\01_yokota\01_persona.md` をテキストエディタで開き、キャラクター設定を記入します。

設定項目: 性格・話し方・趣味・最近の出来事・口癖・苦手なもの等。
詳細は `members/templates/01_persona.md.example` を参照。

### 6. 会話モードを設定

`members\01_yokota\mode.env` を作成（テンプレート: `members/templates/mode.env.example`）。
詳細は「会話モード」セクション参照。

### 7. 起動

`start_poller.bat` をダブルクリックします。

起動時に以下がログに表示されれば正常です：
```
=== Chatwork Webhook Poller 起動 ===
=== config.env パラメータ ===
  CLAUDE_COMMAND=claude
  CLAUDE_MODEL=claude-haiku-4-5
  CLAUDE_TIMEOUT=60秒
  FOLLOWUP_WAIT_SECONDS=30秒
  MAX_AI_CONVERSATION_TURNS=10ターン
  REPLY_COOLDOWN_SECONDS=15秒
  横田 百恵 (01_yokota): 指示ファイル 1件, cwd=...\members\01_yokota
  藤野 楓 (02_fujino): 指示ファイル 1件, cwd=...\members\02_fujino
```

**停止方法:** Ctrl+C で安全に停止します（処理中のメッセージは完了してから終了）。

## 動作の仕組み

### 基本フロー

1. SQS キューを**空になるまで全件読み込み**
2. 宛先メンバーごとにメッセージをグループ化（自分自身のメッセージは自動除外）
3. メンバーごとに**並列**で以下を実行：
   - 複数メッセージが溜まっていた場合、先行分を文脈として含め、最後の1件に対して返信
   - `members/00_common_rules.md` + メンバー個別の `.md` をプロンプトに組み込む
   - Claude Code（`claude -p --model`）を実行して返信文を生成
4. Chatwork API 経由でルームに返信（`[rp]` タグ自動付与）
5. 会話記録を `chat_history_{ルームID}.md` に保存

### 特殊処理

| 機能 | 動作 |
|------|------|
| **[rp]タグ自動付与** | AI出力に`[To:]`や`[rp]`がなければ、コード側で送信者への`[rp]`を自動付与 |
| **[To:]自発発言** | AIが送信者以外に話しかける場合、`[To:アカウントID]名前さん` を出力可能 |
| **フォローアップ** | 「確認します」等のキーワード検出 → 待機 → 情報収集 → 再返信 |
| **AI会話チェーン** | 人間の発言で開始、AI同士は `MAX_AI_CONVERSATION_TURNS` で自動停止 |
| **連投防止** | 同一メンバーは前回発言から `REPLY_COOLDOWN_SECONDS` 秒待機 |
| **sender補完** | SQSのsender_account_idが空の場合、Chatwork APIから自動取得 |
| **ルーム別口調** | `room_{ルームID}.md` があればそのルーム専用の指示を追加読み込み |
| **CLAUDE.md** | メンバーフォルダに `CLAUDE.md` を置くとClaude Codeが自動で読み込む（記憶・指示用） |
| **許可外ルーム拒否** | ホワイトリスト外のルームはClaude起動せず `rejected_rooms.log` に記録 |

## 設定パラメータ（config.env）

### 必須

| パラメータ | 説明 |
|-----------|------|
| `SQS_QUEUE_URL` | SQSキューのURL |
| `CW_TOKEN_GURIKO` | グリ姉のChatwork APIトークン（エラー報告用） |
| `CW_TOKEN_YOKOTA` | 横田百恵のChatwork APIトークン |
| `CW_TOKEN_FUJINO` | 藤野楓のChatwork APIトークン |
| `CW_ERROR_ROOM_ID` | エラー報告先のChatworkルームID |

### オプション

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `AWS_PROFILE` | (なし) | AWSプロファイル名。未設定なら`AWS_ACCESS_KEY_ID`で直接認証 |
| `CLAUDE_COMMAND` | claude | Claude Code のコマンドパス。PATHで見つからない場合にフルパス指定 |
| `CLAUDE_MODEL` | claude-haiku-4-5 | 使用モデル（`claude-haiku-4-5` / `claude-sonnet-4-6` / `claude-opus-4-6`） |
| `CLAUDE_TIMEOUT` | 60 | Claude Code 実行タイムアウト（秒） |
| `FOLLOWUP_WAIT_SECONDS` | 30 | フォローアップ返信までの待機（秒） |
| `MAX_AI_CONVERSATION_TURNS` | 10 | AI同士の会話上限メッセージ数 |
| `REPLY_COOLDOWN_SECONDS` | 15 | 同一メンバーの連投防止クールダウン（秒） |
| `ALLOWED_ROOMS_YOKOTA` | (空=全許可) | 横田の許可ルームID（カンマ区切り） |
| `ALLOWED_ROOMS_FUJINO` | (空=全許可) | 藤野の許可ルームID（カンマ区切り） |
| `MAINTENANCE_ROOM_ID` | (空) | メンテナンスコマンドを受け付けるルームID |

## 会話モード

4種類の会話モードがあり、メンバーごと・ルームごとに設定できます。

| モード | 名前 | 説明 |
|--------|------|------|
| 0 | メンテナンス | 機械的に端的。改行禁止。1行で回答。絵文字・雑談・感情表現禁止 |
| 1 | 業務 | 端的に短くわかりやすく。丁寧語だが装飾・雑談なし。1〜3行 |
| 2 | ペルソナ | ペルソナ設定に準拠し感情豊かに話す。キャラクターらしい口調 |
| 3 | ペルソナ+ | ペルソナに加え、ルーム内の他メンバーに時折話を振る（3〜4回に1回） |

### 設定方法（メンバーフォルダの mode.env）

```env
# デフォルト（0=メンテナンス/1=業務/2=ペルソナ/3=ペルソナ+）
TALK_MODE=2

# ルーム別（ルームID:モード）
TALK_MODE=426936385:3
TALK_MODE=427388771:1
```

上記例: ルーム426936385ではペルソナ+、427388771では業務、その他はペルソナ

`mode.env` がなければデフォルト1（業務）。テンプレートは `members/templates/mode.env.example`。

**優先順位:** ルーム別(ルームID:モード) > デフォルト(TALK_MODE) > 1(業務)

## メンテナンスコマンド

`MAINTENANCE_ROOM_ID` で指定したルームで、メンバー宛に以下のコマンドを送信できます。
Claudeは起動せず、即座に結果を返します。

| コマンド | 説明 |
|---------|------|
| `/status` | メンバーの設定状況（.mdファイル一覧、会話モード、パラメータ値） |
| `/session` | 全メンバーのClaude実行状態（実行中/停止中、経過秒数、モデル名） |

## メンバーの追加方法

1. `members/templates/setup_member.bat` でフォルダ作成
2. `01_persona.md` にキャラクター設定を記入
3. `mode.env` に会話モードを設定
4. `windows_poller.py` の `MEMBERS` に新メンバーを追加
5. `config.env` に `CW_TOKEN_新メンバー=...` と `ALLOWED_ROOMS_新メンバー=...` を追加
6. ポーラー再起動

## 前提条件

- Windows 10/11
- Python 3.x
- Claude Code（`claude` コマンドが使えること）
- AWS SQS キューおよび Chatwork Webhook（Lambda）の設定が完了していること

## トラブルシューティング

| 症状 | 原因・対処 |
|------|-----------|
| 起動時「必須環境変数が未設定」 | `config.env` が存在しないか、トークンが空 |
| 返信が来ない | ログで `Claude Code タイムアウト` を確認。`CLAUDE_TIMEOUT` を増やす |
| 二重返信が出る | 2台でポーラーが動いていないか確認。1台のみにする |
| AI同士が止まらない | `MAX_AI_CONVERSATION_TURNS` を下げる |
| 連続で同じ質問をぶつける | `REPLY_COOLDOWN_SECONDS` を上げる |
| `Claude Code が見つかりません: claude` | 下記「PATHの設定」を参照 |
| Ctrl+Cで停止しない | 処理中のメッセージ完了を待っています。しばらく待ってください |

### PATHの設定

`claude` コマンドが `start_poller.bat`（cmd.exe）から見つからない場合：

**1. claude のインストール先を確認（PowerShell）**
```powershell
where.exe claude
```

**2. PATH に追加（PowerShell）**
```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\ユーザー名\AppData\Roaming\npm", "User")
```

**3. ウィンドウを開き直して** `start_poller.bat` を再実行。

または `config.env` に `CLAUDE_COMMAND=C:\...\claude.cmd` でフルパス指定も可能。

> `claude install` でネイティブビルドに切り替えた場合、インストール先が異なります。`where.exe claude` で確認してください。
