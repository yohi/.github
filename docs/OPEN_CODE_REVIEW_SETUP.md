# OpenCodeReview GitHub Actions セットアップガイド

このリポジトリには、Alibaba 製 AI コードレビューツール **OpenCodeReview (OCR)** を GitHub Actions で実行するためのワークフローが含まれています。

## 概要

OpenCodeReview は、PR の差分を LLM に送信してレビューコメントを生成する CLI ツールです。Claude Code などの汎用エージェントと比較してトークン消費が約 1/9 で、高精度なレビュー結果が得られます。

このワークフローは以下のタイミングで OCR を実行します。

- PR が開かれたとき (`pull_request_target: opened`)
- PR に新しいコミットがプッシュされたとき (`pull_request_target: synchronize`)
- PR が再起動またはレビュー準備完了になったとき (`pull_request_target: reopened, ready_for_review`)
- PR に `/open-code-review` または `@open-code-review` というコメントが投稿されたとき

レビュー結果は PR の差分行にインラインコメントとして投稿されます。

## 前提条件

- GitHub リポジトリの管理者権限 (Secrets / Variables の設定が必要)
- LLM プロバイダの API エンドポイントと API キー (OpenAI, Anthropic, DeepSeek など)
- Git >= 2.41
- Node.js >= 14 (ワークフロー内では Node 20 を使用)

## セットアップ手順

### 1. リポジトリ Secrets の設定

**Settings → Secrets and variables → Actions** で以下の Secret を登録してください。

| Secret 名 | 必須 | 説明 | 例 |
|---|---|---|---|
| `OCR_LLM_URL` | ✅ | LLM API のエンドポイント URL | `https://api.openai.com/v1/chat/completions`<br>`https://api.anthropic.com/v1/messages` |
| `OCR_LLM_AUTH_TOKEN` | ✅ | LLM API の認証トークン | `sk-...` または `sk-ant-...` |
| `OCR_LLM_MODEL` | ✅ | 使用するモデル名 (デフォルトなし) | `gpt-4o`, `claude-opus-4-6`, `deepseek-chat` |

> [!WARNING]
> `OCR_LLM_AUTH_TOKEN` は機密情報です。必ず Secrets に登録し、コードやログに直接書かないでください。

### 2. (任意) Repository Variables の設定

Anthropic Claude を使用する場合は、Variables で以下の変数を設定します。

| Variable 名 | 値 | 説明 |
|---|---|---|
| `OCR_LLM_USE_ANTHROPIC` | `true` または `false` | `true` にすると Anthropic プロトコルを使用。デフォルトは `false` (OpenAI 互換) |

### 3. ワークフローファイルの配置

このリポジトリでは既に以下のファイルが配置されています。

```
.github/workflows/ocr-review.yml           # メインの OCR ワークフロー
.github/workflows/scripts/post-ocr-comments.js  # レビューコメント投稿スクリプト
```

他リポジトリに導入する場合は、これらを同じパスにコピーしてください。

### 4. ブランチ保護ルールの確認

マージをブロックする必要がある場合は、ブランチ保護ルールを手動で設定してください。

1. **Settings → Branches → Add branch protection rule**
2. Branch name pattern: `main` (または対象ブランチ)
3. **Require status checks to pass before merging** にチェック
4. ステータスチェック検索で `ocr-review` を選択して追加

> [!NOTE]
> OCR 自体はコメントを投稿するだけでマージをブロックしません。ブロックしたい場合はブランチ保護ルールで対応してください。

## 使用方法

### 自動レビュー

対象ブランチに向けた PR を作成または更新すると、自動的に OCR が差分をレビューしてコメントを投稿します。

### 手動再レビュー

PR に以下のいずれかのコメントを投稿すると、再度 OCR が実行されます。

```
/open-code-review
```

または

```
@open-code-review
```

### ローカルでの動作確認

PR を作成する前に、ローカルで OCR の動作を確認できます。

```bash
# インストール
npm install -g @alibaba-group/open-code-review

# 設定 (初回のみ)
ocr config set llm.url "https://api.openai.com/v1/chat/completions"
ocr config set llm.auth_token "sk-..."
ocr config set llm.model "gpt-4o"

# レビュー実行
ocr review --from main --to feature-branch
```

## カスタマイズ

### バージョンの固定

`.github/workflows/ocr-review.yml` のインストール行を変更してバージョンを固定できます。

```yaml
# 変更前
- run: npm install -g @alibaba-group/open-code-review@latest

# 変更後 (例: v1.0.0 に固定)
- run: npm install -g @alibaba-group/open-code-review@1.0.0
```

### 並列数の調整

大規模な PR やレート制限が厳しい場合は、`--concurrency` の値を変更してください。

```yaml
# ocr-review.yml 内の該当行を変更
ocr review \
  --concurrency 3 \  # デフォルトは 5
  ...
```

### GitHub App での認証 (推奨オプション)

デフォルトでは `GITHUB_TOKEN` を使用してコメントを投稿しますが、GitHub App を使用するとより厳格な権限管理が可能です。

#### GitHub App の作成

1. **Settings → Developer settings → GitHub Apps → New GitHub App**
2. 以下の権限を付与:
   - Pull requests: Read & Write
   - Contents: Read-only
   - Metadata: Read-only
3. Private key を生成してダウンロード
4. App ID と Installation ID を記録

#### Secrets に App 情報を登録

| Secret 名 | 説明 |
|---|---|
| `GITHUB_APP_ID` | GitHub App の App ID |
| `GITHUB_APP_PRIVATE_KEY` | ダウンロードした Private key の内容 |
| `GITHUB_APP_INSTALLATION_ID` | App をインストールしたリポジトリの Installation ID |

#### ワークフローにトークン生成ステップを追加

`.github/workflows/ocr-review.yml` の最初に以下のステップを追加してください。

```yaml
    steps:
      - name: Generate GitHub App token
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.GITHUB_APP_ID }}
          private-key: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
          installation-id: ${{ secrets.GITHUB_APP_INSTALLATION_ID }}
          permission-pull-requests: write
          permission-contents: read
```

その後、`secrets.GITHUB_TOKEN` の使用箇所を `${{ steps.app-token.outputs.token }}` に置き換えてください。

### カスタムレビュールール

特定のファイルパターンに対してルールを適用したい場合は、`--rule` オプションを使用できます。

```bash
ocr review --rule ./review-rules.json --from main --to feature-branch
```

ルールファイルの書式については [OCR 公式ドキュメント](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/review-rules.md) を参照してください。

### thinking-mode の無効化

現在のワークフローは互換性のため thinking-mode を無効化しています。

```bash
ocr config set llm.extra_body '{"thinking": {"type": "disabled"}}'
```

使用する LLM プロバイダが thinking-mode を必須とする場合は、この行を削除または変更してください。

## トラブルシューティング

### `Cannot find merge-base` エラー

**原因**: shallow clone によって履歴が不足している。

**対処**: `.github/workflows/ocr-review.yml` の `actions/checkout` で `fetch-depth: 0` が設定されていることを確認してください。

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # この行が必要
```

### `Failed to parse OCR output` エラー

**原因**: LLM の URL または認証トークンが間違っている。

**対処**: Secrets の `OCR_LLM_URL` と `OCR_LLM_AUTH_TOKEN` を再確認してください。ワークフロー実行時に `/tmp/ocr-stderr.log` にエラー詳細が記録されます。

### コメントが間違った行に投稿される

**原因**: レビュー実行とコメント投稿の間で差分が変わった。

**対処**: 自動的に通常の Issue コメントにフォールバックします。PR を更新して再レビューしてください。

### `API error 403` (GitHub App 使用時)

**原因**: GitHub App の権限が不足している、または Installation ID が間違っている。

**対処**: GitHub App の権限設定と Secrets の値を再確認してください。

## デバッグ

ワークフローが失敗した場合、以下のファイルがアーティファクトとしてアップロードされます。

- `ocr-debug-logs/ocr-result.json`: OCR の生出力
- `ocr-debug-logs/ocr-stderr.log`: 標準エラー出力

**Actions → 該当ワークフロー → Artifacts** からダウンロードして内容を確認してください。

## 参考リンク

- [OpenCodeReview GitHub リポジトリ](https://github.com/alibaba/open-code-review)
- [OCR CI/CD ドキュメント](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/integrations/ci.md)
- [OCR 設定ガイド](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/configuration.md)
- [OCR CLI リファレンス](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/cli-reference.md)
