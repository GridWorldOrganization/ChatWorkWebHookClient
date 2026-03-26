# Contributing

ClaudeWorkMulti へのコントリビューションを歓迎します。

## 開発環境

- Python 3.12+
- Windows PC（ポーラーの動作確認用）
- ChatWork アカウント（テスト用）
- AWS アカウント（SQS キュー）

## コントリビューションの流れ

1. このリポジトリを Fork する
2. Feature ブランチを作成する (`git checkout -b feature/my-feature`)
3. 変更をコミットする (`git commit -m 'Add my feature'`)
4. ブランチを Push する (`git push origin feature/my-feature`)
5. Pull Request を作成する

## コーディング規約

- Python コードは既存のスタイルに合わせる
- 関数には docstring を記述する
- config.env に新しいパラメータを追加した場合は `config.env.example` と `README.md` の設定一覧も更新する
- バッチファイル内の表示メッセージは英語（日本語はバッチの括弧構文と競合するため）

## バグ報告

[Issues](https://github.com/GridWorldOrganization/ClaudeWorkMulti/issues) から報告してください。

以下を含めると解決が早くなります：
- 再現手順
- 期待する動作
- 実際の動作（ログ出力）
- `config.env` の関連パラメータ（トークン等の機密情報は除く）
