# OpenCodeReview GitHub Actions セットアップガイド

このリポジトリは `yohi` 配下の全リポジトリのデフォルト設定を管理する **dot-github リポジトリ** です。Alibaba 製 AI コードレビューツール **OpenCodeReview (OCR)** を **再利用ワークフロー (Reusable Workflow)** として提供しています。

## 概要

OpenCodeReview は、PR の差分を LLM に送信してレビューコメントを生成する CLI ツールです。Claude Code などの汎用エージェントと比較してトークン消費が約 1/9 で、高精度なレビュー結果が得られます。

このリポジトリのワークフロー自体がレビューを実行するのではなく、**dotfiles などの各リポジトリに配置した薄い呼び出しワークフローが `uses:` で呼び出す** 構成になっています。トリガー条件は呼び出し側で設定します:

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

呼び出し側リポジトリ (dotfiles など) は以下のように設定します:

### 呼び出し側ワークフローの例

各リポジトリの `.github/workflows/ocr-review.yml` として配置:

```yaml
name: OpenCodeReview

on:
  pull_request_target:
    types: [opened, synchronize, reopened, ready_for_review]
  issue_comment:
    types: [created]

jobs:
  call-ocr-review:
    if: >-
      github.event_name == 'pull_request_target' ||
      (github.event_name == 'issue_comment' &&
       github.event.issue.pull_request &&
       (startsWith(github.event.comment.body, '/open-code-review') ||
        startsWith(github.event.comment.body, '@open-code-review')))
    uses: yohi/.github/.github/workflows/ocr-review.yml@master
    secrets:
      OCR_LLM_URL: ${{ secrets.OCR_LLM_URL }}
      OCR_LLM_AUTH_TOKEN: ${{ secrets.OCR_LLM_AUTH_TOKEN }}
      OCR_LLM_MODEL: ${{ secrets.OCR_LLM_MODEL }}
```

サンプルファイル: [`.github/workflows/caller-example.yml`](../.github/workflows/caller-example.yml)

### 呼び出し側の Secrets 設定

**Settings → Secrets and variables → Actions** で以下を登録してください (呼び出し元リポジトリごとに必要)。
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

### 中央管理ファイル (このリポジトリ)

このリポジトリで管理されるファイル:

```
.github/workflows/ocr-review.yml                  # Reusable Workflow (workflow_call)
.github/workflows/caller-example.yml              # 呼び出し側のサンプル
.github/workflows/scripts/post-ocr-comments.js    # コメント投稿スクリプト (Reusable から curl で取得)
```

### Secrets のスコープ

- **呼び出し側 (dotfiles 等)**: `OCR_LLM_URL` / `OCR_LLM_AUTH_TOKEN` / `OCR_LLM_MODEL` を登録
- **このリポジトリ自体**: この `.github` リポジトリで PR を作成した場合に動作させたい場合のみ Secrets を登録

### 3. ブランチ保護ルールの確認 (呼び出し側リポジトリ)

マージをブロックする必要がある場合は、ブランチ保護ルールを手動で設定してください。

1. **Settings → Branches → Add branch protection rule**
2. Branch name pattern: `main` (または対象ブランチ)
3. **Require status checks to pass before merging** にチェック
4. ステータスチェック検索で `call-ocr-review / ocr-review` を選択して追加

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

呼び出し側リポジトリのワークフローで `ocr-version` input を指定します。

```yaml
jobs:
  call-ocr-review:
    uses: yohi/.github/.github/workflows/ocr-review.yml@master
    with:
      ocr-version: "1.0.0"
    secrets:
      OCR_LLM_URL: ${{ secrets.OCR_LLM_URL }}
      OCR_LLM_AUTH_TOKEN: ${{ secrets.OCR_LLM_AUTH_TOKEN }}
      OCR_LLM_MODEL: ${{ secrets.OCR_LLM_MODEL }}
```

大規模な PR やレート制限が厳しい場合は、呼び出し側で `concurrency` input を変更してください。

```yaml
    with:
      concurrency: 3
```

### GitHub App での認証 (推奨オプション)

デフォルトでは呼び出し側の `secrets.GITHUB_TOKEN` を使用してコメントを投稿しますが、GitHub App を使用するとより厳格な権限管理が可能です。再利用ワークフロー内で `actions/create-github-app-token@v1` を使用する形にカスタマイズしてください。

#### GitHub App の作成

1. **Settings → Developer settings → GitHub Apps → New GitHub App**
2. 以下の権限を付与:
   - Pull requests: Read & Write
   - Issues: Read & Write
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

#### ワークフローへの追加設定

呼び出し側 (caller workflow) は `uses:` で再利用ワークフローを呼び出すため、GitHub App トークン生成と `secrets.GITHUB_TOKEN` の置換手順は再利用ワークフロー (`.github/workflows/ocr-review.yml`) 側に配置し、Secrets も引き渡す必要があります。

##### 1. 再利用ワークフロー (`.github/workflows/ocr-review.yml`) 側の設定

Secrets の受け取り宣言を追加します。

```yaml
on:
  workflow_call:
    secrets:
      OCR_LLM_URL:
        required: true
      OCR_LLM_AUTH_TOKEN:
        required: true
      OCR_LLM_MODEL:
        required: true
      GITHUB_APP_ID:
        required: false
      GITHUB_APP_PRIVATE_KEY:
        required: false
      GITHUB_APP_INSTALLATION_ID:
        required: false
```

ジョブの最初にトークン生成ステップを追加します。

```yaml
    steps:
      - name: Generate GitHub App token
        if: ${{ secrets.GITHUB_APP_ID != '' }}
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.GITHUB_APP_ID }}
          private-key: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
          installation-id: ${{ secrets.GITHUB_APP_INSTALLATION_ID }}
          permission-pull-requests: write
          permission-issues: write
          permission-contents: read
```

その後、`ocr-review.yml` 内の `GITHUB_TOKEN` の参照箇所を以下のように更新します。

```yaml
      - name: Post review comments
        if: always()
        env:
          GITHUB_TOKEN: ${{ steps.app-token.outputs.token || secrets.GITHUB_TOKEN }}
```

##### 2. 呼び出し側ワークフロー (`caller-example.yml` 等) 側の設定

呼び出し側では Secret を再利用ワークフローへ引き渡すよう設定します。

```yaml
    secrets:
      OCR_LLM_URL: ${{ secrets.OCR_LLM_URL }}
      OCR_LLM_AUTH_TOKEN: ${{ secrets.OCR_LLM_AUTH_TOKEN }}
      OCR_LLM_MODEL: ${{ secrets.OCR_LLM_MODEL }}
      GITHUB_APP_ID: ${{ secrets.GITHUB_APP_ID }}
      GITHUB_APP_PRIVATE_KEY: ${{ secrets.GITHUB_APP_PRIVATE_KEY }}
      GITHUB_APP_INSTALLATION_ID: ${{ secrets.GITHUB_APP_INSTALLATION_ID }}
```

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

### コメントが特定の行に投稿されない・スキップされる

**原因**: レビュー実行結果に含まれるファイル・行番号が、PR の Diff（変更差分）の範囲外にある場合。

**対処**: `post-ocr-comments.js` は PR の Diff 範囲内にある行のみにインラインコメントを投稿します。Diff 外へのコメントはスキップされます。必要に応じて PR を更新し、再度コメント (`/open-code-review`) でレビューを実行してください。

### `API error 403` (GitHub App 使用時)

**原因**: GitHub App の権限が不足している、または Installation ID が間違っている。

**対処**: GitHub App の権限設定と Secrets の値を再確認してください。

## デバッグ

ワークフローが失敗した場合、以下のファイルがアーティファクトとしてアップロードされます。

- `ocr-debug-logs/ocr-result.json`: OCR の生出力
- `ocr-debug-logs/ocr-stderr.log`: 標準エラー出力

**Actions → 該当ワークフロー → Artifacts** からダウンロードして内容を確認してください。

## 導入モデルの比較: Reusable Workflow 方式 vs GitHub App 方式 (Zero-YAML)

OpenCodeReview の運用・展開方法には、本ドキュメントで解説している **Reusable Workflow (再利用ワークフロー) 方式** に加えて、各リポジトリへのファイル配置を完全にゼロにする **GitHub App 方式** が存在します。

| 比較項目 | A. Reusable Workflow 方式 (現行) | B. GitHub App 方式 (ゼロYAML構成) |
| :--- | :--- | :--- |
| **各リポジトリ側の設定** | **必要** (`.github/workflows/ocr-review.yml` のコピーが必要) | **不要**（リポジトリ側の YAML や設定ファイルは 0 行） |
| **セットアップ体験** | 各リポジトリに呼び出し用 YAML をコミット | アプリを対象リポジトリ（または Org 全体）に「インストール」するだけ |
| **Secrets の管理** | 各リポジトリ or Organization Secrets | Webhook サーバー（バックエンド）側で一元管理 |
| **実行環境 / インフラ** | GitHub Actions (GitHub ランナー) | 外部サーバー (Cloud Run / AWS Lambda / 独自VPS など) |
| **メンテナンス** | `yohi/.github` 側のワークフロー更新が全リポジトリに反映 | Webhook サーバー側のロジック更新が全リポジトリに反映 |

### B. GitHub App 方式（Zero-YAML インストール）のアーキテクチャ概要

各リポジトリ側に `.github/` や YAML ファイルを 1 行も置きたくない場合は、Webhook をトリガーとする GitHub App 構成を採用します。

```mermaid
graph TD
    PR[Pull Request 作成/更新] -->|GitHub Webhook| AppServer[GitHub App Webhook サーバー]
    
    subgraph "External Server (Cloud Run / Lambda / VPS)"
        AppServer -->|1. Webhook 受信| Auth[GitHub App Token 発行]
        Auth -->|2. Diff 取得 & Checkout| Engine[OCR Engine (npx @alibaba-group/open-code-review)]
        Engine -->|3. LLM API 呼び出し| LLM[LLM Provider (OpenAI/Anthropic/DeepSeek)]
        Engine -->|4. レビュー結果パース| Poster[GitHub API Review Commenter]
    end

    Poster -->|5. Post Comments| PRComment[PR に直接インラインコメント投稿]
```

#### GitHub App 方式の構築ステップ:
1. **GitHub App の作成**: GitHub Developer Settings で App を作成し、`Pull requests (Read/Write)` および `Contents (Read)` の権限と Webhook URL を設定。
2. **Webhook サーバーのデプロイ**: Webhook を受信した際に `ocr review` を実行し、結果を GitHub API で PR コメントとして返却するマイクロサービスをデプロイ。
3. **インストール**: レビューを行いたいリポジトリ（またはアカウント全体）に作成した App をインストール。これだけで、対象リポジトリで PR を作成すると自動的にレビューが動作します。

---

## 参考リンク

- [OpenCodeReview GitHub リポジトリ](https://github.com/alibaba/open-code-review)
- [OCR CI/CD ドキュメント](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/integrations/ci.md)
- [OCR 設定ガイド](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/configuration.md)
- [OCR CLI リファレンス](https://github.com/alibaba/open-code-review/blob/main/pages/src/content/docs/en/cli-reference.md)

